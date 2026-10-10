"""Job specs for the National Research Platform runs (docs/nrp_runbook.md; docs/deviations.md, 2026-10-11).

Every remaining stage is written once, on the Mac, as a spec file ``specs/<stage>.jsonl`` (one queue job per line)
with a manifest. Run ids are computed with a pinned code reference (``code_ref``, the git tag ``nrp-code-v1``)
instead of the generating commit, so the Mac and the cluster compute the same ids and the results merge by id.
Building specs is pure: it reads tracked files only (splits, tuned hyperparameters, committed results for the
checkpoint index, the GPU benchmark), and uses no GPU and no network.

Stages, programme group (priority order) and job counts for the v1 backbone:
    N2a  relax 818 (minus the hosts already relaxed, ``hosts``), peval 183, embed 240, geomeval 180
    N2b  loco 30, moment 60, cgcnn 18, capped 33 (POST HOC)
    N3   cv 180 per backbone (EXTENSION): {S, D} x K in {10, 20} x folds x seeds 0-2
    N4   precision 480 (EXTENSION): {S, D} x B in {400, 654} x (r = 10..29 x seeds 0-4 + r = 0..9 x seeds 3, 4)
The N2a and N2b stages reuse the S12 builders (``dftgnn.train.s12``) unchanged.
"""
from __future__ import annotations

import functools
import hashlib
import json
from collections import Counter
from pathlib import Path

from dftgnn.config import Config, load_config
from dftgnn.split import SPLITS_DIR, budget_train, load_split
from dftgnn.split.cv import CV_KS, CV_NAME, split_name
from dftgnn.split.ext import EXT_RESAMPLES
from dftgnn.train import RunSpec, resolve_hosts, run_id
from dftgnn.train import s12 as S12
from dftgnn.train.stages import TUNED, _job, load_tuned, tuned_hparams

REPO_ROOT = Path(__file__).resolve().parents[3]
SPECS_DIR = REPO_ROOT / "specs"
CODE_REF = "nrp-code-v1"
STAGES = ("relax", "peval", "embed", "geomeval", "loco", "moment", "cgcnn", "capped", "cv", "precision")
GROUP = {"relax": "N2a", "peval": "N2a", "embed": "N2a", "geomeval": "N2a", "loco": "N2b", "moment": "N2b",
         "cgcnn": "N2b", "capped": "N2b", "cv": "N3", "precision": "N4"}
LABEL = {"relax": "registered", "peval": "registered", "embed": "registered",
         "geomeval": "registered (B = 200 DESCRIPTIVE EXTRA)", "loco": "registered", "moment": "registered",
         "cgcnn": "registered", "capped": "POST HOC", "cv": "EXTENSION", "precision": "EXTENSION"}
EXPECTED = {"relax": 818, "peval": 183, "embed": 240, "geomeval": 180, "loco": 30, "moment": 60, "cgcnn": 18,
            "capped": 33, "cv": 180, "precision": 480}
BACKBONES = ("v1", "v2")
V2_STAGES = ("cv", "precision")             # stages that get a v2 version once the v2 backbone is merged
PRIORITY_STRIDE = 100_000
PRECISION_BUDGETS = (400, 654)
PRECISION_NEW = (EXT_RESAMPLES, range(5))   # r = 10..29, seeds 0-4
PRECISION_REG = (range(10), (3, 4))         # r = 0..9, seeds 3 and 4
CV_SEEDS = (0, 1, 2)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read_hosts_file(path: Path) -> list[str]:
    """One host_id per line; blank lines and lines starting with '#' are ignored."""
    hosts = [ln.strip() for ln in Path(path).read_text().splitlines() if ln.strip() and not ln.startswith("#")]
    if len(set(hosts)) != len(hosts):
        raise ValueError(f"{path}: duplicate host ids")
    return sorted(hosts)


# ----------------------------------------------------------------------------------------- new stages
def build_cv(code: str, gsha: str, tuned: dict, cfg: Config, table: dict | None) -> list[dict]:
    """N3: S and D x K in {10, 20} x folds x seeds 0-2, a654 hyperparameters, results/cv/."""
    d = tuned["d_variant"]
    cv = load_split(CV_NAME)
    jobs = []
    for k in CV_KS:
        for f in cv["by_k"][str(k)]["folds"]:
            for s in CV_SEEDS:
                for m in ("S", d):
                    spec = RunSpec(model=m, **tuned_hparams(tuned, m, 654), split=split_name(k, f["fold"]),
                                   r=f["fold"], budget=f["n_train"], seed=s, results_subdir="cv",
                                   tags={"extension": "N3_cv", "k": k})
                    jobs.append(_job(spec, "cv", code, gsha, table=table))
    return jobs


def precision_cells() -> list[tuple[int, int, int]]:
    """(r, B, seed) of the precision extension: new resamples x seeds 0-4, then registered x seeds 3-4."""
    out = []
    for rs, seeds in (PRECISION_NEW, PRECISION_REG):
        out += [(r, b, s) for r in rs for b in PRECISION_BUDGETS for s in seeds]
    return out


def build_precision(code: str, gsha: str, tuned: dict, cfg: Config, table: dict | None) -> list[dict]:
    """N4: S and D at B = 400 and 654, hyperparameters by the registered budget-to-anchor map, results/precision/."""
    d = tuned["d_variant"]
    b2a = cfg.tuning.budget_to_anchor
    jobs = []
    for r, b, s in precision_cells():
        for m in ("S", d):
            spec = RunSpec(model=m, **tuned_hparams(tuned, m, b2a[b]), split=f"outer_r{r}", r=r, budget=b, seed=s,
                           results_subdir="precision", tags={"extension": "N4_precision"})
            jobs.append(_job(spec, "precision", code, gsha, table=table))
    return jobs


# ------------------------------------------------------------------------------------------- generator
def _benchmark() -> dict | None:
    from dftgnn.train import admission

    try:
        return admission.load_benchmark()
    except (OSError, KeyError):
        return None


def build_stage(stage: str, *, code_ref: str = CODE_REF, backbone: str = "v1", hosts: list[str] | None = None,
                tuned_path: Path = TUNED, cfg: Config | None = None) -> list[dict]:
    """Jobs of one stage, with ``code_ref``, ``backbone``, ``group``, ``label`` and a global ``priority``.

    ``hosts`` (relax and geomeval): the relax top-up list. relax builds only these hosts; geomeval drops the
    dependencies on hosts outside it (their relaxed geometry comes from the earlier, ingested runs).
    """
    from dftgnn.graphs.store import manifest_sha

    if stage not in STAGES:
        raise ValueError(f"unknown stage {stage!r}")
    if backbone not in BACKBONES:
        raise ValueError(f"unknown backbone {backbone!r}")
    if backbone == "v2":
        if stage not in V2_STAGES:
            raise ValueError(f"stage {stage!r} has a v1 version only")
        raise NotImplementedError("the v2 backbone is not merged yet; FINISH M2 wires it into cv and precision")
    cfg = cfg if cfg is not None else load_config()
    tuned, gsha, table, code = load_tuned(tuned_path), manifest_sha(), _benchmark(), code_ref
    if stage in ("peval", "embed", "geomeval"):
        prim = _primary()
    if stage == "relax":
        jobs = S12.build_relax(code)
        if hosts is not None:
            unknown = set(hosts) - {j["spec"]["host_id"] for j in jobs}
            if unknown:
                raise ValueError(f"hosts not in universe v1: {sorted(unknown)[:5]}")
            jobs = [j for j in jobs if j["spec"]["host_id"] in set(hosts)]
    elif stage == "peval":
        jobs = S12.build_peval(code, gsha, tuned, prim, cfg, table)
    elif stage == "embed":
        jobs = S12.build_embed(code, prim, cfg, table)
    elif stage == "geomeval":
        relax = S12.build_relax(code)
        keep = None if hosts is None else {j["run_id"] for j in relax if j["spec"]["host_id"] in set(hosts)}
        jobs = S12.build_geomeval(code, prim, relax, cfg, table)
        if keep is not None:
            jobs = [{**j, "after": [a for a in j["after"] if a in keep]} for j in jobs]
    elif stage == "loco":
        jobs = S12.build_loco(code, gsha, tuned, cfg, table)
    elif stage == "moment":
        jobs = S12.build_moment(code, gsha, tuned, cfg, table)
    elif stage == "cgcnn":
        jobs = S12.build_cgcnn(code, gsha, cfg, table)
    elif stage == "capped":
        jobs = S12.build_capped(code, gsha, table)
    elif stage == "cv":
        jobs = build_cv(code, gsha, tuned, cfg, table)
    else:
        jobs = build_precision(code, gsha, tuned, cfg, table)
    base = STAGES.index(stage) * PRIORITY_STRIDE
    out = []
    for i, j in enumerate(jobs):
        spec = dict(j["spec"])
        if "lr" in spec:                                   # RunSpec jobs: the runner reads code_ref from the spec
            spec["code_ref"] = code_ref
            if run_id(RunSpec.from_dict(spec), code_ref, gsha) != j["run_id"]:
                raise RuntimeError(f"run id of {j['run_id']} does not reproduce from its spec")
        out.append({**j, "spec": spec, "stage": stage, "code_ref": code_ref, "backbone": backbone,
                    "group": GROUP[stage], "tranche": GROUP[stage], "label": LABEL[stage], "priority": base + i})
    return out


def expected_count(stage: str, hosts: list[str] | None) -> int:
    return len(hosts) if stage == "relax" and hosts is not None else EXPECTED[stage]


def dumps_jsonl(jobs: list[dict]) -> bytes:
    return "".join(json.dumps(j, sort_keys=True, separators=(",", ":")) + "\n" for j in jobs).encode()


def manifest(stage: str, jobs: list[dict], body: bytes, *, jsonl_name: str, code_ref: str, backbone: str,
             hosts_file: Path | None, tuned_path: Path) -> dict:
    """Counts and hashes of a spec file; contains no time stamp, so it is reproducible."""
    from dftgnn.graphs.store import manifest_sha

    def rel(p: Path) -> str:
        p = Path(p).resolve()
        return str(p.relative_to(REPO_ROOT)) if p.is_relative_to(REPO_ROOT) else str(p)

    return {"stage": stage, "group": GROUP[stage], "label": LABEL[stage], "code_ref": code_ref,
            "backbone": backbone, "jsonl": jsonl_name, "sha256": hashlib.sha256(body).hexdigest(),
            "count": len(jobs), "counts_by_model": dict(sorted(Counter(j["spec"]["model"] for j in jobs).items())),
            "priority_range": [min(j["priority"] for j in jobs), max(j["priority"] for j in jobs)] if jobs else None,
            "graphs_manifest_sha256": manifest_sha(),
            "splits_manifest_sha256": sha256_file(SPLITS_DIR / "MANIFEST.sha256"),
            "tuned": {"path": rel(tuned_path), "sha256": sha256_file(tuned_path)},
            "hosts_file": None if hosts_file is None else {"path": rel(hosts_file), "sha256": sha256_file(hosts_file)},
            "generator": "scripts/queue/make_specs.py"}


# --------------------------------------------------------------------------------------------- checks
@functools.lru_cache(maxsize=1)
def _primary() -> dict:
    from dftgnn.train import runindex

    return runindex.primary(runindex.load())


def leakage_hosts(job: dict, cfg: Config | None = None) -> list[tuple[set, set]]:
    """(test hosts, train + validation hosts) of every model a job trains or evaluates; [] for relax."""
    cfg = cfg if cfg is not None else load_config()
    st, sp = job["stage"], job["spec"]
    if st == "relax":
        return []
    if "lr" in sp:
        h = resolve_hosts(RunSpec.from_dict(sp), cfg)
        return [(set(h["test"]), set(h["train"]) | set(h["val"]))]
    if st == "embed":
        s = load_split(f"outer_r{sp['r']}")
        return [(set(s["test"]), set(budget_train(s, sp["budget"])))]
    if st == "geomeval":
        from dftgnn.mlip import geomeval as GE

        out = []
        for rec in GE.components(_primary(), sp["geo_model"], sp["r"], sp["budget"], sp["seed"]).values():
            h = resolve_hosts(RunSpec.from_dict(rec["spec"]), cfg)
            out.append((set(h["test"]), set(h["train"]) | set(h["val"])))
        return out
    raise ValueError(f"no leakage rule for stage {st!r}")


def check_no_leakage(job: dict, cfg: Config | None = None) -> None:
    for test, seen in leakage_hosts(job, cfg):
        if not test or test & seen:
            raise AssertionError(f"{job['run_id']}: test hosts overlap training/validation ({len(test & seen)})")


# ------------------------------------------------------------------------------------------ enqueueing
def load_spec_file(path: Path) -> list[dict]:
    """Jobs of ``specs/<stage>.jsonl`` after checking it against ``<stage>.manifest.json`` (sha256 and count)."""
    path = Path(path)
    man = json.loads(path.with_name(path.name.removesuffix(".jsonl") + ".manifest.json").read_text())
    body = path.read_bytes()
    if hashlib.sha256(body).hexdigest() != man["sha256"]:
        raise ValueError(f"{path}: sha256 differs from its manifest")
    jobs = [json.loads(ln) for ln in body.decode().splitlines() if ln]
    if len(jobs) != man["count"]:
        raise ValueError(f"{path}: {len(jobs)} jobs, manifest says {man['count']}")
    return jobs


def shard(jobs: list[dict], spec: str | None) -> list[dict]:
    """Jobs of shard ``"I/N"``: those with int(run_id, 16) % N == I (stable, independent of file order)."""
    if not spec:
        return jobs
    i, n = (int(x) for x in spec.split("/"))
    if not 0 <= i < n:
        raise ValueError(f"bad shard {spec!r}")
    return [j for j in jobs if int(j["run_id"], 16) % n == i]


def task_result_verified(rid: str) -> bool:
    from dftgnn import tasks

    return any(tasks.verified(tasks.result_path(st, rid), rid) for st in tasks.SUBDIR)


def resolve_deps(jobs: list[dict], queue_root: Path, verified=task_result_verified) -> list[dict]:
    """Keep a dependency that is in this batch or already in the queue (any state); drop one whose result is
    already present and verifies (e.g. relax results ingested from an earlier run or another shard); refuse
    anything else, so a stage is never enqueued ahead of what it needs."""
    ids = {j["run_id"] for j in jobs}
    known = {f.stem for s in ("pending", "running", "done", "failed") for f in (Path(queue_root) / s).glob("*.json")}
    out = []
    for j in jobs:
        keep = []
        for a in j.get("after", []):
            if a in ids or a in known:
                keep.append(a)
            elif not verified(a):
                raise ValueError(f"{j['run_id']} ({j['stage']}) depends on {a}: not in this batch, not in the queue "
                                 "and no verified result; enqueue that stage first")
        out.append({**j, "after": keep})
    return out

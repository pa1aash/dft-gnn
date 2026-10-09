"""Non-training queue tasks of the S12 session: ``relax``, ``embed``, ``geomeval``.

A task job is ``{"run_id", "stage", "spec": {"model": <stage>, "r", "budget", "seed", ...}, "after", "est_peak_gb",
"priority", "tranche"}``; the run id is ``infer.task_id`` of a key that includes the code SHA. Every task writes a
result JSON via write_result under ``results/<subdir>/<run_id>.json`` whose payload lists its artefacts
(``artifacts``: path and sha256), so the outbox packs them like training runs. Every task is idempotent: a verified
result is not recomputed (``verified``).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from dftgnn import infer
from dftgnn.graphs.store import sha256_file
from dftgnn.io.results import write_result

REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_STAGES = ("relax", "embed", "geomeval")
SUBDIR = {"relax": "mlip_v1", "embed": "embeddings_v1", "geomeval": "geomeval"}


def mace_sha() -> str:
    """sha256 of the MACE-MP-0 medium checkpoint as recorded in the tracked results/mace_model.json."""
    return json.loads((REPO_ROOT / "results" / "mace_model.json").read_text())["payload"]["sha256"]


def result_path(stage: str, rid: str) -> Path:
    return REPO_ROOT / "results" / SUBDIR[stage] / f"{rid}.json"


def _rel(p: Path) -> str:
    return str(Path(p).resolve().relative_to(REPO_ROOT))


def artifact(p: Path) -> dict:
    return {"path": _rel(p), "sha256": sha256_file(p)}


def verified(path: Path, rid: str) -> bool:
    try:
        pay = json.loads(path.read_text())["payload"]
    except (OSError, KeyError, json.JSONDecodeError):
        return False
    if pay.get("run_id") != rid:
        return False
    arts = list(pay.get("artifacts", [])) + ([pay["predictions"]] if pay.get("predictions") else [])
    return all((REPO_ROOT / a["path"]).is_file() and sha256_file(REPO_ROOT / a["path"]) == a["sha256"] for a in arts)


# ----------------------------------------------------------------------------------------------- relax
def relax_key(host_id: str, code: str) -> dict:
    return {"stage": "relax", "host_id": host_id, "code_sha": code, "mace_model_sha256": mace_sha()}


class RelaxContext:
    """Per-process cache: unit cells, tiling map, universe, MACE calculator."""

    def __init__(self, device: str):
        from dftgnn.mlip import mace_model, release

        self.cells = release.unit_cells()
        self.tmap = pd.read_parquet(REPO_ROOT / "data/processed/tiling_map_v1.parquet").set_index("host_id")
        self.u = pd.read_parquet(REPO_ROOT / "data/processed/universe_v1.parquet")
        self.hosts = release.host_table(self.u).set_index("host_id")
        path = mace_model.model_path()
        self.msha = sha256_file(path)
        if self.msha != mace_sha():
            raise RuntimeError("MACE checkpoint differs from results/mace_model.json")
        self.calc = mace_model.calculator(device, path)


def run_relax(rid: str, spec: dict, ctx: RelaxContext, out_dir: Path | None = None) -> Path:
    from dftgnn.mlip import release
    from dftgnn.mlip.pipeline import host_job
    from dftgnn.mlip.relax import OUT_DIR

    out_dir = out_dir or OUT_DIR
    h = spec["host_id"]
    vac = sorted(int(v) for v in ctx.u.vacancy_atom_index[ctx.u.host_id == h])
    rec = host_job(h, ctx.cells[h], release.read_supercell(ctx.hosts.loc[h, "cif"]), vac, ctx.tmap.loc[h].to_dict(),
                   ctx.calc, model_sha256=ctx.msha, out_dir=out_dir)
    arts = [artifact(out_dir / f"{h}.json")] + [artifact(out_dir / a["path"]) for a in rec["files"].values()]
    pay = {"run_id": rid, "spec": spec, **{k: v for k, v in rec.items() if k not in ("files", "skipped")},
           "artifacts": arts}
    return write_result(rid, pay, results_dir=result_path("relax", rid).parent)


# ----------------------------------------------------------------------------------------------- embed
def embed_key(r: int, budget: int, kind: str, s_run: str, code: str) -> dict:
    return {"stage": "embed", "r": r, "budget": budget, "kind": kind, "checkpoint_run_id": s_run, "code_sha": code}


def run_embed(rid: str, spec: dict, sites: infer.Sites, prim: dict, device=None) -> Path:
    from dftgnn import embeddings as E

    r, b, kind = spec["r"], spec["budget"], spec["kind"]
    rec = prim[("S", f"outer_r{r}", b, 0)]
    name = f"r{r}_B{b}_{kind}"
    if not E.done(name):
        arrays = E.extract(kind, rec, sites, r, b, device=device)
        E.write(arrays, name, {"r": r, "budget": b, "kind": kind, "checkpoint_run_id": rec["run_id"],
                               "registered_control": kind in ("trained", "init0"),
                               "label": "DESCRIPTIVE variance of the random-init control"
                               if kind in ("init1", "init2") else None})
    side = json.loads((E.OUT_DIR / f"{name}.json").read_text())
    pay = {"run_id": rid, "spec": spec, **side,
           "artifacts": [artifact(E.OUT_DIR / f"{name}.npz"), artifact(E.OUT_DIR / f"{name}.json")]}
    return write_result(rid, pay, results_dir=result_path("embed", rid).parent)


# -------------------------------------------------------------------------------------------- geomeval
def run_geomeval(rid: str, spec: dict, sites: infer.Sites, prim: dict, key: dict, device=None,
                 mlip_dir: Path | None = None) -> Path:
    from dftgnn.mlip import geomeval as GE
    from dftgnn.mlip.relax import OUT_DIR

    comps = GE.components(prim, spec["geo_model"], spec["r"], spec["budget"], spec["seed"])
    frame, info = GE.run(spec["geo_model"], spec["r"], spec["budget"], spec["seed"], comps, sites,
                         mlip_dir=mlip_dir or OUT_DIR, device=device)
    rdir = result_path("geomeval", rid).parent
    (rdir / "predictions").mkdir(parents=True, exist_ok=True)
    pp = rdir / "predictions" / f"{rid}.parquet"
    frame.to_parquet(pp, index=False)
    pay = {"run_id": rid, "task_id": rid, "spec": spec, "key": key, **info,
           "predictions": {**artifact(pp), "rows": len(frame)}}
    return write_result(rid, pay, results_dir=rdir)


def geomeval_key(geo_model: str, r: int, budget: int, seed: int, comps: dict, code: str) -> dict:
    from dftgnn.mlip import geomeval as GE

    return {"stage": "geomeval", "model": geo_model, "r": r, "budget": budget, "seed": seed,
            "components": {k: v["run_id"] for k, v in comps.items()}, "code_sha": code,
            "tiling_summary_sha256": sha256_file(GE.TILING_SUMMARY), "mace_model_sha256": mace_sha()}


# ---------------------------------------------------------------------------------------------- dispatch
class TaskRunner:
    """Executes task jobs inside a queue worker, with lazily built per-process state."""

    def __init__(self, store, device):
        self.store, self.device = store, device
        self._sites = self._prim = self._relax = None

    @property
    def sites(self) -> infer.Sites:
        if self._sites is None:
            self._sites = infer.Sites(self.store)
        return self._sites

    @property
    def prim(self) -> dict:
        if self._prim is None:
            from dftgnn.train import runindex

            self._prim = runindex.primary(runindex.load())
        return self._prim

    def __call__(self, job: dict) -> dict:
        stage, rid, spec = job["stage"], job["run_id"], job["spec"]
        out = result_path(stage, rid)
        if verified(out, rid):
            return {"status": "skipped", "result": str(out)}
        if stage == "relax":
            if self._relax is None:
                self._relax = RelaxContext(str(self.device))
            path = run_relax(rid, spec, self._relax)
        elif stage == "embed":
            path = run_embed(rid, spec, self.sites, self.prim, self.device)
        elif stage == "geomeval":
            path = run_geomeval(rid, spec, self.sites, self.prim, job["key"], self.device)
        else:
            raise ValueError(f"unknown task stage {stage!r}")
        return {"status": "done", "result": str(path)}

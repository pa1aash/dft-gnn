"""Build job specs for a named stage and add them to jobs/pending/.

    python scripts/queue/enqueue.py smoke
    python scripts/queue/enqueue.py kiyohara --hparams tuned.json [--d-variant D-state]
    python scripts/queue/enqueue.py sweep [--tuned configs/tuned_v1.yaml] --dry-run
    python scripts/queue/enqueue.py c0_official [--tuned configs/tuned_v1.yaml]

Builders exist for smoke, kiyohara, pilot_epochs, c0_pilot, c0_ablate, c0_capcheck, sweep, c0_official, the S09
session and the S12 session (``s12``: relax, peval, embed, geomeval, loco, moment, cgcnn, capped; each also
buildable alone). Tuning runs through scripts/tune/, not the queue. ``sweep`` builds the
primary sweep (S, D, P1 and P over resamples x budgets x seeds) together with the Kiyohara-split jobs.
``--dry-run`` prints job counts, the cost-table GPU-hours and the run-id check, and enqueues nothing.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from _common import QUEUE, ROOT

from dftgnn import jobqueue as Q
from dftgnn.graphs.store import manifest_sha
from dftgnn.train import admission, code_sha
from dftgnn.train import s12 as S12
from dftgnn.train import stages as ST


C0_CODE_SHA = "1e4d6340a865dbbb0bb93f4bbffbe9f7a7271a4f"     # code SHA of the official C0 runs (tag tuned-v1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=ST.STAGES)
    ap.add_argument("--hparams", help="JSON of tuned hyperparameters per model (kiyohara)")
    ap.add_argument("--d-variant", choices=["D-state", "D-late"])
    ap.add_argument("--tuned", default=str(ST.TUNED), help="tuned hyperparameters (sweep, c0_official)")
    ap.add_argument("--dry-run", action="store_true", help="print counts and cost; enqueue nothing")
    ap.add_argument("--queue", default=str(QUEUE))
    ap.add_argument("--code", help="build the jobs against this commit SHA instead of HEAD (the commit the pod's "
                                    "workers run; docs/deviations.md 2026-10-09)")
    ap.add_argument("--manifest", help="write the run ids of the built jobs to this JSON file (session, capsens)")
    a = ap.parse_args()
    code, gsha = a.code or code_sha(), manifest_sha()
    try:
        table = admission.load_benchmark()
    except (OSError, KeyError):
        table = None
        print("no results/gpu_benchmark.json: jobs carry no est_peak_gb (workers treat them as solo)")
    if a.stage == "smoke":
        jobs = ST.build_smoke(code, gsha, table)
    elif a.stage == "pilot_epochs":
        jobs = ST.build_pilot_epochs(code, gsha, table)
    elif a.stage == "c0_pilot":
        jobs = ST.build_c0_pilot(code, gsha, table=table)
    elif a.stage == "c0_capcheck":
        jobs = ST.build_c0_capcheck(code, gsha, table)
    elif a.stage == "c0_ablate":
        jobs = ST.build_c0_pilot(code, gsha, table=table, ablate="vacancy_flag")
    elif a.stage == "kiyohara":
        if not a.hparams:
            raise SystemExit("kiyohara needs --hparams (tuned values; tuning has not run yet)")
        jobs = ST.build_kiyohara(code, gsha, ST.load_hparams(a.hparams), d_variant=a.d_variant, table=table)
    elif a.stage == "sweep":
        tuned = ST.load_tuned(Path(a.tuned))
        jobs = ST.build_sweep(code, gsha, tuned, table=table)
        jobs += ST.build_kiyohara(code, gsha, ST.kiyohara_hparams_from_tuned(tuned), d_variant=tuned["d_variant"],
                                  table=table)
    elif a.stage == "capsens":
        jobs = ST.build_capsens(code, gsha, ST.load_tuned(Path(a.tuned)), table=table)
    elif a.stage == "session":
        jobs, reused = ST.build_session(code, gsha, ST.load_tuned(Path(a.tuned)), table=table,
                                        c0_code=C0_CODE_SHA)
        print(f"reusing {len(reused)} official C0 runs as the Kiyohara-split S runs: "
              + ", ".join(sorted(j["run_id"] for j in reused)))
    elif a.stage in ("diag_cross", "d_ablation", "dlate", "review"):
        builder = {"diag_cross": ST.build_diag_cross, "d_ablation": ST.build_d_ablation, "dlate": ST.build_dlate,
                   "review": ST.build_review}[a.stage]
        jobs = builder(code, gsha, ST.load_tuned(Path(a.tuned)), table=table)
    elif a.stage == "p_v2":
        jobs = ST.build_p_v2(code, gsha, ST.load_tuned(ST.TUNED_V2), ST.load_tuned(ST.TUNED), table=table)
    elif a.stage == "v2":
        jobs = ST.build_v2(code, gsha, ST.load_tuned(ST.TUNED_V2), table=table)
    elif a.stage in ("loco", "v2_screen"):
        builder = {"loco": ST.build_loco, "v2_screen": ST.build_v2_screen}[a.stage]
        jobs = builder(code, gsha, ST.load_tuned(Path(a.tuned)), table=table)
        for i, j in enumerate(sorted(jobs, key=lambda j: -j["spec"]["budget"])):   # longest runs first
            j["priority"] = i
    elif a.stage == "c0_official":
        jobs = ST.build_c0_official(code, gsha, ST.load_tuned(Path(a.tuned)), table=table)
    elif a.stage in ("s12", *S12.STAGE_ORDER):
        stages = S12.STAGE_ORDER if a.stage == "s12" else (("relax", "geomeval") if a.stage == "geomeval"
                                                           else (a.stage,))
        jobs = S12.build_s12(code, gsha, ST.load_tuned(Path(a.tuned)), table=table, stages=stages)
        if a.stage == "geomeval":
            jobs = [j for j in jobs if j["stage"] == "geomeval"]
        if a.dry_run:
            s12_report(jobs)
            return
    else:
        raise SystemExit(f"stage {a.stage!r} has no builder yet")
    if a.dry_run:
        dry_run_report(a.stage, jobs)
        return
    if a.manifest:
        Path(a.manifest).write_text(json.dumps([j["run_id"] for j in jobs]))
    root = Q.init(Path(a.queue))
    added = sum(Q.enqueue(root, j) for j in jobs)
    print(f"{a.stage}: {len(jobs)} jobs built, {added} added, {len(jobs) - added} already known")


def dry_run_report(stage: str, jobs: list[dict]) -> None:
    """Job counts by stage and model, run-id uniqueness and the cost table's GPU-hours."""
    ids = [j["run_id"] for j in jobs]
    if len(set(ids)) != len(ids):
        raise SystemExit(f"run ids are not unique: {len(ids) - len(set(ids))} duplicates")
    known = set(ids)
    missing = [a for j in jobs for a in j["after"] if a not in known]
    if missing:
        raise SystemExit(f"{len(missing)} dependencies point outside the stage")
    split = Counter("kiyohara" if j["spec"]["split"] == "kiyohara" else "outer" for j in jobs)
    by = Counter((("kiyohara" if j["spec"]["split"] == "kiyohara" else "outer"), j["spec"]["model"]) for j in jobs)
    if stage == "session":
        print("  tranches: " + ", ".join(f"{k} {v}" for k, v in sorted(Counter(j["tranche"] for j in jobs).items())))
    trained = sum(j["spec"]["model"] != "P" for j in jobs)
    print(f"{stage} dry run: {len(jobs)} jobs ({trained} trained, {len(jobs) - trained} P evaluations); "
          f"run ids unique: {len(set(ids))}; " + ", ".join(f"{k} {v}" for k, v in sorted(split.items())))
    for (sp, m), n in sorted(by.items()):
        print(f"  {sp:9s} {m:8s} {n}")
    est = [j.get("est_peak_gb") for j in jobs]
    if all(e is not None for e in est):
        print(f"  est_peak_gb: min {min(est):.2f}, max {max(est):.2f} GiB")
    try:
        stages = {s["stage"]: s for s in json.loads((ROOT / "results" / "cost_table.json").read_text())
                  ["payload"]["stages"]}
    except (OSError, KeyError):
        return
    for s in ("sweep", "kiyohara") if stage in ("sweep", "session") else (stage,):
        if s in stages:
            print(f"  cost table {s}: {stages[s]['runs']} runs, central {stages[s]['central_gpu_h']:.1f} GPU-h, "
                  f"upper {stages[s]['upper_gpu_h']:.1f} GPU-h")


def s12_report(jobs: list[dict]) -> None:
    """S12 dry run: counts per stage, a sample of run ids, GPU-hours (central, upper), cost and the guard."""
    ids = [j["run_id"] for j in jobs]
    if len(set(ids)) != len(ids):
        raise SystemExit(f"run ids are not unique: {len(ids) - len(set(ids))} duplicates")
    known = set(ids)
    missing = [a for j in jobs for a in j["after"] if a not in known]
    if missing:
        raise SystemExit(f"{len(missing)} dependencies point outside the built jobs")
    est = S12.estimate(jobs)
    print(f"s12 dry run: {len(jobs)} jobs, run ids unique, dependencies inside the session")
    print(f"  {'stage':9s} {'tranche':7s} {'jobs':>5s} {'central GPU-h':>14s} {'upper GPU-h':>12s}  sample run id")
    for s in S12.STAGE_ORDER:
        js = [j for j in jobs if j["stage"] == s]
        if not js:
            continue
        e = est["stages"][s]
        print(f"  {s:9s} {js[0]['tranche']:7s} {len(js):5d} {e['central_gpu_h']:14.2f} {e['upper_gpu_h']:12.2f}  "
              f"{js[0]['run_id']}")
    print(f"  total central {est['central_gpu_h']:.1f} GPU-h (${est['central_usd']:.0f}), upper "
          f"{est['upper_gpu_h']:.1f} GPU-h (${est['upper_usd']:.0f}) at ${est['rate_usd_per_h']:.2f}/h; "
          f"recommended guard (upper + 10%): {est['guard_gpu_h']:.1f} GPU-h")
    for note in est["notes"]:
        print(f"  note: {note}")


if __name__ == "__main__":
    main()

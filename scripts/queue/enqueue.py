"""Build job specs for a named stage and add them to jobs/pending/.

    python scripts/queue/enqueue.py smoke
    python scripts/queue/enqueue.py kiyohara --hparams tuned.json [--d-variant D-state]

Builders exist for smoke, kiyohara, pilot_epochs, c0_pilot, c0_ablate and c0_capcheck; tune, sweep, loco and
sensitivity come later.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from _common import QUEUE

from dftgnn import jobqueue as Q
from dftgnn.graphs.store import manifest_sha
from dftgnn.train import admission, code_sha
from dftgnn.train import stages as ST


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=ST.STAGES)
    ap.add_argument("--hparams", help="JSON of tuned hyperparameters per model (kiyohara)")
    ap.add_argument("--d-variant", choices=["D-state", "D-late"])
    ap.add_argument("--queue", default=str(QUEUE))
    a = ap.parse_args()
    code, gsha = code_sha(), manifest_sha()
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
    else:
        raise SystemExit(f"stage {a.stage!r} has no builder yet")
    root = Q.init(Path(a.queue))
    added = sum(Q.enqueue(root, j) for j in jobs)
    print(f"{a.stage}: {len(jobs)} jobs built, {added} added, {len(jobs) - added} already known")


if __name__ == "__main__":
    main()

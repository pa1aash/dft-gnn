"""CPU smoke that checks a code change leaves v1 training bit-identical (smoke only; writes no result record).

S, D-state and P1 with the tuned-v1 a50 values, seed 0, 3 epochs, on resample 0 at budget 25: the first 20 hosts
of the budget order train, the next 5 validate, and the first 10 test hosts (sorted) are predicted. Prints one
JSON line per model with the sha256 of the prediction parquet, the metrics and the epoch history; the parquet is
written to ``--out``. Run the same command on two code trees and compare.

    python scripts/smoke/merge_equivalence_smoke.py --out DIR [--store DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import torch

from dftgnn.config import load_config
from dftgnn.graphs import store as G
from dftgnn.split import budget_train, load_split
from dftgnn.train import RunSpec, Store, train_run
from dftgnn.train.stages import load_tuned, tuned_hparams

torch.set_num_threads(3)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--store", default=str(G.STORE_DIR), help="graph store directory (default: this tree's)")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    cfg = load_config()
    sp = load_split("outer_r0")
    pool = budget_train(sp, 25)
    hosts = {"train": pool[:20], "val": pool[20:25], "test": sorted(sp["test"])[:10]}
    data = Store(store_dir=Path(a.store))
    tuned = load_tuned()
    for model in ("S", "D-state", "P1"):
        spec = RunSpec(model=model, **tuned_hparams(tuned, model, 50), split="outer_r0", r=0, budget=25, seed=0,
                       hosts=hosts, max_epochs=3, patience=3, smoke=True, tags={"smoke": "merge_equivalence"})
        pay = train_run(spec, data, cfg, device=torch.device("cpu"), log=lambda m: None)
        path = out / f"{model}.parquet"
        pay["predictions"].to_parquet(path, index=False)
        print(json.dumps({"model": model, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                          "rows": len(pay["predictions"]), "metrics": pay["metrics"],
                          "epochs_run": pay["epochs_run"], "best_epoch": pay["best_epoch"],
                          "history": pay["history"]}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

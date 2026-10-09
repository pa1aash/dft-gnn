"""CPU timing of checkpoint inference for the S12 cost estimate (smoke=true; results/smoke/inference_timing.json).

    nice -n 15 python scripts/smoke/inference_timing.py

Times the forward pass (graph batching included) of the seed-0, resample-0 S, D and P1 checkpoints at the three
tuning anchors' budgets (25 -> a50 hyperparameters ... 654 -> a654) on 80 test sites each, 3 torch threads.
No prediction is evaluated against a target.
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import torch

from dftgnn import infer
from dftgnn.io.results import write_result
from dftgnn.split import load_split
from dftgnn.train import Store, runindex

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    torch.set_num_threads(3)
    sites = infer.Sites(Store())
    prim = runindex.primary(runindex.load())
    test = sorted(load_split("outer_r0")["test"])
    pos = sites.positions(test)[:80]
    graphs = sites.dft_graphs(sorted(set(sites.host_id[pos])))
    rows = []
    for m in ("S", "D-state", "P1"):
        for b in (50, 200, 654):
            rec = prim[(m, "outer_r0", b, 0)]
            net, ck = infer.load(rec)
            infer.predict(net, ck, sites, graphs, pos[:8])                 # warm-up
            t0 = time.time()
            infer.predict(net, ck, sites, graphs, pos)
            dt = (time.time() - t0) / len(pos)
            rows.append({"model": m, "budget": b, "hp": rec["spec"]["hp"], "s_per_site": dt})
            print(rows[-1], flush=True)
    t = np.array([r["s_per_site"] for r in rows])
    write_result("inference_timing", {
        "smoke": True, "note": "CPU timing for the S12 cost estimate; no metric computed; excluded from analysis",
        "rows": rows, "s_per_site_forward": {"mean": float(t.mean()), "max": float(t.max())},
        "n_sites": len(pos), "torch_threads": 3,
        "basis": f"Mac CPU, 3 threads, {len(pos)} resample-0 test sites, S/D/P1 at B=50/200/654, seed 0"},
        results_dir=ROOT / "results" / "smoke")


if __name__ == "__main__":
    main()

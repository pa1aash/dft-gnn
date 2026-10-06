"""Seconds per epoch (training epoch plus the validation pass) at each training budget (S07 step 6; ON the pod).

Model S, hidden 64, 3 blocks, batch 32, set2set, one worker, nothing else on the GPU, torch threads set to
the container's CPU quota. Resample 0, seed 0, the clarified validation split, budgets of
``budgets.hosts`` plus the Kiyohara split. The cost table uses these to scale the benchmark's
654-host epoch time to every budget instead of assuming proportionality to the number of sites.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

REPS = 5


def main() -> None:
    import torch
    from benchmark_gpu import build, epoch

    from dftgnn.config import load_config
    from dftgnn.io.results import write_result
    from dftgnn.train import RunSpec, Store, _predict, available_cpus, resolve_hosts

    device = torch.device("cuda")
    torch.set_num_threads(max(1, int(available_cpus())))
    data, cfg = Store(verify=False), load_config()
    desc = data.sites["desc"].float()
    rows = []
    for name, split, r, b in [*(("outer_r0", "outer_r0", 0, b) for b in cfg.budgets.hosts),
                              ("kiyohara", "kiyohara", -1, 0)]:
        spec = RunSpec(model="S", hp={}, lr=1e-3, weight_decay=1e-5, batch_size=32, split=split, r=r,
                       budget=b, seed=0, eval_test=False)
        h = resolve_hosts(spec, cfg)
        pos, val = data.positions(h["train"]), data.positions(h["val"])
        torch.manual_seed(0)
        net, opt, y = build(data, pos, 64, 3, device)
        gen = torch.Generator().manual_seed(0)
        epoch(net, opt, data, pos, y, 32, gen, device)                  # warm-up
        tr, ev = [], []
        for _ in range(REPS):
            tr.append(epoch(net, opt, data, pos, y, 32, gen, device))
            torch.cuda.synchronize()
            t0 = time.perf_counter()
            _predict(net, data, val, y, desc, 32, device)
            torch.cuda.synchronize()
            ev.append(time.perf_counter() - t0)
        rows.append({"split": name, "budget_hosts": b if name != "kiyohara" else len(h["train"]) + len(h["val"]),
                     "n_train_sites": len(pos), "n_val_sites": len(val),
                     "train_epoch_s_median": float(np.median(tr)), "val_pass_s_median": float(np.median(ev)),
                     "epoch_total_s": float(np.median(tr) + np.median(ev))})
        print(rows[-1], flush=True)
    payload = {"definition": __doc__, "torch_threads": torch.get_num_threads(), "rows": rows}
    print(write_result("gpu_epoch_scaling", payload))


if __name__ == "__main__":
    main()

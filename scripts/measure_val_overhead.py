"""Seconds of one validation pass relative to one training epoch (S07 step 6; runs ON the pod).

The cost table scales the benchmark's training-epoch time by this factor, because the training loop
evaluates the validation hosts after every epoch. Model S, hidden 64, 3 blocks, batch 32, resample 0,
budget 654; the validation sites are the 10% of training hosts of ``dftgnn.split.val_split``. Single
worker, nothing else on the GPU.
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
    from dftgnn.train import RunSpec, Store, _predict, resolve_hosts

    device = torch.device("cuda")
    data = Store(verify=False)
    cfg = load_config()
    spec = RunSpec(model="S", hp={}, lr=1e-3, weight_decay=1e-5, batch_size=32, split="outer_r0", r=0,
                   budget=654, seed=0)
    hosts = resolve_hosts(spec, cfg)
    pos, val = data.positions(hosts["train"]), data.positions(hosts["val"])
    net, opt, y = build(data, pos, 64, 3, device)
    gen = torch.Generator().manual_seed(0)
    epoch(net, opt, data, pos, y, 32, gen, device)                      # warm-up
    desc = data.sites["desc"].float()
    tr, ev = [], []
    for _ in range(REPS):
        tr.append(epoch(net, opt, data, pos, y, 32, gen, device))
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        _predict(net, data, val, y, desc, 32, device)
        torch.cuda.synchronize()
        ev.append(time.perf_counter() - t0)
    payload = {"definition": __doc__, "n_train_sites": int(len(pos)), "n_val_sites": int(len(val)),
               "train_epoch_s": tr, "val_pass_s": ev, "train_epoch_s_median": float(np.median(tr)),
               "val_pass_s_median": float(np.median(ev)),
               "val_overhead_fraction": float(np.median(ev) / np.median(tr))}
    print(write_result("gpu_val_overhead", payload))


if __name__ == "__main__":
    main()

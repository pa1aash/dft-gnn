"""CPU seconds per training step for pod sizing (S06 step 7). Writes results/cpu_step_timing.json.

A step is forward + L1 loss + backward + AdamW update of model S (3 MEGNet blocks, Set2Set pooling)
on a batch of 32 copies of one host graph: the host with the most atoms, the host with the most edges
(the memory worst case) and a median-size host. It is
timed at hidden width 64 and 128 with the default torch thread count and with 1 thread. The bytes of
tensors saved for backward per step are summed through ``saved_tensors_hooks``. That sum does not
depend on the device, so it estimates the activation memory of the same step on a GPU.
"""
from __future__ import annotations

import time

import numpy as np
import torch

from dftgnn.graphs import collate_sites
from dftgnn.models import HParams, build_model, n_parameters
from dftgnn.train import Store

BATCH, WARMUP, REPS = 32, 1, 3


def saved_bytes(net, batch) -> int:
    total = 0

    def pack(t):
        nonlocal total
        total += t.numel() * t.element_size()
        return t

    with torch.autograd.graph.saved_tensors_hooks(pack, lambda t: t):
        loss = net(batch).abs().mean()
    loss.backward()
    return total


def time_step(data: Store, pos: int, hidden: int, threads: int) -> dict:
    torch.set_num_threads(threads)
    torch.manual_seed(0)
    net = build_model("S", HParams(hidden_width=hidden, megnet_blocks=3, readout_mlp_width=hidden))
    opt = torch.optim.AdamW(net.parameters(), lr=1e-3)
    b = collate_sites(data.graphs, data.sites, [pos] * BATCH)
    ts = []
    for k in range(WARMUP + REPS):
        t0 = time.perf_counter()
        loss = torch.nn.functional.l1_loss(net(b), b.y)
        opt.zero_grad()
        loss.backward()
        opt.step()
        if k >= WARMUP:
            ts.append(time.perf_counter() - t0)
    return {"hidden_width": hidden, "threads": threads, "n_parameters": n_parameters(net),
            "batch_nodes": int(b.num_nodes), "batch_edges": int(b.edge_index.shape[1]),
            "step_s_median": float(np.median(ts)), "step_s_min": float(min(ts)),
            "saved_activation_bytes": saved_bytes(net, b)}


def main() -> None:
    from dftgnn.config import load_config
    from dftgnn.io.results import write_result

    cfg = load_config()
    data = Store()
    hidx = data.sites["host_idx"].tolist()
    natoms = np.array([data.graphs[h]["z"].shape[0] for h in hidx])
    nedges = np.array([data.graphs[h]["edge_index"].shape[1] for h in hidx])
    med = int(np.median([g["z"].shape[0] for g in data.graphs]))
    picks = {"largest": int(np.argmax(natoms)), "most_edges": int(np.argmax(nedges)),
             "median": int(np.nonzero(natoms == med)[0][0])}
    default_threads = torch.get_num_threads()
    rows = []
    for label, pos in picks.items():
        for hidden in (64, 128):
            for threads in (default_threads, 1):
                r = {"host": label, "site_id": data.sites["site_id"][pos], "atoms": int(natoms[pos]),
                     "edges": int(nedges[pos]),
                     **time_step(data, pos, hidden, threads)}
                print(r, flush=True)
                rows.append(r)
    import platform

    payload = {"definition": __doc__, "batch_size": BATCH, "warmup": WARMUP, "reps": REPS,
               "megnet_blocks": 3, "pooling": "set2set", "machine": platform.platform(),
               "processor": platform.processor(), "default_threads": default_threads, "rows": rows}
    print(write_result("cpu_step_timing", payload, config=cfg))


if __name__ == "__main__":
    main()

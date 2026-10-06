"""CPU seconds per training step for pod sizing (S06 step 7). Writes results/cpu_step_timing.json.

A step is forward + L1 loss + backward + AdamW update of model S (3 MEGNet blocks, Set2Set pooling)
on a batch of copies of one host graph: the host with the most atoms, the host with the most edges
(the memory worst case) and a median-size host, at hidden width 64 and 128.

Activation memory: the bytes of tensors saved for backward are summed through
``saved_tensors_hooks`` at batch 4 and scaled to batch 32. Every saved tensor is per node, per edge or
per graph, so the sum is exactly linear in the batch size. The sum does not depend on the device and
estimates the activation memory of the same step on a GPU (weights, gradients and optimiser state add
about 16 bytes per parameter).

Timing: batch 32 is timed directly when its activations fit under ``CPU_MEM_LIMIT`` (the Mac has
8 GiB of RAM; larger batches swap and the timing would measure the disk). Otherwise batch 8 is timed
and the result is scaled by 4, which assumes step time linear in batch size. Such rows carry
``timed_batch`` = 8 and ``extrapolated`` = true.
"""
from __future__ import annotations

import time

import numpy as np
import torch

from dftgnn.graphs import collate_sites
from dftgnn.models import HParams, build_model, n_parameters
from dftgnn.train import Store

BATCH, PROBE_BATCH, SMALL_BATCH = 32, 4, 8
WARMUP, REPS = 1, 3
CPU_MEM_LIMIT = 2.5 * 2**30


def _net(hidden: int):
    torch.manual_seed(0)
    return build_model("S", HParams(hidden_width=hidden, megnet_blocks=3, readout_mlp_width=hidden))


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


def time_batch(net, batch) -> list[float]:
    opt = torch.optim.AdamW(net.parameters(), lr=1e-3)
    ts = []
    for k in range(WARMUP + REPS):
        t0 = time.perf_counter()
        loss = torch.nn.functional.l1_loss(net(batch), batch.y)
        opt.zero_grad()
        loss.backward()
        opt.step()
        if k >= WARMUP:
            ts.append(time.perf_counter() - t0)
    return ts


def measure(data: Store, pos: int, hidden: int) -> dict:
    net = _net(hidden)
    probe = collate_sites(data.graphs, data.sites, [pos] * PROBE_BATCH)
    act32 = saved_bytes(net, probe) * BATCH // PROBE_BATCH
    timed = BATCH if act32 <= CPU_MEM_LIMIT else SMALL_BATCH
    b = collate_sites(data.graphs, data.sites, [pos] * timed)
    ts = np.array(time_batch(_net(hidden), b)) * (BATCH / timed)
    return {"hidden_width": hidden, "n_parameters": n_parameters(net), "batch_size": BATCH,
            "timed_batch": timed, "extrapolated": timed != BATCH,
            "step_s_median": float(np.median(ts)), "step_s_min": float(ts.min()),
            "saved_activation_bytes_batch32": int(act32),
            "batch32_nodes": int(probe.num_nodes * BATCH // PROBE_BATCH),
            "batch32_edges": int(probe.edge_index.shape[1] * BATCH // PROBE_BATCH)}


def main() -> None:
    import platform

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
    rows = []
    for label, pos in picks.items():
        for hidden in (64, 128):
            r = {"host": label, "site_id": data.sites["site_id"][pos], "atoms": int(natoms[pos]),
                 "edges": int(nedges[pos]), **measure(data, pos, hidden)}
            print(r, flush=True)
            rows.append(r)
    payload = {"definition": __doc__, "megnet_blocks": 3, "pooling": "set2set", "warmup": WARMUP,
               "reps": REPS, "cpu_mem_limit_bytes": CPU_MEM_LIMIT, "machine": platform.platform(),
               "processor": platform.processor(), "torch_threads": torch.get_num_threads(),
               "rows": rows}
    print(write_result("cpu_step_timing", payload, config=cfg))


if __name__ == "__main__":
    main()

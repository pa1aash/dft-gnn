"""GPU memory and throughput benchmark of model S (S07 step 2). Runs ON the pod; training hosts only.

Data: resample 0, budget 654, training hosts after the clarified validation split (seed 0); test hosts
are never loaded into a batch.

Grid: hidden width {64, 128} x batch {16, 32, 64} x MEGNet blocks {2, 3, 4} x set2set. Blocks 2 and 4
are the extremes of the search space (S07 brief); 3 is added so that every (hidden, batch, blocks)
cell of the search space has a measured peak for the queue's VRAM admission. Each cell trains one full
epoch with shuffled batches exactly as the training loop does (collate, forward, L1 on the standardised
target, backward, AdamW step) and records seconds per epoch and ``torch.cuda.max_memory_allocated`` over
the epoch. The adversarial peak is one step on a batch made of the B training sites with the most
edges (two steps, so the AdamW state is included).

Concurrency: hidden 64, batch 32, blocks 3. N in {1, 2, 4, 8} worker processes each train one epoch
after a warm-up, released together by a barrier; the aggregate rate is N epochs over the wall time
from release to the last finish. nvidia-smi is sampled every 0.25 s for GPU utilisation. Each repeat
(``--reps``) is reported. Peak host RAM per worker is ``ru_maxrss``.
"""
from __future__ import annotations

import argparse
import itertools
import multiprocessing as mp
import resource
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

HIDDEN, BATCH, BLOCKS = (64, 128), (16, 32, 64), (2, 3, 4)
LR, WD, DROPOUT, SEED = 1e-3, 1e-5, 0.1, 0


def train_positions(data):
    from dftgnn.config import load_config
    from dftgnn.train import RunSpec, resolve_hosts

    spec = RunSpec(model="S", hp={}, lr=LR, weight_decay=WD, batch_size=32, split="outer_r0", r=0,
                   budget=654, seed=SEED)
    hosts = resolve_hosts(spec, load_config())
    return data.positions(hosts["train"]), hosts


def build(data, pos, hidden, blocks, device):
    import torch

    from dftgnn.models import HParams, Standardiser, build_model

    target = data.sites["target"]
    y = Standardiser.fit(target[pos].view(-1, 1))(target.view(-1, 1)).view(-1).float()
    hp = HParams(hidden_width=hidden, megnet_blocks=blocks, dropout=DROPOUT, readout_mlp_width=hidden,
                 pooling="set2set")
    n_host = len(data.sites["desc_host_names"])
    net = build_model("S", hp, n_host=n_host, n_site=data.sites["desc"].shape[1] - n_host,
                      cutoff=data.meta["cutoff_A"]).to(device)
    opt = torch.optim.AdamW(net.parameters(), lr=LR, weight_decay=WD)
    return net, opt, y


def step(net, opt, data, idx, y, device):
    import torch

    from dftgnn.graphs import collate_sites

    b = collate_sites(data.graphs, data.sites, idx, y=y).to(device)
    loss = torch.nn.functional.l1_loss(net(b), b.y)
    opt.zero_grad()
    loss.backward()
    opt.step()


def epoch(net, opt, data, pos, y, bs, gen, device) -> float:
    """One shuffled epoch; returns seconds."""
    import torch

    net.train()
    order = pos[torch.randperm(len(pos), generator=gen).numpy()]
    if device.type == "cuda":
        torch.cuda.synchronize()
    t0 = time.perf_counter()
    for k in range(0, len(order), bs):
        step(net, opt, data, order[k:k + bs], y, device)
    if device.type == "cuda":
        torch.cuda.synchronize()
    return time.perf_counter() - t0


def edge_counts(data, pos) -> np.ndarray:
    host_idx = data.sites["host_idx"].numpy()
    return np.array([data.graphs[int(host_idx[p])]["edge_index"].shape[1] for p in pos])


def grid(data, pos, device) -> list[dict]:
    import torch

    ec = edge_counts(data, pos)
    rows = []
    for hidden, bs, blocks in itertools.product(HIDDEN, BATCH, BLOCKS):
        torch.manual_seed(SEED)
        gen = torch.Generator().manual_seed(SEED)
        net, opt, y = build(data, pos, hidden, blocks, device)
        for k in range(2):                       # warm-up (cuDNN/allocator); not counted
            step(net, opt, data, pos[k * bs:(k + 1) * bs], y, device)
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        base = torch.cuda.memory_allocated()
        secs = epoch(net, opt, data, pos, y, bs, gen, device)
        realistic = torch.cuda.max_memory_allocated()
        reserved = torch.cuda.max_memory_reserved()
        top = pos[np.argsort(-ec, kind="stable")[:bs]]
        torch.cuda.reset_peak_memory_stats()
        for _ in range(2):
            step(net, opt, data, top, y, device)
        torch.cuda.synchronize()
        worst = torch.cuda.max_memory_allocated()
        rows.append({"hidden": hidden, "batch": bs, "blocks": blocks, "pooling": "set2set",
                     "n_train_sites": len(pos), "steps": int(np.ceil(len(pos) / bs)),
                     "s_per_epoch": secs, "realistic_peak_bytes": int(realistic),
                     "realistic_peak_reserved_bytes": int(reserved), "weights_state_bytes": int(base),
                     "worst_case_peak_bytes": int(worst),
                     "worst_batch_edges": int(ec[np.argsort(-ec, kind="stable")[:bs]].sum()),
                     "spec_grid": blocks != 3 or (hidden, bs) == (64, 32)})
        print(f"h{hidden} b{bs} k{blocks}: {secs:.1f} s/epoch, realistic {realistic / 2**30:.2f} GiB, "
              f"worst {worst / 2**30:.2f} GiB", flush=True)
        del net, opt
        torch.cuda.empty_cache()
    return rows


def worker(i, n, threads, barrier, out):
    import torch

    from dftgnn.train import Store

    torch.set_num_threads(threads)
    device = torch.device("cuda")
    data = Store(verify=False)
    pos, _ = train_positions(data)
    torch.manual_seed(i)
    net, opt, y = build(data, pos, 64, 3, device)
    for k in range(3):
        step(net, opt, data, pos[k * 32:(k + 1) * 32], y, device)
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    gen = torch.Generator().manual_seed(1000 + i)
    barrier.wait()
    t0 = time.time()
    secs = epoch(net, opt, data, pos, y, 32, gen, device)
    t1 = time.time()
    out.put({"worker": i, "t_start": t0, "t_end": t1, "epoch_s": secs,
             "gpu_peak_bytes": int(torch.cuda.max_memory_allocated()),
             "host_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024})


class Sampler(threading.Thread):
    def __init__(self, every=0.25):
        super().__init__(daemon=True)
        self.every, self.samples, self._stop_ev = every, [], threading.Event()

    def run(self):
        while not self._stop_ev.is_set():
            r = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used",
                                "--format=csv,noheader,nounits"], capture_output=True, text=True, check=False)
            try:
                u, m = (float(x) for x in r.stdout.strip().split(","))
                self.samples.append((time.time(), u, m))
            except ValueError:
                pass
            self._stop_ev.wait(self.every)

    def stop(self):
        self._stop_ev.set()
        self.join()


def concurrency(levels, reps) -> list[dict]:
    from dftgnn.train import available_cpus

    cpus = available_cpus()
    ctx = mp.get_context("spawn")
    rows = []
    for n in levels:
        threads = max(1, int(cpus // n))
        for rep in range(reps):
            barrier, out = ctx.Barrier(n), ctx.Queue()
            procs = [ctx.Process(target=worker, args=(i, n, threads, barrier, out)) for i in range(n)]
            samp = Sampler()
            samp.start()
            for p in procs:
                p.start()
            res = [out.get(timeout=1800) for _ in procs]
            for p in procs:
                p.join()
            samp.stop()
            t0, t1 = min(r["t_start"] for r in res), max(r["t_end"] for r in res)
            wall = t1 - t0
            win = [(u, m) for t, u, m in samp.samples if t0 <= t <= t1]
            rows.append({
                "workers": n, "rep": rep, "torch_threads_per_worker": threads, "wall_s": wall,
                "aggregate_epochs_per_hour": n * 3600 / wall,
                "per_worker_epoch_s": sorted(r["epoch_s"] for r in res),
                "gpu_util_mean_pct": float(np.mean([u for u, _ in win])) if win else None,
                "gpu_util_max_pct": float(max(u for u, _ in win)) if win else None,
                "gpu_mem_used_max_mib": float(max(m for _, m in win)) if win else None,
                "n_util_samples": len(win),
                "gpu_peak_bytes_per_worker": max(r["gpu_peak_bytes"] for r in res),
                "host_peak_rss_bytes_per_worker": max(r["host_peak_rss_bytes"] for r in res)})
            print(f"{n} workers rep {rep}: wall {wall:.1f}s, {n * 3600 / wall:.0f} epochs/h, "
                  f"util {rows[-1]['gpu_util_mean_pct']}", flush=True)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", type=int, nargs="+", default=[1, 2, 4, 8])
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--skip-grid", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args()

    import torch

    from dftgnn.io.results import write_result
    from dftgnn.train import Store, available_cpus

    device = torch.device("cuda")
    data = Store(verify=False)
    pos, hosts = train_positions(data)
    payload = {"definition": __doc__, "device": torch.cuda.get_device_name(0),
               "total_vram_bytes": torch.cuda.get_device_properties(0).total_memory,
               "available_cpus": available_cpus(), "n_train_hosts": len(hosts["train"]),
               "n_train_sites": len(pos), "test_hosts_used": 0,
               "dropout": DROPOUT, "lr": LR, "weight_decay": WD,
               "grid": [] if a.skip_grid else grid(data, pos, device),
               "concurrency": concurrency(a.levels, a.reps)}
    if not a.no_write:
        print(write_result("gpu_benchmark", payload))


if __name__ == "__main__":
    main()

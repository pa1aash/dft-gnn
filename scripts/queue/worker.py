"""Queue worker: N processes, each claiming jobs atomically until the queue is drained.

    python scripts/queue/worker.py --max-concurrent 8 --device cuda

Launch one invocation per GPU (CUDA_VISIBLE_DEVICES selects it). Torch threads are split evenly between the
processes over the CPUs the container may use (cgroup quota, not the host core count).
"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import os
import socket
from pathlib import Path

from _common import QUEUE


def child(queue: str, name: str, device: str, threads: int) -> None:
    import torch

    from dftgnn import jobqueue as Q
    from dftgnn.train import RunSpec, Store
    from dftgnn.train.runner import execute

    torch.set_num_threads(threads)
    dev = torch.device(device)
    if dev.type == "mps":
        raise SystemExit("MPS is not used for training")
    data = Store()

    def run(job: dict) -> dict:
        out = execute(RunSpec.from_dict(job["spec"]), data, device=dev, log=lambda *_: None)
        if out["run_id"] != job["run_id"]:
            raise RuntimeError(f"run id mismatch {out['run_id']} != {job['run_id']} (code or graphs differ)")
        return {"status": out["status"], "result": str(out["result"]), "device": str(dev),
                "torch_threads": threads}

    n = Q.run_worker(Path(queue), name, run, log=lambda m: print(m, flush=True))
    print(f"{name}: ran {n} jobs", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-concurrent", type=int, default=1)
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    ap.add_argument("--queue", default=str(QUEUE))
    ap.add_argument("--threads", type=int, default=0, help="torch threads per process (0: auto)")
    a = ap.parse_args()
    if a.device == "cuda":
        import torch

        if not torch.cuda.is_available():
            raise SystemExit("--device cuda but CUDA is unavailable")
    from dftgnn.train import available_cpus

    threads = a.threads or max(1, int(available_cpus() // a.max_concurrent))
    host = socket.gethostname()
    ctx = mp.get_context("spawn")
    procs = [ctx.Process(target=child, args=(a.queue, f"{host}-{os.getpid()}-w{i}", a.device, threads))
             for i in range(a.max_concurrent)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    bad = [p.exitcode for p in procs if p.exitcode]
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()

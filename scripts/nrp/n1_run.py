"""N1 GPU-repeatability runs: the 12 sweep specs (S and D-state; B = 654 and 200; resample 0; seeds 0-2) on the
GPU of the current node, sequentially, one process, no MPS.

    python scripts/nrp/n1_run.py --out-root results/nrp/n1 [--pass-label pass2] [--device cuda]

The specs come from the sweep stage builder (``dftgnn.train.stages.build_sweep``, the builder behind
scripts/queue/enqueue.py) with the tuned-v1 values at each budget's anchor and the frozen max_epochs 200 /
patience 30, selected by (model, r, B, seed) and left unchanged. Each run trains through ``dftgnn.train.train_run``
and is written to ``<out-root>/<gpu-class-slug>/<node hostname>[/<pass-label>]/`` (result JSON, predictions
parquet, checkpoint) with ``write_result`` from a clean tree. Besides the training payload, every record carries the
GPU model, UUID, driver, CUDA version, node hostname, pod hostname, torch and matgl versions, the torch
determinism flags in effect, wall time and peak GPU memory. Idempotent: a run whose record verifies (run id and
artefact hashes) is skipped. A failing run is reported and retried once; the script exits non-zero if any run
still fails.
"""
from __future__ import annotations

import argparse
import os
import re
import socket
import subprocess
import sys
import time
import traceback
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import torch

from dftgnn.config import load_config
from dftgnn.graphs.store import sha256_file
from dftgnn.io.results import write_result
from dftgnn.train import RunSpec, Store, code_sha, run_id, train_run
from dftgnn.train import stages as ST
from dftgnn.train.runner import verify_result

KEYS = [(m, b, s) for m in ("S", "D-state") for b in (654, 200) for s in (0, 1, 2)]


def hardware() -> dict:
    q = subprocess.run(["nvidia-smi", "--query-gpu=name,uuid,driver_version,memory.total", "--format=csv,noheader"],
                       capture_output=True, text=True, check=True).stdout.strip().splitlines()[0].split(", ")
    smi = subprocess.run(["nvidia-smi"], capture_output=True, text=True, check=True).stdout
    cuda = re.search(r"CUDA Version: ([0-9.]+)", smi)
    return {"gpu_model": q[0], "gpu_uuid": q[1], "driver": q[2], "gpu_memory": q[3],
            "cuda_driver_version": cuda.group(1) if cuda else None, "torch_cuda": torch.version.cuda,
            "node_hostname": os.environ.get("NODE_NAME", "unknown"), "pod_hostname": socket.gethostname(),
            "torch": torch.__version__, "matgl": metadata.version("matgl")}


def determinism() -> dict:
    return {"use_deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
            "deterministic_warn_only": torch.is_deterministic_algorithms_warn_only_enabled(),
            "cudnn_deterministic": torch.backends.cudnn.deterministic, "cudnn_benchmark": torch.backends.cudnn.benchmark,
            "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG")}


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower().replace("nvidia", "")).strip("-")


def specs(cfg) -> list[RunSpec]:
    tuned = ST.load_tuned()
    jobs = ST.build_sweep(code_sha(), "unused", tuned, cfg)
    by = {}
    for j in jobs:
        s = j["spec"]
        if s["r"] == 0 and (s["model"], s["budget"], s["seed"]) in KEYS:
            by[(s["model"], s["budget"], s["seed"])] = RunSpec.from_dict(s)
    if set(by) != set(KEYS):
        raise SystemExit(f"sweep builder gave {sorted(by)}")
    return [by[k] for k in KEYS]


def run_one(spec: RunSpec, data: Store, cfg, out: Path, hw: dict, device) -> str:
    rid = run_id(spec, code_sha(), data.manifest_sha)
    res_path = out / f"{rid}.json"
    if verify_result(res_path, rid):
        return "skipped"
    ck = out / "checkpoints" / f"{rid}.pt"
    t0 = time.time()
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
    res = train_run(spec, data, cfg, device=device, ckpt_path=ck, log=lambda *_: None)
    frame = res.pop("predictions")
    (out / "predictions").mkdir(parents=True, exist_ok=True)
    pp = out / "predictions" / f"{rid}.parquet"
    frame.to_parquet(pp, index=False)
    rel = lambda p: str(p.relative_to(ROOT))
    payload = {"run_id": rid, "spec": spec.to_dict(), "smoke": False, "code_sha": code_sha(),
               "graphs_manifest_sha256": data.manifest_sha, **res,
               "predictions": {"path": rel(pp), "sha256": sha256_file(pp), "rows": len(frame)},
               "checkpoint": {"path": rel(ck), "sha256": sha256_file(ck)},
               "hardware": hw, "determinism": determinism(), "run_wall_time_s": time.time() - t0,
               "key": {"model": spec.model, "r": spec.r, "B": spec.budget, "seed": spec.seed}}
    write_result(rid, payload, config=cfg, results_dir=out)
    return "done"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-root", default="results/nrp/n1")
    ap.add_argument("--pass-label", default="")
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    cfg = load_config()
    device = torch.device(a.device)
    hw = hardware()
    out = ROOT / a.out_root / slug(hw["gpu_model"]) / hw["node_hostname"]
    if a.pass_label:
        out = out / a.pass_label
    out.mkdir(parents=True, exist_ok=True)
    data = Store()
    failed = []
    print(f"N1 on {hw['gpu_model']} ({hw['node_hostname']}), writing to {out.relative_to(ROOT)}", flush=True)
    for spec in specs(cfg):
        key = (spec.model, spec.budget, spec.seed)
        for attempt in (1, 2):
            try:
                st = run_one(spec, data, cfg, out, hw, device)
                print(f"{key}: {st}", flush=True)
                break
            except Exception:  # noqa: BLE001 - reported, retried once
                print(f"{key}: attempt {attempt} failed\n{traceback.format_exc()}", flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()
                if attempt == 2:
                    failed.append(key)
    print(f"failed: {failed}", flush=True)
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()

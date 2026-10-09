"""Run one geometry-condition inference task (src/dftgnn/mlip/geomeval.py); idempotent.

    python scripts/infer/geomeval.py --model S --r 0 --seed 0 --budget 654 [--device cuda]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from dftgnn import infer
from dftgnn.graphs.store import sha256_file
from dftgnn.io.results import write_result
from dftgnn.mlip import geomeval as GE
from dftgnn.mlip import mace_model
from dftgnn.train import Store, code_sha, runindex


def verified(out: Path, tid: str) -> bool:
    try:
        pay = json.loads(out.read_text())["payload"]
        return pay["task_id"] == tid and sha256_file(GE.REPO_ROOT / pay["predictions"]["path"]) == pay["predictions"]["sha256"]
    except (OSError, KeyError, json.JSONDecodeError):
        return False


def main(argv=None) -> str:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=["S", "D", "P"])
    ap.add_argument("--r", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--budget", type=int, required=True)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--results", default=str(GE.RESULTS))
    a = ap.parse_args(argv)
    torch.set_num_threads(a.threads)
    comps = GE.components(runindex.primary(runindex.load()), a.model, a.r, a.budget, a.seed)
    key = GE.task_key(a.model, a.r, a.budget, a.seed, comps, code_sha(), sha256_file(mace_model.model_path()))
    tid = infer.task_id(key)
    rdir = Path(a.results)
    if verified(rdir / f"{tid}.json", tid):
        print(f"{tid}: already done")
        return tid
    frame, info = GE.run(a.model, a.r, a.budget, a.seed, comps, infer.Sites(Store()), device=torch.device(a.device))
    (rdir / "predictions").mkdir(parents=True, exist_ok=True)
    pp = rdir / "predictions" / f"{tid}.parquet"
    frame.to_parquet(pp, index=False)
    write_result(tid, {"task_id": tid, "key": key, **info,
                       "predictions": {"path": str(pp.relative_to(GE.REPO_ROOT)), "sha256": sha256_file(pp),
                                       "rows": len(frame)}}, results_dir=rdir)
    print(f"{tid}: {info['n_hosts_evaluated']} hosts, {info['n_sites']} sites x 3 conditions")
    return tid


if __name__ == "__main__":
    main()

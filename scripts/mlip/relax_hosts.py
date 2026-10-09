"""Relax hosts with MACE-MP-0 medium (float64) and tile them (src/dftgnn/mlip/relax.py).

    nice -n 15 python scripts/mlip/relax_hosts.py --hosts mp-2133 mp-3187 [--device cpu] [--out-dir DIR]

Idempotent per host. The pod runs one host per queue job (stage ``relax``).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from dftgnn.graphs.store import sha256_file
from dftgnn.mlip import mace_model, release
from dftgnn.mlip.relax import OUT_DIR, relax_host

ROOT = Path(__file__).resolve().parents[2]
TILING = ROOT / "data" / "processed" / "tiling_map_v1.parquet"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hosts", nargs="+", required=True)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    ap.add_argument("--threads", type=int, default=3)
    a = ap.parse_args()
    import torch

    torch.set_num_threads(a.threads)
    cells = release.unit_cells()
    tmap = pd.read_parquet(TILING).set_index("host_id")
    path = mace_model.model_path()
    calc = mace_model.calculator(a.device, path)
    msha = sha256_file(path)
    for h in a.hosts:
        rec = relax_host(h, cells[h], tmap.loc[h].to_dict(), calc, model_sha256=msha, out_dir=Path(a.out_dir))
        print(f"{h}: converged {rec['converged']} steps {rec['steps']} fmax {rec['final_fmax_eV_per_A']:.4f} "
              f"s/step {rec['s_per_step']:.3f} skipped {rec['skipped']}", flush=True)


if __name__ == "__main__":
    main()

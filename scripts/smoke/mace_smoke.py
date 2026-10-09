"""MACE relaxation smoke on this Mac's CPU (smoke=true; outputs in data/processed/mlip_smoke/ and
results/smoke/mace_smoke.json, excluded from every analysis).

    nice -n 15 python scripts/smoke/mace_smoke.py [--n 3|5]

Hosts (5): ZnO, Sr2SnO4, the largest unit cell, the smallest-cell Ce host (f element), the smallest-cell Bi or
Pb host (heavy cation). With --n 3 (memory pressure) only the three smallest-cell of these are relaxed. In
both cases a timing-only probe runs 5 energy+force+stress evaluations on the largest unit cell, so the
per-step cost at the largest size is measured without a full relaxation.
"""
from __future__ import annotations

import argparse
import resource
import sys
import time
from pathlib import Path

import pandas as pd
import torch

from dftgnn.graphs.store import sha256_file
from dftgnn.io.results import write_result
from dftgnn.mlip import mace_model, release
from dftgnn.mlip.relax import relax_host

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "processed" / "mlip_smoke"


def peak_rss_mb() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return (r if sys.platform == "darwin" else r * 1024) / 2**20


def pick(t: pd.DataFrame) -> dict:
    t = t.sort_values(["n_uc", "host_id"])
    ce = t[t.formula.str.contains(r"Ce(?![a-z])")].iloc[0]
    hv = t[t.formula.str.contains(r"(?:Bi|Pb)(?![a-z])")].iloc[0]
    big = t.sort_values(["n_uc", "host_id"], ascending=[False, True]).iloc[0]
    return {"ZnO": t[t.formula == "ZnO"].iloc[0], "Sr2SnO4": t[t.formula == "Sr2SnO4"].iloc[0],
            "largest_cell": big, "f_element": ce, "heavy_cation": hv}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5, choices=[3, 5])
    a = ap.parse_args()
    torch.set_num_threads(3)
    tmap = pd.read_parquet(ROOT / "data/processed/tiling_map_v1.parquet")
    chosen = pick(tmap)
    roles = sorted(chosen, key=lambda k: (int(chosen[k].n_uc), k))[: a.n]
    cells = release.unit_cells()
    path = mace_model.model_path()
    rss0 = peak_rss_mb()
    calc = mace_model.calculator("cpu", path)
    msha = sha256_file(path)
    rows = []
    for role in roles:
        r = chosen[role]
        rec = relax_host(r.host_id, cells[r.host_id], r.to_dict(), calc, model_sha256=msha, out_dir=OUT, force=True)
        rows.append({"role": role, "host_id": r.host_id, "formula": r.formula, "n_atoms_uc": int(r.n_uc),
                     "n_atoms_sc": int(r.n_sc), **{k: rec[k] for k in (
                         "converged", "steps", "final_fmax_eV_per_A", "s_per_step", "relax_wall_s",
                         "initial_volume_A3", "final_volume_A3", "tiled")}, "peak_rss_mb_so_far": peak_rss_mb()})
        print(rows[-1], flush=True)
    big = chosen["largest_cell"]
    from pymatgen.io.ase import AseAtomsAdaptor

    atoms = AseAtomsAdaptor.get_atoms(cells[big.host_id])
    atoms.calc = calc
    times = []
    for k in range(5):
        atoms.rattle(1e-4, seed=k)
        t0 = time.time()
        atoms.get_potential_energy()
        atoms.get_forces()
        atoms.get_stress()
        times.append(time.time() - t0)
    probe = {"host_id": big.host_id, "formula": big.formula, "n_atoms_uc": int(big.n_uc),
             "s_per_eval_first": times[0], "s_per_eval_rest_mean": sum(times[1:]) / 4}
    print("timing probe", probe, flush=True)
    pay = {"smoke": True, "note": "MACE relaxation smoke on CPU: pipeline and timing check only, excluded from "
           "every analysis", "n_requested": a.n, "shrunk_for_memory_pressure": a.n == 3,
           "hosts_all_roles": {k: v.formula for k, v in chosen.items()}, "relaxed": rows, "timing_probe": probe,
           "peak_rss_mb": peak_rss_mb(), "rss_before_model_mb": rss0, "torch_threads": torch.get_num_threads(),
           "device": "cpu", "model_sha256": msha}
    write_result("mace_smoke", pay, results_dir=ROOT / "results" / "smoke")


if __name__ == "__main__":
    main()

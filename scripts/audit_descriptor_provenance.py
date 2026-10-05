"""Where do the K21 descriptor columns come from? Pristine unit cell vs defect calculation.

For each ML-subset row, recompute descriptors from pristine-host data shipped in
bulk_visual_data.json and compare with the CSV value.  Also test q-invariance across the three
charge-state CSVs.  No target values are read in this module.
"""
from __future__ import annotations

import json
import warnings
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from pymatgen.analysis.local_env import VoronoiNN
from pymatgen.core import Element, Structure

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/raw/unpacked/oxygen_vacancies_db"
ML = DB / "vacancy_formation_energy_ml"
DESC_DROP = ("formula", "full_name", "vacancy_formation_energy")


def host_rows(args) -> list[dict]:
    formula, rows = args
    b = json.loads((DB / f"oxygen_vacancies_db_data/{formula}/bulk_visual_data.json").read_text())
    st = Structure.from_dict(b["structure_graph"]["structure"])
    bc = np.array(b["bader_charges"])
    dos = b["dos_plot_data"]
    E = np.array(dos["relative_energies"])
    out = []
    for r in rows:
        lab = r["full_name"].split("_Va_")[1]
        eq = b["sites"][lab]["equivalent_atoms"]
        i = eq[0]
        rec = {"full_name": r["full_name"],
               "bader_charge_absdiff": float(min(abs(bc[k] - r["bader_charge"]) for k in eq)),
               "band_gap_vs_gga_absdiff": abs(r["band_gap"] - b["gga_band_gap"]),
               "ele_diele_absdiff": abs(r["ave_ele_diele"] - b["ave_ele_diele"]),
               "ion_diele_absdiff": abs(r["ave_ion_diele"] - b["ave_ion_diele"])}
        # O-2p centre from the pristine unit-cell site-projected DOS
        names = dos["names"]
        k = names.index(lab) if lab in names else None
        if k is not None:
            p = next(x for x in dos["doses"][k] if x["name"] == "p")
            rho = np.array(p["dos"], dtype=float).sum(axis=0)
            m = E <= 0
            rec["o2p_absdiff"] = abs(-(E[m] * rho[m]).sum() / rho[m].sum() - r["o2p_center_from_vbm"])
        # neighbour aggregates from the pristine unit cell (Voronoi solid-angle weights)
        polys = VoronoiNN().get_voronoi_polyhedra(st, i)
        tot = sum(p["solid_angle"] for p in polys.values())
        w, q, x, el = [], [], [], {}
        for p in polys.values():
            s = p["site"]
            kk = min(range(len(st)), key=lambda m: np.linalg.norm(((st[m].frac_coords - s.frac_coords + 0.5) % 1) - 0.5))
            w.append(p["solid_angle"] / tot)
            q.append(bc[kk])
            x.append(Element(s.specie.symbol).X)
            el[s.specie.symbol] = el.get(s.specie.symbol, 0) + w[-1]
        w, q, x = np.array(w), np.array(q), np.array(x)
        sel = w > 1 / 12
        rec.update({
            "nn_ave_bader_absdiff": abs((w * q).sum() - r["nn_ave_bader_charge"]),
            "nn_ave_eleneg_absdiff": abs((w * x).sum() - r["nn_ave_eleneg"]),
            "nn_max_bader_absdiff": abs(q[sel].max() - r["nn_max_bader_charge"]) if sel.any() else None,
            "nn_min_eleneg_absdiff": abs(x[sel].min() - r["nn_min_eleneg"]) if sel.any() else None,
            "nn_min_bader_absdiff": abs(q[sel].min() - r["nn_min_bader_charge"]) if sel.any() else None,
            "nn_max_eleneg_absdiff": abs(x[sel].max() - r["nn_max_eleneg"]) if sel.any() else None,
            "w_element_maxabsdiff": float(max(abs(el.get(e, 0) - r.get(e, 0)) for e in set(el) | {c for c in r if len(c) <= 2 and c[0].isupper()})),
        })
        out.append(rec)
    return out


def summarise(df: pd.DataFrame) -> dict:
    s = {}
    for c in df.columns[1:]:
        v = df[c].dropna()
        s[c] = {"n": int(len(v)), "max_absdiff": float(v.max()), "frac_within_1e-3": float((v < 1e-3).mean())}
    return s


def main() -> dict:
    ml = pd.read_csv(ML / "charge0.csv", index_col=0)
    ml = ml.drop(columns=["vacancy_formation_energy"])  # target never touched here
    jobs = [(f, g.to_dict("records")) for f, g in ml.groupby("formula")]
    with Pool() as pool:
        rows = [r for part in pool.map(host_rows, jobs, chunksize=4) for r in part]
    df = pd.DataFrame(rows)
    df.to_csv(ROOT / "data/processed/audit/descriptor_provenance.csv", index=False)
    res = {"recomputed_from_pristine_unit_cell": summarise(df), "n_rows": len(df)}
    # q-invariance
    m = [pd.read_csv(ML / f"charge{q}.csv", index_col=0).set_index("full_name") for q in (0, 1, 2)]
    desc = [c for c in m[0].columns if c not in DESC_DROP]
    inv = {}
    for q in (1, 2):
        com = m[0].index.intersection(m[q].index)
        cols = [c for c in desc if c in m[q].columns]
        inv[f"q0_vs_q{q}"] = {"common_sites": len(com), "columns_compared": len(cols),
                              "columns_that_differ": [c for c in cols if (m[0].loc[com, c] - m[q].loc[com, c]).abs().max() > 1e-9]}
    res["q_invariance"] = inv
    res["n_descriptor_columns"] = len(desc)
    return res


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))

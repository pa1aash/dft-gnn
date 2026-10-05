"""Flatten the Kumagai release into audit tables (data/processed/audit/*.csv).

Reads, per host, defect_visual_data.json, bulk_visual_data.json, chem_pot_diag.json and
site_info/<formula>/{cell_info.txt,supercell.cif}. No filtering, no modelling.
"""
from __future__ import annotations

import json
import re
from multiprocessing import Pool
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/raw/unpacked/oxygen_vacancies_db"
DATA = DB / "oxygen_vacancies_db_data"
SITE = DB / "site_info"
OUT = ROOT / "data/processed/audit"


def parse_cell_info(txt: str) -> dict:
    head = {
        "space_group": re.search(r"Space group: (.*)", txt).group(1).strip(),
        "transformation": re.search(r"Transformation matrix: (.*)", txt).group(1).strip(),
        "multiplicity": int(re.search(r"Cell multiplicity: (\d+)", txt).group(1)),
    }
    sites = []
    for blk in txt.split("Irreducible element: ")[1:]:
        lab = blk.split("\n", 1)[0].strip()
        g = lambda key: re.search(key + r": (.*)", blk).group(1).strip()  # noqa: E731
        eq = g("Equivalent atoms")
        idx = [i for seg in eq.split() for i in range(int(seg.split("..")[0]), int(seg.split("..")[1]) + 1)]
        sites.append({
            "label": lab, "wyckoff": g("Wyckoff letter"), "site_symmetry": g("Site symmetry"),
            "coord": g("Coordination"), "equiv": eq, "n_equiv": len(idx), "equiv_first": idx[0],
            "frac": [float(x) for x in g("Fractional coordinates").split()],
            "eneg": float(g("Electronegativity")), "ox": g("Oxidation state"),
        })
    return {**head, "sites": sites}


def one(formula: str) -> dict:
    d = json.loads((DATA / formula / "defect_visual_data.json").read_text())
    b = json.loads((DATA / formula / "bulk_visual_data.json").read_text())
    summ = d["defect_energy_summary"]
    shallows = set(d["shallows"])
    unusual = d["unusual_defects"]
    states = d["defect_states"]
    rows = []
    for site, de in summ["defect_energies"].items():
        for q, e in zip(de["charges"], de["defect_energies"], strict=True):
            key = f"{site}_{q}"
            rows.append({
                "formula": formula, "site": site, "q": q, "full_name": f"{formula}_{site}",
                "formation_energy": e["formation_energy"], "is_shallow": e["is_shallow"],
                "in_shallows_list": key in shallows,
                "pc_term": e["energy_corrections"].get("pc term"),
                "alignment_term": e["energy_corrections"].get("alignment term"),
                "flags": "|".join(unusual.get(key, [])), "state": states.get(key),
                "atom_io": json.dumps(de["atom_io"]),
            })
    states_rows = [{"formula": formula, "key": k, "status": v} for k, v in states.items()]
    st = b["structure_graph"]["structure"]
    lat = st["lattice"]
    host = {
        "formula": formula, "mp_id": b["mp_id"], "space_group": b["space_group"],
        "space_group_num": b["space_group_num"], "band_gap": b["band_gap"],
        "gga_band_gap": b["gga_band_gap"], "ave_ele_diele": None, "n_atoms_uc": len(st["sites"]),
        "uc_a": lat["a"], "uc_b": lat["b"], "uc_c": lat["c"], "uc_volume": lat["volume"],
        "bader_host": json.dumps(b["bader_charges"]), "vbm": d["vbm"], "cbm": d["cbm"],
        "n_vac_calcs_states": len(states),
        "elements": "|".join(sorted({s["species"][0]["element"] for s in st["sites"]})),
        "sites_json": json.dumps({k: {x: v[x] for x in ("element", "wyckoff_letter",
                                  "site_symmetry")} for k, v in b["sites"].items()}),
    }
    host["ave_ele_diele"] = b["ave_ele_diele"]
    host["ave_ion_diele"] = b["ave_ion_diele"]
    ci = parse_cell_info((SITE / formula / "cell_info.txt").read_text())
    cif = (SITE / formula / "supercell.cif").read_text()
    m = {k: float(re.search(rf"_cell_length_{k}\s+(\S+)", cif).group(1)) for k in "abc"}
    ang = {k: float(re.search(rf"_cell_angle_{k}\s+(\S+)", cif).group(1))
           for k in ("alpha", "beta", "gamma")}
    host.update({f"sc_{k}": v for k, v in m.items()})
    host.update({f"sc_{k}": v for k, v in ang.items()})
    host["sc_natoms"] = len(re.findall(r"^\s+[A-Z][a-z]?\s+\S+\s+1\s+[-\d.]+\s+[-\d.]+\s+[-\d.]+\s+1\s*$",
                                       cif, re.M))
    host["sc_transformation"] = ci["transformation"]
    host["sc_multiplicity"] = ci["multiplicity"]
    cells = [{"formula": formula, **s} for s in ci["sites"]]
    return {"rows": rows, "host": host, "cells": cells, "states": states_rows}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    forms = sorted(p.name for p in DATA.iterdir() if p.is_dir())
    with Pool() as pool:
        res = pool.map(one, forms, chunksize=8)
    pd.DataFrame([r for x in res for r in x["rows"]]).to_csv(OUT / "defects_full.csv", index=False)
    pd.DataFrame([x["host"] for x in res]).to_csv(OUT / "hosts_full.csv", index=False)
    pd.DataFrame([r for x in res for r in x["states"]]).to_csv(OUT / "defect_states.csv", index=False)
    cells = pd.DataFrame([c for x in res for c in x["cells"]])
    cells["frac"] = cells["frac"].map(json.dumps)
    cells.to_csv(OUT / "cell_sites.csv", index=False)
    print(len(forms), "hosts")


if __name__ == "__main__":
    main()

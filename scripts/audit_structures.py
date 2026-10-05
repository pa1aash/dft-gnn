"""Structure audit: CIF join coverage, pristine-vs-defect test, site identification, families."""
from __future__ import annotations

import ast
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from pymatgen.core import Composition, Element, Structure

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
AUD = ROOT / "data/processed/audit"
DB = ROOT / "data/raw/unpacked/oxygen_vacancies_db"
SITE = DB / "site_info"


def parse_equiv(eq: str) -> list[int]:
    return [i for seg in eq.split() for i in range(int(seg.split("..")[0]), int(seg.split("..")[1]) + 1)]


def audit_host(formula: str, host: pd.Series, cells: pd.DataFrame) -> dict:
    st = Structure.from_file(SITE / formula / "supercell.cif")
    uc_json = json.loads((DB / f"oxygen_vacancies_db_data/{formula}/bulk_visual_data.json").read_text())
    uc = Structure.from_dict(uc_json["structure_graph"]["structure"])
    mult = int(host.sc_multiplicity)
    o_idx = [i for i, s in enumerate(st) if s.specie.symbol == "O"]
    row = {
        "formula": formula, "n_atoms_sc": len(st), "n_atoms_uc": len(uc), "multiplicity": mult,
        "n_atoms_equals_uc_times_mult": len(st) == len(uc) * mult,
        "composition_equals_uc_times_mult": st.composition.reduced_composition == uc.composition.reduced_composition
        and abs(st.composition.num_atoms - uc.composition.num_atoms * mult) < 1e-9,
        "n_O_sc": len(o_idx), "n_O_uc": sum(1 for s in uc if s.specie.symbol == "O"),
        "a": st.lattice.a, "b": st.lattice.b, "c": st.lattice.c,
        "alpha": st.lattice.alpha, "beta": st.lattice.beta, "gamma": st.lattice.gamma,
        "volume_sc": st.volume, "volume_uc": uc.volume, "volume_ratio": st.volume / uc.volume / mult,
        "min_dist": float(np.min(st.distance_matrix + np.eye(len(st)) * 99)) if len(st) <= 500 else None,
        "reduced_formula": uc.composition.reduced_formula,
    }
    # site identification
    o_cells = cells[(cells.formula == formula) & cells.label.str.startswith("O")]
    covered: list[int] = []
    ok_first = ok_all_O = ok_counts = True
    cn = {}
    for _, c in o_cells.iterrows():
        idx = parse_equiv(c.equiv)
        covered += idx
        frac = np.array(json.loads(c.frac))
        first = st[idx[0]]
        d = st.lattice.get_distance_and_image(first.frac_coords, frac)[0]
        ok_first &= d < 1e-2
        ok_all_O &= all(st[i].specie.symbol == "O" for i in idx)
        uc_eq = uc_json["sites"][c.label]["equivalent_atoms"] if c.label in uc_json["sites"] else None
        ok_counts &= uc_eq is not None and len(idx) == len(uc_eq) * mult
        coord = ast.literal_eval(c.coord)
        cn[c.label] = sum(len(v) for v in coord.values())
    row.update({
        "n_O_labels": len(o_cells), "labels_cover_all_O_exactly": sorted(covered) == o_idx,
        "first_equiv_matches_frac": bool(ok_first), "equiv_atoms_all_O": bool(ok_all_O),
        "equiv_counts_match_uc_times_mult": bool(ok_counts), "cn_by_label": json.dumps(cn),
    })
    return row


def main() -> dict:
    hosts = pd.read_csv(AUD / "hosts_full.csv").set_index("formula", drop=False)
    cells = pd.read_csv(AUD / "cell_sites.csv")
    from multiprocessing import Pool
    with Pool() as pool:
        rows = pool.starmap(audit_host, [(f, hosts.loc[f], cells) for f in hosts.index], chunksize=8)
    df = pd.DataFrame(rows)
    df.to_csv(AUD / "structure_audit.csv", index=False)
    return {"n_hosts": len(df)}


if __name__ == "__main__":
    print(main())

"""Hand verification of ZnO end to end: CSV row -> CIF -> the O site to be removed."""
from __future__ import annotations

import io
import json
import re
import tarfile
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from pymatgen.core import Structure

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/raw/unpacked/oxygen_vacancies_db"


def main() -> dict:
    ml = pd.read_csv(DB / "vacancy_formation_energy_ml/charge0.csv", index_col=0)
    row = ml[ml.full_name == "ZnO_Va_O1"].iloc[0]
    info = (DB / "site_info/ZnO/cell_info.txt").read_text()
    label = row.full_name.split("_Va_")[1]  # O1
    blk = info.split(f"Irreducible element: {label}")[1].split("Irreducible element")[0]
    equiv = re.search(r"Equivalent atoms: (\d+)\.\.(\d+)", blk)
    first, last = int(equiv.group(1)), int(equiv.group(2))
    frac = [float(x) for x in re.search(r"Fractional coordinates: (.*)", blk).group(1).split()]
    st = Structure.from_file(DB / "site_info/ZnO/supercell.cif")
    site = st[first]
    out: dict = {
        "csv_row": {"full_name": row.full_name, "target_vacancy_formation_energy_eV": float(row.vacancy_formation_energy),
                    "band_gap": float(row.band_gap), "bader_charge": float(row.bader_charge)},
        "cell_info": {"label": label, "equiv_atoms": f"{first}..{last}", "frac_listed": frac},
        "cif": {"formula": st.composition.formula, "n_atoms": len(st), "lattice_abc": [round(x, 5) for x in st.lattice.abc],
                "angles": [round(x, 3) for x in st.lattice.angles]},
        "site": {"index": first, "species": site.specie.symbol, "frac": [round(x, 6) for x in site.frac_coords],
                 "cart_A": [round(x, 5) for x in site.coords]},
    }
    nn = sorted(st.get_neighbors(site, 3.2), key=lambda n: n.nn_distance)
    shell1 = [n for n in nn if n.nn_distance < 2.5]
    out["first_shell"] = [{"species": n.specie.symbol, "index": int(n.index), "distance_A": round(n.nn_distance, 4)} for n in shell1]
    vec = [n.coords - site.coords for n in shell1]
    ang = [float(np.degrees(np.arccos(np.dot(a, b) / np.linalg.norm(a) / np.linalg.norm(b))))
           for i, a in enumerate(vec) for b in vec[i + 1:]]
    out["zn_o_zn_angles_deg"] = [round(x, 2) for x in sorted(ang)]
    out["second_shell_within_3.2A"] = [{"species": n.specie.symbol, "distance_A": round(n.nn_distance, 3)}
                                        for n in nn if n.nn_distance >= 2.5]
    # every equivalent O has the same shell
    cns = {len([n for n in st.get_neighbors(st[i], 2.5)]) for i in range(first, last + 1)}
    out["coordination_numbers_over_all_150_O"] = sorted(cns)
    out["all_equiv_atoms_are_O"] = all(st[i].specie.symbol == "O" for i in range(first, last + 1))
    out["O_atoms_in_cell"] = sum(1 for s in st if s.specie.symbol == "O")
    # pristine vs defect-relaxed: compare to the q=0 relaxed defect cell
    with tarfile.open(DB / "oxygen_vacancies_db_data/ZnO/ZnO_Va_O1_0.tar.gz") as t:
        name = next(m for m in t.getnames() if m.endswith("CONTCAR-finish"))
        dst = Structure.from_str(t.extractfile(name).read().decode(), fmt="poscar")
    out["defect_relaxed_cell"] = {"n_atoms": len(dst), "formula": dst.composition.formula,
                                  "lattice_abc": [round(x, 5) for x in dst.lattice.abc]}
    # match atoms (same cell, PBC) to find the missing one
    d = st.lattice.get_all_distances(st.frac_coords, dst.frac_coords)
    best = d.min(axis=1)
    missing = int(np.argmax(best))
    out["missing_atom_index_in_pristine"] = missing
    out["missing_atom_species"] = st[missing].specie.symbol
    out["missing_atom_is_target_site"] = missing == first or best[first] > 0.5
    out["missing_atom_match_distance_A"] = float(best[missing])
    out["pristine_vs_relaxed_displacement_A"] = {
        "max_of_matched_atoms": float(np.sort(best)[-2]), "median": float(np.median(best[best < 0.5])),
        "n_atoms_displaced_over_0.05A": int((best[best < 0.5] > 0.05).sum())}
    return out


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))

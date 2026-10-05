"""Join coverage, polymorphs, chemistry families, spin channels (counts only, no decisions)."""
from __future__ import annotations

import json
import warnings
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
from pymatgen.core import Element

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
AUD = ROOT / "data/processed/audit"
DB = ROOT / "data/raw/unpacked/oxygen_vacancies_db"


def spin_channels(formula: str) -> list[dict]:
    d = json.loads((DB / f"oxygen_vacancies_db_data/{formula}/defect_visual_data.json").read_text())
    out = []
    for key, v in d["defect_details"].items():
        info = next((x for x in v if isinstance(x, dict) and "orbital_infos" in x), None)
        out.append({"formula": formula, "key": key, "n_spin_channels": len(info["orbital_infos"]) if info else None})
    return out


def group_of(sym: str) -> int:
    el = Element(sym)
    return 3 if el.is_lanthanoid or el.is_actinoid else el.group


def families(hosts: pd.DataFrame) -> dict:
    cat = hosts.elements.str.split("|").map(lambda e: tuple(sorted(x for x in e if x != "O")))
    grp_set = cat.map(lambda c: tuple(sorted({group_of(x) for x in c})))
    grp_multi = cat.map(lambda c: tuple(sorted(group_of(x) for x in c)))
    return {"hosts": len(hosts), "cation_set": int(cat.nunique()), "group_pattern_distinct_groups": int(grp_set.nunique()),
            "group_pattern_multiset_per_cation": int(grp_multi.nunique()),
            "n_cations_hist": {int(k): int(v) for k, v in cat.map(len).value_counts().sort_index().items()}}


def main() -> dict:
    hosts = pd.read_csv(AUD / "hosts_full.csv")
    defects = pd.read_csv(AUD / "defects_full.csv")
    cells = pd.read_csv(AUD / "cell_sites.csv")
    sa = pd.read_csv(AUD / "structure_audit.csv")
    ml = pd.read_csv(DB / "vacancy_formation_energy_ml/charge0.csv", index_col=0)
    a = defects[defects.q == 0].copy()
    cif_formulas = {p.name for p in (DB / "site_info").iterdir() if p.is_dir()}
    cellkey = set(cells.formula + "_Va_" + cells.label)
    res: dict = {}
    for name, df in (("a_all_neutral", a), ("b_ml_neutral", ml)):
        res[f"cif_join_{name}"] = {
            "rows": len(df), "formula_has_cif": int(df.formula.isin(cif_formulas).sum()),
            "site_label_in_cell_info": int(df.full_name.isin(cellkey).sum()),
            "rows_in_hosts_with_anomalous_cell": int(df.formula.isin(
                sa[~sa.equiv_counts_match_uc_times_mult | ~sa.n_atoms_equals_uc_times_mult].formula).sum()),
        }
    res["cell_info_O_entries"] = int(cells.label.str.startswith("O").sum())
    res["anomalous_hosts"] = sa[~sa.equiv_counts_match_uc_times_mult | ~sa.n_atoms_equals_uc_times_mult][
        ["formula", "n_atoms_sc", "n_atoms_uc", "multiplicity", "volume_ratio", "equiv_counts_match_uc_times_mult"]
    ].to_dict("records")
    # polymorphs
    res["polymorph"] = {
        "release_hosts": len(hosts), "unique_formula_strings": int(hosts.formula.nunique()),
        "unique_reduced_formula_from_structure": int(sa.reduced_formula.nunique()),
        "unique_mp_id": int(hosts.mp_id.nunique()),
        "formulas_with_more_than_one_polymorph": int((hosts.groupby("formula").mp_id.nunique() > 1).sum()),
    }
    # families
    anion = {x for e in hosts.elements for x in e.split("|")} - {"O"}
    non_metal = sorted(x for x in anion if Element(x).is_halogen or Element(x).is_chalcogen
                       or x in ("N", "P", "As", "Sb", "B", "C", "Si", "H"))
    res["families"] = {
        "release_937": families(hosts),
        "a_neutral_hosts": families(hosts[hosts.formula.isin(a.formula)]),
        "b_ml_hosts": families(hosts[hosts.formula.isin(ml.formula)]),
        "elements_in_release": len(anion) + 1,
        "hosts_without_any_cation_other_than_O": int((hosts.elements == "O").sum()),
        "possible_non_oxide_anion_elements_present": non_metal,
    }
    # host element groups (magnetic 3d check by composition: Mn-Ni excluded by K21 Sec II A)
    mag3d = {"Mn", "Fe", "Co", "Ni"}
    res["hosts_with_Mn_Fe_Co_Ni"] = int(hosts.elements.map(lambda e: bool(mag3d & set(e.split("|")))).sum())
    # spin channels in defect calculations
    with Pool() as pool:
        sp = pd.DataFrame([r for rows in pool.map(spin_channels, list(hosts.formula), chunksize=8) for r in rows])
    sp["q"] = sp.key.str.rsplit("_", n=1).str[1].astype(int)
    res["spin_channels_in_defect_calcs"] = {
        f"q{q}": sp[sp.q == q].n_spin_channels.value_counts(dropna=False).to_dict() for q in (0, 1, 2)}
    res["spin_channels_in_defect_calcs"] = {k: {str(a): int(b) for a, b in v.items()} for k, v in
                                            res["spin_channels_in_defect_calcs"].items()}
    nsp0 = sp[(sp.q == 0) & (sp.n_spin_channels == 2)]
    res["neutral_spin_polarised_calcs"] = {"entries": len(nsp0), "hosts": int(nsp0.formula.nunique()),
                                           "in_b": int(nsp0.merge(ml.assign(key="Va_" + ml.full_name.str.split("_Va_").str[1] + "_0"),
                                                                  left_on=["formula", "key"], right_on=["formula", "key"]).shape[0])}
    return res


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))

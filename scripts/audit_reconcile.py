"""Universe reconciliation: full release (a), K21 ML subset (b), 937 hosts (c), K25 sets (d)."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUD = ROOT / "data/processed/audit"
DB = ROOT / "data/raw/unpacked/oxygen_vacancies_db"
K25 = ROOT / "data/raw/unpacked/ML_charged_defects/oxy_vac_data"
DYN_UNSTABLE = ("K2Cd2O3", "Ba2Ti(GeO4)2", "Cs2O")  # K21 Sec. III A / K21-SM Fig. S4
FLAGS = ("vacancy_split", "unknown", "not same config from init", "energy strange")


def k25_entries(variant: str) -> pd.DataFrame:
    rows = []
    for p in sorted((K25 / variant).glob("*.json")):
        d = json.loads(p.read_text())
        for name, idx, val, q in zip(d["target_site_names"], d["target_site_indices"],
                                     d["target_vals"], d["charges"], strict=True):
            rows.append({"formula": d["formula"], "site": f"Va_{name}", "site_index": idx,
                         "q": q, "target": val})
    df = pd.DataFrame(rows)
    df["full_name"] = df.formula + "_" + df.site
    return df


def flag_table(df: pd.DataFrame) -> dict:
    out = {"n": len(df), "hosts": int(df.formula.nunique())}
    fl = df["flags"].fillna("")
    for f in FLAGS:
        out[f] = int(fl.str.split("|").map(lambda x, f=f: f in x).sum())
    out["any_unusual_flag"] = int((fl != "").sum())
    shallow = df["is_shallow"].eq(True)
    undetermined = df["is_shallow"].isna()  # band edges undetermined (K21 Sec. III A: 59)
    out["PHS_is_shallow"] = int(shallow.sum())
    out["band_edges_undetermined"] = int(undetermined.sum())
    out["PHS_in_shallows_list"] = int(df.in_shallows_list.sum())
    out["supergroup"] = 0  # string never occurs in unusual_defects (checked below)
    out["dynamically_unstable_host"] = int(df.formula.isin(DYN_UNSTABLE).sum())
    out["fizzled_or_failed"] = None
    out["any_flag_or_PHS_or_dyn"] = int(((fl != "") | shallow | undetermined | df.formula.isin(DYN_UNSTABLE)).sum())
    out["clean_all_flags"] = int(((fl == "") & ~shallow & ~undetermined & ~df.formula.isin(DYN_UNSTABLE)).sum())
    return out


def main() -> dict:
    d = pd.read_csv(AUD / "defects_full.csv")
    hosts = pd.read_csv(AUD / "hosts_full.csv")
    states = pd.read_csv(AUD / "defect_states.csv")
    states["q"] = states.key.str.rsplit("_", n=1).str[1].astype(int)
    ml = {q: pd.read_csv(DB / f"vacancy_formation_energy_ml/charge{q}.csv", index_col=0) for q in (0, 1, 2)}
    res: dict = {}

    a = d[d.q == 0].copy()
    b = ml[0]
    in_b = a.full_name.isin(b.full_name)
    res["a_all_neutral_completed"] = {"entries": len(a), "hosts": int(a.formula.nunique())}
    res["a_attempted_neutral"] = {
        "entries": int((states.q == 0).sum()),
        "fizzled": int(((states.q == 0) & (states.status == "fizzled")).sum()),
        "hosts": int(states[states.q == 0].formula.nunique())}
    res["b_ml_subset"] = {"entries": len(b), "hosts": int(b.formula.nunique()),
                          "b_subset_of_a": bool(b.full_name.isin(a.full_name).all())}
    res["c_release_hosts"] = {"hosts": len(hosts), "unique_mp_id": int(hosts.mp_id.nunique()),
                              "hosts_with_no_completed_neutral": sorted(set(hosts.formula) - set(a.formula))}
    res["flags_a"] = flag_table(a)
    res["flags_b"] = flag_table(a[in_b])
    res["flags_a_minus_b"] = flag_table(a[~in_b])
    # flags in (a) at charge 1 and 2 for the record
    res["flags_all_charges"] = {int(q): flag_table(d[d.q == q]) for q in (0, 1, 2)}
    res["ml_by_charge"] = {int(q): {"entries": len(v), "hosts": int(v.formula.nunique())} for q, v in ml.items()}
    # unusual_defects flag vocabulary
    vocab = sorted({x for s in d["flags"].dropna() for x in s.split("|")})
    res["flag_vocabulary_in_unusual_defects"] = vocab

    # K25
    k_with = k25_entries("materials_coreAlign_with_PHS")
    k_wo = k25_entries("materials_coreAlign")
    for name, k in (("with_PHS", k_with), ("without_PHS", k_wo)):
        k0 = k[k.q == 0]
        res[f"d_k25_{name}"] = {
            "hosts_files": int(k.formula.nunique()), "all_charge_entries": len(k),
            "sites_distinct": int(k.full_name.nunique()), "neutral_entries": len(k0),
            "neutral_hosts": int(k0.formula.nunique()),
            "q1_entries": int((k.q == 1).sum()), "q2_entries": int((k.q == 2).sum()),
            "neutral_in_a": int(k0.full_name.isin(a.full_name).sum()),
            "neutral_in_b": int(k0.full_name.isin(b.full_name).sum()),
            "neutral_not_in_a": int((~k0.full_name.isin(a.full_name)).sum()),
        }
    k0w, k0o = k_with[k_with.q == 0], k_wo[k_wo.q == 0]
    res["d_overlaps"] = {
        "b_minus_k25_with": int((~b.full_name.isin(k0w.full_name)).sum()),
        "b_minus_k25_without": int((~b.full_name.isin(k0o.full_name)).sum()),
        "k25_without_minus_b": int((~k0o.full_name.isin(b.full_name)).sum()),
        "k25_with_minus_b": int((~k0w.full_name.isin(b.full_name)).sum()),
        "b_and_k25_without": int(b.full_name.isin(k0o.full_name).sum()),
        "b_and_k25_with": int(b.full_name.isin(k0w.full_name).sum()),
        "a_minus_k25_with": int((~a.full_name.isin(k0w.full_name)).sum()),
    }
    return res


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))

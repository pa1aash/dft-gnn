"""Kiyohara et al. (PRL 135, 246101) released split mapped onto our keys."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from audit_reconcile import AUD, DB, K25, k25_entries

ROOT = Path(__file__).resolve().parents[1]


def lists(ph: str) -> dict[str, list[str]]:
    return {sp: [x for x in (K25 / f"{sp}_{ph}_PHS.txt").read_text().splitlines() if x.strip()]
            for sp in ("train", "val", "test")}


def main() -> dict:
    b = pd.read_csv(DB / "vacancy_formation_energy_ml/charge0.csv", index_col=0)
    a = pd.read_csv(AUD / "defects_full.csv")
    a = a[a.q == 0]
    hosts = set(pd.read_csv(AUD / "hosts_full.csv").formula)
    res: dict = {"reported": {"q0_test_MAE_eV": 0.29, "q1_test_MAE_eV": 0.22, "q2_test_MAE_eV": 0.37,
                              "source": "K25 p. 2, p. 6, Fig. 3(a); K25-SI (see docs/provenance.md row 10)",
                              "test_set_size_oxides_reported": "about 140 (Fig. 3 caption); 139 in test_wo_PHS.txt"}}
    for ph, variant in (("wo", "materials_coreAlign"), ("w", "materials_coreAlign_with_PHS")):
        sp = lists(ph)
        ent = k25_entries(variant)
        ent0 = ent[ent.q == 0]
        allf = [f for v in sp.values() for f in v]
        r = {"n_formulas": {k: len(v) for k, v in sp.items()}, "total": len(allf), "unique_total": len(set(allf)),
             "disjoint": len(allf) == len(set(allf)),
             "formulas_not_in_release": len(set(allf) - hosts),
             "formulas_in_json_variant_not_in_split": sorted(set(ent.formula) - set(allf)),
             "formulas_in_split_not_in_json_variant": sorted(set(allf) - set(ent.formula))}
        for name, f in sp.items():
            e0 = ent0[ent0.formula.isin(f)]
            r[name] = {
                "hosts": len(f), "k25_neutral_entries": len(e0),
                "hosts_in_b": len(set(f) & set(b.formula)), "entries_in_b": int(e0.full_name.isin(b.full_name).sum()),
                "b_entries_in_these_hosts": int(b.formula.isin(f).sum()),
                "b_entries_in_these_hosts_not_in_k25_entries": int((~b[b.formula.isin(f)].full_name.isin(e0.full_name)).sum()),
                "release_neutral_entries_in_these_hosts": int(a.formula.isin(f).sum()),
            }
        r["b_hosts_not_in_any_split"] = int(len(set(b.formula) - set(allf)))
        r["b_entries_not_in_any_split_host"] = int((~b.formula.isin(allf)).sum())
        res[f"split_{ph}_PHS"] = r
    return res


if __name__ == "__main__":
    import json
    print(json.dumps(main(), indent=1, default=str))

"""Descriptive target sanity for neutral E_f. No descriptor-target correlation, no model."""
from __future__ import annotations

import numpy as np
import pandas as pd

from audit_reconcile import AUD, DB, k25_entries


def main() -> dict:
    a = pd.read_csv(AUD / "defects_full.csv")
    a0 = a[a.q == 0]
    b = pd.read_csv(DB / "vacancy_formation_energy_ml/charge0.csv", index_col=0)
    y = b.vacancy_formation_energy
    mu, sd = y.mean(), y.std(ddof=1)
    z = (y - mu) / sd
    out_df = b.loc[z.abs() > 4, ["full_name", "vacancy_formation_energy"]].assign(z=z[z.abs() > 4])
    q = y.quantile([0, .01, .05, .25, .5, .75, .95, .99, 1])
    j = b.merge(a0[["full_name", "formation_energy", "pc_term", "alignment_term"]], on="full_name",
                suffixes=("_hostcol", "_release"))
    diff = (j.vacancy_formation_energy - j.formation_energy_release).abs()
    k0 = k25_entries("materials_coreAlign_with_PHS")
    k0 = k0[k0.q == 0].merge(a0[["full_name", "formation_energy"]], on="full_name")
    return {
        "n": len(y), "units": "eV (per vacancy, neutral, reference mu_O: Delta mu_O = 0 as released)",
        "mean": float(mu), "sd_ddof1": float(sd), "min": float(y.min()), "max": float(y.max()),
        "quantiles": {str(k): float(v) for k, v in q.items()},
        "skew": float(y.skew()), "excess_kurtosis": float(y.kurt()),
        "outliers_beyond_4sd": out_df.to_dict("records"),
        "n_beyond_3sd": int((z.abs() > 3).sum()),
        "release_neutral_pc_term_all_zero": bool((a0.pc_term.fillna(0).abs() < 1e-12).all()),
        "release_neutral_alignment_term_all_zero": bool((a0.alignment_term.fillna(0).abs() < 1e-12).all()),
        "release_neutral_max_abs_pc_term": float(a0.pc_term.abs().max()),
        "release_neutral_max_abs_alignment_term": float(a0.alignment_term.abs().max()),
        "one_value_per_site": bool(a0.full_name.is_unique and b.full_name.is_unique),
        "ml_vs_release_same_site": {"matched": len(j), "n_mismatch_gt_1e-9": int((diff > 1e-9).sum()),
                                    "max_abs_diff": float(diff.max())},
        "k25_neutral_vs_release": {"matched": len(k0), "n_mismatch_gt_1e-6": int(((k0.target - k0.formation_energy).abs() > 1e-6).sum()),
                                   "max_abs_diff": float((k0.target - k0.formation_energy).abs().max())},
        "csv_column_named_formation_energy_is_host_property": True,
        "release_neutral_formation_energy_nonfinite": int((~np.isfinite(a0.formation_energy)).sum()),
        "release_neutral_min": float(a0.formation_energy.min()), "release_neutral_max": float(a0.formation_energy.max()),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(main(), indent=1, default=str))

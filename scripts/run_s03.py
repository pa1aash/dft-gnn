"""S03: filter cascade, gate G0, variance decomposition, spin bookkeeping (all via write_result).

Rebuilds the universe from the release, checks it against the tracked IDs file, then writes
results/{filter_cascade,g0,variance_decomposition,spin_bookkeeping}.json. If G0 fails it
writes GATE_FAIL.md and stops before the analyses.
"""
from __future__ import annotations

import hashlib
import math
import sys
import warnings

import numpy as np
import pandas as pd

from dftgnn.config import load_config
from dftgnn.data import universe as U
from dftgnn.io.results import REPO_ROOT, write_result
from dftgnn.stats.variance import oneway_icc, within_group_spread

warnings.filterwarnings("ignore")
G0_MIN_HOSTS = 400
ICC_RULE = 0.70
N_BOOT = 2000


def reml_check(y: np.ndarray, groups: np.ndarray) -> dict:
    import statsmodels.formula.api as smf

    df = pd.DataFrame({"y": y, "g": groups})
    fit = smf.mixedlm("y ~ 1", df, groups=df["g"]).fit(reml=True)
    sb2, sw2 = float(fit.cov_re.iloc[0, 0]), float(fit.scale)
    return {"estimator": "REML (statsmodels MixedLM), point estimate only, cross-check",
            "sigma2_between": sb2, "sigma2_within": sw2, "icc": sb2 / (sb2 + sw2),
            "converged": bool(fit.converged)}


def main() -> None:
    cfg = load_config()
    uni, cas = U.build_universe(cfg, return_cascade=True)
    ids = U.ids_csv_bytes(uni)
    if ids != U.IDS_FILE.read_bytes():
        sys.exit("universe does not reproduce the tracked IDs file; rebuild and commit first")
    ids_sha = hashlib.sha256(ids).hexdigest()

    # ---- filter cascade
    k25 = uni.kiyohara_split.value_counts().to_dict()
    write_result("filter_cascade", {
        "universe": cfg.data.universe, "ids_file": "data/universe_v1_ids.csv",
        "ids_sha256": ids_sha, "filters_applied": list(cfg.data.filters),
        "steps": cas.steps, "d3": cas.d3,
        "kiyohara_split_sites": {k: int(k25.get(k, 0)) for k in ("train", "val", "test", "absent")},
        "kiyohara_split_hosts": {k: int(v) for k, v in
                                 uni.groupby("kiyohara_split").formula.nunique().items()},
        "notes": [
            ("release step counts completed neutral calculations (2121 attempted, 18 fizzled; "
             "data_audit.md section 3)."),
            ("formulas are counted as distinct pymatgen reduced formulas; the release has no "
             "polymorphs, so formulas equal hosts at every step."),
            ("release -> ml_subset reasons are inferred from release flags; the K21 filter code "
             "is not released. The 4 Sr2Zr7O16 O5-O8 entries carry no flag."),
            ("Kiyohara split: the without-PHS lists of K25-code; 'absent' means the host is in "
             "no list."),
        ],
    }, config=cfg)

    # ---- gate G0
    n_hosts = int(uni.formula.nunique())
    passed = n_hosts >= G0_MIN_HOSTS
    max_budget = math.floor((1 - cfg.split.test_fraction) * n_hosts)
    if not passed:
        (REPO_ROOT / "GATE_FAIL.md").write_text(
            f"# Gate G0 failed\n\nFinal universe has {n_hosts} hosts (< {G0_MIN_HOSTS}).\n"
            f"See results/filter_cascade.json for the step at which hosts were lost.\n")
    write_result("g0", {
        "criterion": f"final host count >= {G0_MIN_HOSTS}", "n_hosts": n_hosts,
        "n_sites": len(uni), "n_formulas": int(uni.reduced_formula.nunique()), "pass": passed,
        "test_fraction": cfg.split.test_fraction,
        "max_feasible_training_budget_hosts": max_budget,
        "max_budget_rule": "floor((1 - test_fraction) * n_hosts)",
    }, config=cfg)
    if not passed:
        sys.exit(f"G0 FAIL: {n_hosts} hosts")

    # ---- variance decomposition (target only)
    y = uni.target_Ef_eV.to_numpy()
    seed = cfg.split.seeds[0]
    host = oneway_icc(y, uni.formula.to_numpy(), n_boot=N_BOOT, ci=cfg.stats.ci, seed=seed)
    formula = oneway_icc(y, uni.reduced_formula.to_numpy(), n_boot=N_BOOT, ci=cfg.stats.ci,
                         seed=seed)
    multi = uni[uni.groupby("formula").formula.transform("size") >= 2]
    sens = oneway_icc(multi.target_Ef_eV.to_numpy(), multi.formula.to_numpy(), n_boot=N_BOOT,
                      ci=cfg.stats.ci, seed=seed)
    within_on = bool(host["icc"] >= ICC_RULE)
    write_result("variance_decomposition", {
        "target": "target_Ef_eV (neutral O-vacancy formation energy, eV, as released by K21)",
        "universe": cfg.data.universe, "ids_sha256": ids_sha,
        "host": host, "formula": formula,
        "polymorph_note": "no reduced formula has more than one host in the universe, so the "
                          "formula grouping equals the host grouping",
        "host_reml_crosscheck": reml_check(y, uni.formula.to_numpy()),
        "host_sensitivity_hosts_with_ge2_sites": sens,
        "within_host_spread": within_group_spread(y, uni.formula.to_numpy()),
        "rule": {
            "statement": "Pre-specified: if ICC_host >= 0.70, within-host residual MAE becomes a "
                         "reported secondary metric throughout.",
            "threshold": ICC_RULE, "applied_to": "ICC_host point estimate (method of moments)",
            "metric_definition": (
                "Within-host residual MAE: over test hosts with >= 2 sites, for site j of host i "
                "r_ij = (y_ij - mean_j y_ij) - (yhat_ij - mean_j yhat_ij), i.e. each host's mean "
                "prediction is subtracted from its predictions and each host's mean target from "
                "its targets; the metric is the mean of |r_ij| over all such sites. "
                "Implemented as dftgnn.stats.variance.within_host_residual_mae."),
        },
        "outcome": {"icc_host": host["icc"], "icc_host_ci": host["icc_ci"],
                    "within_host_secondary_metric": within_on},
    }, config=cfg)

    # ---- spin bookkeeping (no modelling)
    m = uni.defect_moment_muB
    sp = uni[uni.spin_polarised]
    big = uni[m.abs() > 0.5]
    qs = (0.0, 0.05, 0.25, 0.5, 0.75, 0.95, 1.0)
    write_result("spin_bookkeeping", {
        "source": ("defect_visual_data.json -> defect_details['Va_<label>_0'][1] "
                   "(pydefect BandEdgeOrbitalInfos of the final neutral defect calculation). The "
                   "release has no magnetisation field; spin_polarised = two spin channels in "
                   "orbital_infos; defect_moment_muB = sum_k w_k sum_b (occ_up - occ_down) over "
                   "the stored band window."),
        "window_check": {"min_lowest_band_occupation_both_channels":
                         float(uni.window_floor_min_occupation.min()),
                         "kpt_weights_note": "weights sum to 1 for every entry (checked in S03)",
                         "meaning": "lowest stored band fully occupied in both channels for every "
                                    "entry, so the window sum equals the cell moment"},
        "n_entries": len(uni), "n_spin_polarised": len(sp),
        "n_hosts_with_spin_polarised_entry": int(sp.formula.nunique()),
        "n_abs_moment_gt_0p5": len(big),
        "moment_quantiles_spin_polarised": {f"q{round(q * 100):02d}": float(sp.defect_moment_muB.quantile(q))
                                            for q in qs},
        "moment_counts_spin_polarised_rounded_0p1": {
            f"{k:.1f}": int(v) for k, v in sp.defect_moment_muB.round(1).value_counts().sort_index().items()},
        "entries_abs_moment_gt_0p5": [
            {"site_id": r.site_id, "defect_moment_muB": round(float(r.defect_moment_muB), 4),
             "target_Ef_eV": round(float(r.target_Ef_eV), 4)}
            for r in big.sort_values("site_id").itertuples()],
        "target_by_group_eV": {
            "spin_polarised_mean": float(sp.target_Ef_eV.mean()),
            "not_spin_polarised_mean": float(uni.target_Ef_eV[~uni.spin_polarised].mean()),
            "abs_moment_gt_0p5_mean": float(big.target_Ef_eV.mean()),
        },
    }, config=cfg)
    print(f"G0 pass, hosts={n_hosts}, max budget={max_budget}, ICC_host={host['icc']:.4f} "
          f"{host['icc_ci']}, ICC_formula={formula['icc']:.4f} {formula['icc_ci']}, "
          f"within_host={within_on}, spin={len(sp)}, |m|>0.5={len(big)}")


if __name__ == "__main__":
    main()

"""S10 steps 2-3: G1 primary and secondary analyses (ANALYSIS_PLAN §7, §11; docs/deviations.md 2026-10-08).

Reads results/analysis/eval_table.parquet and eval_capsens.parquet (hashes checked against
results/g1_eval_table.json) and writes, via write_result,

    g1_primary           MAE_S, MAE_D, A per budget (two-sided 95% intervals, one-sided 95% upper bound,
                         per-resample A), N*, the C2 ceiling, descriptive baseline curves
    g1_within_host       within-host residual MAE of S and D, A_within, N*_within; host-mean MAE (descriptive)
    g1_cap_sensitivity   A(600) vs A(200) at B = 654 on resamples 0-2 and the pre-specified 0.02 eV rule
    g1_variance          seed and resample SDs of S and D; single-seed vs seed-ensemble A (descriptive)

    python scripts/analysis/g1_analysis.py
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from dftgnn.config import load_config
from dftgnn.io.results import write_result
from dftgnn.stats.g1 import (
    BOOT_SEED,
    HierDraws,
    contrast,
    n_star,
    point_metric,
    resample_stats,
    summarize,
)

ROOT = Path(__file__).resolve().parents[2]
DESCRIPTIVE = ("B0", "RF-Kumagai", "RF-electronic", "RF-structural", "host-mean oracle")
BOOT_TEXT = ("paired hierarchical bootstrap: in each replicate, R resamples drawn with replacement, then the "
             "test hosts of each drawn resample drawn with replacement (all sites of a drawn host), metric "
             "recomputed per slot and averaged over the R slots; one draw set shared by every model, budget "
             "and metric; numpy default_rng(seed), per slot integers() then multinomial(); percentiles by "
             "numpy quantile (linear)")


def plan_value(key: str) -> float:
    block = (ROOT / "docs" / "ANALYSIS_PLAN.md").read_text().split("```yaml prereg", 1)[1]
    return float(re.search(rf"^{re.escape(key)}:\s*(\S+)", block, re.MULTILINE).group(1))


def load_table(name: str, ref: dict) -> pd.DataFrame:
    path = ROOT / ref["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == ref["sha256"], f"{name}: hash differs from record"
    return pd.read_parquet(path)


def stats_by(df: pd.DataFrame, model: str, budgets, resamples) -> dict[int, list[np.ndarray]]:
    sub = df[df.model == model]
    return {B: [resample_stats(sub[(sub.B == B) & (sub.r == r)]) for r in resamples] for B in budgets}


def per_budget(c: dict, names=("S", "D", "A")) -> dict:
    return {str(B): {names[0]: v["a"], names[1]: v["b"], names[2]: v["diff"]} for B, v in c.items()}


def main() -> None:
    cfg = load_config()
    delta = float(cfg.stats.delta_eV)
    assert delta == plan_value("stats.delta_eV") == 0.05, "delta differs from the frozen plan"
    n_boot = int(cfg.analysis.bootstrap.draws)
    assert n_boot == plan_value("analysis.bootstrap.draws") == 2000
    q_up = float(cfg.analysis.n_star.upper_quantile)
    ci = float(cfg.analysis.display_ci)
    c2_ci = float(cfg.analysis.c2_ceiling_ci)
    assert ci == c2_ci == 0.95 and q_up == 0.95
    budgets = list(cfg.budgets.hosts)
    c2_budget = int(cfg.analysis.c2_ceiling_budget)
    R = int(cfg.split.n_outer_resamples)
    resamples = list(range(R))

    rec = json.loads((ROOT / "results" / "g1_eval_table.json").read_text())
    files = rec["payload"]["files"]
    table = load_table("eval_table", files["eval_table"])
    capt = load_table("eval_capsens", files["eval_capsens"])
    provenance = {"eval_table": files["eval_table"], "eval_capsens": files["eval_capsens"],
                  "eval_table_record_git_sha": rec["git_sha"]}

    S = stats_by(table, "S", budgets, resamples)
    D = stats_by(table, "D", budgets, resamples)
    n_hosts = [len(s) for s in S[budgets[0]]]
    for B in budgets:
        assert [len(s) for s in S[B]] == [len(d) for d in D[B]] == n_hosts, "test hosts differ across budgets"
    draws = HierDraws.make(n_hosts, n_boot, BOOT_SEED)
    boot = {"draws": n_boot, "seed": BOOT_SEED, "generator": "numpy.random.default_rng", "method": BOOT_TEXT,
            "n_resamples": R, "test_hosts_per_resample": n_hosts, "two_sided_ci": ci,
            "one_sided_upper_quantile": q_up}

    # ---------------------------------------------------------------- primary (C1, C2)
    prim = contrast(S, D, draws, "mae", ci=ci, upper_quantile=q_up)
    ns = n_star({B: prim[B]["diff"]["upper_one_sided"] for B in budgets}, delta)
    c2 = prim[c2_budget]["diff"]
    desc = {}
    for m in DESCRIPTIVE:
        st = stats_by(table, m, budgets, resamples)
        desc[m] = {str(B): summarize([point_metric(s, "mae") for s in st[B]], draws.replicates(st[B], "mae"),
                                     ci=ci, upper_quantile=q_up) for B in budgets}
    g1_primary = {
        "metric": "site-level test MAE (eV) of the seed-ensemble mean prediction",
        "advantage": "A = MAE_S - MAE_D (positive: DFT electronic descriptors help)",
        "models": {"S": "structure-only MEGNet", "D": "D-state (selected injection variant)"},
        "budgets": budgets, "delta_eV": delta, "bootstrap": boot,
        "per_budget": per_budget(prim, ("MAE_S", "MAE_D", "A")),
        "n_star": ns,
        "c2_ceiling": {"budget": c2_budget, "A": c2["mean"], "ci": c2["ci"], "ci_level": c2_ci,
                       "per_resample": c2["per_resample"]},
        "descriptive_curves": {"note": "extra curves; same bootstrap draws; no test", "mae": desc},
        "input": provenance,
    }

    # ---------------------------------------------------------------- secondary
    wh = contrast(S, D, draws, "within_host_mae", ci=ci, upper_quantile=q_up)
    ns_w = n_star({B: wh[B]["diff"]["upper_one_sided"] for B in budgets}, delta)
    hm = contrast(S, D, draws, "host_mean_mae", ci=ci, upper_quantile=q_up)
    n_ge2 = [int((s[:, 8] > 0).sum()) for s in S[budgets[0]]]
    g1_within = {
        "within_host_residual_mae": {
            "definition": "per test host with >= 2 sites: (pred - host mean pred) - (target - host mean target); "
                          "MAE over those sites; single-site hosts excluded from this metric only",
            "test_hosts_with_ge2_sites_per_resample": n_ge2,
            "per_budget": per_budget(wh, ("S", "D", "A_within")), "n_star_within": ns_w},
        "host_mean_mae": {"definition": "mean over test hosts of |mean target - mean prediction|, each host once",
                          "descriptive": True, "per_budget": per_budget(hm, ("S", "D", "S_minus_D"))},
        "delta_eV": delta, "bootstrap": boot, "input": provenance,
    }

    # ---------------------------------------------------------------- epoch-cap sensitivity
    cap_r = sorted(capt.r.unique())
    assert cap_r == list(cfg.sensitivity.epoch_cap.resamples)
    cb = int(cfg.sensitivity.epoch_cap.budget)
    for m in ("S", "D"):   # the 200-cap comparators are the sweep ensembles
        a = capt[(capt.model == m) & (capt.cap == 200)].set_index(["r", "site_id"]).y_pred.sort_index()
        b = table[(table.model == m) & (table.B == cb) & table.r.isin(cap_r)].set_index(["r", "site_id"]).y_pred
        assert np.array_equal(a.to_numpy(), b.loc[a.index].to_numpy()), "cap-200 comparator differs from sweep"
    cst = {(m, c): [resample_stats(capt[(capt.model == m) & (capt.cap == c) & (capt.r == r)]) for r in cap_r]
           for m in ("S", "D") for c in (200, 600)}
    draws3 = HierDraws.make([len(s) for s in cst[("S", 200)]], n_boot, BOOT_SEED)
    rep = {k: draws3.replicates(v, "mae") for k, v in cst.items()}
    pt = {k: np.array([point_metric(s, "mae") for s in v]) for k, v in cst.items()}
    a200, a600 = pt[("S", 200)] - pt[("D", 200)], pt[("S", 600)] - pt[("D", 600)]
    r200, r600 = rep[("S", 200)] - rep[("D", 200)], rep[("S", 600)] - rep[("D", 600)]
    thr = float(cfg.sensitivity.epoch_cap.cap_insensitive_if_abs_delta_A_le_eV)
    dA = float(a600.mean() - a200.mean())
    g1_cap = {
        "budget": cb, "resamples": cap_r, "seeds": [0, 1, 2], "caps": [200, 600],
        "A_200": summarize(a200, r200, ci=ci, upper_quantile=q_up),
        "A_600": summarize(a600, r600, ci=ci, upper_quantile=q_up),
        "A_600_minus_A_200": summarize(a600 - a200, r600 - r200, ci=ci, upper_quantile=q_up),
        "mae": {f"{m}_cap{c}": summarize(pt[(m, c)], rep[(m, c)], ci=ci, upper_quantile=q_up)
                for m in ("S", "D") for c in (200, 600)},
        "rule": {"threshold_eV": thr, "statistic": "|A(600) - A(200)| (point estimate, mean over resamples 0-2)",
                 "abs_difference_eV": abs(dA), "cap_insensitive": bool(abs(dA) <= thr)},
        "caveat": "the resample level of this bootstrap draws from only 3 resamples",
        "bootstrap": {**boot, "n_resamples": len(cap_r),
                      "test_hosts_per_resample": [len(s) for s in cst[("S", 200)]]},
        "input": provenance,
    }

    # ---------------------------------------------------------------- variance tables (descriptive)
    sw = table[table.model.isin(["S", "D"])]
    single = {}
    for s in (0, 1, 2):
        e = (sw[f"y_pred_seed{s}"] - sw.y_true).abs()
        single[s] = e.groupby([sw.model, sw.B, sw.r]).mean()
    ss = pd.DataFrame(single)                                   # index (model, B, r), columns seeds
    ens = (sw.y_pred - sw.y_true).abs().groupby([sw.model, sw.B, sw.r]).mean()
    var = {}
    for m in ("S", "D"):
        var[m] = {}
        for B in budgets:
            x = ss.loc[(m, B)]
            var[m][str(B)] = {
                "mean_single_seed_mae": float(x.to_numpy().mean()),
                "seed_sd_mean_over_resamples": float(x.std(axis=1, ddof=1).mean()),
                "seed_sd_per_resample": [float(v) for v in x.std(axis=1, ddof=1)],
                "ensemble_mae_mean": float(ens.loc[(m, B)].mean()),
                "resample_sd_of_ensemble_mae": float(ens.loc[(m, B)].std(ddof=1)),
                "resample_sd_of_single_seed_mae": [float(v) for v in x.std(axis=0, ddof=1)]}
    a_var = {}
    for B in budgets:
        a_ss = ss.loc[("S", B)] - ss.loc[("D", B)]               # rows r, columns seed
        a_en = ens.loc[("S", B)] - ens.loc[("D", B)]
        a_var[str(B)] = {
            "ensemble_A_mean": float(a_en.mean()), "ensemble_A_sd_over_resamples": float(a_en.std(ddof=1)),
            "single_seed_A_mean": float(a_ss.to_numpy().mean()),
            "single_seed_A_sd_over_all_30": float(a_ss.to_numpy().std(ddof=1)),
            "single_seed_A_within_resample_sd_mean": float(a_ss.std(axis=1, ddof=1).mean()),
            "single_seed_A_per_resample_seed": a_ss.to_numpy().tolist()}
    g1_variance = {"definitions": "docs/deviations.md 2026-10-08 (§11 variance tables); sample SDs, ddof = 1",
                   "models": var, "advantage": a_var, "descriptive": True, "input": provenance}

    for name, payload in (("g1_primary", g1_primary), ("g1_within_host", g1_within),
                          ("g1_cap_sensitivity", g1_cap), ("g1_variance", g1_variance)):
        print(write_result(name, payload, config=cfg))


if __name__ == "__main__":
    main()

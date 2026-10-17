"""Render docs/w2_diagnostics.md from the W2 records in results/derived_w2/ (no computation).

    python analysis/w2/make_docs.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "results" / "derived_w2"
OUT = ROOT / "docs" / "w2_diagnostics.md"


def load(name: str) -> dict:
    r = json.loads((REC / f"{name}.json").read_text())
    return {**r["payload"], "_git": r["git_sha"][:7]}


def f3(x: float | None, sign: bool = True) -> str:
    return "n/a" if x is None else (f"{x:+.3f}" if sign else f"{x:.3f}")


def ci(v: list[float]) -> str:
    return f"[{v[0]:+.3f}, {v[1]:+.3f}]"


def yn(b: bool) -> str:
    return "yes" if b else "no"


def section_a(a: dict) -> list[str]:
    out = ["## (a) Descriptor network at 25 and 50 training hosts", "",
           (f"Record: `results/derived_w2/w2_descriptor_small_budget.json` (git {a['_git']}). Single-run MAE of every "
           "resample x seed run of D (eV). Outlying run: MAE above the Tukey fence Q3 + 1.5 IQR of the 30 runs of the "
           "budget. Extreme site: absolute error above 10 eV (the DFT targets lie between 1.6 and 8.3 eV). z: the "
           "largest |z| over the 22 descriptors of D, standardised with the training sites of that run "
           "(`dftgnn.train.resolve_hosts` on the stored run spec, population SD, as in `Standardiser.fit`)."), ""]
    for B, v in a["budgets"].items():
        out += [f"### {B} training hosts", "",
                ("| Run | MAE | Outlying | Extreme sites | Share of abs. error from them | MAE without them | "
                "Median z, extreme sites | Median z, other sites | Descriptor with largest z | Best validation MAE | "
                "Epochs |"), "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in v["runs"]:
            zd = ", ".join(f"{k} ({n})" for k, n in r["max_z_descriptors_extreme_sites"].items()) or "-"
            z = r["median_max_abs_z_extreme_sites"]
            mz = f"{z:.0f}" if z is not None and not math.isnan(z) else "-"  # no extreme site
            out.append(f"| r{r['r']} s{r['seed']} | {r['mae']:.3f} | {yn(r['outlying'])} | {r['n_extreme_sites']} | "
                       f"{r['share_of_abs_error_from_extreme_sites']:.2f} | {r['mae_without_extreme_sites']:.3f} | {mz} | "
                       f"{r['median_max_abs_z_other_sites']:.1f} | {zd} | {r['best_val_mae_eV']:.3f} | {r['epochs_run']} |")
        m, s_ = v["D_run_mae"], v["S_run_mae_reference"]
        aa, ac = v["A_all_runs"], v["A_outlying_runs_removed"]
        out += ["", f"- Tukey fence {v['tukey_fence_eV']:.3f} eV; outlying runs: {', '.join(v['outlying_runs'])}.",
                (f"- D run MAE: median {m['median']:.3f}, 10% trimmed mean {m['trimmed_mean_10pc']:.3f}, mean "
                f"{m['mean']:.3f}, max {m['max']:.3f} eV (S for reference: median {s_['median']:.3f}, trimmed mean "
                f"{s_['trimmed_mean_10pc']:.3f})."),
                f"- Non-finite predictions in {v['n_runs_with_nonfinite']} runs; non-finite training or validation "
                f"loss in {v['n_runs_with_nonfinite_history']} runs. {v['n_runs_with_extreme_sites']} of 30 runs carry "
                f"{v['n_extreme_sites_total']} extreme sites in all, {v['share_of_abs_error_from_extreme_sites']:.2f} of "
                "the absolute error of the budget; hosts: " + ", ".join(v["extreme_formulae_all_runs"]) + ".",
                (f"- A, all runs: {f3(aa['A'])} {ci(aa['ci95'])}, upper {f3(aa['upper_one_sided_95'])} (MAE of D "
                f"{aa['MAE_D']['mean']:.3f}); outlying runs removed: {f3(ac['A'])} {ci(ac['ci95'])}, upper "
                f"{f3(ac['upper_one_sided_95'])} (MAE of D {ac['MAE_D']['mean']:.3f}; resamples kept: "
                f"{len(ac['resamples_kept'])}, D runs kept: {ac['n_D_runs_kept']})."), ""]
    return out


def section_b(b: dict) -> list[str]:
    out = ["## (b) Training-limit counts", "",
           (f"Record: `results/derived_w2/w2_training_limit.json` (git {b['_git']}). A run is capped when it stopped "
           f"at the epoch limit ({b['max_epochs'][0]} epochs) rather than by early stopping. P is P1 then D and has "
           "no epochs of its own; a P run counts as capped when its P1 or D component is. Sweep design, 10 "
           "resamples x 3 seeds."), "", "| Training hosts | S | D | P1 | P (P1 or D component) |", "|---|---|---|---|---|"]
    for B, v in b["counts_sweep_10x3"].items():
        if v["S"]["n_runs"] == 0:
            continue
        out.append(f"| {B} | {v['S']['n_capped']} / {v['S']['n_runs']} | {v['D']['n_capped']} / {v['D']['n_runs']} | "
                   f"{v['P1']['n_capped']} / {v['P1']['n_runs']} | {v['P']['n_capped_component']} / {v['P']['n_runs']} |")
    out += ["", "Paired cells at 654 hosts (same resample and seed; single-run MAE, eV; A_cell = MAE_S - MAE_D):", "",
            "| Design | Cell type | Cells | Mean MAE S | Mean MAE D | Mean A_cell |", "|---|---|---|---|---|---|"]
    names = {"S_capped_D_uncapped": "S capped, D not", "S_uncapped_D_capped": "D capped, S not",
             "both_capped": "both capped", "neither_capped": "neither capped", "all": "all"}
    for des, lab in (("precision_30x5", "30 x 5"), ("sweep_10x3", "10 x 3")):
        for k, g in b["at_654"][des]["groups"].items():
            out.append(f"| {lab} | {names[k]} | {g['n_cells']} | {f3(g['mean_mae_S'], False)} | "
                       f"{f3(g['mean_mae_D'], False)} | {f3(g['mean_A_cell'])} |")
    p, s_ = b["at_654"]["precision_30x5"], b["at_654"]["sweep_10x3"]
    e = b["at_654"]["ensemble_A_point_30x5"]
    out += ["", (f"- 30 x 5: mean A_cell {f3(p['mean_A_cell_all'])} with all cells, {f3(p['mean_A_cell_without_capped_cells'])} "
                f"without the cells that hold a capped run: the capped cells {p['sign_of_effect']} by "
                f"{abs(p['effect_of_capped_cells_on_mean_A_cell']):.4f} eV. Capped S runs have a lower MAE than "
                f"uncapped ones by {abs(p['capped_minus_uncapped_mae_S']):.3f} eV."),
            (f"- 10 x 3: {f3(s_['mean_A_cell_all'])} against {f3(s_['mean_A_cell_without_capped_cells'])} "
            f"({s_['sign_of_effect']}, {abs(s_['effect_of_capped_cells_on_mean_A_cell']):.4f} eV)."),
            (f"- Seed-ensemble A at 654 (30 x 5, point only): {f3(e['all_runs'])} with all runs, "
            f"{f3(e['capped_runs_removed'])} with the {e['n_capped_runs_removed']} capped runs removed."), ""]
    return out


def section_c(c: dict) -> list[str]:
    out = ["## (c) Crossover with the forest", "",
           (f"Record: `results/derived_w2/w2_forest_crossover.json` (git {c['_git']}). Difference of the seed-ensemble "
           "MAE and RF-Kumagai (eV), paired G1 hierarchical bootstrap (the C1 draws). Below = the two-sided 95% "
           "interval lies below 0."), "", "| Training hosts | S - RF | 95% | below | D - RF | 95% | below |",
           "|---|---|---|---|---|---|---|"]
    for B in ("25", "50", "100", "200", "400", "654"):
        s_, d = c["S"][B], c["D"][B]
        out.append(f"| {B} | {f3(s_['difference'])} | {ci(s_['ci95'])} | {yn(s_['below_with_95_interval'])} | "
                   f"{f3(d['difference'])} | {ci(d['ci95'])} | {yn(d['below_with_95_interval'])} |")
    out += ["", (f"- S: point below the forest from {c['S']['smallest_budget_point_below']} hosts; below with a 95% "
                f"interval first at {c['S']['smallest_budget_below_with_95_interval']} hosts."),
            (f"- D: point below from {c['D']['smallest_budget_point_below']} hosts; below with a 95% interval from "
            f"{c['D']['smallest_budget_below_with_95_interval']} hosts on."), ""]
    return out


def section_d(d: dict) -> list[str]:
    bb = d["budgets"]
    out = ["## (d) The bound at 200, 400 and 654 training hosts", "",
           (f"Record: `results/derived_w2/w2_bound_spread.json` (git {d['_git']}). A with its two-sided 95% interval "
           "and one-sided upper bound; the spread is that of the per-resample A (seed ensemble) and of single runs."), "",
           ("| Training hosts | Design | A | 95% | upper | bootstrap SD | SD over resamples | min, max over resamples | "
           "resamples above 0.05 | resamples below 0 | single-run SD |"), "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in ("200", "400", "654", "400_30x5", "654_30x5"):
        v = bb[k]
        out.append(f"| {k.split('_')[0]} | {v['design']} | {f3(v['A'])} | {ci(v['ci95'])} | {f3(v['upper_one_sided_95'])} | "
                   f"{f3(v.get('boot_sd'), False)} | {v['sd_over_resamples']:.3f} | {f3(v['min_resample_A'])}, "
                   f"{f3(v['max_resample_A'])} | {v['n_resamples_A_above_delta']} | {v['n_resamples_A_below_0']} | "
                   f"{f3(v['single_run_A']['sd_over_30_runs'], False) if 'single_run_A' in v else 'n/a'} |")
    out += [""]
    return out


def section_e(e: dict) -> list[str]:
    s_ = e["summary"]
    out = ["## (e) Screening, final network", "",
           (f"Record: `results/derived_w2/w2_screening_sites.json` (git {e['_git']}). S at {s_['budget']} training hosts; "
           "prediction = seed-ensemble mean averaged over the resamples that hold the host out (N). Cations: the "
           "cation elements of the oxide and the number bonded to the removed oxygen (first shell)."), "",
           "| Oxide | Site | Cations (first shell) | DFT (eV) | Prediction (eV) | Error (eV) | N |", "|---|---|---|---|---|---|---|"]
    for r in e["sites"]:
        out.append(f"| {r['oxide']} | {r['site']} | {', '.join(r['cation_elements'])} ({r['first_shell_cations']}) | "
                   f"{r['dft_eV']:.3f} | {r['prediction_eV']:.3f} | {r['error_eV']:+.3f} | {r['n_resamples']} |")
    out += ["", (f"Pooled MAE {s_['mae_eV']:.3f} eV, 95% interval [{s_['mae_ci95'][0]:.3f}, {s_['mae_ci95'][1]:.3f}] "
                f"(host-cluster bootstrap, {s_['n_hosts']} hosts); bias {s_['bias_eV']:+.3f} eV; {s_['n_over_prediction']} "
                f"over- and {s_['n_under_prediction']} under-predicted; largest error {s_['max_abs_err_eV']:.3f} eV "
                f"({s_['worst_site']})."), ""]
    return out


def main() -> None:
    a, b, c, d, e = (load(n) for n in ("w2_descriptor_small_budget", "w2_training_limit", "w2_forest_crossover",
                                       "w2_bound_spread", "w2_screening_sites"))
    rep = [x["reproduction_summary"] for x in (a, b, c, d, e)]
    intro = (Path(__file__).with_name("diagnostics_text.md")).read_text()
    lines = [intro.rstrip(), ""]
    for sec, rec in ((section_a, a), (section_b, b), (section_c, c), (section_d, d), (section_e, e)):
        lines += sec(rec)
    r = rep[0]
    lines += ["## Reproduction", "",
              (f"{r['n_comparisons']} comparisons, {r['n_values_compared']} values shared with earlier records; maximum "
              f"absolute difference {r['max_abs_difference']:.1e}; all below 1e-9: {yn(r['all_reproduced_below_1e-9'])}."),
              "", "| Comparison | Reference | Values | Max abs difference |", "|---|---|---|---|"]
    for k, v in a["reproduction"].items():
        lines.append(f"| {k} | {v['reference']} | {v['n_values_compared']} | {v['max_abs_difference']:.1e} |")
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

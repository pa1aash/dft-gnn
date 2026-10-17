"""C1: render the final-network table and the default-initialisation ablation table from the C1 records.

Reads ``results/derived_c1/final_network_summary.json``, ``default_init_ablation.json`` and ``loco_family.json``
(nothing is recomputed) and writes ``docs/c1_final_network_table.md`` and ``docs/c1_ablation_table.md``.

    python analysis/c1/make_docs.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "results" / "derived_c1"
ORDER = ("B25", "B50", "B100", "B200", "B400", "B400_30x5", "B654", "B654_30x5", "CV_k10", "CV_k20", "LOCO")
LABEL = {"B400_30x5": "400 (30 x 5)", "B654_30x5": "654 (30 x 5)", "CV_k10": "CV K = 10", "CV_k20": "CV K = 20",
         "LOCO": "LOCO (5 folds)"}


def load(name: str) -> dict:
    return json.loads((REC / f"{name}.json").read_text())


def mae(m: dict | None) -> str:
    if not m:
        return "n/a"
    return f"{m['mean']:.3f} [{m['ci95'][0]:.3f}, {m['ci95'][1]:.3f}]"


def yn(b: bool) -> str:
    return "yes" if b else "no"


def a_cols(a: dict) -> list[str]:
    return [f"{a['A']:+.3f}", f"[{a['ci95'][0]:+.3f}, {a['ci95'][1]:+.3f}]", f"{a['upper_one_sided_95']:+.3f}",
            yn(a["two_sided_within_pm_delta"]), yn(a["upper_below_delta"])]


def table(rows: dict, with_baselines: bool) -> list[str]:
    head = ["Training hosts", "Design", "MAE S", "MAE D"]
    if with_baselines:
        head += ["MAE P", "MAE RF", "MAE B0"]
    head += ["A", "A, two-sided 95%", "A, one-sided 95% upper", "two-sided inside +-0.05", "upper < 0.05", "Source"]
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for i, key in enumerate(k for k in ORDER if k in rows):
        r = rows[key]
        x = LABEL.get(key, key[1:])
        hosts = f"{r['x_training_hosts']:.1f}" if key.startswith(("CV", "LOCO")) else x
        name = x if key.startswith(("CV", "LOCO")) else ("sweep 10 x 3" if "_" not in key else "precision 30 x 5")
        cols = [hosts, name, mae(r.get("MAE_S")), mae(r.get("MAE_D"))]
        if with_baselines:
            cols += [mae(r.get("MAE_P")), mae(r.get("MAE_RF")), mae(r.get("MAE_B0"))]
        cols += a_cols(r["A"]) + [f"[{i + 1}]"]
        out.append("| " + " | ".join(cols) + " |")
    out.append("")
    for i, key in enumerate(k for k in ORDER if k in rows):
        r = rows[key]
        note = f" Not available: {r['missing']}." if r.get("missing") else ""
        out.append(f"[{i + 1}] {'; '.join(r['source_records'])}.{note}")
    return out


def final_doc() -> str:
    rec = load("final_network_summary")
    p = rec["payload"]
    rows = p["table"]["rows"]
    rep = p["reproduction_summary"]
    lines = [
        "# C1: final-network evidence table",
        "",
        "Final network: the He-initialised, validation-tuned network (v2 in the repository; `configs/tuned_v2.yaml`).",
        f"Record: `results/derived_c1/final_network_summary.json` (git {rec['git_sha'][:7]}), written by",
        "`analysis/c1/final_network.py`; this file is rendered from it by `analysis/c1/make_docs.py`.",
        "",
        "MAE in eV, point with two-sided 95% bootstrap interval. A = MAE_S - MAE_D (positive: the DFT electronic",
        "descriptors lower the error). delta = 0.05 eV. \"two-sided inside +-0.05\": the two-sided 95% interval lies",
        "strictly inside (-0.05, +0.05) eV. \"upper < 0.05\": the one-sided 95% upper bound is below 0.05 eV.",
        "RF is RF-Kumagai; B0 is the two-parameter physics floor. Estimators are the existing ones, unchanged:",
        "G1 hierarchical bootstrap (sweep, 2000 replicates, seed 20261008), the A1 precision analysis (30 x 5),",
        "the A1 paired host-cluster bootstrap (CV, 818 hosts), the M1 host bootstrap of pooled folds (LOCO).",
        "",
        *table(rows, True),
        "",
        "## Two-sided intervals at the sizes that carry the claim",
        "",
        ("| Point | Training hosts | A | two-sided 95% | upper one-sided 95% | inside +-0.05 | upper < 0.05 | "
         "interval excludes 0 |"),
        "|---|---|---|---|---|---|---|---|",
    ]
    for key, hosts in (("B654", "654"), ("B654_30x5", "654"), ("CV_k10", f"{rows['CV_k10']['x_training_hosts']:.1f}"),
                       ("CV_k20", f"{rows['CV_k20']['x_training_hosts']:.1f}"), ("LOCO", "654.4 (mean)")):
        a = rows[key]["A"]
        lines.append(f"| {LABEL.get(key, '654 (sweep 10 x 3)')} | {hosts} | {a['A']:+.4f} | "
                     f"[{a['ci95'][0]:+.4f}, {a['ci95'][1]:+.4f}] | {a['upper_one_sided_95']:+.4f} | "
                     f"{yn(a['two_sided_within_pm_delta'])} | {yn(a['upper_below_delta'])} | "
                     f"{yn(a['ci95_excludes_zero'])} |")
    lines += [
        "",
        "At 654 (sweep and pooled 30 x 5), about 736 and about 777 training hosts, the two-sided 95% interval of A",
        "lies inside +-0.05 eV, so \"within 0.05 eV\" is supported at those sizes, not only \"upper bound below",
        "0.05 eV\". At 30 x 5 and in both CV designs the interval also excludes zero: D is better than S by a",
        "small, nonzero amount (0.02 to 0.03 eV) at those sizes. Under leave-one-family-out the interval is not",
        "inside +-0.05 eV and the upper bound exceeds 0.05 eV (see `docs/c1_coverage.md`, section LOCO).",
        "",
        "## Within-host spread of the predictions (descriptive)",
        "",
        "Mean over (resample, test host with >= 2 sites) of the SD of the seed-ensemble prediction across the",
        "host's sites, divided by the same SD of the DFT targets (definition of `results/g1_diagnostics.json`).",
        "",
        "| Model | " + " | ".join(str(b) for b in (25, 50, 100, 200, 400, 654)) + " |",
        "|---|" + "---|" * 6,
    ]
    sp = p["table"]["within_host_prediction_spread"]
    for m in ("S", "D", "P"):
        lines.append(f"| {m} | " + " | ".join(f"{sp[m][str(b)]['ratio_ensemble_to_target']:.3f}"
                                             for b in (25, 50, 100, 200, 400, 654)) + " |")
    lines += [
        "",
        "## Reproduction",
        "",
        (f"{rep['n_comparisons']} comparisons, {rep['n_values_compared']} values shared with existing records; "
         f"maximum absolute difference {rep['max_abs_difference']:.1e} eV; all below 1e-9: "
         f"{yn(rep['all_reproduced_below_1e-9'])}. Per comparison:"),
        "",
        "| Comparison | Reference | Values | Max abs difference |",
        "|---|---|---|---|",
    ]
    for g, d in p["reproduction"].items():
        for k, v in d.items():
            lines.append(f"| {g}.{k} | {v['reference']} | {v['n_values_compared']} | {v['max_abs_difference']:.1e} |")
    return "\n".join(lines) + "\n"


def ablation_doc() -> str:
    rec = load("default_init_ablation")
    p = rec["payload"]
    rows = p["table"]["rows"]
    sr = p["site_resolution"]
    bs = (25, 50, 100, 200, 400, 654)
    lines = [
        "# C1: default-initialisation ablation (appendix table)",
        "",
        "Ablation network: default (PyTorch) initialisation, tuned for v1 (v1 in the repository; the originally",
        f"registered backbone). Record: `results/derived_c1/default_init_ablation.json` (git {rec['git_sha'][:7]}),",
        "rendered by `analysis/c1/make_docs.py`. Same estimators, seeds and draws as the final-network table",
        "(`docs/c1_final_network_table.md`); MAE in eV with two-sided 95% intervals; A = MAE_S - MAE_D.",
        "",
        *table(rows, False),
        "",
        "## Site resolution of S (S10 and S10b diagnostics)",
        "",
        "Ratio of the within-host SD of the predictions to the within-host SD of the DFT targets (mean over",
        "resamples and test hosts with >= 2 sites; seed-ensemble predictions). The v1 values reproduce",
        "`results/g1_diagnostics.json`; the v2 row uses the same code. A ratio near 0 means S predicts one value",
        "per host.",
        "",
        "| Network | Model | " + " | ".join(str(b) for b in bs) + " |",
        "|---|---|" + "---|" * 6,
    ]
    for m in ("S", "D"):
        for bb, nm in (("v1", "default init (ablation)"), ("v2", "final")):
            lines.append(f"| {nm} | {m} | " + " | ".join(f"{sr[m][bb][str(b)]['ratio_ensemble_to_target']:.3f}"
                                                         for b in bs) + " |")
    s10b = sr["s10b_forensic_v1_S"]["values"]
    tgt = sr["S"]["v1"]["25"]["target_eV"]
    lines += [
        "",
        f"Mean within-host target SD: {tgt:.3f} eV (identical for every budget and network).",
        "",
        "S10b checkpoint forensic (v1 S, resample 0, seed 0, 30 hosts; median SD across labelled sites over the",
        "median target SD, `results/s_site_resolution_forensic.json`): " +
        ", ".join(f"B = {b}: {s10b[str(b)]['ratio']:.4f}" for b in bs) + ".",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    (ROOT / "docs" / "c1_final_network_table.md").write_text(final_doc())
    (ROOT / "docs" / "c1_ablation_table.md").write_text(ablation_doc())


if __name__ == "__main__":
    main()

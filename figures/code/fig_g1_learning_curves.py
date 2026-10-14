"""G1 learning-curve figure (M3b): ANALYSIS_PLAN section 14, both backbones, through the paper style.

Same record as scripts/analysis/fig_g1.py (kept unchanged) for the originally registered backbone (v1):
results/g1_primary.json (G1 estimator; ``per_budget`` and ``descriptive_curves``). The primary backbone (v2)
comes from results/c1c2_v2.json (same estimand and design; point values identical to our recomputation,
docs/ingest_report.md row 8). Optional EXTENSION records (figures/code/inputs_paper.py) are drawn when present.
Written to figures/si/ by default: an unnumbered file kept beside the SI, not cited in the text (Figure 2 and
Figure 3 carry the same series; docs/figure_numbering.md).

    (a) site-level test MAE of B0, RF-Kumagai, S and D against training hosts, with the published values
    (b) A = MAE_S - MAE_D with the margin delta and zero

    python figures/code/fig_g1_learning_curves.py [--results-root DIR] [--out-dir DIR]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inputs_paper as ip
import style_paper as sp

STEM = "fig_g1_learning_curves"
# Published values (docs/baselines.md, "published reference" rows); drawn as reference lines only.
KUMAGAI_RF_EV = 0.34      # Kumagai et al. 2021, q = 0, 700 training oxides
KIYOHARA_CGCNN_EV = 0.29  # Kiyohara et al. 2025, q = 0, their split
REF_KUMAGAI = ("Kumagai et al. RF (published)", "published")
REF_KIYOHARA = ("Kiyohara et al. CGCNN (published)", "published-alt")


def _g1(p: dict, get):
    budgets = [int(b) for b in p["budgets"]]
    rows = [get(str(b)) for b in budgets]
    return budgets, [r["mean"] for r in rows], [r["ci"][0] for r in rows], [r["ci"][1] for r in rows]


def main() -> Path:
    a = ip.cli(__doc__)
    out_dir = a.out_dir if a.out_dir != ip.ROOT / "figures" / "main" else ip.ROOT / "figures" / "si"
    g1 = ip.require("g1_primary", a.results_root)
    v2 = ip.require("c1c2_v2", a.results_root)
    ext = ip.extensions(a.results_root)
    per, desc = g1["per_budget"], g1["descriptive_curves"]["mae"]
    x_max = ip.x_upper(ext)

    fig, (ax1, ax2) = sp.figure("single", height_mm=94.0, ncols=2)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.94, bottom=0.395, wspace=0.30)
    tops = []
    for key in ("B0", "RF-Kumagai"):
        x, m, lo, hi = _g1(g1, lambda b, k=key: desc[k][b])
        sp.baseline_curve(ax1, x, m, lo, hi, key)
        tops += m
    for model, g1key in (("S", "MAE_S"), ("D", "MAE_D")):
        x, m, lo, hi = ip.mae_series(v2, model)
        sp.band_curve(ax1, x, m, lo, hi, model, "v2")
        tops += m
        x, m, lo, hi = _g1(g1, lambda b, k=g1key: per[b][k])
        sp.band_curve(ax1, x, m, lo, hi, model, "v1")
        tops += m
        for (kind, arm), p in ext.items():
            sp.ext_points(ax1, *ip.mae_series(p, model), model, kind, arm)
    sp.reference_line(ax1, KUMAGAI_RF_EV, REF_KUMAGAI[0], REF_KUMAGAI[1], sp.COLORS["RF-Kumagai"])
    sp.reference_line(ax1, KIYOHARA_CGCNN_EV, REF_KIYOHARA[0], REF_KIYOHARA[1])
    sp.budget_axis(ax1, x_max=x_max)
    ax1.set_ylabel("Site test MAE (eV)")
    ax1.set_ylim(0.0, 1.06 * max(tops))

    sp.reference_line(ax2, g1["delta_eV"], "", "delta")
    sp.reference_line(ax2, 0.0, "", "zero")
    x, m, lo, hi, _ = ip.a_series(v2)
    sp.band_curve(ax2, x, m, lo, hi, "A", "v2")
    spans = list(m)
    x, m, lo, hi = _g1(g1, lambda b: per[b]["A"])
    sp.band_curve(ax2, x, m, lo, hi, "A", "v1")
    spans += m + lo + hi
    for (kind, arm), p in ext.items():
        x, m, lo, hi, _ = ip.a_series(p)
        sp.ext_points(ax2, x, m, lo, hi, "A", kind, arm)
        spans += m
    sp.budget_axis(ax2, x_max=x_max)
    lo_, hi_ = min(spans), max(spans + [g1["delta_eV"]])
    ax2.set_ylim(lo_ - 0.08 * (hi_ - lo_), hi_ + 0.08 * (hi_ - lo_))
    ax2.set_ylabel(r"$A$ (eV)")

    handles = [sp.model_handle("S"), sp.model_handle("D"), sp.baseline_handle("B0"),
               sp.baseline_handle("RF-Kumagai"),
               *(sp.backbone_handle(v) for v in sp.BACKBONES),
               sp.reference_handle(REF_KUMAGAI[0], REF_KUMAGAI[1], sp.COLORS["RF-Kumagai"]),
               sp.reference_handle(*REF_KIYOHARA),
               sp.reference_handle(r"margin $\delta$", "delta"), sp.reference_handle("zero", "zero"),
               *sp.series_handles(k for k, _ in ext)]
    sp.legend_handles(fig, handles, ncol=2)
    sp.panel_letters(fig, (ax1, ax2))
    pdf = sp.save(fig, Path(out_dir) / STEM, png=True)
    ip.write_caption(out_dir, STEM, caption(ext))
    return pdf


def caption(ext: dict) -> str:
    return f"""
**Figure G1. Learning curves of the neutral oxygen-vacancy formation energy.** (**a**) Site-level test mean
absolute error (MAE, eV) against the number of training hosts (logarithmic axis; budgets `payload.budgets`)
for the two-descriptor physics floor B0, the random forest on the Kumagai descriptors (RF-Kumagai), the
structure-only MEGNet S and the descriptor model D (S given the host-electronic and site-electronic DFT
descriptors of the pristine host, D-state injection). The thin horizontal lines are published values, not
results of this work: the random-forest MAE of Kumagai et al. (`paper/refs.bib` key `Kumagai2021insights`) and the
structure-only CGCNN MAE of Kiyohara et al. (`paper/refs.bib` key `Kiyohara2025machinelearning`); both values and their
conditions are in `docs/baselines.md` (published-reference rows). (**b**) The advantage of the DFT descriptors,
A = MAE_S − MAE_D, with the margin δ (dashed, `payload.delta_eV`) and zero (dotted). Solid lines, filled
circles and filled bands: primary backbone (v2), adopted after diagnostics of the originally registered
backbone, from `results/c1c2_v2.json`, keys `payload.mae.<B>.<S|D-state>.mae` (`mean`, `ci`) and
`payload.A_mae.<B>` (`A`, `ci95`). Dashed lines, open circles and hatched bands: originally registered
backbone (v1), from `results/g1_primary.json`, keys `payload.per_budget.<B>.<MAE_S|MAE_D|A>` (`mean`, `ci`);
N* in `payload.n_star`. B0 and RF-Kumagai do not depend on the backbone (squares on thinner lines):
`results/g1_primary.json`, key `payload.descriptive_curves.mae.<B0|RF-Kumagai>.<B>`. Every point is the mean
over the registered outer resamples (`payload.bootstrap.n_resamples`, each holding out
`payload.bootstrap.test_hosts_per_resample` test hosts, grouped by formula, with nested training budgets);
S and D predictions are the mean over the training seeds per test site. Bands are two-sided intervals at
the level `payload.bootstrap.two_sided_ci` of `results/g1_primary.json` from the paired hierarchical bootstrap (`payload.bootstrap`: resamples, then test hosts within each resample,
all sites of a drawn host kept). The v2 intervals come from the bootstrap of `results/c1c2_v2.json`; our
recomputation with the G1 generator (`results/ingest_m1_recompute.json`, `payload.v2_arm`) gives the same
point values. {ip.drawn_note(ext)} Script: `figures/code/fig_g1_learning_curves.py`.
"""


if __name__ == "__main__":
    print(main())

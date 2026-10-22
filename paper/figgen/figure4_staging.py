"""Figure 4: staging with the descriptor predictor P1 tuned and trained to convergence. MAE of S, D and P, and the
contrasts P - S and P - D, at the same training sizes. Replaces figures/code/figure4_staging.py as the source of
figures/main/figure4_staging.pdf; layout, colours and legend are that script's (imported, not edited).

Input (read-only): results/derived_staging/staging_fair.json (``budgets.<B>.mae.<S|D|P>``,
``budgets.<B>.<P_minus_S|P_minus_D>``, ``delta_eV``).

    (a) seed-ensemble test MAE of S, D and P against training hosts, two-sided 95% bands
    (b) P - S (staging against learning from structure directly) and P - D (cost of predicting rather than knowing
        the descriptors), two-sided 95% bands, the tolerance +-delta and zero

Axes span the point estimates and the P - S intervals; wider bands (D and P - D at 25 and 50 training hosts) are
clipped and their full intervals are in the record.

    python paper/figgen/figure4_staging.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "figures" / "code"))
import figure4_staging as f4
import network_style as ns
import style_paper as sp

SUB, STEM = "main", "figure4_staging"
RECORD = ROOT / "results" / "derived_staging" / "staging_fair.json"
CONTRASTS = ("P_minus_S", "P_minus_D")
CONTRAST_COLORS = {"P_minus_S": f4.CONTRAST_COLORS["P_minus_S"], "P_minus_D": f4.CONTRAST_COLORS["D_minus_P"]}
CONTRAST_LABELS = {"P_minus_S": r"P $-$ S", "P_minus_D": r"P $-$ D"}


def main() -> Path:
    rec = ns.payload(RECORD)
    delta = rec["delta_eV"]

    fig, (ax_a, ax_b) = sp.figure("single", height_mm=78.0, ncols=2)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.93, bottom=0.30, wspace=0.32)

    span_a = []
    for m in f4.MODELS:
        x, mean, lo, hi = f4.series(rec, lambda b, m=m: b["mae"][m])
        ns.curve(ax_a, x, mean, lo, hi, sp.COLORS[m])
        span_a += mean
    ax_a.set_ylim(*ns.limits(span_a))
    sp.budget_axis(ax_a)
    ax_a.set_ylabel("Test MAE (eV)")

    span_b = [delta, -delta, 0.0]
    ns.delta_lines(ax_b, delta)
    ns.zero_line(ax_b)
    for key in CONTRASTS:
        x, mean, lo, hi = f4.series(rec, lambda b, key=key: b[key])
        ns.curve(ax_b, x, mean, lo, hi, CONTRAST_COLORS[key])
        span_b += mean + (lo + hi if key == "P_minus_S" else [])
    ax_b.set_ylim(*ns.limits(span_b))
    sp.budget_axis(ax_b)
    ax_b.set_ylabel("Difference in test MAE (eV)")

    handles = [*(sp.model_handle(m, f4.MODEL_LABELS[m]) for m in f4.MODELS),
               *(ns.line_handle(CONTRAST_COLORS[k], CONTRAST_LABELS[k]) for k in CONTRASTS),
               ns.delta_handle(r"$\pm\delta$"), ns.zero_handle()]
    sp.legend_handles(fig, handles, ncol=3)
    sp.panel_letters(fig, (ax_a, ax_b))
    pdf = sp.save(fig, ns.out_path(SUB, STEM))
    ns.write_caption(SUB, STEM, CAPTION)
    return pdf


CAPTION = """
**Figure 4. Predicting the descriptors from structure against learning the energy from structure directly.** (**a**)
Test MAE of S, D and the staged network P, which passes descriptors predicted from the pristine structure by P1 to the
trained D of the same training set and seed. (**b**) P − S, staging against learning from structure directly, and
P − D, the cost of predicting rather than knowing the descriptors, with the tolerance ±δ. Bands are two-sided
bootstrap intervals, clipped at the axis limits, values in `results/derived_staging/staging_fair.json`.
"""


if __name__ == "__main__":
    print(main())

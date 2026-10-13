"""Figure 3, extended (A1, EXTENSION): A = MAE_S - MAE_D against training hosts beyond the registered budgets.

An extension of the Figure 3 data; `figures/code/fig3_advantage.py` is unchanged. Registered budgets 25 to 654
from results/c1c2_v2.json and results/c1c2_v1.json (key ``A_mae``, bands); the precision-refined estimates at
400 and 654 (pooled 30 resamples x 5 seeds) from results/precision_g1_<arm>.json; the grouped K-fold CV points at
about 736 (K = 10) and 777 (K = 20) training hosts from results/cv_g1_<arm>.json. All four extension records are
required here.

    (a) every budget, with the margin delta and zero
    (b) from 200 training hosts up, with the one-sided 95% upper bounds of every point

    python figures/code/fig_extended_budget.py [--results-root DIR] [--out-dir DIR]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inputs_paper as ip
import style_paper as sp

STEM = "fig3_advantage_extended"
ZOOM_FROM = 200
UB_MARKER = {"marker": "_", "ms": 7.0, "mew": 1.2, "ls": "none"}


def _upper(ax, x, ub, version: str) -> None:
    ax.plot(x, ub, color=sp.COLORS["A"], alpha=1.0 if sp.BACKBONE_FILLED[version] else 0.55, zorder=6,
            **UB_MARKER)


def main() -> Path:
    a = ip.cli(__doc__)
    arms = ip.arms(a.results_root)
    ext = {(kind, arm): ip.require(rec, a.results_root) for (kind, arm), (rec, _) in ip.EXTENSIONS.items()}
    delta = arms["v2"]["delta_eV"]

    fig, axes = sp.figure("single", height_mm=72.0, ncols=2)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.93, bottom=0.31, wspace=0.30)
    spans = {0: [0.0, delta], 1: [0.0, delta]}
    for i, ax in enumerate(axes):
        sel = (lambda x: True) if i == 0 else (lambda x: x >= ZOOM_FROM)
        sp.reference_line(ax, delta, "", "delta")
        sp.reference_line(ax, 0.0, "", "zero")
        series = [(arm, ip.a_series(arms[arm]), None) for arm in sp.BACKBONES]
        series += [(arm, ip.a_series(ext[(kind, arm)]), kind) for kind in ("precision", "cv") for arm in sp.BACKBONES]
        for arm, (x, m, lo, hi, ub), kind in series:
            keep = [j for j, xx in enumerate(x) if sel(xx)]
            x, m, lo, hi, ub = ([v[j] for j in keep] for v in (x, m, lo, hi, ub))
            if kind is None:
                sp.band_curve(ax, x, m, lo, hi, "A", arm)
            else:
                sp.ext_points(ax, x, m, lo, hi, "A", kind, arm)
            if i == 1:
                _upper(ax, x if kind is None else sp.ext_x(x, kind, arm), ub, arm)
                spans[i] += lo + hi + ub
            else:
                spans[i] += m + ([] if kind is None else lo + hi)
        sp.budget_axis(ax, x_max=ip.x_upper(ext), x_min=None if i == 0 else ZOOM_FROM / 1.15)
        lo_, hi_ = min(spans[i]), max(spans[i])
        pad = 0.08 * (hi_ - lo_)
        ax.set_ylim(lo_ - pad, hi_ + pad)
        ax.set_ylabel(sp.LABELS["A"].split(" =")[0] + " (eV)")

    from matplotlib.lines import Line2D
    handles = [*(sp.backbone_handle(v) for v in sp.BACKBONES),
               sp.reference_handle(r"margin $\delta$", "delta"), sp.reference_handle("zero", "zero"),
               Line2D([], [], color=sp.COLORS["A"], label="one-sided 95% upper bound", **UB_MARKER),
               sp.ext_handle("precision"), sp.ext_handle("cv")]
    sp.legend_handles(fig, handles, ncol=3)
    sp.panel_letters(fig, axes)
    pdf = sp.save(fig, Path(a.out_dir) / STEM)
    ip.write_caption(a.out_dir, STEM, CAPTION)
    return pdf


CAPTION = """
**Figure 3 (extended). The advantage of explicit DFT descriptors beyond the registered training budgets
(EXTENSION).** A = MAE_S − MAE_D (eV; positive when the descriptors help) against the number of training hosts
(logarithmic axis). (**a**) Every point; the axis spans the point estimates and the extension intervals.
(**b**) From 200 training hosts up; horizontal bars are the one-sided 95% upper bounds of A. Lines with bands:
the registered 10-resample x 3-seed analysis, `results/c1c2_v2.json` and `results/c1c2_v1.json`, key
`payload.A_mae.<B>` (`A`, `ci95`, `upper_one_sided_95`). Diamonds, drawn just left of their budget: the
precision extension pooled over 30 resamples x 5 seeds at B = 400 and 654, `results/precision_g1_v2.json` and
`results/precision_g1_v1.json`, same keys (the 10 x 5 and 30 x 3 subsets in `payload.beside_subsets`; every
subset in `results/precision_a_b400_b654.json`). Squares: grouped K-fold CV with K = 10 and K = 20, pooled
out-of-fold predictions, placed at the mean fold training size `payload.x_training_hosts.<k10|k20>`,
`results/cv_g1_v2.json` and `results/cv_g1_v1.json`, keys `payload.A_mae.<k10|k20>` (fold-level SD in
`fold_sd`); full analysis in `results/cv_extended_budget.json`, the extended-budget statement under
`payload.extended_budget_statement`. Filled markers, solid line and filled band: primary backbone (v2), adopted
after diagnostics of the originally registered backbone; open markers, dashed line, hatched band and lighter
bars: originally registered backbone (v1). The dashed horizontal line is the margin δ (`payload.delta_eV`), the
dotted line zero. Bands and bars are two-sided 95% intervals: paired hierarchical bootstrap over resamples and
test hosts for the registered and precision points, paired host-cluster bootstrap over the 818 hosts for the CV
points. The precision and CV points are EXTENSION results, not pre-registered (`docs/deviations.md`, rows of
2026-10-11 and 2026-10-14). Script: `figures/code/fig_extended_budget.py`.
"""


if __name__ == "__main__":
    print(main())

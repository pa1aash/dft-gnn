"""Figure 3 (M3b): the advantage A = MAE_S - MAE_D of the DFT descriptors, both backbones.

Same records as scripts/make_figures.py (kept unchanged): results/c1c2_v2.json and results/c1c2_v1.json, key
``A_mae``. Optional EXTENSION records (figures/code/inputs_paper.py) are drawn when present.

    (a) A against training hosts over every budget, with the margin delta and zero
    (b) the same at the largest budgets, with the one-sided 95% upper bounds that decide N*

    python figures/code/fig3_advantage.py [--results-root DIR] [--out-dir DIR]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inputs_paper as ip
import style_paper as sp

STEM = "fig3_advantage"
ZOOM_FROM = 200          # first budget of panel (b)
UB_MARKER = {"marker": "_", "ms": 7.0, "mew": 1.2, "ls": "none"}


def _upper(ax, x, ub, version: str) -> None:
    ax.plot(x, ub, color=sp.COLORS["A"], alpha=1.0 if sp.BACKBONE_FILLED[version] else 0.55, zorder=6,
            **UB_MARKER)


def main() -> Path:
    a = ip.cli(__doc__)
    arms = ip.arms(a.results_root)
    ext = ip.extensions(a.results_root)
    delta = arms["v2"]["delta_eV"]

    fig, axes = sp.figure("single", height_mm=70.0, ncols=2)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.93, bottom=0.31, wspace=0.30)
    spans = {0: [0.0, delta], 1: [0.0, delta]}
    for i, ax in enumerate(axes):
        sel = (lambda x: True) if i == 0 else (lambda x: x >= ZOOM_FROM)
        sp.reference_line(ax, delta, "", "delta")
        sp.reference_line(ax, 0.0, "", "zero")
        series = [(arm, ip.a_series(arms[arm]), None) for arm in sp.BACKBONES]
        series += [(arm, ip.a_series(p), kind) for (kind, arm), p in ext.items()]
        for arm, (x, m, lo, hi, ub), kind in series:
            keep = [j for j, xx in enumerate(x) if sel(xx)]
            x, m, lo, hi, ub = ([v[j] for j in keep] for v in (x, m, lo, hi, ub))
            if kind is None:
                sp.band_curve(ax, x, m, lo, hi, "A", arm)
            else:
                sp.ext_points(ax, x, m, lo, hi, "A", kind, arm)
            if i == 1:
                if all(u is not None for u in ub):
                    _upper(ax, x if kind is None else sp.ext_x(x, kind, arm), ub, arm)
                spans[i] += lo + hi + [u for u in ub if u is not None]
            else:
                spans[i] += m
        sp.budget_axis(ax, x_max=ip.x_upper(ext), x_min=None if i == 0 else ZOOM_FROM / 1.15)
        lo_, hi_ = min(spans[i]), max(spans[i])
        pad = 0.08 * (hi_ - lo_)
        ax.set_ylim(lo_ - pad, hi_ + pad)
        ax.set_ylabel(sp.LABELS["A"].split(" =")[0] + " (eV)")

    handles = [*(sp.backbone_handle(v) for v in sp.BACKBONES),
               sp.reference_handle(r"margin $\delta$", "delta"), sp.reference_handle("zero", "zero")]
    from matplotlib.lines import Line2D
    handles.append(Line2D([], [], color=sp.COLORS["A"], label="one-sided 95% upper bound", **UB_MARKER))
    handles += [sp.ext_handle(k) for k in sorted({k for k, _ in ext})]
    sp.legend_handles(fig, handles, ncol=3)
    sp.panel_letters(fig, axes)
    pdf = sp.save(fig, Path(a.out_dir) / STEM)
    ip.write_caption(a.out_dir, STEM, caption(ext))
    return pdf


def caption(ext: dict) -> str:
    return f"""
**Figure 3. The advantage of explicit DFT descriptors over structure alone.** A = MAE_S − MAE_D (eV; positive
when the descriptors help) against the number of training hosts (logarithmic axis). (**a**) Every budget,
`payload.budgets`; the axis spans the point estimates, and intervals reaching beyond it are clipped (full
intervals in the keys below). (**b**) The budgets from 200 training hosts up, where the decision on the margin
is made; the horizontal bars are the one-sided 95% upper bounds of A, `upper_one_sided_95`, which define N*
(the smallest budget whose upper bound lies below δ at it and at every larger budget). Solid line with filled
circles: primary backbone (v2), adopted after diagnostics of the originally registered backbone; dashed line
with open circles, a hatched band and lighter bars: originally registered backbone (v1). Values:
`results/c1c2_v2.json` and
`results/c1c2_v1.json`, key `payload.A_mae.<B>` (`A`, two-sided 95% interval `ci95`, `upper_one_sided_95`);
N* and the ceiling at the largest budget in `payload.N_star` and `payload.C2` of the same files. The dashed
horizontal line is the margin δ (`payload.delta_eV`), the dotted line zero. Shaded bands are two-sided 95%
intervals from the paired hierarchical bootstrap. {ip.drawn_note(ext)} Script: `figures/code/fig3_advantage.py`.
"""


if __name__ == "__main__":
    print(main())

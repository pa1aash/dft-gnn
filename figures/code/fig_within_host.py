"""Within-host figure (M3b): can the networks tell the oxygen sites of one host apart? Both backbones.

Same records as scripts/make_figures.py (kept unchanged): results/c1c2_v2.json and results/c1c2_v1.json, keys
``mae.<B>.<S|D-state>.within_host_skill`` and ``A_within_host``. Optional EXTENSION records
(figures/code/inputs_paper.py) are drawn when present.

    (a) within-host skill of S and D against training hosts (0: the model ranks hosts but not sites)
    (b) the within-host advantage of the DFT descriptors, with the margin delta and zero

    python figures/code/fig_within_host.py [--results-root DIR] [--out-dir DIR]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inputs_paper as ip
import style_paper as sp

STEM = "fig_within_host"


def main() -> Path:
    a = ip.cli(__doc__)
    arms = ip.arms(a.results_root)
    ext = ip.extensions(a.results_root)
    delta = arms["v2"]["delta_eV"]
    x_max = ip.x_upper(ext)

    fig, (ax1, ax2) = sp.figure("single", height_mm=82.0, ncols=2)
    fig.subplots_adjust(left=0.105, right=0.985, top=0.93, bottom=0.33, wspace=0.32)
    sp.reference_line(ax1, 0.0, "", "zero")
    for model in ("S", "D"):
        for arm in sp.BACKBONES:
            sp.band_curve(ax1, *ip.mae_series(arms[arm], model, "within_host_skill"), model, arm)
        for (kind, arm), p in ext.items():
            sp.ext_points(ax1, *ip.mae_series(p, model, "within_host_skill"), model, kind, arm)
    sp.budget_axis(ax1, x_max=x_max)
    ax1.set_ylabel("Within-host skill (eV)")

    sp.reference_line(ax2, delta, "", "delta")
    sp.reference_line(ax2, 0.0, "", "zero")
    for arm in sp.BACKBONES:
        x, m, lo, hi, _ = ip.a_series(arms[arm], "A_within_host")
        sp.band_curve(ax2, x, m, lo, hi, "A", arm)
    for (kind, arm), p in ext.items():
        x, m, lo, hi, _ = ip.a_series(p, "A_within_host")
        sp.ext_points(ax2, x, m, lo, hi, "A", kind, arm)
    sp.budget_axis(ax2, x_max=x_max)
    ax2.set_ylabel(r"$A_\mathrm{within}$ (eV)")

    handles = [sp.model_handle("S"), sp.model_handle("D"),
               *(sp.backbone_handle(v) for v in sp.BACKBONES),
               sp.reference_handle(r"margin $\delta$", "delta"), sp.reference_handle("zero", "zero"),
               *sp.series_handles(k for k, _ in ext)]
    sp.legend_handles(fig, handles, ncol=3)
    sp.panel_letters(fig, (ax1, ax2))
    pdf = sp.save(fig, Path(a.out_dir) / STEM)
    ip.write_caption(a.out_dir, STEM, caption(ext))
    return pdf


def caption(ext: dict) -> str:
    return f"""
**Figure. Site resolution within a host.** (**a**) Within-host skill of S (structure only) and D (structure
plus the DFT descriptors of the pristine host and site) against the number of training hosts (logarithmic
axis): the within-host residual MAE of a predictor that is constant within each host, minus the model's, on
the same test hosts with at least two oxygen sites. Zero (dotted) means the model ranks hosts but does not
distinguish the sites of a host. Key `payload.mae.<B>.<S|D-state>.within_host_skill` (`mean`, two-sided
interval `ci`). (**b**) The within-host advantage of the descriptors, A_within = within-host residual MAE of S
minus that of D, with the margin δ (dashed, `payload.delta_eV`) and zero (dotted); key
`payload.A_within_host.<B>` (`A`, `ci95`), and the within-host N* in `payload.N_star_within_host`. Solid lines,
filled circles and filled bands: primary backbone (v2), adopted after diagnostics of the originally
registered backbone; dashed lines, open circles and hatched bands: originally registered backbone (v1).
Values from `results/c1c2_v2.json` and `results/c1c2_v1.json` (registered outer resamples; prediction of each
site the mean over the training seeds; two-sided intervals at the level `payload.bootstrap.two_sided_ci` of `results/g1_primary.json`, from the paired
hierarchical bootstrap). The v1 values
also appear, with the G1 estimator, in `results/g1_within_host.json`. {ip.drawn_note(ext)}
Script: `figures/code/fig_within_host.py`.
"""


if __name__ == "__main__":
    print(main())

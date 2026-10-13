"""Figure 2 (M3b): learning curves of S and D for both backbones against the trivial and descriptor baselines.

Same records as scripts/make_figures.py (kept unchanged): results/c1c2_v2.json and results/c1c2_v1.json for the
networks, results/diagnostics_sweep.json (``references``) for the training mean, B0 and RF-Kumagai on the same
outer test sites. Optional EXTENSION records (figures/code/inputs_paper.py) are drawn when present.

    (a) S, primary backbone (v2) solid and originally registered backbone (v1) dashed, with the baselines
    (b) D (D-state), likewise

    python figures/code/fig2_learning_curves.py [--results-root DIR] [--out-dir DIR]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inputs_paper as ip
import style_paper as sp

STEM = "fig2_learning_curves"
BASELINES = (("mean", "mean", (1, 2)), ("B0", "B0", None), ("RF-Kumagai", "RF-Kumagai", None))


def main() -> Path:
    a = ip.cli(__doc__)
    arms = ip.arms(a.results_root)
    refs = ip.require("diagnostics_sweep", a.results_root)["references"]
    ext = ip.extensions(a.results_root)
    budgets = [int(b) for b in arms["v2"]["budgets"]]

    fig, axes = sp.figure("single", height_mm=84.0, ncols=2, sharey=True)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.93, bottom=0.33, wspace=0.12)
    tops = []
    for ax, model in zip(axes, ("S", "D")):
        for key, rkey, dashes in BASELINES:
            x, m, lo, hi = ip.ref_series(refs, rkey, budgets)
            sp.baseline_curve(ax, x, m, lo, hi, key, dashes=dashes)
            tops += m
        for arm in sp.BACKBONES:
            x, m, lo, hi = ip.mae_series(arms[arm], model)
            sp.band_curve(ax, x, m, lo, hi, model, arm)
            tops += m
        for (kind, arm), p in ext.items():
            x, m, lo, hi = ip.mae_series(p, model)
            sp.ext_points(ax, x, m, lo, hi, model, kind, arm)
            tops += m
        sp.budget_axis(ax, x_max=ip.x_upper(ext))
    axes[0].set_ylabel("Site test MAE (eV)")
    axes[0].set_ylim(0.2, 1.06 * max(tops))

    handles = [sp.model_handle("S"), sp.model_handle("D"),
               *(sp.baseline_handle(k, dashes=d) for k, _, d in BASELINES),
               *(sp.backbone_handle(v) for v in sp.BACKBONES),
               *sp.series_handles(k for k, _ in ext)]
    sp.legend_handles(fig, handles, ncol=3)
    sp.panel_letters(fig, axes)
    pdf = sp.save(fig, Path(a.out_dir) / STEM)
    ip.write_caption(a.out_dir, STEM, caption(ext))
    return pdf


def caption(ext: dict) -> str:
    return f"""
**Figure 2. Learning curves of the structure-only and descriptor-augmented networks.** Site-level test mean
absolute error (MAE, eV) of the neutral oxygen-vacancy formation energy against the number of training hosts
(logarithmic axis, budgets `payload.budgets`). (**a**) The structure-only network S; (**b**) the network D,
which also receives the DFT descriptors of the pristine host and site (D-state injection). Solid lines with
filled circles: primary backbone (v2), adopted after diagnostics of the originally registered backbone;
dashed lines with open circles and hatched bands: originally registered backbone (v1). Both are trained and
evaluated on the
same registered outer resamples, with the prediction of each test site the mean over the training seeds.
Values: `results/c1c2_v2.json` and `results/c1c2_v1.json`, key `payload.mae.<B>.S.mae` (a) and
`payload.mae.<B>.D-state.mae` (b), each with `mean` and the two-sided interval `ci` at the level `payload.bootstrap.two_sided_ci` of `results/g1_primary.json`
(paired hierarchical bootstrap over resamples and then test hosts). Baselines, which do not depend on the backbone (squares on
thinner lines): the training-mean predictor (dotted), the two-descriptor physics floor B0 and the random
forest on the Kumagai descriptors (RF-Kumagai), from `results/diagnostics_sweep.json`, key
`payload.references.<B>.<mean|B0|RF-Kumagai>`, evaluated on the same test sites. Bands are these
intervals; bands are clipped at the axis limits, and their full extent is in the keys above. {ip.drawn_note(ext)}
Script: `figures/code/fig2_learning_curves.py`.
"""


if __name__ == "__main__":
    print(main())

"""SI figure (A1, EXTENSION, descriptive): A = MAE_S - MAE_D of single runs by GPU class.

Reads the descriptive GPU-class tables of results/precision_a_b400_b654.json and results/cv_extended_budget.json
(``payload.descriptive.gpu_class``; rule: `docs/deviations.md`, row of 2026-10-14, item e1). Per backbone, design
point and GPU class: the mean over paired cells (same resample or fold, budget and seed; S and D both run on that
class) of single-run MAE_S - MAE_D, with the descriptive 95% interval of a bootstrap over the cells. Classes
without a paired cell are not drawn. No test.

    (a) precision, B = 400   (b) precision, B = 654   (c) grouped CV, K = 10   (d) grouped CV, K = 20

    python figures/code/fig_si_gpu_class.py [--results-root DIR] [--out-dir DIR]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inputs_paper as ip
import style_paper as sp

STEM = "fig_si_gpu_class"
CLASSES = ("A10", "RTX 3090", "L4", "RTX 4090", "original sweep")
TICK = {"A10": "A10", "RTX 3090": "RTX 3090", "L4": "L4", "RTX 4090": "RTX 4090", "original sweep": "sweep"}
PANELS = (("precision_a_b400_b654", "precision|400", "precision"), ("precision_a_b400_b654", "precision|654", "precision"),
          ("cv_extended_budget", "cv|10", "cv"), ("cv_extended_budget", "cv|20", "cv"))
DODGE = {"v2": -0.14, "v1": 0.14}


def main() -> Path:
    a = ip.cli(__doc__)
    out_dir = a.out_dir if a.out_dir != ip.ROOT / "figures" / "main" else ip.ROOT / "figures" / "si"
    recs = {n: ip.require(n, a.results_root) for n in {p[0] for p in PANELS}}
    delta = recs["cv_extended_budget"]["delta_eV"]
    fig, axes = sp.figure("single", height_mm=118.0, ncols=2, nrows=2)
    fig.subplots_adjust(left=0.10, right=0.985, top=0.95, bottom=0.2, wspace=0.28, hspace=0.42)
    axes = axes.ravel()
    for ax, (rec, key, kind) in zip(axes, PANELS):
        rows = recs[rec]["descriptive"]["gpu_class"][key]
        sp.reference_line(ax, delta, "", "delta")
        sp.reference_line(ax, 0.0, "", "zero")
        present = [c for c in CLASSES if any(r["gpu_class"] == c and r.get("A_paired_cells") for r in rows)]
        ys = [0.0, delta]
        for arm in sp.BACKBONES:
            pts = [(present.index(r["gpu_class"]) + DODGE[arm], r["A_paired_cells"]) for r in rows
                   if r["backbone"] == arm and r.get("A_paired_cells") and r["gpu_class"] in present]
            if not pts:
                continue
            x = [p[0] for p in pts]
            m = [p[1]["A"] for p in pts]
            lo = [p[1]["ci95_descriptive"][0] for p in pts]
            hi = [p[1]["ci95_descriptive"][1] for p in pts]
            ax.errorbar(x, m, yerr=[[mm - ll for mm, ll in zip(m, lo)], [hh - mm for mm, hh in zip(m, hi)]],
                        fmt=sp.EXT_MARKERS[kind], ms=sp.EXT_MARKER_SIZE, color=sp.COLORS["A"], ecolor=sp.COLORS["A"],
                        elinewidth=sp.REF_W, capsize=0, mew=0.8, ls="none", zorder=5,
                        mfc=sp.COLORS["A"] if sp.BACKBONE_FILLED[arm] else "white", mec=sp.COLORS["A"])
            ys += lo + hi
        ax.set_xticks(range(len(present)))
        ax.set_xticklabels([TICK[c] for c in present])
        ax.set_xlim(-0.6, len(present) - 0.4)
        pad = 0.08 * (max(ys) - min(ys))
        ax.set_ylim(min(ys) - pad, max(ys) + pad)
        ax.set_ylabel(r"$A$ (eV)")
        ax.set_xlabel("GPU class")

    from matplotlib.lines import Line2D
    handles = [Line2D([], [], color="#000000", ls="none", marker="o", ms=sp.MARKER_SIZE, mfc=f, mec="#000000",
                      mew=0.8, label=sp.BACKBONE_LABELS[v]) for v, f in (("v2", "#000000"), ("v1", "white"))]
    handles += [sp.reference_handle(r"margin $\delta$", "delta"), sp.reference_handle("zero", "zero"),
                sp.ext_handle("precision"), sp.ext_handle("cv")]
    sp.legend_handles(fig, handles, ncol=3)
    sp.panel_letters(fig, axes)
    pdf = sp.save(fig, Path(out_dir) / STEM)
    ip.write_caption(out_dir, STEM, CAPTION)
    return pdf


CAPTION = """
**Figure S (GPU class). The advantage A by GPU class of the training runs (EXTENSION, descriptive, no test).**
A = MAE_S − MAE_D (eV) of single runs, averaged over the paired cells in which the S run and the D run of the same
resample or fold, budget and seed both ran on the same GPU class. (**a**) Precision extension, B = 400.
(**b**) Precision extension, B = 654. (**c**) Grouped K-fold CV, K = 10. (**d**) Grouped K-fold CV, K = 20.
Classes: NVIDIA A10, GeForce RTX 3090, L4 and GeForce RTX 4090 of the cluster pool, and "sweep", the original
sweep runs of resamples 0 to 9, seeds 0 to 2 (precision only). RTX 4090 was not part of the N1 repeatability runs.
GPU class was not randomised with respect to resample, fold or seed, so differences between classes are not
separable from them and are not read as hardware effects. Values: `results/precision_a_b400_b654.json` and
`results/cv_extended_budget.json`, key `payload.descriptive.gpu_class.<design|point>` (`A_paired_cells.A`,
`ci95_descriptive`, `n_paired_cells`, `n_runs`); classes without a paired cell are not drawn. Bars: descriptive
95% percentile intervals from a bootstrap over the paired cells (`bootstrap_seed`). Filled markers: primary
backbone (v2), adopted after diagnostics of the originally registered backbone; open markers: originally
registered backbone (v1). Diamonds: precision extension; squares: grouped K-fold CV. Dashed line: the margin δ;
dotted line: zero. Rule: `docs/deviations.md`, row of 2026-10-14, item e1. Script:
`figures/code/fig_si_gpu_class.py`.
"""


if __name__ == "__main__":
    print(main())

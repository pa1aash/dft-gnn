"""SI figure (A5): the advantage A under the high-moment and capped-twin sensitivities, and CGCNN versus MEGNet.

Reads results/sens_high_moment_v1.json (EXTENSION), results/sens_capped_post_hoc.json (POST HOC) and
results/sens_cgcnn.json (EXTENSION, untuned, descriptive); rules: `docs/deviations.md`, rows of 2026-10-10
(§5, §12) and 2026-10-14 (§5, §12). The three sensitivity stages ran on the originally registered backbone (v1)
only; the primary backbone (v2) appears with its primary result in (a) and as a MEGNet comparator in (b).

    (a) A at B = 654: primary (v2 and v1), high moment (v1, common test sites) and capped twins (v1)
    (b) site MAE of S and D at B = 50, 200, 654 on resample 0: MEGNet v2, MEGNet v1 and CGCNN

    python figures/code/fig_si_sensitivities.py [--results-root DIR] [--out-dir DIR]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inputs_paper as ip
import style_paper as sp
from matplotlib.lines import Line2D

STEM = "fig_si_sensitivities"
CGCNN_MARKER = "X"
CGCNN_LABEL = "CGCNN, untuned (EXTENSION)"
DODGE_A = {"v2": -0.12, "v1": 0.12}
CGCNN_DODGE = 1.08          # multiplicative x offset of the CGCNN points on the log budget axis
UPPER_HALF_WIDTH = 0.09


def a_points(hm: dict, cp: dict) -> list[tuple[int, str, dict]]:
    """(category index, backbone, block with mean / ci / upper_one_sided) of panel (a)."""
    v2 = cp["v2_primary_654"]["primary"]["A"]
    return [(0, "v2", v2), (0, "v1", cp["per_budget"]["654"]["primary"]["A"]),
            (1, "v1", hm["high_moment"]["A"]), (2, "v1", cp["per_budget"]["654"]["capped_twins"]["A"])]


def draw_a(ax, pts, delta) -> None:
    sp.reference_line(ax, delta, "", "delta")
    sp.reference_line(ax, 0.0, "", "zero")
    c = sp.COLORS["A"]
    for i, arm, b in pts:
        x = i + DODGE_A[arm]
        lo, hi = b["ci"]
        eb = ax.errorbar([x], [b["mean"]], yerr=[[b["mean"] - lo], [hi - b["mean"]]], fmt=sp.MARKER,
                         ms=sp.MARKER_SIZE + 0.6, color=c, ecolor=c, elinewidth=sp.REF_W + 0.2, capsize=0, mew=0.8,
                         mfc=c if sp.BACKBONE_FILLED[arm] else "white", mec=c, zorder=5)
        eb[2][0].set_linestyle(sp.BACKBONE_LS[arm])
        u = b["upper_one_sided"]
        ax.plot([x - UPPER_HALF_WIDTH, x + UPPER_HALF_WIDTH], [u, u], color=c, lw=sp.LINE_W, solid_capstyle="butt")
    ax.set_xticks(range(3))
    ax.set_xticklabels(["primary", "high moment", "capped twins"])
    ax.set_xlim(-0.55, 2.55)
    ax.set_ylabel(r"$A$ at the largest budget (eV)")
    ax.set_xlabel("analysis")


def draw_b(ax, cg) -> None:
    budgets = cg["budgets"]
    for fam, arm in (("megnet_v2", "v2"), ("megnet_v1", "v1")):
        for m in ("S", "D"):
            rows = [cg["table"][fam][str(B)][m]["mae"] for B in budgets]
            sp.band_curve(ax, budgets, [r["point"] for r in rows], [r["ci95"][0] for r in rows],
                          [r["ci95"][1] for r in rows], m, arm)
    for m in ("S", "D"):
        rows = [cg["table"]["cgcnn"][str(B)][m]["mae"] for B in budgets]
        x = [B * CGCNN_DODGE for B in budgets]
        y = [r["point"] for r in rows]
        ax.errorbar(x, y, yerr=[[a - r["ci95"][0] for a, r in zip(y, rows)], [r["ci95"][1] - a for a, r in zip(y, rows)]],
                    fmt=CGCNN_MARKER, ms=sp.EXT_MARKER_SIZE + 0.6, color=sp.COLORS[m], ecolor=sp.COLORS[m],
                    elinewidth=sp.REF_W, capsize=0, ls="none", mew=0.6, mec=sp.COLORS[m], zorder=6)
    ax.set_xscale("log")
    ax.set_xticks(budgets)
    ax.set_xticklabels([str(b) for b in budgets])
    ax.minorticks_off()
    ax.set_xlim(budgets[0] / 1.35, budgets[-1] * 1.35)
    ax.set_xlabel("training hosts")
    ax.set_ylabel("test MAE (eV)")


def main() -> Path:
    a = ip.cli(__doc__)
    out_dir = a.out_dir if a.out_dir != ip.ROOT / "figures" / "main" else ip.ROOT / "figures" / "si"
    hm = ip.require("sens_high_moment_v1", a.results_root)
    cp = ip.require("sens_capped_post_hoc", a.results_root)
    cg = ip.require("sens_cgcnn", a.results_root)
    fig, axes = sp.figure("single", height_mm=82.0, ncols=2, nrows=1)
    fig.subplots_adjust(left=0.10, right=0.985, top=0.94, bottom=0.25, wspace=0.32)
    draw_a(axes[0], a_points(hm, cp), hm["delta_eV"])
    draw_b(axes[1], cg)
    handles = [sp.backbone_handle("v2"), sp.backbone_handle("v1"), sp.model_handle("S"), sp.model_handle("D"),
               Line2D([], [], color="#000000", ls="none", marker=CGCNN_MARKER, ms=sp.EXT_MARKER_SIZE + 0.6,
                      label=CGCNN_LABEL),
               Line2D([], [], color=sp.COLORS["A"], lw=sp.LINE_W, ls="none", marker="_", ms=6,
                      label="one-sided 95% upper bound"),
               sp.reference_handle(r"margin $\delta$", "delta"), sp.reference_handle("zero", "zero")]
    sp.legend_handles(fig, handles, ncol=3)
    sp.panel_letters(fig, axes)
    pdf = sp.save(fig, Path(out_dir) / STEM)
    ip.write_caption(out_dir, STEM, CAPTION)
    return pdf


CAPTION = """
**Figure S (sensitivities). The advantage A under the high-moment exclusion and the longer epoch cap, and an
untuned CGCNN beside the MEGNet backbones.** (**a**) A = MAE_S − MAE_D (eV; positive when the DFT descriptors
help) at the largest training budget, from the seed-ensemble site MAE averaged over the registered outer resamples.
"primary": the primary result of each backbone (`results/sens_capped_post_hoc.json`, keys
`payload.v2_primary_654.primary.A` and `payload.per_budget.654.primary.A`; the latter reproduces
`results/g1_primary.json`, `payload.per_budget.654.A`, checked in `payload.sanity_g1_primary`). "high moment"
(EXTENSION): S and D retrained with the entries whose defect magnetic moment exceeds the registered threshold
(`payload.threshold_muB`, entries in `payload.excluded_entries`) removed from training and test sites, compared on
the common test sites (`results/sens_high_moment_v1.json`, key `payload.high_moment.A`; the primary result on the
same sites is `payload.primary_common_sites.A` and the paired change `payload.change_high_moment_minus_primary.A`).
"capped twins" (POST HOC): every primary-sweep run that stopped at the epoch cap replaced by its rerun with the
larger cap (`results/sens_capped_post_hoc.json`, key `payload.per_budget.654.capped_twins.A`; paired change
`payload.per_budget.654.change_twin_minus_primary.A`). Both sensitivities exist for the originally registered
backbone only. Markers: point estimates (`mean`); bars: two-sided intervals (`ci`) of the G1 hierarchical bootstrap
with the G1 draws (`payload.bootstrap`); short horizontal bars: one-sided upper bounds (`upper_one_sided`); dashed
line: the margin δ (`payload.delta_eV`); dotted line: zero. (**b**) Seed-ensemble test MAE (eV) of S (blue) and D
(green) on a single outer resample (`payload.resample`) at the budgets `payload.budgets`, for the MEGNet backbones
(lines with bands) and for CGCNN with fixed, untuned optimiser settings (crosses, drawn just right of their budget)
(`results/sens_cgcnn.json`, key `payload.table.<family>.<budget>.<S|D>.mae`, families `megnet_v2`, `megnet_v1` and
`cgcnn`; parameter counts in `payload.parameter_counts`). Bands and bars in (b) are two-sided intervals (`ci95`) of
a host-cluster bootstrap over the test hosts of that resample, shared by every series (`payload.bootstrap`); with
one resample they reflect test-host sampling only, not resample or split variation, and no test is made. Filled
markers and solid lines: primary backbone (v2), adopted after diagnostics of the originally registered backbone;
open markers and dashed lines: originally registered backbone (v1). Analysis rules: `docs/deviations.md`, cited
under `payload.rule` and `payload.label` of the records. Script: `figures/code/fig_si_sensitivities.py`.
"""


if __name__ == "__main__":
    print(main())

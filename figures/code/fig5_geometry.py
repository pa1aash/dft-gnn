"""Figure 5: geometry robustness (C3b). ΔMAE under MLIP geometry and per-host prediction change, at B = 654.

Inputs: results/geometry_c3b.json (the registered geometry analysis on the originally registered backbone v1 and our
818 MACE-MP-0 relaxations; written by analysis/geometry_analysis.py under the rules of the docs/deviations.md row of
2026-10-14, §9 step A3) and results/analysis/geometry_host_change.parquet (per-host mean |prediction change|, sha256
checked against that record). No run record is aggregated here.

    (a) ΔMAE = MAE(c) - MAE(DFT geometry) of S, D and P for c = MLIP geometry and MLIP geometry rescaled to the DFT
        volume, two-sided 95% intervals, zero line
    (b-d) per host, the mean |prediction change| against the isotropic strain eps_v of its relaxation, one panel per
        model (S, D, P), the two conditions by marker; logarithmic y axis

All series are v1 (originally registered backbone): open markers and dashed interval bars. No v2 geometry evaluation
on these relaxations exists.

    python figures/code/fig5_geometry.py [--results-root DIR] [--out-dir DIR]
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inputs_paper as ip
import style_paper as sp

STEM = "fig5_geometry"
VERSION = "v1"
B = "654"
MODELS = ("S", "D", "P")
CONDS = ("mlip", "mlip_rescaled")
COND_MARKERS = {"mlip": "o", "mlip_rescaled": "v"}
COND_LABELS = {"mlip": "MLIP geometry", "mlip_rescaled": "MLIP geometry rescaled to the DFT volume"}
DODGE = {"mlip": -0.12, "mlip_rescaled": 0.12}
X_COMPONENT = "eps_v"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def host_change(payload: dict, root: Path) -> pd.DataFrame:
    meta = payload["input"]["host_change"]
    path = root.parent / meta["path"] if (root.parent / meta["path"]).exists() else ip.ROOT / meta["path"]
    if sha256(path) != meta["sha256"]:
        raise ValueError(f"{path}: sha256 differs from results/geometry_c3b.json")
    return pd.read_parquet(path)


def _open(color: str) -> dict:
    return {"mfc": "white", "mec": color, "mew": 0.8}


def main() -> Path:
    from matplotlib.lines import Line2D
    from matplotlib.ticker import MaxNLocator

    a = ip.cli(__doc__)
    pay = ip.require("geometry_c3b", a.results_root)
    ch = host_change(pay, ip.results_dir(a.results_root))
    ch = ch[ch.B == int(B)]

    fig = sp.figure("single", height_mm=128.0)[0]
    fig.clf()
    gs = fig.add_gridspec(2, 3, left=0.1, right=0.985, top=0.95, bottom=0.27, hspace=0.55, wspace=0.42)
    ax_a = fig.add_subplot(gs[0, :])
    axes_b = [fig.add_subplot(gs[1, j]) for j in range(3)]

    # (a) ΔMAE with two-sided 95% intervals
    dm = pay["budgets"][B]["delta_mae"]
    for i, m in enumerate(MODELS):
        c = sp.COLORS[m]
        for cond in CONDS:
            d = dm[m][cond]
            eb = ax_a.errorbar(i + DODGE[cond], d["mean"], yerr=[[d["mean"] - d["ci95"][0]], [d["ci95"][1] - d["mean"]]],
                               fmt=COND_MARKERS[cond], ms=sp.MARKER_SIZE + 1, color=c, ecolor=c, elinewidth=sp.LINE_W * 0.8,
                               capsize=2.0, **_open(c))
            eb[-1][0].set_linestyle(sp.BACKBONE_LS[VERSION])
    sp.reference_line(ax_a, 0.0, "", "zero")
    ax_a.set_xticks(range(len(MODELS)))
    ax_a.set_xticklabels(MODELS)
    ax_a.set_xlim(-0.6, len(MODELS) - 0.4)
    ax_a.set_xlabel("Model")
    ax_a.set_ylabel(r"$\Delta$MAE (eV)")

    # (b-d) per-host |prediction change| against eps_v
    for ax, m in zip(axes_b, MODELS, strict=True):
        c = sp.COLORS[m]
        for cond in CONDS:
            s = ch[(ch.model == m) & (ch.condition == cond) & (ch.mean_abs_change > 0)]
            ax.scatter(s[X_COMPONENT], s.mean_abs_change, s=6, marker=COND_MARKERS[cond], facecolors="none",
                       edgecolors=c, linewidths=0.45, alpha=0.6)
        ax.set_yscale("log")
        ax.set_xlabel(r"$\varepsilon_v$")
        lo = ch[X_COMPONENT].min()
        ax.set_xlim(min(0.0, lo), ch[X_COMPONENT].max() * 1.05)
        ax.xaxis.set_major_locator(MaxNLocator(3))
    axes_b[0].set_ylabel("|Prediction change| (eV)")

    handles = [*(sp.model_handle(m) for m in MODELS),
               *(Line2D([], [], color="#000000", ls="none", marker=COND_MARKERS[k], ms=sp.MARKER_SIZE + 1,
                        **_open("#000000"), label=COND_LABELS[k]) for k in CONDS),
               sp.backbone_handle(VERSION), sp.reference_handle("zero", "zero")]
    sp.legend_handles(fig, handles, ncol=2)
    sp.panel_letters(fig, [ax_a, *axes_b])
    pdf = sp.save(fig, Path(a.out_dir) / STEM)
    ip.write_caption(a.out_dir, STEM, caption())
    return pdf


def caption() -> str:
    return """
**Figure 5. Geometry robustness: models trained on DFT host geometry evaluated on MACE-MP-0 relaxed hosts.** The
pristine host unit cells were relaxed with MACE-MP-0 (medium model, double precision; cell and positions) and tiled onto the release
supercells (`docs/deviations.md`: the geometry, relaxation and tiling rows); the models are not retrained. Three
inference conditions: (i) DFT geometry, (ii) MLIP geometry and (iii) MLIP geometry isotropically rescaled to the DFT
volume. S is the structure-only model, D the descriptor model, which keeps its DFT descriptors under every condition
(a fixed oracle, so its change isolates the graph input), and P the staged model (predicted descriptors into D).
Values: `results/geometry_c3b.json`, the registered geometry analysis; every `payload` key below belongs to that
record unless another file is named. All series are the originally registered backbone (v1), drawn with open markers and dashed interval bars, at the
registered budget (key `payload.budgets.654`); the descriptive extra budget is under `payload.budgets.200` and is not
drawn. (**a**) ΔMAE = MAE(condition) − MAE(DFT geometry) of the seed-ensemble predictions on the same test sites, for
MLIP geometry (circles) and MLIP geometry rescaled to the DFT volume (down triangles), with two-sided 95% intervals of
the paired hierarchical bootstrap over resamples and test hosts named in `payload.estimator`: key
`payload.budgets.654.delta_mae.<S|D|P>.<mlip|mlip_rescaled>` (`mean`, `ci95`); the marginal MAE of each condition is
under `payload.budgets.654.mae`. The dotted line is zero. The null rule of the geometry section of
`docs/ANALYSIS_PLAN.md` and its outcome are under `payload.null_rule` (`outcome`, `median_internal_rmsd_A`,
`intervals_excluding_zero`). (**b**–**d**) For S (**b**), D (**c**) and P (**d**), each point is one test host: the
mean over its test sites and resamples of the absolute change of the seed-ensemble prediction from DFT geometry,
under MLIP geometry (circles) and under the rescaled MLIP geometry (down triangles), against the isotropic strain
ε_v of the host's relaxation (`results/analysis/geometry_host_change.parquet`, hashed in `payload.input.host_change`).
ε_v is drawn because it carries the largest joint-fit coefficient for S and P in the pooled regression of the
per-host change on the three geometry components (`payload.regression.strata.pooled.<S|P>_654.joint.coef_per_sd`);
the deviatoric-strain and internal-RMSD fits, the d-electron strata and the non-converged sensitivity are under
`payload.regression` and `payload.nonconverged_sensitivity`. The y axes are logarithmic; hosts whose change is
exactly zero (D under the rescaled condition only) cannot be drawn on them and are listed in the parquet file. The
distributions of the three components, by d-electron bin and by GPU class of the relaxation, are in
`results/geometry_descriptive.json`. No v2 geometry evaluation on these relaxations (ours, of every host of the universe) exists; the collaborator's
v2 evaluation on his own relaxations is a post hoc descriptive cross-check (`payload.cross_check_809` of
`results/geometry_descriptive.json`) and is not drawn. Script: `figures/code/fig5_geometry.py`.
"""


if __name__ == "__main__":
    print(main())

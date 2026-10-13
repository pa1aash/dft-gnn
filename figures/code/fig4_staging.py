"""Figure 4: staging (C3a). MAE of S, D and P, and the contrasts D - P and P - S, both backbones.

Inputs: results/staging_v2.json (primary backbone, POST HOC) and results/staging_v1.json (originally registered
backbone; the registered staging analysis), written by analysis/staging_analysis.py under the rules of the
docs/deviations.md row of 2026-10-14 (§8). No run record is aggregated here.

    (a) seed-ensemble test MAE of S, D and P against training hosts, two-sided 95% bands
    (b) D - P (cost of predicting the descriptors) and P - S (staging against end-to-end), two-sided 95% bands,
        the equivalence margins +delta_P and -delta_P and zero

Axes span the point estimates and the P - S intervals; wider bands (D and D - P at the smallest budgets) are clipped
and their full intervals are in the records.

    python figures/code/fig4_staging.py [--results-root DIR] [--out-dir DIR]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inputs_paper as ip
import style_paper as sp

STEM = "fig4_staging"
CONTRAST_COLORS = {"P_minus_S": sp.COLORS["P"], "D_minus_P": sp.COLORS["A"]}
CONTRAST_LABELS = {"P_minus_S": r"P $-$ S (staging against end-to-end)",
                   "D_minus_P": r"D $-$ P (cost of predicting the descriptors)"}
MODELS = ("S", "D", "P")


def series(payload: dict, getter):
    x = sorted(int(b) for b in payload["budgets"])
    rows = [getter(payload["budgets"][str(b)]) for b in x]
    return x, [r["mean"] for r in rows], [r["ci95"][0] for r in rows], [r["ci95"][1] for r in rows]


def _curve(ax, x, m, lo, hi, color: str, version: str) -> None:
    sp.band(ax, x, lo, hi, color, version)
    ax.plot(x, m, color=color, lw=sp.LINE_W, ls=sp.BACKBONE_LS[version], marker=sp.MARKER, ms=sp.MARKER_SIZE,
            mfc=color if sp.BACKBONE_FILLED[version] else "white", mec=color, mew=0.8)


def _limits(values, pad: float = 0.08):
    lo, hi = min(values), max(values)
    return lo - pad * (hi - lo), hi + pad * (hi - lo)


def main() -> Path:
    from matplotlib.lines import Line2D

    a = ip.cli(__doc__)
    arms = {v: ip.require(f"staging_{v}", a.results_root)["payload"] for v in sp.BACKBONES}
    delta = arms["v2"]["delta_P_eV"]
    if arms["v1"]["delta_P_eV"] != delta:
        raise ValueError("the two records carry different margins")

    fig, axes = sp.figure("single", height_mm=84.0, ncols=2)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.94, bottom=0.36, wspace=0.32)
    ax_a, ax_b = axes

    span_a = []
    for v in sp.BACKBONES:
        for m in MODELS:
            x, mean, lo, hi = series(arms[v], lambda b, m=m: b["mae"][m])
            _curve(ax_a, x, mean, lo, hi, sp.COLORS[m], v)
            span_a += mean
    ax_a.set_ylim(*_limits(span_a))
    sp.budget_axis(ax_a)
    ax_a.set_ylabel("Test MAE (eV)")

    span_b = [delta, -delta, 0.0]
    for ref in (delta, -delta):
        sp.reference_line(ax_b, ref, "", "delta")
    sp.reference_line(ax_b, 0.0, "", "zero")
    for v in sp.BACKBONES:
        for key in ("D_minus_P", "P_minus_S"):
            x, mean, lo, hi = series(arms[v], lambda b, key=key: b[key])
            _curve(ax_b, x, mean, lo, hi, CONTRAST_COLORS[key], v)
            span_b += mean + (lo + hi if key == "P_minus_S" else [])
    ax_b.set_ylim(*_limits(span_b))
    sp.budget_axis(ax_b)
    ax_b.set_ylabel("Difference in test MAE (eV)")

    handles = [*(sp.model_handle(m) for m in MODELS),
               *(Line2D([], [], color=CONTRAST_COLORS[k], lw=sp.LINE_W, marker=sp.MARKER, ms=sp.MARKER_SIZE,
                        mfc=CONTRAST_COLORS[k], mec=CONTRAST_COLORS[k], label=CONTRAST_LABELS[k])
                 for k in ("P_minus_S", "D_minus_P")),
               *(sp.backbone_handle(v) for v in sp.BACKBONES),
               sp.reference_handle(r"equivalence margins $\pm\delta_P$", "delta"), sp.reference_handle("zero", "zero")]
    sp.legend_handles(fig, handles, ncol=2)
    sp.panel_letters(fig, axes)
    pdf = sp.save(fig, Path(a.out_dir) / STEM)
    ip.write_caption(a.out_dir, STEM, caption())
    return pdf


def caption() -> str:
    return """
**Figure 4. Staging: predicting the DFT descriptors from structure and passing them to the descriptor model.** The
staged model P feeds the descriptors predicted by P1 from the pristine host structure into the trained descriptor
model D of the same resample, budget and seed (pairing in `docs/deviations.md`: the staging-pairing
clarification and the A2 implementation row); S is the structure-only model. Training hosts on a logarithmic axis. (**a**) Seed-ensemble test MAE
of S, D and P (eV): `payload.budgets.<B>.mae.<S|D|P>` (`mean`, two-sided interval `ci95`). (**b**) The two staging
contrasts of the staging section of `docs/ANALYSIS_PLAN.md`: D − P, the cost of predicting rather than knowing the descriptors (negative:
P worse than D), key `payload.budgets.<B>.D_minus_P`; and P − S, staging against end-to-end learning (negative: P
better than S), key `payload.budgets.<B>.P_minus_S` (`mean`, `ci95`; the TOST interval `ci90`, the one-sided
bounds `lower_one_sided_95` and `upper_one_sided_95`, the outcome `report` and `noninferior`). The dashed lines
are the equivalence margins plus and minus δ_P (`payload.delta_P_eV`), the dotted line zero. The outcome of P − S
at every budget follows the TOST rule of the collaborator (`docs/deviations.md`: the TOST row and its ratification;
POST HOC) and is listed in `payload.summary.outcome_by_budget`. Records: `results/staging_v2.json`
(solid lines, filled markers, filled bands: primary backbone (v2), adopted after diagnostics of the originally
registered backbone, POST HOC) and `results/staging_v1.json` (dashed lines, open markers, hatched bands:
originally registered backbone (v1), the registered staging analysis). Bands are the two-sided intervals of the
paired hierarchical bootstrap over resamples and test hosts named in `payload.estimator` (one draw set for S, D,
P, every budget and both backbones). The axes span the point estimates and the P − S intervals; the bands of D in
(a) and of D − P in (b) at the smallest budgets reach beyond them and are clipped (full intervals under the keys
above). Integrity checks (counts, pairing, true-descriptor swap-in): `payload.integrity`; P1 descriptor accuracy:
`payload.p1_descriptors`. Script: `figures/code/fig4_staging.py`.
"""


if __name__ == "__main__":
    print(main())

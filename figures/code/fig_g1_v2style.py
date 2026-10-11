"""G1 learning curves redrawn through the paper style (M3), to exercise figures/code/style_paper.py.

Same data and panels as scripts/analysis/fig_g1.py (results/g1_primary.json); the S10 figure
figures/main/fig_g1_learning_curves.pdf is kept unchanged.

    python figures/code/fig_g1_v2style.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import style_paper as sp

ROOT = sp.ROOT
KUMAGAI_RF_EV = 0.34      # Kumagai et al. 2021, q = 0, N = 700 (docs/baselines.md)
KIYOHARA_CGCNN_EV = 0.29  # Kiyohara et al. 2025, q = 0 (claims C0)


def main() -> Path:
    p = json.loads((ROOT / "results" / "g1_primary.json").read_text())["payload"]
    B = [int(b) for b in p["budgets"]]
    per, desc = p["per_budget"], p["descriptive_curves"]["mae"]

    def series(get):
        return ([get(b)["mean"] for b in B], [get(b)["ci"][0] for b in B], [get(b)["ci"][1] for b in B])

    fig, (ax1, ax2) = sp.figure("single", height_mm=72.0, ncols=2)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.93, bottom=0.37, wspace=0.30)
    sp.learning_curve_panel(
        ax1, B,
        {"B0": series(lambda b: desc["B0"][str(b)]),
         "RF-Kumagai": series(lambda b: desc["RF-Kumagai"][str(b)]),
         "S": series(lambda b: per[str(b)]["MAE_S"]),
         "D": series(lambda b: per[str(b)]["MAE_D"])},
        refs=((KUMAGAI_RF_EV, "Kumagai et al. RF, 0.34 eV", "published", sp.COLORS["RF-Kumagai"]),
              (KIYOHARA_CGCNN_EV, "Kiyohara et al. CGCNN, 0.29 eV", "published-alt", None)),
        ylim=(0.0, 1.3))
    sp.advantage_panel(ax2, B, *series(lambda b: per[str(b)]["A"]), delta=p["delta_eV"])
    sp.legend_below(fig, (ax1, ax2), ncol=3)
    sp.panel_letters(fig, (ax1, ax2))
    return sp.save(fig, ROOT / "figures" / "main" / "fig_g1_learning_curves_v2style")


if __name__ == "__main__":
    print(main())

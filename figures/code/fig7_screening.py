"""Figure 7 (M8): screening demonstration (C5) on named oxide crystals, both backbones.

Input: ``figures/main/data/screening_demo.json`` (written by figures/code/screening_data.py through
``write_result``; the sites and aggregation of results/screening_c5.json, per-resample spread added).

    (a) predicted against DFT neutral oxygen-vacancy formation energy, one marker per site, y = x dashed
    (b) predicted minus DFT for the same sites, grouped by oxide in ascending order of the oxide's mean DFT energy

Markers: oxide colour; primary backbone (v2) filled with solid bars, originally registered backbone (v1) open
with dashed bars. A bar spans the minimum to the maximum of the seed-ensemble predictions over the outer
resamples in which the host was held out; a site held out in one resample has no bar.

    python figures/code/fig7_screening.py [--record FILE] [--out-dir DIR]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inputs_paper as ip
import style_paper as sp

STEM = "fig7_screening"
RECORD = ip.ROOT / "figures" / "main" / "data" / "screening_demo.json"
OXIDE_COLORS = {"ZnO": "#E69F00", "SnO2": "#56B4E9", "Ga2O3": "#009E73", "TiO2": "#F0E442", "ZrO2": "#0072B2",
                "MgO": "#D55E00", "Al2O3": "#CC79A7"}
OXIDE_TEX = {"ZnO": "ZnO", "SnO2": r"SnO$_2$", "Ga2O3": r"Ga$_2$O$_3$", "TiO2": r"TiO$_2$", "ZrO2": r"ZrO$_2$",
             "MgO": "MgO", "Al2O3": r"Al$_2$O$_3$"}
DODGE = 0.025        # eV, horizontal offset between the two backbones in (a)
CAP = 1.6
MS = 4.2


def draw(ax, x, y, lo, hi, color: str, version: str) -> None:
    """One site of one backbone: marker with a min-max bar (none when the host was held out once)."""
    filled = sp.BACKBONE_FILLED[version]
    if hi > lo:
        _, caps, bars = ax.errorbar(x, y, yerr=[[y - lo], [hi - y]], fmt="none", ecolor=color, elinewidth=0.9,
                                    capsize=CAP, capthick=0.9, zorder=3)
        if not filled:
            for b in bars:
                b.set_linestyle(sp.BACKBONE_LS[version])
    ax.plot([x], [y], ls="none", marker="o", ms=MS, mfc=color if filled else "white", mec=color if filled else color,
            mew=0.9 if filled else 1.2, zorder=4)


def main() -> Path:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--record", type=Path, default=RECORD)
    ap.add_argument("--out-dir", type=Path, default=ip.ROOT / "figures" / "main")
    a = ap.parse_args()
    rec = json.loads(a.record.read_text())["payload"]
    sites, idx = rec["sites"], rec["site_index"]

    mean_dft = {c: np.mean([s["dft_eV"] for k, s in sites.items() if idx[k]["candidate"] == c]) for c in OXIDE_COLORS}
    order = sorted(sites, key=lambda k: (mean_dft[idx[k]["candidate"]], idx[k]["label"]))

    fig, (a1, a2) = sp.figure("single", height_mm=80.0, ncols=2, gridspec_kw={"width_ratios": [1.0, 1.1]})
    fig.subplots_adjust(left=0.085, right=0.99, top=0.93, bottom=0.36, wspace=0.30)

    # (a) predicted against DFT
    lims = (4.3, 8.0)
    a1.plot(lims, lims, color=sp.COLORS["reference"], lw=sp.REF_W, dashes=sp.REF_DASHES["published-alt"], zorder=1)
    for k in order:
        s, c = sites[k], OXIDE_COLORS[idx[k]["candidate"]]
        for v, dx in (("v2", -DODGE), ("v1", DODGE)):
            draw(a1, s["dft_eV"] + dx, s[v]["pred_eV"], s[v]["min_eV"], s[v]["max_eV"], c, v)
    a1.set_xlim(*lims)
    a1.set_ylim(*lims)
    a1.set_aspect("equal", adjustable="box")
    a1.set_xlabel(r"DFT $E_\mathrm{f}$ (eV)")
    a1.set_ylabel(r"Predicted $E_\mathrm{f}$ (eV)")

    # (b) signed error per site
    a2.axhline(0.0, color=sp.COLORS["reference"], lw=sp.REF_W, dashes=sp.REF_DASHES["zero"], zorder=1)
    for i, k in enumerate(order):
        s, c = sites[k], OXIDE_COLORS[idx[k]["candidate"]]
        for v, dx in (("v2", -0.11), ("v1", 0.11)):
            e = s[v]["signed_err_eV"]
            draw(a2, i + dx, e, e - (s[v]["pred_eV"] - s[v]["min_eV"]), e + (s[v]["max_eV"] - s[v]["pred_eV"]), c, v)
    a2.set_xlim(-0.6, len(order) - 0.4)
    a2.set_xticks(range(len(order)))
    a2.set_xticklabels([f"{OXIDE_TEX[idx[k]['candidate']]} O$_{idx[k]['label'][1:]}$" for k in order],
                       rotation=50, ha="right", rotation_mode="anchor")
    a2.tick_params(axis="x", length=2.5)
    a2.set_ylabel(r"Predicted $-$ DFT (eV)")
    lim = max(abs(s[v][b] - s["dft_eV"]) for s in sites.values() for v in ("v1", "v2") for b in ("min_eV", "max_eV"))
    a2.set_ylim(-1.08 * lim, 1.08 * lim)

    from matplotlib.lines import Line2D
    handles = [Line2D([], [], ls="none", marker="o", ms=MS, mfc=OXIDE_COLORS[c], mec=OXIDE_COLORS[c], label=OXIDE_TEX[c])
               for c in sorted(OXIDE_COLORS, key=mean_dft.get)]
    handles += [sp.backbone_handle(v, color="#4D4D4D") for v in sp.BACKBONES]
    sp.legend_handles(fig, handles, ncol=4)
    sp.panel_letters(fig, (a1, a2))
    pdf = sp.save(fig, Path(a.out_dir) / STEM)
    ip.write_caption(a.out_dir, STEM, caption())
    return pdf


def caption() -> str:
    return """
**Figure 7. Out-of-sample neutral oxygen-vacancy formation energies of named oxides, both backbones.** One marker
per oxygen site of the screening oxides present in universe v1 (ZnO, SnO$_2$, Ga$_2$O$_3$, TiO$_2$, ZrO$_2$, MgO and
Al$_2$O$_3$), for hosts that were held out in at least one outer resample; the model is S at the screening budget
`payload.budget`. (**a**) Predicted against DFT formation energy with the dashed line y = x; the two backbones of one
site are offset horizontally by a fixed small amount so that their bars do not overlap. (**b**) Predicted minus DFT
for the same sites, grouped by oxide in ascending order of the oxide's mean DFT energy; the dotted line is zero error.
Filled markers with solid bars: primary backbone (v2), adopted after diagnostics of the originally registered
backbone; open markers with dashed bars: originally registered backbone (v1). Colour identifies the oxide. A marker is
the mean over the outer resamples in which the host was held out of the seed-ensemble prediction (`mean_over_resamples_tested`,
as in `results/screening_c5.json`, keys `payload.sites[].S_eV` for v1 and `S_v2_eV` for v2, `dft_eV`); a bar runs from the
smallest to the largest of those per-resample predictions (`min_eV`, `max_eV`, counts in `n_resamples`), and a site held
out in one resample has no bar. Values for every marker: `figures/main/data/screening_demo.json`, keys
`payload.sites.<site>.{dft_eV, v2, v1}`, built by `figures/code/screening_data.py` from the S run records of `results/`
(v1) and `results/v2_sweep/` (v2); the screening MAE of each backbone with its host-cluster interval is in
`payload.summary.<v1|v2>.{mae_eV, mae_ci}` of that file. The candidate oxides absent from the release or removed by the
perturbed-host-state filter are listed in `results/screening_absence.json`, key `payload.candidates`. Structure render of
an SnO$_2$ site: Figure S8, `figures/si/structure_sno2_vacancy.png`. Script: `figures/code/fig7_screening.py`.
"""


if __name__ == "__main__":
    print(main())

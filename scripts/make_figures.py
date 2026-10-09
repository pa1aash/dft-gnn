"""Main-text learning-curve figures, generated from the result records only.

    python scripts/make_figures.py

Reads results/c1c2_v1.json, results/c1c2_v2.json (if present) and results/diagnostics_sweep.json (training-mean
predictor, B0 and RF-Kumagai per budget; the same outer test sites for every model). Writes vector PDFs at the
printed width to figures/main/ and prints a LaTeX snippet with each caption, whose numbers are read from the same
records. Style: scripts/paper.mplstyle (Computer Modern, 7.5-8.5 pt). Colours (Okabe-Ito) have one meaning
throughout: S blue, D vermilion, RF-Kumagai green, B0 black, training mean grey.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "main"
W = 6.5
COL = {"S": "#0072B2", "D": "#D55E00", "RF": "#009E73", "B0": "#000000", "mean": "#7F7F7F"}
ARM_STYLE = {"v1": {"ls": "-", "mfc": "full"}, "v2": {"ls": "--", "mfc": "white"}}
ARM_NAME = {"v1": "pre-registered", "v2": "v2"}
D_KEY = "D-state"


def load(name: str) -> dict | None:
    p = ROOT / "results" / f"{name}.json"
    return json.loads(p.read_text())["payload"] if p.exists() else None


def save(fig, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.pdf"
    fig.savefig(path, metadata={"CreationDate": None})
    plt.close(fig)
    return path


def panel_letter(ax, s: str) -> None:
    ax.text(-0.02, 1.02, f"({s})", transform=ax.transAxes, ha="right", va="bottom", fontweight="bold")


def _band(ax, x, mean, lo, hi, color, ls="-", marker="o", mfc=None, label=None, z=3):
    ax.fill_between(x, lo, hi, color=color, alpha=0.15, lw=0, zorder=z - 1)
    ax.plot(x, mean, ls=ls, marker=marker, color=color, mfc=color if mfc in (None, "full") else mfc, mew=0.9,
            label=label, zorder=z)


def _budget_axis(ax, budgets):
    ax.set_xscale("log")
    ax.set_xticks(budgets)
    ax.set_xticklabels([str(b) for b in budgets])
    ax.minorticks_off()
    ax.set_xlabel("Training hosts $B$")


def fig_learning_curves(arms: dict, refs: dict) -> tuple[Path, str]:
    budgets = sorted(int(b) for b in refs)
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.7), sharey=True, layout="constrained")
    for ax, (arm, res) in zip(axes, arms.items(), strict=False):
        for key, col, ls, mk, lab in (("mean", COL["mean"], ":", "", "training mean"),
                                       ("B0", COL["B0"], "--", "", "B0 (physics floor)"),
                                       ("RF-Kumagai", COL["RF"], "-", "s", "RF-Kumagai")):
            m = [refs[str(b)][key]["mean"] for b in budgets]
            lo = [refs[str(b)][key]["ci"][0] for b in budgets]
            hi = [refs[str(b)][key]["ci"][1] for b in budgets]
            _band(ax, budgets, m, lo, hi, col, ls=ls, marker=mk or "None", label=lab, z=2)
        bb = [int(b) for b in res["budgets"]]
        for model, key in (("S", "S"), ("D", D_KEY)):
            st = ARM_STYLE[arm]
            m = [res["mae"][str(b)][key]["mae"]["mean"] for b in bb]
            lo = [res["mae"][str(b)][key]["mae"]["ci"][0] for b in bb]
            hi = [res["mae"][str(b)][key]["mae"]["ci"][1] for b in bb]
            _band(ax, bb, m, lo, hi, COL[model], ls=st["ls"], marker="o" if model == "S" else "^", mfc=st["mfc"],
                  label=model, z=4)
        _budget_axis(ax, budgets)
        ax.set_title(f"{ARM_NAME[arm]} backbone")
    axes[0].set_ylabel("Site test MAE (eV)")
    axes[0].set_ylim(0.2, 1.35)
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="outside lower center", ncol=5)
    for ax, s in zip(axes, "ab", strict=False):
        panel_letter(ax, s)
    if len(arms) == 1:
        axes[1].set_visible(False)
    v1 = arms["v1"]
    cap = (r"\caption{Structure-only (S) and descriptor-augmented (D) graph networks against trivial and "
           r"descriptor baselines across training budgets. Site-level test MAE over ten formula-grouped "
           r"20\% host hold-outs, from the mean prediction of three seeds; bands are 95\% hierarchical "
           r"bootstrap intervals (resamples, then test hosts; 2000 draws). Training mean predicts every site "
           r"with the mean target of the training hosts; B0 is the linear fit on oxide stability and band gap; "
           rf"RF-Kumagai is the random forest on 70 DFT descriptors. At $B=654$, S reaches "
           rf"{v1['mae']['654']['S']['mae']['mean']:.3f}~eV and D {v1['mae']['654'][D_KEY]['mae']['mean']:.3f}~eV"
           + (r"; (b) repeats the networks with the v2 backbone." if "v2" in arms else ".") + "}")
    return save(fig, "fig2_learning_curves"), cap


def fig_advantage(arms: dict, delta: float) -> tuple[Path, str]:
    fig, ax = plt.subplots(figsize=(3.25, 2.4), layout="constrained")
    ax.axhline(0, color="0.6", lw=0.6, zorder=1)
    ax.axhline(delta, color="0.3", lw=0.8, ls="--", zorder=1)
    handles = [Line2D([], [], color="0.3", ls="--", lw=0.8, label=rf"margin $\delta={delta:g}$ eV")]
    for i, (arm, res) in enumerate(arms.items()):
        bb = [int(b) for b in res["budgets"]]
        off = 1 + 0.06 * (i - (len(arms) - 1) / 2)          # small horizontal dodge on the log axis
        x = [b * off for b in bb]
        a = [res["A_mae"][str(b)]["A"] for b in bb]
        lo = [res["A_mae"][str(b)]["ci95"][0] for b in bb]
        hi = [res["A_mae"][str(b)]["ci95"][1] for b in bb]
        ub = [res["A_mae"][str(b)]["upper_one_sided_95"] for b in bb]
        st = ARM_STYLE[arm]
        ax.errorbar(x, a, yerr=[[ai - li for ai, li in zip(a, lo, strict=True)],
                                [hi_ - ai for ai, hi_ in zip(a, hi, strict=True)]],
                    fmt="o", ls=st["ls"], color="0.15", mfc="0.15" if st["mfc"] == "full" else "white", lw=0.9,
                    zorder=3)
        ax.plot(x, ub, ls="None", marker="_", ms=7, mew=1.2, color="0.15", zorder=4)
        handles.append(Line2D([], [], color="0.15", ls=st["ls"], marker="o",
                              mfc="0.15" if st["mfc"] == "full" else "white", label=f"{ARM_NAME[arm]} backbone"))
    handles.append(Line2D([], [], color="0.15", ls="None", marker="_", ms=7, mew=1.2, label="one-sided 95% bound"))
    _budget_axis(ax, [int(b) for b in arms["v1"]["budgets"]])
    ax.set_ylabel(r"Advantage $A$ (eV)")
    ax.legend(handles=handles, loc="upper right")
    v1 = arms["v1"]
    ns = v1["N_star"]
    cap = (r"\caption{The advantage of explicit DFT descriptors over structure alone falls below the margin "
           rf"only at the largest budget. Points are the advantage $A=\mathrm{MAE}_S-\mathrm{MAE}_D$ (positive when the "
           r"descriptors help) with two-sided 95\% intervals (paired hierarchical "
           r"bootstrap, 2000 draws); bars mark the one-sided 95\% upper bound used for $N^*$; the dashed line is "
           rf"$\delta$. Pre-registered backbone: $N^*$ {ns['label']} ({ns['N_star']} hosts); at $B=654$, "
           rf"$A={v1['C2']['A']:+.3f}$~eV [{v1['C2']['ci95'][0]:+.3f}, {v1['C2']['ci95'][1]:+.3f}].}}")
    return save(fig, "fig3_advantage"), cap


def fig_within_host(arms: dict) -> tuple[Path, str]:
    fig, ax = plt.subplots(figsize=(3.25, 2.4), layout="constrained")
    ax.axhline(0, color="0.5", lw=0.7, ls=":", zorder=1)
    handles = [Line2D([], [], color="0.5", ls=":", label="no within-host skill")]
    for arm, res in arms.items():
        bb = [int(b) for b in res["budgets"]]
        st = ARM_STYLE[arm]
        for model, key, mk in (("S", "S", "o"), ("D", D_KEY, "^")):
            sk = [res["mae"][str(b)][key]["within_host_skill"] for b in bb]
            _band(ax, bb, [v["mean"] for v in sk], [v["ci"][0] for v in sk], [v["ci"][1] for v in sk], COL[model],
                  ls=st["ls"], marker=mk, mfc=st["mfc"])
            handles.append(Line2D([], [], color=COL[model], ls=st["ls"], marker=mk,
                                  mfc=COL[model] if st["mfc"] == "full" else "white",
                                  label=f"{model}, {ARM_NAME[arm]}"))
    _budget_axis(ax, [int(b) for b in arms["v1"]["budgets"]])
    ax.set_ylabel("Within-host skill (eV)")
    ax.legend(handles=handles, loc="upper left")
    s654 = arms["v1"]["mae"]["654"]["S"]["within_host_skill"]
    cap = (r"\caption{Below 400 training hosts the pre-registered networks do not distinguish the oxygen sites "
           r"of a host. Within-host skill is the within-host residual MAE of a predictor that is constant within "
           r"each host minus the model's, on the same test hosts, so 0 (dotted) means the model ranks hosts but "
           r"not sites. Bands are 95\% paired hierarchical bootstrap intervals (2000 draws). Pre-registered S "
           rf"reaches {s654['mean']:.3f}~eV [{s654['ci'][0]:.3f}, {s654['ci'][1]:.3f}] at $B=654$.}}")
    return save(fig, "fig_within_host"), cap


def main() -> None:
    plt.style.use(str(ROOT / "scripts" / "paper.mplstyle"))
    arms = {a: r for a in ("v1", "v2") if (r := load(f"c1c2_{a}")) is not None and r.get("budgets")}
    diag = load("diagnostics_sweep")
    refs = diag["references"]
    for path, cap in (fig_learning_curves(arms, refs), fig_advantage(arms, arms["v1"]["delta_eV"]),
                      fig_within_host(arms)):
        print(path.relative_to(ROOT))
        print(cap, "\n")


if __name__ == "__main__":
    main()

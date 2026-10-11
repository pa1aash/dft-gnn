"""One figure style for the whole paper (M3). Wraps ``dftgnn.viz.style`` (S10) without editing it.

Conventions, fixed for every plot in the paper:

* widths: MDPI text width 138.6 mm (``single``) and full page width 184.6 mm (``full``), from the class
  geometry recorded in docs/venue.md; heights are free;
* one sans-serif family (Arial) for text and mathtext, embedded as TrueType (Type 42) in a vector PDF;
* one fixed colour per model (Okabe-Ito hues): B0 grey, RF-Kumagai orange, S blue, D bluish green,
  P reddish purple; the advantage A in black; published reference values in dark grey;
* dataset version by line style: universe v1 solid with filled markers, v2 dashed with open markers;
* one marker shape, line width and band alpha for every curve; bands are two-sided 95% intervals;
* no in-plot text other than axis labels, tick labels and panel letters; the legend sits outside the data
  area (below the panels); numbers, sample sizes and definitions go in the caption file.

Check every output with ``figures/code/qa_figure.py``.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
from dftgnn.viz import style as base

MM = base.MM
WIDTHS_MM = {"single": 138.6, "full": 184.6}   # docs/venue.md (mdpi.cls geometry)
WIDTHS_IN = {k: v * MM for k, v in WIDTHS_MM.items()}
BUDGETS = base.BUDGETS

FONT = "Arial"
COLORS = {
    "B0": base.COLORS["B0"],                  # grey      #7F7F7F
    "RF-Kumagai": base.COLORS["RF-Kumagai"],  # orange    #E69F00
    "S": base.COLORS["S"],                    # blue      #0072B2
    "D": base.COLORS["D"],                    # green     #009E73
    "P": "#CC79A7",                           # Okabe-Ito reddish purple
    "A": base.COLORS["A"],                    # black
    "reference": base.COLORS["reference"],    # dark grey
}
LABELS = {**base.LABELS, "P": "P (staged: predicted descriptors into D)", "A": r"$A$ = MAE$_S$ $-$ MAE$_D$"}
VERSION_LS = {"v1": "-", "v2": (0, (4.0, 2.0))}
VERSION_FILLED = {"v1": True, "v2": False}

LINE_W = base.LINE_W          # 1.2 pt model curves
REF_W = base.REF_W            # 0.7 pt reference lines
BAND_ALPHA = base.BAND_ALPHA  # 0.22
MARKER = "o"
MARKER_SIZE = 3.0
PARITY_SIZE = 4.0             # scatter area (pt^2)
PARITY_ALPHA = 0.45
REF_DASHES = {"delta": (4, 2), "zero": (1, 2), "published": (4, 2), "published-alt": (1.5, 1.5)}


def apply() -> None:
    """S10 rcParams plus a single Arial family for text and mathtext, TrueType embedding, exact widths."""
    base.apply()
    mpl.rcParams.update({
        "font.sans-serif": [FONT],
        "mathtext.fontset": "custom",
        "mathtext.rm": FONT, "mathtext.it": f"{FONT}:italic", "mathtext.bf": f"{FONT}:bold",
        "mathtext.sf": FONT, "mathtext.cal": FONT, "mathtext.fallback": None,
        "axes.unicode_minus": True,
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "savefig.bbox": None, "savefig.transparent": False,
        "legend.handlelength": 2.6, "legend.columnspacing": 1.2,
    })


def figure(width: str = "single", height_mm: float = 70.0, ncols: int = 1, nrows: int = 1, **kw):
    """A figure at an MDPI width; returns (fig, axes)."""
    apply()
    fig, axes = plt.subplots(nrows, ncols, figsize=(WIDTHS_IN[width], height_mm * MM), **kw)
    return fig, axes


def _line_kw(key: str, version: str) -> dict:
    c = COLORS[key]
    return {"color": c, "lw": LINE_W, "ls": VERSION_LS[version], "marker": MARKER, "ms": MARKER_SIZE,
            "mfc": c if VERSION_FILLED[version] else "white", "mec": c, "mew": 0.8}


def band_curve(ax, x, mean, lo, hi, key: str, version: str = "v1", label: str | None = None) -> None:
    """A model curve with its two-sided 95% band."""
    ax.fill_between(x, lo, hi, color=COLORS[key], alpha=BAND_ALPHA, linewidth=0)
    if label is None:
        label = LABELS.get(key, key) + ("" if version == "v1" else f", {version}")
    ax.plot(x, mean, label=label, **_line_kw(key, version))


def reference_line(ax, y: float, label: str, kind: str = "published", color: str | None = None) -> None:
    ax.axhline(y, color=color or COLORS["reference"], lw=REF_W, dashes=REF_DASHES[kind], label=label)


def learning_curve_panel(ax, x, series: dict, version: str = "v1", refs=(), ylim=None,
                         ylabel: str = "Test MAE (eV)") -> None:
    """Test error against training hosts. ``series`` maps model key -> (mean, lo, hi);
    ``refs`` is a sequence of (y, label, kind, colour-or-None)."""
    for key, (m, lo, hi) in series.items():
        band_curve(ax, x, m, lo, hi, key, version)
    for y, label, kind, colour in refs:
        reference_line(ax, y, label, kind, colour)
    base.budget_axis(ax)
    ax.set_ylabel(ylabel)
    if ylim is not None:
        ax.set_ylim(*ylim)


def advantage_panel(ax, x, mean, lo, hi, delta: float, version: str = "v1", key: str = "A",
                    label: str | None = None, ylabel: str = r"$A$ (eV)") -> None:
    """A = MAE_S - MAE_D (or another paired difference) with its band, the margin delta and zero."""
    band_curve(ax, x, mean, lo, hi, key, version, label=label or LABELS[key])
    reference_line(ax, delta, rf"$\delta$ = {delta:g} eV", "delta")
    reference_line(ax, 0.0, "zero", "zero")
    base.budget_axis(ax)
    ax.set_ylabel(ylabel)


def parity_panel(ax, y_true, y_pred, key: str, lims=None, label: str | None = None,
                 xlabel: str = r"DFT $E_\mathrm{f}$ (eV)", ylabel: str = r"Predicted $E_\mathrm{f}$ (eV)") -> None:
    """Predicted against DFT values with the y = x line; square, shared limits, no in-plot statistics."""
    import numpy as np

    yt, yp = np.asarray(y_true, float), np.asarray(y_pred, float)
    if lims is None:
        lo, hi = float(min(yt.min(), yp.min())), float(max(yt.max(), yp.max()))
        pad = 0.04 * (hi - lo)
        lims = (lo - pad, hi + pad)
    ax.plot(lims, lims, color=COLORS["reference"], lw=REF_W, dashes=REF_DASHES["published-alt"], label="y = x")
    ax.scatter(yt, yp, s=PARITY_SIZE, color=COLORS[key], alpha=PARITY_ALPHA, linewidths=0,
               label=label or LABELS.get(key, key))
    ax.set_xlim(*lims)
    ax.set_ylim(*lims)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)


def legend_below(fig, axes, ncol: int = 3, y: float = 0.0) -> None:
    """One figure legend below the panels (outside every data area), de-duplicated by label."""
    seen, hs, ls = set(), [], []
    for ax in (axes if hasattr(axes, "__iter__") else [axes]):
        for h, lab in zip(*ax.get_legend_handles_labels()):
            if lab not in seen:
                seen.add(lab)
                hs.append(h)
                ls.append(lab)
    fig.legend(hs, ls, loc="lower center", ncol=ncol, bbox_to_anchor=(0.5, y))


def panel_letters(fig, axes, letters: str = "abcdefgh") -> None:
    for ax, letter in zip(axes, letters):
        base.panel_letter(fig, ax, letter)


def save(fig, stem, png: bool = False) -> Path:
    """Vector PDF (and optionally a 300 dpi PNG preview); returns the PDF path."""
    stem = Path(stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    pdf = stem.with_suffix(".pdf")
    fig.savefig(pdf)
    if png:
        fig.savefig(stem.with_suffix(".png"), dpi=300)
    plt.close(fig)
    return pdf

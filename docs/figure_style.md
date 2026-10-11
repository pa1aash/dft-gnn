# Figure style and QA (M3)

One visual language for every figure of the paper. Plot code imports `figures/code/style_paper.py`
(which wraps `src/dftgnn/viz/style.py` without changing it); structure renders go through
`blender/render_host.py` (see `blender/README.md`).

## Plots

| Item | Convention |
|---|---|
| Width | 138.6 mm (`single`, MDPI text width) or 184.6 mm (`full`), from the mdpi.cls geometry in `docs/venue.md`. Height free. |
| Format | Vector PDF, fonts embedded as TrueType (Type 42), no creation date (byte-stable reruns). |
| Font | Arial for all text, including mathtext (no DejaVu or Computer Modern fallback). 8 pt labels, 7 pt ticks and legend, 9 pt bold panel letters. |
| Model colours | B0 grey `#7F7F7F`, RF-Kumagai orange `#E69F00`, S blue `#0072B2`, D bluish green `#009E73`, P reddish purple `#CC79A7` (Okabe-Ito); advantage A black; published reference lines dark grey `#4D4D4D`. |
| Dataset version | universe v1 solid line, filled markers; v2 dashed (4, 2), open markers. |
| Marks | circles 3 pt, model lines 1.2 pt, reference lines 0.7 pt (published: dashes (4, 2) or (1.5, 1.5); margin delta: (4, 2); zero: dotted (1, 2)); bands are two-sided 95% intervals at alpha 0.22; parity points 4 pt^2 at alpha 0.45. |
| Axes | Learning curves: log x axis in training hosts, ticks at 25, 50, 100, 200, 400, 654. Parity: square, shared limits, y = x line. Top and right spines off. |
| Text | Only axis labels, tick labels, panel letters (a), (b) outside the top-left corner, and one legend below the panels. Numbers, n, definitions and statistics go in `<figure>.caption.md`. |

Helpers: `figure`, `learning_curve_panel`, `advantage_panel`, `parity_panel`, `band_curve`,
`reference_line`, `legend_below`, `panel_letters`, `save`.

## QA

`python figures/code/qa_figure.py <pdf> [...]` checks, on page 1: no raster images; every font embedded;
one font family; width 138.6 or 184.6 mm (+/- 0.5 mm; or `--width-mm`); and no text whose box centre lies
inside an axes (axes found from the clip rectangles matplotlib writes for data artists). Exit status 0 only if
all checks pass.

Status of the figures in `figures/main/` on 2026-10-11:

| Figure | Result |
|---|---|
| `fig_g1_learning_curves_v2style.pdf` | PASS |
| `fig_g1_learning_curves.pdf` (S10) | FAIL one_family (Arial + DejaVu Sans from mathtext); all else passes |
| `fig2_learning_curves.pdf`, `fig3_advantage.pdf` | FAIL one_family (Computer Modern), width (164.0 / 81.5 mm) |
| `fig_within_host.pdf` | FAIL one_family, width (81.5 mm), no_text_in_axes (legend inside the data area) |

The older figures are kept as they are; they should be regenerated through `style_paper.py` before submission.

## Structure renders

Cycles PNG at 300 dpi at the MDPI text width (1637 px for 138.6 mm), at most 128 samples, white background,
RGB. Element colours, vacancy marker and camera conventions: `blender/README.md`.

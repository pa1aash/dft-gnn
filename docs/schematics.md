# Schematics (M4)

TikZ sources for the method figures, in `schematics/`. Each `fig_*.tex` is a standalone LaTeX file that
compiles on its own to a vector PDF (pdfLaTeX, fonts embedded and subset) and inputs the shared preamble
`schematics/common.tex`. Captions live beside each source as `fig_<name>.caption.md`; the figures carry no
explanatory text, only model, stage and quantity names and panel letters.

| File | Placement | Content | Size (mm) |
|---|---|---|---|
| `fig_pipeline.tex` | Figure 1 | Supercell, 5.0 Å radius graph and MEGNet backbone; S, D, P side by side with RF and B0 | 137.5 x 81.5 |
| `fig_readout.tex` | Figure S1 (Figure 2 when written; SI since M3b) | Readout [h_v ‖ pooled h ‖ u] to MLP to E_f for S; D-state injection points | 133.4 x 53.9 |
| `fig_cascade.tex` | Figure S2 (S1 when written) | Filter cascade, step names only (counts stay in Table 1) | 137.4 x 22.2 |
| `fig_splits.tex` | Figure S3 (S2 when written) | Grouped hold-out with nested budgets, Kiyohara split, K-fold CV, leave-one-chemistry-out | 136.3 x 65.2 |

All four fit the MDPI text width of 138.6 mm (`docs/venue.md` B1), so they are placed at natural size;
the figure font is 8 pt TeX Gyre Heros (Helvetica metrics, as the matplotlib figures use Arial/Helvetica),
with `sansmath` for symbols. Placement is the final numbering (F1c, `docs/figure_numbering.md`); the caption files of
record here keep the numbers they were written with, and the SI caption files in `figures/si/` carry the final
ones.

## Palette

`common.tex` defines the model colours as the hex values of `src/dftgnn/viz/style.py` (Okabe-Ito hues),
extended with two entries that style.py does not yet have:

| Name | Model | Hex |
|---|---|---|
| `cB0` | B0 physics floor | 7F7F7F |
| `cRF` | RF-Kumagai | E69F00 |
| `cS` | S | 0072B2 |
| `cD` | D | 009E73 |
| `cP` | P and P1 (new) | CC79A7 |
| `cO` | flagged vacancy O site (new, not a model) | D55E00 |

v2 is not a colour: a v2 model is drawn as a dashed outline (`v2=<colour>` style) in its model's colour.
If the results figures later show P or v2, `style.py` should take the same values (CC79A7; dashed lines).

## Build

```sh
cd schematics
latexmk -r latexmkrc                 # builds all four PDFs
sh render.sh fig_pipeline            # one figure + 200 dpi PNG preview in .cache/schematics/ (untracked)
```

`latexmkrc` fixes `SOURCE_DATE_EPOCH` (2026-10-11) so rebuilds are byte-identical. Requires `standalone`,
`tgheros`, `sansmath` and PGF/TikZ. The PDFs are tracked; the aux files and PNG previews are not.

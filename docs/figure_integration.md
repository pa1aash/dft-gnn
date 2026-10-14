# Figure integration for the manuscript (M3b)

Edits that `paper/` needs to pick up the M3b figures. M3b did not touch `paper/`; a later paper session
applies these. Line numbers refer to `paper/sections/methods.tex` and `paper/sections/results.tex` at
`origin/main` `9e91760`.

## 1. Figure 1 (`fig:schematic`, methods.tex lines 18-31)

`figures/main/fig1_overview.pdf` is the finished two-panel composite, 138.6 mm wide (the text width), with the
panel letters (a) and (b) inside it and the same stacked layout as the current block: (a) the pipeline
schematic at the full width, (b) the ZnO render centred at 0.45 of the width below it, 2 pt between letter and
panel, 6 pt between the rows. It replaces the two minipages.

Replace lines 20-29:

```latex
\begin{minipage}{\linewidth}
\centering
\textbf{(a)}\\[2pt]
\IfFileExists{../schematics/fig_pipeline.pdf}{\includegraphics[width=\linewidth]{../schematics/fig_pipeline.pdf}}{\figph{fig_pipeline}}
\end{minipage}\\[6pt]
\begin{minipage}{0.45\linewidth}
\centering
\textbf{(b)}\\[2pt]
\IfFileExists{\figpath/main/fig1_zno_vacancy.png}{\includegraphics[width=\linewidth]{fig1_zno_vacancy.png}}{\figph{fig1_zno_vacancy}}
\end{minipage}
```

with the single line

```latex
\figph{fig1_overview}
```

Keep line 19 (`\centering`), the caption (line 30) and `\label{fig:schematic}` unchanged. The references
`Figure~\ref{fig:schematic}b` (line 14) stay valid. The caption's sentence "A dashed outline marks the v2 form
of a backbone" describes the schematic as drawn; see section 5.

## 2. Readout schematic to the SI

The readout schematic (`schematics/fig_readout.pdf`, the former main-text Figure 2 in `docs/schematics.md`) is
not included anywhere in `paper/` at `9e91760`. Its role moves to the SI: `figures/si/fig_readout.pdf` (the
same vector PDF centred on a 138.6 mm page) with `figures/si/fig_readout.caption.md` (Figure S1 in the final numbering of F1c;
it was S3 until then, with the filter cascade and the split schematic as S1 and S2). When the SI document exists, include it
with `\figph{fig_readout}`; `\graphicspath` already lists `figures/si/`. Since F1b, the cascade and splits (final numbers S2 and S3) also exist as
`figures/si/fig_cascade.pdf` and `figures/si/fig_splits.pdf` (the schematics centred on a 138.6 mm page, caption
files beside them; `figures/code/fig_si_schematics.py`), included with `\figph{fig_cascade}` and
`\figph{fig_splits}`. The final placement of every figure is in `docs/figure_inventory.md`. Methods text that describes the readout
(Section `sec:backbones`) may cite it as Figure S1.

## 3. Results figures (results.tex)

The rebuilt figures keep their stems, so the existing `\figph` lines pick them up unchanged, except for the
width of Figure 3:

| line | now | change to | why |
|---|---|---|---|
| 11 | `\figph{fig2_learning_curves}` | unchanged | `figures/main/fig2_learning_curves.pdf` is 138.6 mm wide |
| 17 | `\figph[0.6\linewidth]{fig3_advantage}` | `\figph{fig3_advantage}` | Figure 3 is now two panels at 138.6 mm; at 0.6 the 7 pt ticks would print at 4.2 pt |

Both caption stubs can be filled from `figures/main/fig2_learning_curves.caption.md` and
`figures/main/fig3_advantage.caption.md`, which name the record and key of every plotted value. In LaTeX, the
numbers come from the generated macros of those keys, not from the caption files.

Not yet referenced in `paper/` when this section was written: the G1 and within-host figures. Their placement
is settled in F1c (section 7): within-host is Figure 6, G1 is unnumbered.

## 4. Backbone wording in captions

Every figure caption file uses "primary backbone (v2)" (solid lines, filled markers, filled bands) and
"originally registered backbone (v1)" (dashed lines, open markers, hatched bands), and describes v2 as
adopted after diagnostics of v1. None calls v2 pre-registered. Paper captions should keep that wording.

## 5. Open conflicts for the paper session

- `schematics/fig_pipeline.pdf` marks the v2 form of a backbone with a dashed outline. Under the author
  decision of 2026-10-11, v2 is drawn solid and v1 dashed in every figure. The schematic (source
  `schematics/fig_pipeline.tex`, outside the M3b scope) needs the convention swapped, or its caption must say
  that the dashed outline there is the v2 variant, contrary to the results figures. Figure 1 is rebuilt with
  `python figures/code/fig1_overview.py` after any schematic change.
- results.tex line 8 quotes N*, the error at 654 hosts and the ceiling from `results/g1_primary.json` (the
  originally registered backbone) without saying so, while methods.tex makes v2 primary. The v2 values are in
  `results/c1c2_v2.json`.

## 6. F2: extension series in the results figures (2026-10-14)

- `figures/main/fig3_advantage.pdf` is now the extended Figure 3: the registered budgets with bands, the
  precision-refined points at the two largest outer-resample budgets and the grouped K-fold CV points beyond them,
  with the one-sided upper bounds of every point in panel (b). It is built by `figures/code/fig3_advantage.py`,
  which now follows the logic of `figures/code/fig_extended_budget.py` but keeps the extension records optional.
  The stem, width (138.6 mm, two panels) and `\figph{fig3_advantage}` line of section 3 are unchanged.
- `figures/main/fig3_advantage_extended.pdf` and its caption file were removed from `figures/main` once the new
  Figure 3 was checked against it (same records, same points; only the CV marker and one legend entry differ).
  `figures/code/fig_extended_budget.py` is kept; rerunning it writes `fig3_advantage_extended.pdf` back into
  `figures/main`, so pass `--out-dir` to a scratch directory if it is needed for comparison.
- Figure 2, G1 and the within-host figure draw the same extension points. Marker shape and legend alone separate
  the series: circles on lines, registered outer resamples; diamonds, precision (EXTENSION); triangles, K-fold CV
  (EXTENSION). CV moved from squares to triangles because the baselines use squares.
- The caption files now contain no typed numbers (records, keys and figure identifiers only), state that the CV
  test sets differ from the registered ones, and label each series as registered design or EXTENSION; v2 is never
  called pre-registered. The paper's caption text should take its numbers from the macros of those keys.
- Heights changed (Figure 2 84 mm, G1 94 mm, within-host 82 mm, Figure 3 72 mm); widths unchanged, so no
  `\figph` width needs editing.

## 7. F1c: final numbering (2026-10-14)

The final numbers are in `docs/figure_numbering.md` (old file names to numbers) and `docs/figure_inventory.md`.
For the paper session:

- Main text: Figure 1 overview, 2 learning curves, 3 advantage, 4 staging, 5 geometry, 6 within-host, 7
  screening. Figure 6 is new in the text: `\figph{fig6_within_host}` (138.6 mm, no width argument), caption
  from `figures/main/fig6_within_host.caption.md`. `figures/main/fig_within_host.pdf` is a copy under the old
  name, kept only because files outside the figure scope name it; do not include it. At `origin/main`
  `bdbc8bd`, `paper/sections/results.tex` line 47 still includes `\figph{fig6_probe}` as the main-text Figure
  6; under this numbering that slot is the within-host figure and the probe goes to the SI as Figure S7.
- SI: S1 readout (`\figph{fig_readout}`), S2 cascade (`\figph{fig_cascade}`), S3 splits (`\figph{fig_splits}`),
  S4 within-host groups (`fig_si_withinhost_groups`), S5 GPU class (`fig_si_gpu_class`), S6 sensitivities
  (`fig_si_sensitivities`), S7 latent probe (`fig6_probe`), S8 SnO2 render (`structure_sno2_vacancy.png`). The
  Methods reference to the readout becomes Figure S1 (section 2); the Figure 7 caption cites the render as S8.
- `figures/si/fig_g1_learning_curves.pdf` is kept but not cited and not numbered.
- Extension points of v1 in Figures 2, 3 and 6 (and G1) now have dashed interval bars; the caption files say so
  in the shared extension sentence. Sizes are unchanged, so no `\figph` width changes.

## 8. W1: applied in `paper/sections/results.tex` (2026-10-14)

- Figure 3 is included as `\figph{fig3_advantage}` at the text width (the section 3 edit; the 0.6 width is gone).
- The probe is no longer a main-text figure: `\figph{fig6_probe}` and the label `fig:probe` were removed from
  Results, and the text cites it as Supplementary Figure S7. Figure 6 is `\figph{fig6_within_host}` with label
  `fig:within_host`.
- LaTeX numbers floats in order of appearance, and the Results order puts site resolution (Section 3.4) before
  staging (3.5) and geometry (3.6). To keep the final numbers (4 staging, 5 geometry, 6 within-host), the
  within-host figure environment sits after the geometry figure, at the end of Section 3.6; Section 3.4 refers to
  it by label. Whoever reorders the Results subsections must check the float order again.
- Every caption was rebuilt from its `*.caption.md` in the register of `docs/prose_style.md`, without typed
  numbers; the screening caption moved with its subsection to `paper/sections/results_screening.tex`.
- Supplementary figures are cited in the text as "Supplementary Figure S4" to "S8" (no SI LaTeX document exists
  yet, so these are plain text, not references).


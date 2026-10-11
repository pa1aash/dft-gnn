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
same vector PDF centred on a 138.6 mm page) with `figures/si/fig_readout.caption.md` (Figure S3; S1 and S2 are
the filter cascade and the split schematic in `docs/schematics.md`). When the SI document exists, include it
with `\figph{fig_readout}`; `\graphicspath` already lists `figures/si/`. Methods text that describes the readout
(Section `sec:backbones`) may cite it as Figure S3.

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

Not yet referenced in `paper/`: `figures/main/fig_g1_learning_curves.pdf` (G1, ANALYSIS_PLAN section 14; a
candidate for the SI, since Figures 2 and 3 cover the same estimates) and `figures/main/fig_within_host.pdf`
(within-host skill and A_within). Each has a caption file beside it.

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

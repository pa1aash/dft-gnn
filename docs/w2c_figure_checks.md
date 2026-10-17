# Figure checks after the wording and caption fixes (W2c)

Session W2c, 2026-10-17. Follows `docs/w2b_figure_checks.md`: it fixes the open items of W2b that lie in
`figures/`, `schematics/` and `docs/`, and repeats the figure checks. No number was computed; every figure was
redrawn from the same records, read-only.

## Changes

| Item | Change | Files |
|---|---|---|
| Figure A1 label | the last box of the cascade reads "final 818-host dataset" (three lines, so the schematic stays within the 138.6 mm text width: 137.4 mm, as before) instead of "final universe v1"; 818 is the host count after D3 in `results/filter_cascade.json` | `schematics/fig_cascade.tex` |
| Figure C1 label | panel (d) reads "leave one family out" instead of "leave-one-chemistry-out" | `schematics/fig_splits.tex` |
| Rebuild | `schematics/render.sh` for both schematics, then `figures/code/fig_si_schematics.py` (places them in `figures/si/fig_cascade.pdf` and `fig_splits.pdf`), then `figures/code/figure_moves.py` (the copies `figureA1_cascade.pdf` and `figureC1_splits.pdf`, byte-identical to their sources) | PDFs in `schematics/` and `figures/si/` |
| Figure 2 (b) | already started at 100 training hosts (W2b). Its y-limits span ±δ, every two-sided interval and every one-sided bound (limits −0.067 to 0.184 eV against data from −0.050 to 0.167 eV), so nothing in (b) is clipped. The PDF is unchanged | none |
| Figure 2 caption | one clause gives the reason (b) starts at one hundred hosts: at twenty-five and fifty hosts a handful of test sites whose conduction-band f-character descriptor lies far outside the training range dominate D (`docs/w2_diagnostics.md`, (a)). The caption now also says that the bands of (a) are clipped: the D band reaches 1.83 eV at 25 hosts and 2.74 eV at 50 hosts, above the axis | `figures/code/figure2_descriptor_advantage.py`, `figures/main/figure2_descriptor_advantage.caption.md` |
| Figure H1 caption | says that panel (c) names each descriptor by its release name, as in the descriptor table of Appendix A, instead of renaming the tick labels | `figures/code/figureH1_probe.py`, `figures/si/figureH1_probe.caption.md` |
| Sources in appendix captions | checked against `docs/figure_numbering.md`: A1 (`results/filter_cascade.json`, Table A1), E1 (`results/within_host_breakdown.json`), H1 (`results/probe_descriptive.json`) and I1 (`figures/si/figureI1_sno2_vacancy.render.json`) name the right record. B1 and C1 name none. There is no Figure A2 (`docs/figure_numbering.md`) | `docs/figure_numbering.md` (source column now names the TikZ source and the placing script) |

## PDF text of the schematics

`pdftotext` of every PDF in `figures/main/` and `figures/si/` (former and new stems): no file contains
"universe v1", "leave-one-chemistry-out" or "leave one chemistry out". Figure A1 reads `release neutral entries,
ML subset, D1, D2, D3, excluded (x4), final 818-host dataset`; Figure C1 (d) reads `leave one family out`.

## qa_figure.py

`python figures/code/qa_figure.py figures/main/figure*.pdf figures/si/figure*.pdf`: 6 PASS (Figures 2 to 5, E1,
H1) and 4 documented exceptions with no axes (Figure 1, a schematic and a raster render, and the schematics A1, B1
and C1), as in W2b. Figure A1 is now 138.6 x 22.6 mm (22.2 mm before, one more text line in the last box).

## Text layer

`pdftotext -layout` of every new matplotlib PDF holds only panel letters, axis labels, tick labels and the legend
entries outside the axes, as in W2b. The schematics are diagrams whose labels are their content.

## Captions

`scripts/check_captions.py` rules applied to the 11 caption files, with "(**b**)" converted to `\textbf{b}` so a
panel letter after a full stop starts a sentence: all 11 pass.

| Caption | Sentences | Words |
|---|---|---|
| Figure 1 | 3 | 69 |
| Figure 2 | 3 | 70 |
| Figure 3 | 3 | 69 |
| Figure 4 | 3 | 70 |
| Figure 5 | 3 | 70 |
| Figure A1 | 2 | 67 |
| Figure B1 | 2 | 68 |
| Figure C1 | 2 | 64 |
| Figure E1 | 2 | 65 |
| Figure H1 | 2 | 68 |
| Figure I1 | 2 | 54 |

`python scripts/check_captions.py` (the printed captions in `paper/`, unchanged): 15 captions, 0 failures.

## Vocabulary

The registration vocabulary of `docs/prose_style.md` (rule 2) does not occur in any new caption file; `v2` occurs
only inside record paths, which the rule allows.

## Reproducibility

Rebuilding both schematics, `fig_si_schematics.py`, `figure_moves.py`, `figure2_descriptor_advantage.py` and
`figureH1_probe.py` a second time leaves every PDF byte-identical.

## Gates

- `git diff --stat nrp-code-v3 -- src scripts configs splits specs`: only `scripts/check_captions.py` (+190).
- `git diff --stat results-v1 -- results`: only added files, 3 under `results/derived_c1/` and 5 under
  `results/derived_w2/`.

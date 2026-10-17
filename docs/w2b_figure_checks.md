# Figure checks for the one-network figure set (W2b)

Session W2b, 2026-10-17. Checks run on the figures listed in `docs/figure_numbering.md`. Every new figure was built
from existing records, read-only; nothing was computed beyond plotting.

## House rules applied

- One network, one line style: every network series is a solid line with filled markers and a filled band
  (`figures/code/network_style.py`, on top of `figures/code/style_paper.py`). Designs differ only by marker shape:
  circles on a line for the learning-curve design, diamonds for the pooled 30 resamples x 5 seeds, triangles for
  grouped cross-validation. One-sided upper bounds are short black bars.
- One palette (S blue, D green, P reddish purple, RF-Kumagai orange, B0 grey, paired differences black, P - S
  vermillion) and one type size (8 pt labels, 7 pt ticks and legend, 9 pt bold panel letters) across the
  matplotlib figures; the schematics keep their 8 pt TeX Gyre Heros.
- No text inside any axes: panel letters, axis labels, ticks and one legend below the panels. Numbers, sample
  sizes and definitions are in the caption files and the records.
- Panel (b) of Figure 2 starts at 100 training hosts: A at 25 and 50 hosts (-0.14 and -0.51 eV, intervals up to
  2 eV wide) would flatten the tolerance band. Both values stay in the record and enter panel (a) as the two MAE
  curves.
- Bands wider than the axes are clipped (D and D - P at 25 and 50 hosts in Figure 4; the shuffled-label control of
  the host class at 100 hosts in Figure H1, whose mean is still inside the axes). The captions say so where it
  applies.

## qa_figure.py

`python figures/code/qa_figure.py figures/main/figure*.pdf figures/si/figure*.pdf`:

| Figure | File | vector | fonts | one family | width x height (mm) | no text in axes | Result |
|---|---|---|---|---|---|---|---|
| Figure 1 | `main/figure1_models.pdf` | FAIL (1 raster: the ZnO render, by design) | ok | ok (TeX Gyre Heros) | 138.6 x 142.0 | FAIL (no axes: schematic and render) | documented exception, as the former Figure 1 |
| Figure 2 | `main/figure2_descriptor_advantage.pdf` | ok | ok | ok (Arial) | 138.6 x 80.0 | ok | PASS |
| Figure 3 | `main/figure3_within_host.pdf` | ok | ok | ok (Arial) | 138.6 x 74.0 | ok | PASS |
| Figure 4 | `main/figure4_staging.pdf` | ok | ok | ok (Arial) | 138.6 x 78.0 | ok | PASS |
| Figure 5 | `main/figure5_screening.pdf` | ok | ok | ok (Arial) | 138.6 x 80.0 | ok | PASS |
| Figure A1 | `si/figureA1_cascade.pdf` | ok | ok | ok (TeX Gyre Heros) | 138.6 x 22.2 | FAIL (no axes: schematic) | documented exception, as the former Figure S2 |
| Figure B1 | `si/figureB1_readout.pdf` | ok | ok | ok (TeX Gyre Heros) | 138.6 x 53.9 | FAIL (no axes: schematic) | documented exception, as the former Figure S1 |
| Figure C1 | `si/figureC1_splits.pdf` | ok | ok | ok (TeX Gyre Heros) | 138.6 x 65.2 | FAIL (no axes: schematic) | documented exception, as the former Figure S3 |
| Figure E1 | `si/figureE1_within_host_groups.pdf` | ok | ok | ok (Arial) | 138.6 x 190.0 | ok | PASS |
| Figure H1 | `si/figureH1_probe.pdf` | ok | ok | ok (Arial) | 138.6 x 180.0 | ok | PASS |

Totals: 6 PASS, 4 documented exceptions (Figure 1 and the three schematics), the same exceptions as before
(`docs/figure_style.md`, QA). Figure I1 is a PNG and is outside the PDF check. Reruns of every script give
byte-identical PDFs.

## Text layer

`pdftotext -layout` of every new matplotlib PDF holds only panel letters, axis labels, tick labels and the legend
entries below the panels (the site names of Figure 5 (b) are its x tick labels). `qa_figure.py` finds no word
inside any axes. The schematics (Figures 1 (a), A1, B1, C1) are diagrams whose labels are their content, as before.
Two labels inside the moved schematics, which were copied without redrawing as instructed, do not match the new
vocabulary:

- Figure A1 (`schematics/fig_cascade.tex`) ends in the box `final universe v1`; the glossary term is the final
  dataset.
- Figure C1 (`schematics/fig_splits.tex`), panel (d), reads "leave-one-chemistry-out"; the glossary term is
  leave one family out (the caption uses it).

Both are one-word edits in `schematics/`, outside the W2b scope.

## Captions

The rules of `scripts/check_captions.py` (at most 3 sentences and 70 words, no semicolon, no colon outside a
leading provenance label, no interpretation phrase, no typed number) were applied to the 11 new caption files, with
"(**b**)" after a full stop counted as a new sentence, as the printed `\textbf{b}` form is counted. All 11 pass:

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
| Figure H1 | 2 | 67 |
| Figure I1 | 2 | 54 |

`python scripts/check_captions.py` (the printed captions in `paper/`, unchanged) passes, and `--figure-files`
reports no problem for any new caption file.

## Forbidden words

The forbidden words of `docs/prose_style.md` and its registration vocabulary (the list in its rule 2, plus
`backbone`, `default initialisation` and `universe`), grepped case-insensitively (identifiers case-sensitively)
over the 11 caption files, `docs/figure_numbering.md` and this file, with backticked record paths exempt (rule 2
of `docs/prose_style.md`) and the appendix figure number exempt: 0 hits. In the new code the only hits are the
network's record key in the results files.

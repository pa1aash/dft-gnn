# Figure numbering (W2b, one network)

The numbering of the rewritten manuscript (`docs/story_spec.md`, section v): main Figures 1-5 and appendix figures
A1, B1, C1, E1, H1 and I1. Every figure drawn from results shows one network, the He-initialised, validation-tuned
network (record key `v2`), in one line style (solid line, filled markers, filled band). The number of a figure is
set by the title of its caption file (`**Figure N.**`) and by this table. Session W2b, 2026-10-17; checks in
`docs/w2b_figure_checks.md`. Session W2c (2026-10-17) changed two schematic labels and three captions; checks in
`docs/w2c_figure_checks.md`.

The new figures carry new file stems (`figureN_*`), so the former files are untouched: the paper in `paper/` still
includes them until the prose rewrite switches to the new names, after which the former files and their scripts
can be deleted. The former scripts were not edited and still write the former stems; the new scripts import
`figures/code/style_paper.py` and, read-only, helpers of the former scripts.

## Main text

| Number | File (PDF and `.caption.md`) | Script | Records (read-only) |
|---|---|---|---|
| Figure 1, models and input representation | `figures/main/figure1_models.pdf`; panel (b) `figures/main/fig1_zno_vacancy.png` | `figures/code/figure1_models.py` (panel (a) from `figures/code/figure1_pipeline.tex`) | none |
| Figure 2, site error and descriptor advantage against training hosts | `figures/main/figure2_descriptor_advantage.pdf` | `figures/code/figure2_descriptor_advantage.py` | `results/derived_c1/final_network_summary.json` |
| Figure 3, site resolution within a host | `figures/main/figure3_within_host.pdf` | `figures/code/figure3_within_host.py` | `results/c1c2_v2.json`, `results/precision_g1_v2.json`, `results/cv_g1_v2.json` |
| Figure 4, staging | `figures/main/figure4_staging.pdf` | `figures/code/figure4_staging.py` | `results/staging_v2.json` |
| Figure 5, screening of named oxides | `figures/main/figure5_screening.pdf` | `figures/code/figure5_screening.py` | `figures/main/data/screening_demo.json` |

## Appendices

| Number | File | Script | Source |
|---|---|---|---|
| Figure A1, filter cascade | `figures/si/figureA1_cascade.pdf` | `figures/code/figure_moves.py` (copy) | byte-identical copy of `figures/si/fig_cascade.pdf`, placed by `figures/code/fig_si_schematics.py` from `schematics/fig_cascade.tex`; counts in `results/filter_cascade.json` |
| Figure B1, readout schematic | `figures/si/figureB1_readout.pdf` | `figures/code/figure_moves.py` (copy) | byte-identical copy of `figures/si/fig_readout.pdf`, placed by `figures/code/fig_si_readout.py` from `schematics/fig_readout.tex` |
| Figure C1, split designs | `figures/si/figureC1_splits.pdf` | `figures/code/figure_moves.py` (copy) | byte-identical copy of `figures/si/fig_splits.pdf`, placed by `figures/code/fig_si_schematics.py` from `schematics/fig_splits.tex` |
| Figure E1, within-host breakdown | `figures/si/figureE1_within_host_groups.pdf` | `figures/code/figureE1_within_host_groups.py` | `results/within_host_breakdown.json` (network entries) |
| Figure F1, sensitivities | not built | none | the high-moment exclusion on the network is being rerun; build once its record exists |
| Figure H1, latent probe | `figures/si/figureH1_probe.pdf` | `figures/code/figureH1_probe.py` | `results/probe_descriptive.json` (block `s_v2`) |
| Figure I1, SnO2 structure render | `figures/si/figureI1_sno2_vacancy.png` (with `.render.json`) | `figures/code/figure_moves.py` (copy) | byte-identical copy of `figures/si/structure_sno2_vacancy.png` |

`docs/story_spec.md` lists "Fig. A1-A2, C1" as moves of the two former Figures S2 and S3. Only one figure, the
filter cascade, belongs to Appendix A, so there is no Figure A2; if a second Appendix A figure is wanted, its source
has to be named. Every appendix caption that names a source names the record in the last column of the table above
(Figure A1 also points to the cascade table of Appendix A, Table A1).

## Fate of every former figure

| Former number | Former file | Fate | New number |
|---|---|---|---|
| Figure 1, models and input representation | `figures/main/fig1_overview.pdf` | kept, redrawn: the dashed outline behind each graph network in panel (a) and the key that explained it are removed; nothing else changes | Figure 1 |
| Figure 1 (b), ZnO render | `figures/main/fig1_zno_vacancy.png` | kept, unchanged, as panel (b) | Figure 1 (b) |
| Figure 2, learning curves | `figures/main/fig2_learning_curves.pdf` | merged, network only: becomes panel (a) | Figure 2 (a) |
| Figure 3, advantage A | `figures/main/fig3_advantage.pdf` | merged, network only: becomes panel (b), from 100 training hosts | Figure 2 (b) |
| Figure 4, staging | `figures/main/fig4_staging.pdf` | kept, redrawn on the network | Figure 4 |
| Figure 5, geometry | `figures/main/fig5_geometry.pdf` | deleted from the paper: the relaxed-geometry check becomes a Results paragraph and the Appendix G table | none |
| Figure 6, site resolution within a host | `figures/main/fig6_within_host.pdf` | kept, redrawn on the network | Figure 3 |
| Figure 7, screening | `figures/main/fig7_screening.pdf` | kept, redrawn on the network | Figure 5 |
| Figure S1, readout schematic | `figures/si/fig_readout.pdf` | moved | Figure B1 |
| Figure S2, filter cascade | `figures/si/fig_cascade.pdf` | moved | Figure A1 |
| Figure S3, split designs | `figures/si/fig_splits.pdf` | moved | Figure C1 |
| Figure S4, within-host groups | `figures/si/fig_si_withinhost_groups.pdf` | moved, redrawn on the network | Figure E1 |
| Figure S5, GPU class | `figures/si/fig_si_gpu_class.pdf` | deleted (one Methods sentence replaces it) | none |
| Figure S6, sensitivities | `figures/si/fig_si_sensitivities.pdf` | to be rebuilt on the network; not built in W2b | Figure F1 (pending) |
| Figure S7, latent probe | `figures/si/fig6_probe.pdf` | moved, redrawn on the network's probe record | Figure H1 |
| Figure S8, SnO2 render | `figures/si/structure_sno2_vacancy.png` | moved | Figure I1 |
| unnumbered G1 learning curves | `figures/si/fig_g1_learning_curves.pdf` | deleted from the figure set (never cited; Figure 2 carries the network's curves) | none |

**R3 update (2026-10-17).** The rewritten main text (`paper/sections/`) now includes `figure1_models` to
`figure5_screening` with the labels `fig:models`, `fig:learning_curves`, `fig:within_host`, `fig:staging` and
`fig:screening`; the former main-text files are no longer included by `paper/main.tex`. The appendix figures are
included once the SI is merged into the appendices (`docs/pending_edits.md`).

**A4 update (2026-10-17).** The appendix figures are now included by `paper/main.tex`: Figure A1 (`fig:app_cascade`),
B1 (`fig:app_readout`), C1 (`fig:app_splits`), E1 (`fig:app_within`), H1 (`fig:app_probe`) and I1 (`fig:app_sno2`,
printed 69 mm wide, its 600 ppi width), numbered per appendix by `paper/main.tex`. The printed captions are rewritten
from the `.caption.md` files to the 70-word limit of `scripts/check_captions.py`. Figure F1 is still not built.

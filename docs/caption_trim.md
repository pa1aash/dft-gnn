# Caption trim (F2)

Every figure caption of the article and the Supplementary Materials is at most 3 sentences (target 2) and at most
70 words. A caption says what is plotted (sentence 1), how to read it (sentence 2: marker and line encoding, what
the bars and bands are, and the registered, post hoc and extension labels where a figure mixes them) and,
optionally, where the data come from (sentence 3). Interpretation, results and methods detail belong in the body.
`scripts/check_captions.py` enforces the limits (`make check-captions`, also run by the pre-push hook).

## 1. Caption sources (inventory, compiled before any edit)

### 1.1 Printed figure captions (in scope, trimmed)

The article and the SI print only the inline `\caption{...}` of the figure environments below; no caption is
read from a file. These are the 15 enforced captions.

| Figure | Label | Source |
|---|---|---|
| 1 | `fig:schematic` | `paper/sections/methods.tex` |
| 2 | `fig:learning_curves` | `paper/sections/results.tex` |
| 3 | `fig:advantage` | `paper/sections/results.tex` |
| 4 | `fig:staging` | `paper/sections/results.tex` |
| 5 | `fig:geometry` | `paper/sections/results.tex` |
| 6 | `fig:within_host` | `paper/sections/results.tex` |
| 7 | `fig:screening` | `paper/sections/results_screening.tex` |
| S1 | `fig:readout` | `paper/si/sections/s2_training.tex` |
| S2 | `fig:cascade` | `paper/si/sections/s3_splits.tex` |
| S3 | `fig:splits` | `paper/si/sections/s3_splits.tex` |
| S4 | `fig:withinhost` | `paper/si/sections/s4_withinhost.tex` |
| S5 | `fig:gpu` | `paper/si/sections/s5_hardware.tex` |
| S6 | `fig:sens` | `paper/si/sections/s6_sensitivities.tex` |
| S7 | `fig:probe` | `paper/si/sections/s7_probe.tex` |
| S8 | `fig:sno2` | `paper/si/sections/s8_structures.tex` |

### 1.2 Table captions (not in scope)

The other 15 `\caption` commands of `paper/sections/` and `paper/si/sections/` belong to tables (main:
`tab:filter_cascade`, `tab:tuning`, `tab:headline`, `tab:screening_sites`, `tab:screening_pairs`; SI: the
cascade, descriptor classes, search space, tuned v1 and v2 values, capped runs, within-host groups, N1, GPU class,
first shell and the reproducibility tables). The task covers figure captions only, so they are unchanged and the
check does not parse them.

### 1.3 Caption files beside the figures (not printed, not edited)

These Markdown files record a caption next to each figure file. None is read by `paper/` (W3 reworded the SI
captions from them into the register, and the article captions were written in the section files). Most are
written by the figure code, which is outside the F2 scope, so an edit here would be overwritten at the next
regeneration. `python3 scripts/check_captions.py --figure-files` reports their counts without failing on them.

| File | Written by |
|---|---|
| `figures/main/fig1_overview.caption.md` | by hand (F1b/W3) |
| `figures/main/fig1_zno_vacancy.caption.md` | by hand (render of record) |
| `figures/main/fig2_learning_curves.caption.md` | `figures/code/fig2_learning_curves.py` |
| `figures/main/fig3_advantage.caption.md` | `figures/code/fig3_advantage.py` |
| `figures/main/fig4_staging.caption.md` | `figures/code/fig4_staging.py` |
| `figures/main/fig5_geometry.caption.md` | `figures/code/fig5_geometry.py` (the F1b "caption file" of Fig 5) |
| `figures/main/fig6_within_host.caption.md`, `fig_within_host.caption.md` | `figures/code/fig_within_host.py` (byte-identical copy kept, F1c) |
| `figures/main/fig7_screening.caption.md` | `figures/code/fig7_screening.py` |
| `figures/si/fig_readout.caption.md` | by hand (F1c) |
| `figures/si/fig_cascade.caption.md`, `fig_splits.caption.md` | `figures/code/fig_si_schematics.py`, from `schematics/*.caption.md` |
| `figures/si/fig_si_withinhost_groups.caption.md` | `figures/code/fig_si_withinhost_groups.py` |
| `figures/si/fig_si_gpu_class.caption.md` | `figures/code/fig_si_gpu_class.py` |
| `figures/si/fig_si_sensitivities.caption.md` | `figures/code/fig_si_sensitivities.py` |
| `figures/si/fig6_probe.caption.md` | `figures/code/fig6_probe.py` |
| `figures/si/structure_sno2_vacancy.caption.md` | by hand (F1c) |
| `figures/si/fig_g1_learning_curves.caption.md` | `figures/code/fig_g1_learning_curves.py` (unnumbered, not cited) |
| `schematics/fig_pipeline.caption.md`, `fig_cascade.caption.md`, `fig_readout.caption.md`, `fig_splits.caption.md` | by hand (captions of record of the schematics) |

The schematics pages of the SI (Figures S1 to S3) print the inline captions of section 1.1, not these files.

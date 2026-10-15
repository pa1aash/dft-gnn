# Figure numbering (F1c, final)

The final numbers of every figure, mapped from the file names they were built under. The number of a figure
is set by the title of its caption file (`**Figure N.**`), by this table and by `docs/figure_inventory.md`;
file stems are not renumbered, so a stem's digit can differ from the figure's number (`fig6_probe` is Figure
S7). The one exception is the within-host figure, renamed to `fig6_within_host` on request. Results are frozen
(`results-v1`); nothing was recomputed for the numbering.

## Main text

| Number | Final file | Old file name (before F1c) | Old caption title | Script |
|---|---|---|---|---|
| Figure 1, models and input representation | `figures/main/fig1_overview.pdf` (panel (b): `figures/main/fig1_zno_vacancy.png`) | unchanged | Figure 1 | `figures/code/fig1_overview.py` |
| Figure 2, learning curves of S and D | `figures/main/fig2_learning_curves.pdf` | unchanged | Figure 2 | `figures/code/fig2_learning_curves.py` |
| Figure 3, advantage A | `figures/main/fig3_advantage.pdf` | unchanged | Figure 3 | `figures/code/fig3_advantage.py` |
| Figure 4, staging | `figures/main/fig4_staging.pdf` | unchanged | Figure 4 | `figures/code/fig4_staging.py` |
| Figure 5, geometry robustness | `figures/main/fig5_geometry.pdf` | unchanged | Figure 5 | `figures/code/fig5_geometry.py` |
| Figure 6, site resolution within a host | `figures/main/fig6_within_host.{pdf,caption.md}` | `figures/main/fig_within_host.{pdf,caption.md}` | "Figure." (unnumbered, not placed) | `figures/code/fig_within_host.py` (`STEM = "fig6_within_host"`) |
| Figure 7, screening demonstration | `figures/main/fig7_screening.pdf` | unchanged | Figure 7 | `figures/code/fig7_screening.py` |

Q0 (2026-10-15): `analysis/freeze_table.py` (`FIGURE_RECORDS`) and `deposit/FILES.sha256` now use the final names, nothing
in `paper/`, `analysis/` or `deposit/` names the old file, and the copy `figures/main/fig_within_host.{pdf,caption.md}` has
been deleted. `results/freeze_table.json` is frozen and still records the old name. Before Q0 the copy was kept
because files outside the figure scope named it: `analysis/freeze_table.py` (`FIGURE_RECORDS`),
`results/freeze_table.json` (frozen at `results-v1`, `payload.checks.figures`) and `deposit/FILES.sha256`. The
script writes only the new name; the copy is refreshed by hand (`cp figures/main/fig6_within_host.pdf
figures/main/fig_within_host.pdf`, likewise the caption) until those references move to the new name, after
which it can be deleted.

## Supplementary Information

| Number | File | Old caption title | Script |
|---|---|---|---|
| Figure S1, readout schematic | `figures/si/fig_readout.pdf` | Figure S3 (main-text Figure 2 in `schematics/fig_readout.caption.md`) | `figures/code/fig_si_readout.py` (caption file maintained by hand) |
| Figure S2, filter cascade | `figures/si/fig_cascade.pdf` | Figure S1 | `figures/code/fig_si_schematics.py` (`NUMBERS`) |
| Figure S3, split designs | `figures/si/fig_splits.pdf` | Figure S2 | `figures/code/fig_si_schematics.py` (`NUMBERS`) |
| Figure S4, within-host groups | `figures/si/fig_si_withinhost_groups.pdf` | "Figure." (unnumbered) | `figures/code/fig_si_withinhost_groups.py` |
| Figure S5, GPU class | `figures/si/fig_si_gpu_class.pdf` | "Figure S (GPU class)" | `figures/code/fig_si_gpu_class.py` |
| Figure S6, sensitivities | `figures/si/fig_si_sensitivities.pdf` | "Figure S (sensitivities)" | `figures/code/fig_si_sensitivities.py` |
| Figure S7, latent probe | `figures/si/fig6_probe.pdf` | Figure 6 | `figures/code/fig6_probe.py` |
| Figure S8, structure render (SnO2) | `figures/si/structure_sno2_vacancy.png` | untitled ("Structure render, rutile SnO2") | `blender/render_host.py mp-856 24` (caption file maintained by hand) |

Cross-references updated with the numbers: the Figure 7 caption cites the SnO2 render as Figure S8. The schematic
captions of record in `schematics/` (outside the figure scope) keep the numbers they were written with (readout
Figure 2, cascade S1, splits S2); `figures/code/fig_si_schematics.py` replaces the cascade and splits titles when
it copies them, and `docs/schematics.md` lists the final numbers.

## Unnumbered

| File | Old location | Status |
|---|---|---|
| `figures/si/fig_g1_learning_curves.{pdf,png,caption.md}` (G1 learning curves, ANALYSIS_PLAN section 14) | `figures/main/` | Kept, not cited in the text and not numbered (title "Figure G1"). Figure 2 and Figure 3 carry the same series. `figures/code/fig_g1_learning_curves.py` now writes to `figures/si/` by default. |

Q0 (2026-10-15): `analysis/freeze_table.py` and `deposit/FILES.sha256` now name `si/fig_g1_learning_curves.pdf`; only the
frozen `results/freeze_table.json` keeps the old location. Before Q0, names that still pointed at the old G1 location, outside the figure scope: `analysis/freeze_table.py`
(`FIGURE_RECORDS["main/fig_g1_learning_curves.pdf"]`), `results/freeze_table.json` (frozen) and
`deposit/FILES.sha256`. Session notes (`docs/g1_notes.md`, `docs/a1_notes.md`, `docs/a4_notes.md`,
`docs/results_summary.md`) record the names in use when they were written and are not rewritten.

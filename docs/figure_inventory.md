# Figure inventory (F1b, at `results-v1`)

Final placement of every figure of the paper. Results are frozen (tag `results-v1`); every figure listed here is
drawn from the records named, without recomputation. Captions name the record and key of each plotted value; the
full key lists are in the caption files. Labels follow `docs/provenance_labels.md` and `docs/freeze_notes.md`:
REGISTERED (design and deciding rule fixed before the results; "PRE-REGISTERED" in `docs/provenance_labels.md`),
POST HOC (the primary backbone v2, or a rule fixed after its results) and EXTENSION (compute or analysis beyond
the plan). Where one figure draws series of different provenance, each series' label is given. Style and QA:
`docs/figure_style.md`; manuscript integration: `docs/figure_integration.md`.

## Main text

| Figure | File | Caption file | Source records and keys | Label | Placement |
|---|---|---|---|---|---|
| Fig 1, models and input representation | `figures/main/fig1_overview.pdf` (panel (b) from `figures/main/fig1_zno_vacancy.png`) | `figures/main/fig1_overview.caption.md` (render: `figures/main/fig1_zno_vacancy.caption.md`) | `schematics/fig_pipeline.pdf`; `figures/main/fig1_zno_vacancy.render.json` (`formula`, `n_atoms`, `vacancy_atom_index`, `first_shell`, `cation_O_bond_cutoff_A`, `direction`, `samples`, `dpi`, `width_mm`, `px`); `configs/config.yaml` `graph.cutoff_A` | REGISTERED (method schematic and data illustration; no result) | main text |
| Fig 2, learning curves of S and D | `figures/main/fig2_learning_curves.pdf` | `figures/main/fig2_learning_curves.caption.md` | `results/c1c2_v2.json`, `results/c1c2_v1.json`: `payload.mae.<B>.<S\|D-state>.mae`; `results/diagnostics_sweep.json`: `payload.references.<B>.<mean\|B0\|RF-Kumagai>`; `results/precision_g1_v<1\|2>.json`, `results/cv_g1_v<1\|2>.json`: same keys, `payload.x_training_hosts` | v1 REGISTERED; v2 POST HOC; precision and CV points EXTENSION | main text |
| Fig 3, advantage A | `figures/main/fig3_advantage.pdf` | `figures/main/fig3_advantage.caption.md` | `results/c1c2_v2.json`, `results/c1c2_v1.json`: `payload.A_mae.<B>` (`A`, `ci95`, `upper_one_sided_95`), `payload.N_star`, `payload.C2`, `payload.delta_eV`; `results/precision_g1_v<1\|2>.json`, `results/cv_g1_v<1\|2>.json`: `payload.A_mae.<key>`; `results/cv_extended_budget.json`: `payload.extended_budget_statement` | v1 REGISTERED; v2 POST HOC; precision and CV points EXTENSION | main text |
| Fig 4, staging | `figures/main/fig4_staging.pdf` | `figures/main/fig4_staging.caption.md` | `results/staging_v1.json`, `results/staging_v2.json`: `payload.budgets.<B>.mae.<S\|D\|P>`, `payload.budgets.<B>.D_minus_P`, `payload.budgets.<B>.P_minus_S`, `payload.delta_P_eV`, `payload.summary.outcome_by_budget` | v1 REGISTERED (staging analysis; TOST outcome rule POST HOC); v2 POST HOC | main text |
| Fig 5, geometry robustness | `figures/main/fig5_geometry.pdf` | `figures/main/fig5_geometry.caption.md` | `results/geometry_c3b.json`: `payload.budgets.654.delta_mae.<S\|D\|P>.<mlip\|mlip_rescaled>`, `payload.null_rule`, `payload.regression`; `results/analysis/geometry_host_change.parquet` (hash in `payload.input.host_change`); `results/geometry_descriptive.json` | REGISTERED (v1 at the registered budget; v1 only) | main text |
| Fig 7, screening demonstration | `figures/main/fig7_screening.pdf` | `figures/main/fig7_screening.caption.md` | `figures/main/data/screening_demo.json`: `payload.sites.<site>.{dft_eV, v2, v1}`, `payload.summary.<v1\|v2>.{mae_eV, mae_ci}`; `results/screening_c5.json`: `payload.sites[]`; `results/screening_absence.json`: `payload.candidates` | v1 REGISTERED (registered aggregation); v2 POST HOC; demonstration, no test | main text |

## Supplementary Information

| Figure | File | Caption file | Source records and keys | Label | Placement |
|---|---|---|---|---|---|
| Figure S1, filter cascade | `figures/si/fig_cascade.pdf` (from `schematics/fig_cascade.pdf`) | `figures/si/fig_cascade.caption.md` | counts in Table 1 (`results/filter_cascade.json`); none drawn | REGISTERED (data filter schematic; no result) | SI |
| Figure S2, split designs | `figures/si/fig_splits.pdf` (from `schematics/fig_splits.pdf`) | `figures/si/fig_splits.caption.md` | none drawn | REGISTERED (panels a, b, d); panel c, grouped K-fold CV, EXTENSION | SI |
| Figure S3, readout schematic | `figures/si/fig_readout.pdf` (from `schematics/fig_readout.pdf`) | `figures/si/fig_readout.caption.md` | none drawn | REGISTERED (architecture schematic; no result) | SI |
| Fig 6, latent probe | `figures/si/fig6_probe.pdf` | `figures/si/fig6_probe.caption.md` | `results/probe_c4_v1.json`: `payload.curves.<host\|site>.<trained\|shuffled\|init0\|init1\|init2>.<B>`, `payload.rule`, `payload.C4_holds`, `payload.outcome`; `results/probe_descriptive.json`: `payload.per_descriptor_r2.<trained\|shuffled\|init0>.<descriptor>.654` | REGISTERED (v1 analysis and controls; init1, init2 and panel c descriptive); v2 probe POST HOC, not drawn | SI (moved under the registered rule; C4 does not hold) |
| GPU class | `figures/si/fig_si_gpu_class.pdf` | `figures/si/fig_si_gpu_class.caption.md` | `results/precision_a_b400_b654.json`, `results/cv_extended_budget.json`: `payload.descriptive.gpu_class.<precision\|400, precision\|654, cv\|10, cv\|20>[]` (`A_paired_cells.A`, `A_paired_cells.ci95_descriptive`), `payload.delta_eV` | EXTENSION (descriptive, no test); v2 POST HOC | SI |
| Sensitivities | `figures/si/fig_si_sensitivities.pdf` | `figures/si/fig_si_sensitivities.caption.md` | `results/sens_high_moment_v1.json`: `payload.high_moment.A`; `results/sens_capped_post_hoc.json`: `payload.per_budget.654.<primary\|capped_twins>.A`, `payload.v2_primary_654.primary.A`; `results/sens_cgcnn.json`: `payload.table.<family>.<budget>.<S\|D>.mae` | high-moment EXTENSION; capped twins POST HOC; CGCNN EXTENSION (descriptive); v2 primary values POST HOC | SI |
| Within-host groups | `figures/si/fig_si_withinhost_groups.pdf` | `figures/si/fig_si_withinhost_groups.caption.md` | `results/within_host_breakdown.json`: `payload.groups[]` (`v2\|v1.S\|D.within_host_mae`, `v2.S.zero_skill_mae.point`), `payload.definitions` | EXTENSION; v2 POST HOC | SI |
| Structure render, rutile SnO2 | `figures/si/structure_sno2_vacancy.png` | `figures/si/structure_sno2_vacancy.caption.md` | `figures/si/structure_sno2_vacancy.render.json` | REGISTERED (data illustration; no result) | SI |

## Built but not placed

Two figures in `figures/main/` are not in the main-text list above. They remain built and pass QA; their
placement is the author's decision (see the F1b handoff).

| Figure | File | Caption file | Source records | Label |
|---|---|---|---|---|
| G1 learning curves (ANALYSIS_PLAN §14) | `figures/main/fig_g1_learning_curves.pdf` | `figures/main/fig_g1_learning_curves.caption.md` | `results/g1_primary.json`, `results/c1c2_v2.json`, extension records as Fig 2 | v1 REGISTERED; v2 POST HOC; extension points EXTENSION |
| Within-host skill and A_within | `figures/main/fig_within_host.pdf` | `figures/main/fig_within_host.caption.md` | `results/c1c2_v2.json`, `results/c1c2_v1.json` (`payload.mae.<B>.<S\|D-state>.within_host_skill`, `payload.A_within_host.<B>`), extension records as Fig 2 | v1 REGISTERED; v2 POST HOC; extension points EXTENSION |

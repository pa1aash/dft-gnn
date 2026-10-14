**Figure G1. Learning curves of the neutral oxygen-vacancy formation energy.** (**a**) Site-level test mean
absolute error (MAE, eV) against the number of training hosts (logarithmic axis; budgets `payload.budgets`)
for the two-descriptor physics floor B0, the random forest on the Kumagai descriptors (RF-Kumagai), the
structure-only MEGNet S and the descriptor model D (S given the host-electronic and site-electronic DFT
descriptors of the pristine host, D-state injection). The thin horizontal lines are published values, not
results of this work: the random-forest MAE of Kumagai et al. (`paper/refs.bib` key `Kumagai2021insights`) and the
structure-only CGCNN MAE of Kiyohara et al. (`paper/refs.bib` key `Kiyohara2025machinelearning`); both values and their
conditions are in `docs/baselines.md` (published-reference rows). (**b**) The advantage of the DFT descriptors,
A = MAE_S − MAE_D, with the margin δ (dashed, `payload.delta_eV`) and zero (dotted). Solid lines, filled
circles and filled bands: primary backbone (v2), adopted after diagnostics of the originally registered
backbone, from `results/c1c2_v2.json`, keys `payload.mae.<B>.<S|D-state>.mae` (`mean`, `ci`) and
`payload.A_mae.<B>` (`A`, `ci95`). Dashed lines, open circles and hatched bands: originally registered
backbone (v1), from `results/g1_primary.json`, keys `payload.per_budget.<B>.<MAE_S|MAE_D|A>` (`mean`, `ci`);
N* in `payload.n_star`. B0 and RF-Kumagai do not depend on the backbone (squares on thinner lines):
`results/g1_primary.json`, key `payload.descriptive_curves.mae.<B0|RF-Kumagai>.<B>`. Every point is the mean
over the registered outer resamples (`payload.bootstrap.n_resamples`, each holding out
`payload.bootstrap.test_hosts_per_resample` test hosts, grouped by formula, with nested training budgets);
S and D predictions are the mean over the training seeds per test site. Bands are two-sided intervals at
the level `payload.bootstrap.two_sided_ci` of `results/g1_primary.json` from the paired hierarchical bootstrap (`payload.bootstrap`: resamples, then test hosts within each resample,
all sites of a drawn host kept). The v2 intervals come from the bootstrap of `results/c1c2_v2.json`; our
recomputation with the G1 generator (`results/ingest_m1_recompute.json`, `payload.v2_arm`) gives the same
point values. Three series are drawn, each labelled in the legend by its marker shape: circles on lines, the registered outer-resample design (the resamples and budgets are registered; the primary backbone (v2) evaluated on them is not); diamonds, the precision extension (EXTENSION), the pooled estimate over the resamples and seeds named in `payload.design`, drawn just left of its budget; triangles, grouped K-fold CV (EXTENSION), placed at the mean fold training size `payload.x_training_hosts`. The extension series are unconnected points with two-sided interval bars (primary backbone (v2): solid bars, filled markers; originally registered backbone (v1): dashed bars, open markers) and are not pre-registered (label `payload.label` of each record; analysis rules in `docs/deviations.md`, cited under `payload.rules` of the source records). Records: precision extension, originally registered backbone (`results/precision_g1_v1.json`); precision extension, primary backbone (`results/precision_g1_v2.json`); grouped K-fold CV, originally registered backbone (`results/cv_g1_v1.json`); grouped K-fold CV, primary backbone (`results/cv_g1_v2.json`), each with its source analysis in `payload.source_record`. The CV test sets differ from the registered ones: every host is tested once across the folds, including hosts that no outer resample tests, so a CV value is not directly comparable with a registered-budget value at a similar number of training hosts (partition check in `results/cv_extended_budget.json`, `payload.fold_partition`). Script: `figures/code/fig_g1_learning_curves.py`.

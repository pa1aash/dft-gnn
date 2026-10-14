**Figure 6. Site resolution within a host.** (**a**) Within-host skill of S (structure only) and D (structure
plus the DFT descriptors of the pristine host and site) against the number of training hosts (logarithmic
axis): the within-host residual MAE of a predictor that is constant within each host, minus the model's, on
the same test hosts with at least two oxygen sites. Zero (dotted) means the model ranks hosts but does not
distinguish the sites of a host. Key `payload.mae.<B>.<S|D-state>.within_host_skill` (`mean`, two-sided
interval `ci`). (**b**) The within-host advantage of the descriptors, A_within = within-host residual MAE of S
minus that of D, with the margin δ (dashed, `payload.delta_eV`) and zero (dotted); key
`payload.A_within_host.<B>` (`A`, `ci95`), and the within-host N* in `payload.N_star_within_host`. Solid lines,
filled circles and filled bands: primary backbone (v2), adopted after diagnostics of the originally
registered backbone; dashed lines, open circles and hatched bands: originally registered backbone (v1).
Values from `results/c1c2_v2.json` and `results/c1c2_v1.json` (registered outer resamples; prediction of each
site the mean over the training seeds; two-sided intervals at the level `payload.bootstrap.two_sided_ci` of `results/g1_primary.json`, from the paired
hierarchical bootstrap). The v1 values
also appear, with the G1 estimator, in `results/g1_within_host.json`. Three series are drawn, each labelled in the legend by its marker shape: circles on lines, the registered outer-resample design (the resamples and budgets are registered; the primary backbone (v2) evaluated on them is not); diamonds, the precision extension (EXTENSION), the pooled estimate over the resamples and seeds named in `payload.design`, drawn just left of its budget; triangles, grouped K-fold CV (EXTENSION), placed at the mean fold training size `payload.x_training_hosts`. The extension series are unconnected points with two-sided interval bars (primary backbone (v2): solid bars, filled markers; originally registered backbone (v1): dashed bars, open markers) and are not pre-registered (label `payload.label` of each record; analysis rules in `docs/deviations.md`, cited under `payload.rules` of the source records). Records: precision extension, originally registered backbone (`results/precision_g1_v1.json`); precision extension, primary backbone (`results/precision_g1_v2.json`); grouped K-fold CV, originally registered backbone (`results/cv_g1_v1.json`); grouped K-fold CV, primary backbone (`results/cv_g1_v2.json`), each with its source analysis in `payload.source_record`. The CV test sets differ from the registered ones: every host is tested once across the folds, including hosts that no outer resample tests, so a CV value is not directly comparable with a registered-budget value at a similar number of training hosts (partition check in `results/cv_extended_budget.json`, `payload.fold_partition`).
Script: `figures/code/fig_within_host.py`.

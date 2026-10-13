**Figure 2. Learning curves of the structure-only and descriptor-augmented networks.** Site-level test mean
absolute error (MAE, eV) of the neutral oxygen-vacancy formation energy against the number of training hosts
(logarithmic axis, budgets `payload.budgets`). (**a**) The structure-only network S; (**b**) the network D,
which also receives the DFT descriptors of the pristine host and site (D-state injection). Solid lines with
filled circles: primary backbone (v2), adopted after diagnostics of the originally registered backbone;
dashed lines with open circles and hatched bands: originally registered backbone (v1). Both are trained and
evaluated on the
same registered outer resamples, with the prediction of each test site the mean over the training seeds.
Values: `results/c1c2_v2.json` and `results/c1c2_v1.json`, key `payload.mae.<B>.S.mae` (a) and
`payload.mae.<B>.D-state.mae` (b), each with `mean` and the two-sided interval `ci` at the level `payload.bootstrap.two_sided_ci` of `results/g1_primary.json`
(paired hierarchical bootstrap over resamples and then test hosts). Baselines, which do not depend on the backbone (squares on
thinner lines): the training-mean predictor (dotted), the two-descriptor physics floor B0 and the random
forest on the Kumagai descriptors (RF-Kumagai), from `results/diagnostics_sweep.json`, key
`payload.references.<B>.<mean|B0|RF-Kumagai>`, evaluated on the same test sites. Bands are these
intervals; bands are clipped at the axis limits, and their full extent is in the keys above. Three series are drawn, each labelled in the legend by its marker shape: circles on lines, the registered outer-resample design (the resamples and budgets are registered; the primary backbone (v2) evaluated on them is not); diamonds, the precision extension (EXTENSION), the pooled estimate over the resamples and seeds named in `payload.design`, drawn just left of its budget; triangles, grouped K-fold CV (EXTENSION), placed at the mean fold training size `payload.x_training_hosts`. The extension series are unconnected points with two-sided interval bars and are not pre-registered (label `payload.label` of each record; analysis rules in `docs/deviations.md`, cited under `payload.rules` of the source records). Records: precision extension, originally registered backbone (`results/precision_g1_v1.json`); precision extension, primary backbone (`results/precision_g1_v2.json`); grouped K-fold CV, originally registered backbone (`results/cv_g1_v1.json`); grouped K-fold CV, primary backbone (`results/cv_g1_v2.json`), each with its source analysis in `payload.source_record`. The CV test sets differ from the registered ones: every host is tested once across the folds, including hosts that no outer resample tests, so a CV value is not directly comparable with a registered-budget value at a similar number of training hosts (partition check in `results/cv_extended_budget.json`, `payload.fold_partition`).
Script: `figures/code/fig2_learning_curves.py`.

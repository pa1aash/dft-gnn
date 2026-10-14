**Figure 3. The advantage of explicit DFT descriptors over structure alone, at the registered budgets and beyond
them.** A = MAE_S − MAE_D (eV; positive when the descriptors help) against the number of training hosts
(logarithmic axis). (**a**) Every point; the axis spans the point estimates and the extension intervals, and
registered bands reaching beyond it are clipped (full intervals in the keys below). (**b**) The largest
registered budgets and the extension points, where the decision on the margin is made; the horizontal bars are
the one-sided upper bounds of A, `upper_one_sided_95` (quantile `payload.bootstrap.one_sided_upper_quantile` of
`results/g1_primary.json`), which define N* (the smallest budget whose upper bound lies below δ at it and at
every larger budget). Lines with bands, registered outer-resample design: `results/c1c2_v2.json` and
`results/c1c2_v1.json`, key `payload.A_mae.<B>` (`A`, two-sided interval `ci95`, `upper_one_sided_95`), budgets
`payload.budgets`; N* and the ceiling at the largest budget in `payload.N_star` and `payload.C2` of the same
files. Precision-extension points: the same keys in `results/precision_g1_v2.json` and
`results/precision_g1_v1.json` (the smaller subsets in `payload.beside_subsets`; every subset in
`results/precision_a_b400_b654.json`, key `payload.subsets`). CV points: `results/cv_g1_v2.json` and
`results/cv_g1_v1.json`, keys `payload.A_mae.<k10|k20>` (fold-level SD in `fold_sd`) at
`payload.x_training_hosts.<k10|k20>`; the extended-budget statement is in `results/cv_extended_budget.json`,
key `payload.extended_budget_statement`. Solid line, filled markers, filled band and dark bars: primary
backbone (v2), adopted after diagnostics of the originally registered backbone; dashed line, open markers,
hatched band and lighter bars: originally registered backbone (v1). The dashed horizontal line is the margin δ
(`payload.delta_eV`), the dotted line zero. Bands and interval bars are two-sided intervals at the level
`payload.bootstrap.two_sided_ci` of `results/g1_primary.json` (`two_sided_ci` of `payload.estimator` in the
extension source records): paired hierarchical bootstrap over resamples and test hosts for the registered and
precision points, paired host-cluster bootstrap over all hosts for the CV points. Three series are drawn, each labelled in the legend by its marker shape: circles on lines, the registered outer-resample design (the resamples and budgets are registered; the primary backbone (v2) evaluated on them is not); diamonds, the precision extension (EXTENSION), the pooled estimate over the resamples and seeds named in `payload.design`, drawn just left of its budget; triangles, grouped K-fold CV (EXTENSION), placed at the mean fold training size `payload.x_training_hosts`. The extension series are unconnected points with two-sided interval bars (primary backbone (v2): solid bars, filled markers; originally registered backbone (v1): dashed bars, open markers) and are not pre-registered (label `payload.label` of each record; analysis rules in `docs/deviations.md`, cited under `payload.rules` of the source records). Records: precision extension, originally registered backbone (`results/precision_g1_v1.json`); precision extension, primary backbone (`results/precision_g1_v2.json`); grouped K-fold CV, originally registered backbone (`results/cv_g1_v1.json`); grouped K-fold CV, primary backbone (`results/cv_g1_v2.json`), each with its source analysis in `payload.source_record`. The CV test sets differ from the registered ones: every host is tested once across the folds, including hosts that no outer resample tests, so a CV value is not directly comparable with a registered-budget value at a similar number of training hosts (partition check in `results/cv_extended_budget.json`, `payload.fold_partition`).
Script: `figures/code/fig3_advantage.py`.

**Figure 3 (extended). The advantage of explicit DFT descriptors beyond the registered training budgets
(EXTENSION).** A = MAE_S − MAE_D (eV; positive when the descriptors help) against the number of training hosts
(logarithmic axis). (**a**) Every point; the axis spans the point estimates and the extension intervals.
(**b**) From 200 training hosts up; horizontal bars are the one-sided 95% upper bounds of A. Lines with bands:
the registered 10-resample x 3-seed analysis, `results/c1c2_v2.json` and `results/c1c2_v1.json`, key
`payload.A_mae.<B>` (`A`, `ci95`, `upper_one_sided_95`). Diamonds, drawn just left of their budget: the
precision extension pooled over 30 resamples x 5 seeds at B = 400 and 654, `results/precision_g1_v2.json` and
`results/precision_g1_v1.json`, same keys (the 10 x 5 and 30 x 3 subsets in `payload.beside_subsets`; every
subset in `results/precision_a_b400_b654.json`). Squares: grouped K-fold CV with K = 10 and K = 20, pooled
out-of-fold predictions, placed at the mean fold training size `payload.x_training_hosts.<k10|k20>`,
`results/cv_g1_v2.json` and `results/cv_g1_v1.json`, keys `payload.A_mae.<k10|k20>` (fold-level SD in
`fold_sd`); full analysis in `results/cv_extended_budget.json`, the extended-budget statement under
`payload.extended_budget_statement`. Filled markers, solid line and filled band: primary backbone (v2), adopted
after diagnostics of the originally registered backbone; open markers, dashed line, hatched band and lighter
bars: originally registered backbone (v1). The dashed horizontal line is the margin δ (`payload.delta_eV`), the
dotted line zero. Bands and bars are two-sided 95% intervals: paired hierarchical bootstrap over resamples and
test hosts for the registered and precision points, paired host-cluster bootstrap over the 818 hosts for the CV
points. The precision and CV points are EXTENSION results, not pre-registered (`docs/deviations.md`, rows of
2026-10-11 and 2026-10-14). Script: `figures/code/fig_extended_budget.py`.

**Figure S (sensitivities). The advantage A under the high-moment exclusion and the longer epoch cap, and an
untuned CGCNN beside the MEGNet backbones.** (**a**) A = MAE_S − MAE_D (eV; positive when the DFT descriptors
help) at the largest training budget, from the seed-ensemble site MAE averaged over the registered outer resamples.
"primary": the primary result of each backbone (`results/sens_capped_post_hoc.json`, keys
`payload.v2_primary_654.primary.A` and `payload.per_budget.654.primary.A`; the latter reproduces
`results/g1_primary.json`, `payload.per_budget.654.A`, checked in `payload.sanity_g1_primary`). "high moment"
(EXTENSION): S and D retrained with the entries whose defect magnetic moment exceeds the registered threshold
(`payload.threshold_muB`, entries in `payload.excluded_entries`) removed from training and test sites, compared on
the common test sites (`results/sens_high_moment_v1.json`, key `payload.high_moment.A`; the primary result on the
same sites is `payload.primary_common_sites.A` and the paired change `payload.change_high_moment_minus_primary.A`).
"capped twins" (POST HOC): every primary-sweep run that stopped at the epoch cap replaced by its rerun with the
larger cap (`results/sens_capped_post_hoc.json`, key `payload.per_budget.654.capped_twins.A`; paired change
`payload.per_budget.654.change_twin_minus_primary.A`). Both sensitivities exist for the originally registered
backbone only. Markers: point estimates (`mean`); bars: two-sided intervals (`ci`) of the G1 hierarchical bootstrap
with the G1 draws (`payload.bootstrap`); short horizontal bars: one-sided upper bounds (`upper_one_sided`); dashed
line: the margin δ (`payload.delta_eV`); dotted line: zero. (**b**) Seed-ensemble test MAE (eV) of S (blue) and D
(green) on a single outer resample (`payload.resample`) at the budgets `payload.budgets`, for the MEGNet backbones
(lines with bands) and for CGCNN with fixed, untuned optimiser settings (crosses, drawn just right of their budget)
(`results/sens_cgcnn.json`, key `payload.table.<family>.<budget>.<S|D>.mae`, families `megnet_v2`, `megnet_v1` and
`cgcnn`; parameter counts in `payload.parameter_counts`). Bands and bars in (b) are two-sided intervals (`ci95`) of
a host-cluster bootstrap over the test hosts of that resample, shared by every series (`payload.bootstrap`); with
one resample they reflect test-host sampling only, not resample or split variation, and no test is made. Filled
markers and solid lines: primary backbone (v2), adopted after diagnostics of the originally registered backbone;
open markers and dashed lines: originally registered backbone (v1). Analysis rules: `docs/deviations.md`, cited
under `payload.rule` and `payload.label` of the records. Script: `figures/code/fig_si_sensitivities.py`.

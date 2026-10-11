**Figure. Site resolution within a host.** (**a**) Within-host skill of S (structure only) and D (structure
plus the DFT descriptors of the pristine host and site) against the number of training hosts (logarithmic
axis): the within-host residual MAE of a predictor that is constant within each host, minus the model's, on
the same test hosts with at least two oxygen sites. Zero (dotted) means the model ranks hosts but does not
distinguish the sites of a host. Key `payload.mae.<B>.<S|D-state>.within_host_skill` (`mean`, two-sided 95%
interval `ci`). (**b**) The within-host advantage of the descriptors, A_within = within-host residual MAE of S
minus that of D, with the margin δ (dashed, `payload.delta_eV`) and zero (dotted); key
`payload.A_within_host.<B>` (`A`, `ci95`), and the within-host N* in `payload.N_star_within_host`. Solid lines,
filled circles and filled bands: primary backbone (v2), adopted after diagnostics of the originally
registered backbone; dashed lines, open circles and hatched bands: originally registered backbone (v1).
Values from `results/c1c2_v2.json` and `results/c1c2_v1.json` (registered outer resamples; prediction of each
site the mean over the training seeds; 95% intervals from the paired hierarchical bootstrap). The v1 values
also appear, with the G1 estimator, in `results/g1_within_host.json`. No extension series is drawn: the K-fold CV and precision-extension analysis records (`results/cv_g1_v1.json`, `results/cv_g1_v2.json`, `results/precision_g1_v1.json`, `results/precision_g1_v2.json`) do not exist yet.
Script: `figures/code/fig_within_host.py`.

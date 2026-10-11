**Figure 2. Learning curves of the structure-only and descriptor-augmented networks.** Site-level test mean
absolute error (MAE, eV) of the neutral oxygen-vacancy formation energy against the number of training hosts
(logarithmic axis, budgets `payload.budgets`). (**a**) The structure-only network S; (**b**) the network D,
which also receives the DFT descriptors of the pristine host and site (D-state injection). Solid lines with
filled circles: primary backbone (v2), adopted after diagnostics of the originally registered backbone;
dashed lines with open circles and hatched bands: originally registered backbone (v1). Both are trained and
evaluated on the
same registered outer resamples, with the prediction of each test site the mean over the training seeds.
Values: `results/c1c2_v2.json` and `results/c1c2_v1.json`, key `payload.mae.<B>.S.mae` (a) and
`payload.mae.<B>.D-state.mae` (b), each with `mean` and the two-sided 95% interval `ci` (paired hierarchical
bootstrap over resamples and then test hosts). Baselines, which do not depend on the backbone (squares on
thinner lines): the training-mean predictor (dotted), the two-descriptor physics floor B0 and the random
forest on the Kumagai descriptors (RF-Kumagai), from `results/diagnostics_sweep.json`, key
`payload.references.<B>.<mean|B0|RF-Kumagai>`, evaluated on the same test sites. Bands are the 95%
intervals; bands are clipped at the axis limits, and their full extent is in the keys above. No extension series is drawn: the K-fold CV and precision-extension analysis records (`results/cv_g1_v1.json`, `results/cv_g1_v2.json`, `results/precision_g1_v1.json`, `results/precision_g1_v2.json`) do not exist yet.
Script: `figures/code/fig2_learning_curves.py`.

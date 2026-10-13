**Figure S (GPU class). The advantage A by GPU class of the training runs (EXTENSION, descriptive, no test).**
A = MAE_S − MAE_D (eV) of single runs, averaged over the paired cells in which the S run and the D run of the same
resample or fold, budget and seed both ran on the same GPU class. (**a**) Precision extension, B = 400.
(**b**) Precision extension, B = 654. (**c**) Grouped K-fold CV, K = 10. (**d**) Grouped K-fold CV, K = 20.
Classes: NVIDIA A10, GeForce RTX 3090, L4 and GeForce RTX 4090 of the cluster pool, and "sweep", the original
sweep runs of resamples 0 to 9, seeds 0 to 2 (precision only). RTX 4090 was not part of the N1 repeatability runs.
GPU class was not randomised with respect to resample, fold or seed, so differences between classes are not
separable from them and are not read as hardware effects. Values: `results/precision_a_b400_b654.json` and
`results/cv_extended_budget.json`, key `payload.descriptive.gpu_class.<design|point>` (`A_paired_cells.A`,
`ci95_descriptive`, `n_paired_cells`, `n_runs`); classes without a paired cell are not drawn. Bars: descriptive
95% percentile intervals from a bootstrap over the paired cells (`bootstrap_seed`). Filled markers: primary
backbone (v2), adopted after diagnostics of the originally registered backbone; open markers: originally
registered backbone (v1). Diamonds: precision extension; squares: grouped K-fold CV. Dashed line: the margin δ;
dotted line: zero. Rule: `docs/deviations.md`, row of 2026-10-14, item e1. Script:
`figures/code/fig_si_gpu_class.py`.

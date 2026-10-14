**Figure S5. The advantage A by GPU class of the training runs (EXTENSION, descriptive, no test).**
A = MAE_S − MAE_D (eV) of single runs, averaged over the paired cells in which the S run and the D run of the same
resample or fold, budget and seed both ran on the same GPU class. (**a**, **b**) Precision extension, design points
`precision|400` and `precision|654` of `results/precision_a_b400_b654.json`; (**c**, **d**) grouped K-fold CV,
design points `cv|10` and `cv|20` of `results/cv_extended_budget.json`; each under the key
`payload.descriptive.gpu_class`, with the budget or fold count of a row in `point`. The classes on the x axis are
the values of `gpu_class` in those rows: the GPU models of the cluster pool, read from `payload.hardware.gpu_model`
of the run records, and "sweep" (value `original sweep`), the registered sweep runs of the original resamples and
seeds (precision only). Which cluster class was absent from the cross-node repeatability runs, and the size of the
class shifts, are stated in `docs/freeze_notes.md` (caveat on GPU classes; rows `N1-*` of
`results/freeze_table.json`). GPU class was not randomised with respect to resample, fold or seed, so differences
between classes are not separable from them and are not read as hardware effects. Plotted values per row:
`A_paired_cells.A` (marker) and `A_paired_cells.ci95_descriptive` (bar), a descriptive percentile interval from a
bootstrap over the paired cells (`A_paired_cells.bootstrap_seed`); cell and run counts in `n_paired_cells` and
`n_runs`; classes without a paired cell are not drawn. Filled markers and solid bars: primary backbone (v2),
adopted after diagnostics of the originally registered backbone; open markers and dashed bars: originally
registered backbone (v1). Diamonds: precision extension; triangles: grouped K-fold CV. Dashed line: the margin δ
(`payload.delta_eV`); dotted line: zero. Labels and rules: `payload.label` and `payload.rules` of both records (the
descriptive extras of the precision and CV implementation row of `docs/deviations.md`, by GPU class). Script:
`figures/code/fig_si_gpu_class.py`.

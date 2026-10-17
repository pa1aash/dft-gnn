# C1: final-network evidence table

Final network: the He-initialised, validation-tuned network (v2 in the repository; `configs/tuned_v2.yaml`).
Record: `results/derived_c1/final_network_summary.json` (git e731935), written by
`analysis/c1/final_network.py`; this file is rendered from it by `analysis/c1/make_docs.py`.

MAE in eV, point with two-sided 95% bootstrap interval. A = MAE_S - MAE_D (positive: the DFT electronic
descriptors lower the error). delta = 0.05 eV. "two-sided inside +-0.05": the two-sided 95% interval lies
strictly inside (-0.05, +0.05) eV. "upper < 0.05": the one-sided 95% upper bound is below 0.05 eV.
RF is RF-Kumagai; B0 is the two-parameter physics floor. Estimators are the existing ones, unchanged:
G1 hierarchical bootstrap (sweep, 2000 replicates, seed 20261008), the A1 precision analysis (30 x 5),
the A1 paired host-cluster bootstrap (CV, 818 hosts), the M1 host bootstrap of pooled folds (LOCO).

| Training hosts | Design | MAE S | MAE D | MAE P | MAE RF | MAE B0 | A | A, two-sided 95% | A, one-sided 95% upper | two-sided inside +-0.05 | upper < 0.05 | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 25 | sweep 10 x 3 | 1.133 [1.074, 1.198] | 1.275 [0.882, 1.829] | 1.177 [1.121, 1.240] | 0.760 [0.709, 0.811] | 0.769 [0.724, 0.823] | -0.142 | [-0.706, +0.259] | +0.211 | no | no | [1] |
| 50 | sweep 10 x 3 | 0.959 [0.891, 1.050] | 1.468 [0.696, 2.743] | 1.083 [1.009, 1.159] | 0.638 [0.601, 0.679] | 0.742 [0.709, 0.777] | -0.509 | [-1.823, +0.277] | +0.241 | no | no | [2] |
| 100 | sweep 10 x 3 | 0.657 [0.599, 0.717] | 0.574 [0.513, 0.655] | 0.722 [0.665, 0.786] | 0.568 [0.537, 0.602] | 0.731 [0.697, 0.766] | +0.083 | [-0.020, +0.167] | +0.156 | no | no | [3] |
| 200 | sweep 10 x 3 | 0.456 [0.434, 0.478] | 0.432 [0.407, 0.458] | 0.574 [0.543, 0.607] | 0.478 [0.453, 0.505] | 0.726 [0.692, 0.757] | +0.024 | [-0.006, +0.052] | +0.047 | no | yes | [4] |
| 400 | sweep 10 x 3 | 0.382 [0.356, 0.412] | 0.328 [0.308, 0.350] | 0.406 [0.380, 0.433] | 0.399 [0.377, 0.424] | 0.724 [0.693, 0.755] | +0.054 | [+0.027, +0.080] | +0.075 | no | no | [5] |
| 400 (30 x 5) | precision 30 x 5 | 0.385 [0.369, 0.401] | 0.319 [0.307, 0.331] | n/a | n/a | n/a | +0.066 | [+0.051, +0.081] | +0.079 | no | no | [6] |
| 654 | sweep 10 x 3 | 0.296 [0.276, 0.317] | 0.280 [0.263, 0.300] | 0.324 [0.304, 0.346] | 0.346 [0.329, 0.365] | 0.722 [0.691, 0.754] | +0.015 | [-0.008, +0.037] | +0.033 | yes | yes | [7] |
| 654 (30 x 5) | precision 30 x 5 | 0.297 [0.285, 0.309] | 0.264 [0.254, 0.275] | n/a | n/a | n/a | +0.033 | [+0.021, +0.045] | +0.043 | yes | yes | [8] |
| 736.2 | CV K = 10 | 0.279 [0.260, 0.297] | 0.255 [0.238, 0.272] | n/a | n/a | n/a | +0.024 | [+0.005, +0.042] | +0.039 | yes | yes | [9] |
| 777.1 | CV K = 20 | 0.267 [0.249, 0.284] | 0.241 [0.225, 0.255] | n/a | n/a | n/a | +0.026 | [+0.010, +0.043] | +0.040 | yes | yes | [10] |
| 654.4 | LOCO (5 folds) | n/a | n/a | n/a | n/a | n/a | +0.041 | [+0.018, +0.064] | +0.060 | no | no | [11] |

[1] results/staging_v2.json payload.budgets.25.mae (S, D, P); results/g1_primary.json payload.descriptive_curves.mae (B0, RF); results/c1c2_v2.json payload.A_mae (point; interval recomputed with the G1 estimator).
[2] results/staging_v2.json payload.budgets.50.mae (S, D, P); results/g1_primary.json payload.descriptive_curves.mae (B0, RF); results/c1c2_v2.json payload.A_mae (point; interval recomputed with the G1 estimator).
[3] results/staging_v2.json payload.budgets.100.mae (S, D, P); results/g1_primary.json payload.descriptive_curves.mae (B0, RF); results/c1c2_v2.json payload.A_mae (point; interval recomputed with the G1 estimator).
[4] results/staging_v2.json payload.budgets.200.mae (S, D, P); results/g1_primary.json payload.descriptive_curves.mae (B0, RF); results/c1c2_v2.json payload.A_mae (point; interval recomputed with the G1 estimator).
[5] results/staging_v2.json payload.budgets.400.mae (S, D, P); results/g1_primary.json payload.descriptive_curves.mae (B0, RF); results/c1c2_v2.json payload.A_mae (point; interval recomputed with the G1 estimator); results/precision_a_b400_b654.json payload.v2.10x3.400.
[6] results/precision_a_b400_b654.json payload.v2.30x5.400. Not available: P, RF and B0 were not run on resamples 10-29 or with seeds 3-4.
[7] results/staging_v2.json payload.budgets.654.mae (S, D, P); results/g1_primary.json payload.descriptive_curves.mae (B0, RF); results/c1c2_v2.json payload.A_mae (point; interval recomputed with the G1 estimator); results/precision_a_b400_b654.json payload.v2.10x3.654.
[8] results/precision_a_b400_b654.json payload.v2.30x5.654. Not available: P, RF and B0 were not run on resamples 10-29 or with seeds 3-4.
[9] results/cv_extended_budget.json payload.v2.k10. Not available: no CV predictions exist for P, RF or B0 (they would need new fits).
[10] results/cv_extended_budget.json payload.v2.k20. Not available: no CV predictions exist for P, RF or B0 (they would need new fits).
[11] results/ingest_m1_recompute.json payload.loco_v2; results/derived_c1/loco_family.json.

## Two-sided intervals at the sizes that carry the claim

| Point | Training hosts | A | two-sided 95% | upper one-sided 95% | inside +-0.05 | upper < 0.05 | interval excludes 0 |
|---|---|---|---|---|---|---|---|
| 654 (sweep 10 x 3) | 654 | +0.0153 | [-0.0076, +0.0368] | +0.0329 | yes | yes | no |
| 654 (30 x 5) | 654 | +0.0328 | [+0.0206, +0.0449] | +0.0432 | yes | yes | yes |
| CV K = 10 | 736.2 | +0.0236 | [+0.0051, +0.0417] | +0.0386 | yes | yes | yes |
| CV K = 20 | 777.1 | +0.0261 | [+0.0100, +0.0426] | +0.0397 | yes | yes | yes |
| LOCO (5 folds) | 654.4 (mean) | +0.0411 | [+0.0184, +0.0641] | +0.0605 | no | no | yes |

At 654 (sweep and pooled 30 x 5), about 736 and about 777 training hosts, the two-sided 95% interval of A
lies inside +-0.05 eV, so "within 0.05 eV" is supported at those sizes, not only "upper bound below
0.05 eV". At 30 x 5 and in both CV designs the interval also excludes zero: D is better than S by a
small, nonzero amount (0.02 to 0.03 eV) at those sizes. Under leave-one-family-out the interval is not
inside +-0.05 eV and the upper bound exceeds 0.05 eV (see `docs/c1_coverage.md`, section LOCO).

## Within-host spread of the predictions (descriptive)

Mean over (resample, test host with >= 2 sites) of the SD of the seed-ensemble prediction across the
host's sites, divided by the same SD of the DFT targets (definition of `results/g1_diagnostics.json`).

| Model | 25 | 50 | 100 | 200 | 400 | 654 |
|---|---|---|---|---|---|---|
| S | 0.012 | 0.017 | 0.123 | 0.265 | 0.185 | 0.412 |
| D | 0.502 | 0.539 | 0.481 | 0.509 | 0.513 | 0.537 |
| P | 0.007 | 0.010 | 0.119 | 0.222 | 0.289 | 0.381 |

## Reproduction

17 comparisons, 4252 values shared with existing records; maximum absolute difference 8.9e-16 eV; all below 1e-9: yes. Per comparison:

| Comparison | Reference | Values | Max abs difference |
|---|---|---|---|
| cv.v1 | results/cv_extended_budget.json payload.v1 | 190 | 0.0e+00 |
| cv.v2 | results/cv_extended_budget.json payload.v2 | 190 | 0.0e+00 |
| loco.v1 | results/ingest_m1_recompute.json payload.loco_v1 | 60 | 0.0e+00 |
| loco.v2 | results/ingest_m1_recompute.json payload.loco_v2 | 34 | 0.0e+00 |
| precision.v1_10x3 | results/precision_a_b400_b654.json payload.v1.10x3 | 360 | 0.0e+00 |
| precision.v1_30x5 | results/precision_a_b400_b654.json payload.v1.30x5 | 800 | 0.0e+00 |
| precision.v2_10x3 | results/precision_a_b400_b654.json payload.v2.10x3 | 360 | 0.0e+00 |
| precision.v2_30x5 | results/precision_a_b400_b654.json payload.v2.30x5 | 800 | 0.0e+00 |
| sweep.baseline_points_vs_standalone_records | results/b0_physics_floor.json, results/rf_kumagai.json payload.outer.*.aggregate.mae.mean (points; their intervals use a host-cluster bootstrap with seed 0) | 12 | 0.0e+00 |
| sweep.baselines_vs_g1_primary | results/g1_primary.json payload.descriptive_curves.mae | 384 | 0.0e+00 |
| sweep.v1_A_400_654_vs_precision_10x3 | results/precision_a_b400_b654.json payload.v1.10x3 | 96 | 0.0e+00 |
| sweep.v1_S_D_A_vs_g1_primary | results/g1_primary.json payload.per_budget (MAE_S, MAE_D, A: mean, ci, upper_one_sided, boot_sd, sd_over_resamples, per_resample) | 288 | 2.2e-16 |
| sweep.v1_S_D_P_vs_staging_v1 | results/staging_v1.json payload.budgets.*.mae | 234 | 1.1e-16 |
| sweep.v1_within_host_spread_vs_g1_diagnostics | results/g1_diagnostics.json payload.within_host_prediction_sd.values | 36 | 2.8e-17 |
| sweep.v2_A_400_654_vs_precision_10x3 | results/precision_a_b400_b654.json payload.v2.10x3 | 96 | 0.0e+00 |
| sweep.v2_S_D_P_vs_staging_v2 | results/staging_v2.json payload.budgets.*.mae | 234 | 1.1e-16 |
| sweep.v2_points_vs_c1c2_v2 | results/c1c2_v2.json payload.A_mae, mae (points only: its intervals came from the collaborator's bootstrap, a known estimator difference listed in results/freeze_table.json) | 78 | 8.9e-16 |

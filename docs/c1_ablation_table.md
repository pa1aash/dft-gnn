# C1: default-initialisation ablation (appendix table)

Ablation network: default (PyTorch) initialisation, tuned for v1 (v1 in the repository; the originally
registered backbone). Record: `results/derived_c1/default_init_ablation.json` (git e731935),
rendered by `analysis/c1/make_docs.py`. Same estimators, seeds and draws as the final-network table
(`docs/c1_final_network_table.md`); MAE in eV with two-sided 95% intervals; A = MAE_S - MAE_D.

| Training hosts | Design | MAE S | MAE D | A | A, two-sided 95% | A, one-sided 95% upper | two-sided inside +-0.05 | upper < 0.05 | Source |
|---|---|---|---|---|---|---|---|---|---|
| 25 | sweep 10 x 3 | 1.147 [1.092, 1.201] | 1.049 [0.922, 1.155] | +0.098 | [-0.000, +0.208] | +0.189 | no | no | [1] |
| 50 | sweep 10 x 3 | 1.007 [0.946, 1.081] | 0.975 [0.869, 1.090] | +0.032 | [-0.051, +0.110] | +0.097 | no | no | [2] |
| 100 | sweep 10 x 3 | 0.721 [0.667, 0.778] | 0.613 [0.557, 0.673] | +0.108 | [+0.032, +0.179] | +0.168 | no | no | [3] |
| 200 | sweep 10 x 3 | 0.516 [0.488, 0.550] | 0.421 [0.380, 0.473] | +0.095 | [+0.046, +0.137] | +0.132 | no | no | [4] |
| 400 | sweep 10 x 3 | 0.376 [0.348, 0.407] | 0.336 [0.317, 0.357] | +0.040 | [+0.010, +0.073] | +0.067 | no | no | [5] |
| 400 (30 x 5) | precision 30 x 5 | 0.360 [0.343, 0.377] | 0.323 [0.311, 0.335] | +0.038 | [+0.021, +0.054] | +0.052 | no | no | [6] |
| 654 | sweep 10 x 3 | 0.273 [0.252, 0.300] | 0.284 [0.267, 0.304] | -0.012 | [-0.035, +0.014] | +0.009 | yes | yes | [7] |
| 654 (30 x 5) | precision 30 x 5 | 0.267 [0.258, 0.276] | 0.275 [0.265, 0.286] | -0.009 | [-0.020, +0.002] | +0.001 | yes | yes | [8] |
| 736.2 | CV K = 10 | 0.249 [0.233, 0.264] | 0.274 [0.257, 0.292] | -0.025 | [-0.041, -0.009] | -0.011 | yes | yes | [9] |
| 777.1 | CV K = 20 | 0.238 [0.224, 0.253] | 0.259 [0.243, 0.275] | -0.021 | [-0.036, -0.006] | -0.009 | yes | yes | [10] |
| 654.4 | LOCO (5 folds) | n/a | n/a | +0.008 | [-0.015, +0.031] | +0.027 | yes | yes | [11] |

[1] results/staging_v1.json payload.budgets.25.mae (S, D, P); results/g1_primary.json payload.descriptive_curves.mae (B0, RF); results/g1_primary.json payload.per_budget.
[2] results/staging_v1.json payload.budgets.50.mae (S, D, P); results/g1_primary.json payload.descriptive_curves.mae (B0, RF); results/g1_primary.json payload.per_budget.
[3] results/staging_v1.json payload.budgets.100.mae (S, D, P); results/g1_primary.json payload.descriptive_curves.mae (B0, RF); results/g1_primary.json payload.per_budget.
[4] results/staging_v1.json payload.budgets.200.mae (S, D, P); results/g1_primary.json payload.descriptive_curves.mae (B0, RF); results/g1_primary.json payload.per_budget.
[5] results/staging_v1.json payload.budgets.400.mae (S, D, P); results/g1_primary.json payload.descriptive_curves.mae (B0, RF); results/g1_primary.json payload.per_budget; results/precision_a_b400_b654.json payload.v1.10x3.400.
[6] results/precision_a_b400_b654.json payload.v1.30x5.400. Not available: P, RF and B0 were not run on resamples 10-29 or with seeds 3-4.
[7] results/staging_v1.json payload.budgets.654.mae (S, D, P); results/g1_primary.json payload.descriptive_curves.mae (B0, RF); results/g1_primary.json payload.per_budget; results/precision_a_b400_b654.json payload.v1.10x3.654.
[8] results/precision_a_b400_b654.json payload.v1.30x5.654. Not available: P, RF and B0 were not run on resamples 10-29 or with seeds 3-4.
[9] results/cv_extended_budget.json payload.v1.k10. Not available: no CV predictions exist for P, RF or B0 (they would need new fits).
[10] results/cv_extended_budget.json payload.v1.k20. Not available: no CV predictions exist for P, RF or B0 (they would need new fits).
[11] results/ingest_m1_recompute.json payload.loco_v1; results/derived_c1/loco_family.json.

## Site resolution of S (S10 and S10b diagnostics)

Ratio of the within-host SD of the predictions to the within-host SD of the DFT targets (mean over
resamples and test hosts with >= 2 sites; seed-ensemble predictions). The v1 values reproduce
`results/g1_diagnostics.json`; the v2 row uses the same code. A ratio near 0 means S predicts one value
per host.

| Network | Model | 25 | 50 | 100 | 200 | 400 | 654 |
|---|---|---|---|---|---|---|---|
| default init (ablation) | S | 0.001 | 0.004 | 0.000 | 0.001 | 0.272 | 0.454 |
| final | S | 0.012 | 0.017 | 0.123 | 0.265 | 0.185 | 0.412 |
| default init (ablation) | D | 0.168 | 0.149 | 0.497 | 0.521 | 0.475 | 0.478 |
| final | D | 0.502 | 0.539 | 0.481 | 0.509 | 0.513 | 0.537 |

Mean within-host target SD: 0.254 eV (identical for every budget and network).

S10b checkpoint forensic (v1 S, resample 0, seed 0, 30 hosts; median SD across labelled sites over the
median target SD, `results/s_site_resolution_forensic.json`): B = 25: 0.0036, B = 50: 0.0024, B = 100: 0.0010, B = 200: 0.0002, B = 400: 0.1365, B = 654: 0.5420.

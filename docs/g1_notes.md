# G1 notes (S10)

Pre-registered primary analysis of ANALYSIS_PLAN §7, run as frozen (tag `prereg-v1`) with the clarifications
logged in `docs/deviations.md` on 2026-10-08 before any analysis code ran on the sweep predictions. Every number
below is read from `results/g1_primary.json`, `results/g1_within_host.json`, `results/g1_cap_sensitivity.json`,
`results/g1_variance.json` and `results/g1_diagnostics.json`. Energies are in eV.

Setup: 10 outer resamples, 164 test hosts each (359 to 334 sites), training budgets B = 25, 50, 100, 200, 400 and
654 hosts. S and D (D-state) predictions are the seed-ensemble mean over seeds 0, 1 and 2. A = MAE_S − MAE_D;
positive A means the DFT electronic descriptors lower the error. Intervals: paired hierarchical bootstrap, 2000
replicates, seed 20261008, one set of draws shared by every model, budget and metric. Two-sided 95% intervals in
brackets; the one-sided 95% upper bound is the 95th percentile. Margin δ = 0.05 eV.

## G1 outcome

**G1 PASS: N* found at 654**

The evaluation table passed every integrity assertion (378 model-resample-budget-seed cells, including the 18
epoch-cap runs) and reproduces the S09 sanity table to 3 decimals for all 12 (model, budget) cells. The figure is
`figures/main/fig_g1_learning_curves.pdf` with its caption file.

## Primary metric: site-level test MAE (C1, C2)

| B | MAE_S | MAE_D | A [two-sided 95%] | one-sided 95% upper bound | below delta |
|---:|---|---|---|---:|:---:|
| 25 | 1.147 [1.092, 1.201] | 1.049 [0.922, 1.155] | +0.098 [-0.000, +0.208] | +0.189 | no |
| 50 | 1.007 [0.946, 1.081] | 0.975 [0.869, 1.090] | +0.032 [-0.051, +0.110] | +0.097 | no |
| 100 | 0.721 [0.667, 0.778] | 0.613 [0.557, 0.673] | +0.108 [+0.032, +0.179] | +0.168 | no |
| 200 | 0.516 [0.488, 0.550] | 0.421 [0.380, 0.473] | +0.095 [+0.046, +0.137] | +0.132 | no |
| 400 | 0.376 [0.348, 0.407] | 0.336 [0.317, 0.357] | +0.040 [+0.010, +0.073] | +0.067 | no |
| 654 | 0.273 [0.252, 0.300] | 0.284 [0.267, 0.304] | -0.012 [-0.035, +0.014] | +0.009 | yes |

N* = 654 (the one-sided upper bound is below δ at B = 654 only; the largest tested budget, so the "every larger
budget" condition holds trivially there).

C2 ceiling (A at B = 654): −0.012 eV, two-sided 95% interval [−0.035, +0.014].

Per-resample A (seed ensemble):

| B | r0 | r1 | r2 | r3 | r4 | r5 | r6 | r7 | r8 | r9 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 25 | -0.050 | +0.096 | +0.168 | +0.187 | -0.061 | +0.440 | +0.066 | +0.125 | +0.031 | -0.018 |
| 50 | +0.241 | +0.012 | -0.195 | -0.089 | +0.185 | +0.060 | -0.042 | +0.119 | +0.021 | +0.009 |
| 100 | +0.089 | +0.123 | +0.107 | +0.287 | +0.180 | +0.135 | +0.025 | +0.233 | -0.019 | -0.083 |
| 200 | +0.099 | +0.064 | +0.129 | +0.071 | +0.157 | +0.154 | +0.040 | +0.128 | +0.166 | -0.057 |
| 400 | +0.075 | -0.003 | +0.113 | +0.024 | +0.086 | +0.028 | -0.034 | +0.024 | +0.075 | +0.014 |
| 654 | -0.014 | +0.010 | -0.034 | +0.067 | -0.012 | -0.006 | -0.076 | -0.021 | -0.011 | -0.020 |

## Descriptive curves (no test)

Site-level test MAE with the same bootstrap draws. They reproduce `docs/baselines.md`.

| B | B0 | RF-Kumagai | RF-electronic | RF-structural | host-mean oracle |
|---:|---|---|---|---|---|
| 25 | 0.769 [0.724, 0.823] | 0.760 [0.709, 0.811] | 0.767 [0.715, 0.819] | 1.016 [0.947, 1.092] | 0.153 [0.141, 0.167] |
| 50 | 0.742 [0.709, 0.777] | 0.638 [0.601, 0.679] | 0.658 [0.625, 0.693] | 0.849 [0.785, 0.917] | 0.153 [0.141, 0.167] |
| 100 | 0.731 [0.697, 0.766] | 0.568 [0.537, 0.602] | 0.596 [0.565, 0.631] | 0.659 [0.608, 0.716] | 0.153 [0.141, 0.167] |
| 200 | 0.726 [0.692, 0.757] | 0.478 [0.453, 0.505] | 0.532 [0.508, 0.558] | 0.528 [0.499, 0.562] | 0.153 [0.141, 0.167] |
| 400 | 0.724 [0.693, 0.755] | 0.399 [0.377, 0.424] | 0.469 [0.447, 0.492] | 0.439 [0.418, 0.460] | 0.153 [0.141, 0.167] |
| 654 | 0.722 [0.691, 0.754] | 0.346 [0.329, 0.365] | 0.423 [0.404, 0.444] | 0.386 [0.366, 0.407] | 0.153 [0.141, 0.167] |

## Secondary metric: within-host residual MAE

Test hosts with at least two sites per resample: 105, 100, 103, 103, 99, 96, 109, 106, 99, 102.

| B | S | D | A_within [two-sided 95%] | one-sided upper | below delta |
|---:|---|---|---|---:|:---:|
| 25 | 0.187 [0.172, 0.204] | 0.184 [0.170, 0.199] | +0.003 [-0.000, +0.009] | +0.008 | yes |
| 50 | 0.187 [0.172, 0.204] | 0.184 [0.169, 0.200] | +0.004 [+0.000, +0.007] | +0.007 | yes |
| 100 | 0.187 [0.172, 0.204] | 0.183 [0.167, 0.201] | +0.004 [-0.008, +0.015] | +0.013 | yes |
| 200 | 0.187 [0.172, 0.204] | 0.185 [0.171, 0.199] | +0.003 [-0.006, +0.011] | +0.010 | yes |
| 400 | 0.170 [0.156, 0.186] | 0.174 [0.161, 0.188] | -0.003 [-0.012, +0.005] | +0.004 | yes |
| 654 | 0.143 [0.130, 0.157] | 0.161 [0.148, 0.175] | -0.018 [-0.030, -0.007] | -0.008 | yes |

N*_within = 25 (the one-sided upper bound of A_within is below δ at every tested budget).

## Host-mean MAE (descriptive)

| B | S | D | S minus D |
|---:|---|---|---|
| 25 | 1.159 [1.108, 1.210] | 1.039 [0.916, 1.147] | +0.120 [+0.023, +0.226] |
| 50 | 1.017 [0.959, 1.086] | 0.968 [0.852, 1.089] | +0.049 [-0.052, +0.141] |
| 100 | 0.740 [0.692, 0.789] | 0.608 [0.552, 0.665] | +0.132 [+0.061, +0.201] |
| 200 | 0.534 [0.497, 0.577] | 0.409 [0.364, 0.461] | +0.125 [+0.082, +0.166] |
| 400 | 0.365 [0.335, 0.395] | 0.316 [0.296, 0.336] | +0.049 [+0.019, +0.079] |
| 654 | 0.258 [0.233, 0.287] | 0.256 [0.240, 0.272] | +0.002 [-0.021, +0.027] |

## Epoch-cap sensitivity (B = 654, resamples 0-2, seeds 0-2)

| quantity | value |
|---|---|
| A(200) | −0.013 [−0.044, +0.017] |
| A(600) | −0.013 [−0.044, +0.017] |
| A(600) − A(200) | +0.000 [+0.000, +0.000] |
| per-resample A(200) = A(600) | −0.014, +0.010, −0.034 |
| MAE_S (cap 200 and cap 600) | 0.283 [0.260, 0.307] |
| MAE_D (cap 200 and cap 600) | 0.296 [0.263, 0.330] |

Rule (logged 2026-10-07): |A(600) − A(200)| = 0.000 eV ≤ 0.02 eV, so the primary result is **cap-insensitive**.
The resample level of this bootstrap draws from only three resamples. All 18 runs with the 600-epoch cap
reached their best validation epoch at the same epoch as their 200-epoch twins, and their prediction files are
byte-identical (equal sha256; `results/g1_diagnostics.json`). The difference is therefore exactly zero.

## Seed and resample variance (§11, descriptive)

| model | B | mean single-seed MAE | seed SD (mean over resamples) | seed-ensemble MAE | resample SD of ensemble MAE |
|---|---:|---:|---:|---:|---:|
| S | 25 | 1.240 | 0.111 | 1.147 | 0.060 |
| S | 50 | 1.108 | 0.143 | 1.007 | 0.092 |
| S | 100 | 0.821 | 0.140 | 0.721 | 0.083 |
| S | 200 | 0.588 | 0.043 | 0.516 | 0.037 |
| S | 400 | 0.412 | 0.061 | 0.376 | 0.044 |
| S | 654 | 0.307 | 0.045 | 0.273 | 0.036 |
| D | 25 | 1.102 | 0.152 | 1.049 | 0.172 |
| D | 50 | 1.043 | 0.143 | 0.975 | 0.184 |
| D | 100 | 0.662 | 0.092 | 0.613 | 0.083 |
| D | 200 | 0.455 | 0.038 | 0.421 | 0.073 |
| D | 400 | 0.361 | 0.021 | 0.336 | 0.023 |
| D | 654 | 0.303 | 0.015 | 0.284 | 0.023 |

Single-seed and seed-ensemble A (seed s of S paired with seed s of D):

| B | ensemble A | SD over resamples (ensemble A) | mean single-seed A | SD over 30 single-seed A | mean within-resample seed SD of single-seed A |
|---:|---:|---:|---:|---:|---:|
| 25 | +0.098 | 0.148 | +0.138 | 0.260 | 0.232 |
| 50 | +0.032 | 0.128 | +0.064 | 0.244 | 0.211 |
| 100 | +0.108 | 0.113 | +0.160 | 0.161 | 0.127 |
| 200 | +0.095 | 0.069 | +0.132 | 0.078 | 0.050 |
| 400 | +0.040 | 0.045 | +0.052 | 0.075 | 0.064 |
| 654 | -0.012 | 0.036 | +0.005 | 0.059 | 0.048 |
{'below_delta': {'100': False, '200': False, '25': False, '400': False, '50': False, '654': True}, 'budgets_tested': [25, 50, 100, 200, 400, 654], 'delta_eV': 0.05, 'n_star': 654, 'report': '654'} 25 {'A': -0.011606757286799654, 'budget': 654, 'ci': [-0.03476271135087025, 0.014300108125676341], 'ci_level': 0.95, 'per_resample': [-0.013941613501276096, 0.01011690456319736, -0.03413014008034909, 0.06667022582217602, -0.011949635289139227, -0.005543040553066703, -0.07552080183001753, -0.02081418176077493, -0.010799770098259498, -0.020155520140486854]}

## C0, second half (formula-grouped protocol)

S at B = 654 on the formula-grouped protocol: seed-ensemble MAE 0.273 [0.252, 0.300] eV, against the published
0.29 eV (Kiyohara et al.) and the official C0 on Kiyohara's split, 0.283 eV (`results/c0_official.json`). The
mean single-seed MAE is 0.307 eV.

## Observations recorded without interpretation

- Within-host prediction spread (`results/g1_diagnostics.json`): averaged over test hosts with two or more sites,
  the SD of S's seed-ensemble predictions across a host's sites is 1.8e-4, 1.1e-3, 3.8e-5 and 2.0e-4 eV at
  B = 25, 50, 100 and 200, and 0.069 and 0.115 eV at B = 400 and 654. For D it is 0.043, 0.038, 0.126, 0.132,
  0.121 and 0.121 eV. The SD of the targets is 0.254 eV. Accordingly, S's within-host residual MAE at B ≤ 200
  (0.187) equals the value of a predictor that is constant within each host (B0 and the host-mean oracle,
  0.187 at B = 654 in `docs/baselines.md`). Budgets 25 to 200 use the 50- and 200-host anchor hyperparameters
  (set2set pooling for S); 400 and 654 use the 654-host anchor (mean pooling).
- A at B = 654 is negative in 8 of 10 resamples; its two-sided interval contains 0.

## What the result is

Against the frozen decision rules: the one-sided 95% upper bound on A is at or above δ = 0.05 eV at B = 25, 50,
100, 200 and 400 (0.189, 0.097, 0.168, 0.132 and 0.067 eV) and below δ at B = 654 (0.009 eV), so N* = 654. The
C2 ceiling, A at B = 654, is −0.012 eV with two-sided 95% interval [−0.035, +0.014] eV. For the within-host
residual MAE the upper bound is below δ at every tested budget, so N*_within = 25. The epoch-cap rule returns
cap-insensitive (|A(600) − A(200)| = 0.000 eV ≤ 0.02 eV). Under §14 the G1 gate passes.

## Choices fixed in advance that could have changed the result

1. Margin δ = 0.05 eV (§7, `stats.delta_eV`).
2. The one-sided 95% upper bound (95th percentile) as the test statistic, with no multiplicity correction (§7).
3. The requirement that the bound stay below δ at every larger tested budget (§7); the tested budgets
   {25, 50, 100, 200, 400, 654} (§2).
4. Strict comparison U < δ, and N* reported as ">654" if no budget qualifies (clarification 2026-10-08).
5. Seed-ensemble mean over three seeds as the prediction of S and D (§7), rather than per-seed MAEs.
6. Site-level MAE as the primary metric; within-host residual MAE and host-mean MAE as secondary (§7).
7. The hierarchical bootstrap design: 2000 replicates, resamples then hosts, percentile intervals, seed
   20261008, draws shared across models, budgets and metrics (§7; clarification 2026-10-08).
8. No truncation of negative A (clarification 2026-10-08).
9. D = D-state, selected in S08 by the pre-registered validation rule before any test result existed (§4).
10. Hyperparameters per budget from the fixed anchor mapping (§6, `configs/tuned_v1.yaml`).
11. Epoch cap 200 and patience 30 (S07 rule), and the cap-sensitivity rule |ΔA| ≤ 0.02 eV (2026-10-07).
12. The splits, test-host sets and nested budgets (`splits/`, sha256 manifest).
13. Within-host metric over hosts with at least two sites, same δ for N*_within (clarification 2026-10-08).

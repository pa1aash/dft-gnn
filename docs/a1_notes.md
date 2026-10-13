# A1 notes: precision extension (N4) and grouped K-fold CV (N3)

Labels: every result here is EXTENSION. The v2 results are the primary backbone and POST HOC; v1 is the originally
registered backbone. v2 was adopted after diagnostics of v1 and is not pre-registered. v1 versus v2 is descriptive,
with no test.

Rules: `docs/deviations.md`, the row of 2026-10-11 (§7, §11) fixing the N4 and N3 analysis rules (logged before
any cv or precision result existed) and the row of 2026-10-14 (§7, §11), which restates those rules verbatim and
fixes the implementation, logged before any number of this analysis was computed. No 2026-10-12 row concerns these
rules. Margin δ = 0.05 eV; one-sided 95% upper bound = 95th percentile; comparisons with δ are strict.

Records (all via `write_result`, each from a committed script on a clean tree):

| record | script | content |
|---|---|---|
| `results/precision_cv_eval_table.json` | `analysis/precision_cv_eval_table.py` | integrity checks; long tables `results/analysis/precision_eval_long.parquet`, `cv_eval_long.parquet`, `precision_cv_runs.parquet` |
| `results/precision_a_b400_b654.json` | `analysis/precision_analysis.py` | v2 and v1 blocks, subsets 30 x 5, 10 x 3, 10 x 5, 30 x 3; sanity; GPU-class and capped tables |
| `results/cv_extended_budget.json` | `analysis/cv_analysis.py` | v2 and v1 blocks at K = 10 and 20; extended-budget statement; GPU-class and capped tables |
| `results/precision_g1_v1.json`, `results/precision_g1_v2.json`, `results/cv_g1_v1.json`, `results/cv_g1_v2.json` | the two analysis scripts | figure inputs, schema of `results/c1c2_<arm>.json` (`docs/figure_style.md`) |

Inputs: precision 480 (v1) + 480 (v2) new runs and, for r = 0..9, seeds 0-2, the original sweep runs (120 + 120);
CV 180 (v1) + 180 (v2). All passed the integrity assertions of `scripts/analysis/build_eval_table.py`: each run
covers the test sites of its split exactly once, all predictions are finite, no test host is among the training
hosts, targets and hosts equal the universe, prediction hashes and recorded MAEs match. The folds of K = 10 (81 or
82 test hosts, 736 or 737 training hosts) and K = 20 (40 or 41 test hosts, 777 or 778 training hosts) each
partition the 818 hosts; every one of the 1726 sites has one pooled out-of-fold prediction per model and K.

## Sanity checks (before reporting)

The 10 x 3 cells of the precision pool are the original sweep runs in both backbones; no precision-stage spec
repeats a sweep spec, so no re-run on a different GPU class enters this comparison. The new pipeline reproduces the
registered point values A, MAE_S, MAE_D and A_within at B = 400 and 654 for v1 (`results/g1_primary.json`,
`results/c1c2_v1.json`) and v2 (`results/c1c2_v2.json`), and for v1 also the G1 two-sided interval and one-sided
bound with the same draws:

- v1|400: max |difference| 1.7e-16 eV against results/g1_primary.json per_budget (A_within: results/c1c2_v1.json A_within_host) (within 1e-6: True)
- v1|654: max |difference| 1.1e-16 eV against results/g1_primary.json per_budget (A_within: results/c1c2_v1.json A_within_host) (within 1e-6: True)
- v2|400: max |difference| 5.6e-17 eV against results/c1c2_v2.json A_mae, mae, A_within_host (within 1e-6: True)
- v2|654: max |difference| 1.6e-17 eV against results/c1c2_v2.json A_mae, mae, A_within_host (within 1e-6: True)
- v1 seed predictions vs eval_table.parquet: 41328 rows, 0 unmatched, max |difference| 0.0

All differences are floating-point rounding (largest 1.7e-16 eV); there is no mismatch to report. For v2 at B = 654
the G1 estimator gives a one-sided bound of +0.0329 eV on the 10 x 3 runs, against +0.0328 eV in
`results/c1c2_v2.json`, whose bootstrap implementation differs (`scripts/analysis_c1c2.py`); the point values are
identical. The bootstrap seed of the CV analysis is 20261008, as fixed by the 2026-10-11 rule; the brief for this
step named 20261014, which would have changed a fixed rule, so 20261014 is used only for the new descriptive
GPU-class draws (2026-10-14 row, item c).

## Tables

### Table 1. Precision extension: site-level test MAE and A (eV)

**v2 (primary backbone, POST HOC)**

| set | B | MAE_S | MAE_D | A [two-sided 95%] | one-sided upper | below δ |
|---|---:|---|---|---|---:|:---:|
| 30 x 5 (pooled) | 400 | 0.385 [0.369, 0.401] | 0.319 [0.307, 0.331] | +0.066 [+0.051, +0.081] | +0.079 | no |
| 30 x 5 (pooled) | 654 | 0.297 [0.285, 0.309] | 0.264 [0.254, 0.275] | +0.033 [+0.021, +0.045] | +0.043 | yes |
| 10 x 3 (registered) | 400 | 0.382 [0.356, 0.412] | 0.328 [0.308, 0.350] | +0.054 [+0.027, +0.080] | +0.075 | no |
| 10 x 3 (registered) | 654 | 0.296 [0.276, 0.317] | 0.280 [0.263, 0.300] | +0.015 [-0.008, +0.037] | +0.033 | yes |
| 10 x 5 | 400 | 0.376 [0.350, 0.407] | 0.322 [0.302, 0.344] | +0.054 [+0.023, +0.083] | +0.078 | no |
| 10 x 5 | 654 | 0.293 [0.275, 0.313] | 0.274 [0.256, 0.294] | +0.020 [-0.006, +0.042] | +0.039 | yes |
| 30 x 3 | 400 | 0.393 [0.375, 0.409] | 0.327 [0.315, 0.339] | +0.066 [+0.050, +0.081] | +0.079 | no |
| 30 x 3 | 654 | 0.300 [0.287, 0.313] | 0.269 [0.258, 0.279] | +0.031 [+0.019, +0.043] | +0.042 | yes |

**v1 (originally registered backbone)**

| set | B | MAE_S | MAE_D | A [two-sided 95%] | one-sided upper | below δ |
|---|---:|---|---|---|---:|:---:|
| 30 x 5 (pooled) | 400 | 0.360 [0.343, 0.377] | 0.323 [0.311, 0.335] | +0.038 [+0.021, +0.054] | +0.052 | no |
| 30 x 5 (pooled) | 654 | 0.267 [0.258, 0.276] | 0.275 [0.265, 0.286] | -0.009 [-0.020, +0.002] | +0.001 | yes |
| 10 x 3 (registered) | 400 | 0.376 [0.348, 0.407] | 0.336 [0.317, 0.357] | +0.040 [+0.010, +0.073] | +0.067 | no |
| 10 x 3 (registered) | 654 | 0.273 [0.252, 0.300] | 0.284 [0.267, 0.304] | -0.012 [-0.035, +0.014] | +0.009 | yes |
| 10 x 5 | 400 | 0.353 [0.327, 0.384] | 0.329 [0.308, 0.352] | +0.024 [-0.006, +0.057] | +0.052 | no |
| 10 x 5 | 654 | 0.264 [0.249, 0.280] | 0.279 [0.263, 0.295] | -0.015 [-0.035, +0.003] | +0.000 | yes |
| 30 x 3 | 400 | 0.375 [0.357, 0.392] | 0.329 [0.317, 0.341] | +0.047 [+0.029, +0.064] | +0.061 | no |
| 30 x 3 | 654 | 0.273 [0.262, 0.285] | 0.280 [0.270, 0.291] | -0.007 [-0.020, +0.006] | +0.003 | yes |

### Table 2. Grouped K-fold CV: pooled out-of-fold site MAE and A (eV)

| backbone | K | training hosts (mean) | MAE_S | MAE_D | A [two-sided 95%] | one-sided upper | below δ | fold-level SD of A |
|---|---:|---:|---|---|---|---:|:---:|---:|
| v2 | 10 | 736.2 | 0.279 [0.260, 0.297] | 0.255 [0.238, 0.272] | +0.024 [+0.005, +0.042] | +0.039 | yes | 0.029 |
| v2 | 20 | 777.1 | 0.267 [0.249, 0.284] | 0.241 [0.225, 0.255] | +0.026 [+0.010, +0.043] | +0.040 | yes | 0.039 |
| v1 | 10 | 736.2 | 0.249 [0.233, 0.264] | 0.274 [0.257, 0.292] | -0.025 [-0.041, -0.009] | -0.011 | yes | 0.032 |
| v1 | 20 | 777.1 | 0.238 [0.224, 0.253] | 0.259 [0.243, 0.275] | -0.021 [-0.036, -0.006] | -0.009 | yes | 0.037 |

### Table 3. Extended-budget statement (one-sided 95% upper bound on A, eV; δ = 0.05)

| backbone | B = 654 (10 x 3) | K = 10 (736.2 hosts) | K = 20 (777.1 hosts) | passing points | failing points | statement |
|---|---:|---:|---:|---|---|---|
| v2 | +0.033 | +0.039 | +0.040 | 654, k10, k20 | none | holds |
| v1 | +0.009 | -0.011 | -0.009 | 654, k10, k20 | none | holds |

Precision statement (pooled 30 x 5 at B = 654): v2: upper +0.043, holds; v1: upper +0.001, holds. At B = 400: v2: upper +0.079, not below δ; v1: upper +0.052, not below δ.

### Table 4. Within-host residual MAE and A_within (eV)

| backbone | point | within-host S | within-host D | A_within [two-sided 95%] | one-sided upper |
|---|---|---|---|---|---:|
| v2 | precision 30 x 5, B = 400 | 0.174 [0.165, 0.184] | 0.164 [0.156, 0.172] | +0.010 [+0.006, +0.014] | +0.014 |
| v2 | precision 30 x 5, B = 654 | 0.153 [0.144, 0.161] | 0.143 [0.136, 0.150] | +0.010 [+0.004, +0.016] | +0.015 |
| v2 | precision 10 x 3, B = 400 | 0.175 [0.160, 0.191] | 0.168 [0.155, 0.182] | +0.007 [-0.001, +0.014] | +0.013 |
| v2 | precision 10 x 3, B = 654 | 0.150 [0.137, 0.164] | 0.152 [0.139, 0.166] | -0.002 [-0.013, +0.009] | +0.007 |
| v2 | CV K = 10 | 0.141 [0.128, 0.155] | 0.136 [0.124, 0.150] | +0.005 [-0.004, +0.013] | +0.012 |
| v2 | CV K = 20 | 0.141 [0.127, 0.155] | 0.132 [0.120, 0.144] | +0.009 [-0.001, +0.018] | +0.016 |
| v1 | precision 30 x 5, B = 400 | 0.162 [0.154, 0.171] | 0.170 [0.162, 0.178] | -0.007 [-0.012, -0.003] | -0.003 |
| v1 | precision 30 x 5, B = 654 | 0.139 [0.133, 0.145] | 0.158 [0.150, 0.165] | -0.019 [-0.024, -0.014] | -0.014 |
| v1 | precision 10 x 3, B = 400 | 0.170 [0.156, 0.186] | 0.174 [0.161, 0.188] | -0.003 [-0.012, +0.005] | +0.004 |
| v1 | precision 10 x 3, B = 654 | 0.143 [0.130, 0.157] | 0.161 [0.148, 0.175] | -0.018 [-0.030, -0.007] | -0.008 |
| v1 | CV K = 10 | 0.134 [0.122, 0.147] | 0.157 [0.141, 0.173] | -0.022 [-0.033, -0.013] | -0.015 |
| v1 | CV K = 20 | 0.132 [0.120, 0.144] | 0.154 [0.140, 0.169] | -0.022 [-0.032, -0.013] | -0.015 |

### Table 5. A by GPU class (descriptive, no test)

A_class: mean over paired cells (S and D of the same cell on the same class) of single-run MAE_S − MAE_D; interval: descriptive bootstrap over cells. n runs S / D: all runs of that class at that point.

| point | backbone | GPU class | n runs S / D | mean single-run MAE S / D | paired cells | A_class [descriptive 95%] |
|---|---|---|---|---|---:|---|
| precision 400 | v2 | A10 | 43 / 50 | 0.435 / 0.354 | 20 | +0.061 [+0.038, +0.086] |
| precision 400 | v2 | RTX 3090 | 26 / 41 | 0.426 / 0.345 | 4 | +0.050 [-0.019, +0.120] |
| precision 400 | v2 | L4 | 9 / 2 | 0.469 / 0.369 | 1 | +0.041 [+0.041, +0.041] |
| precision 400 | v2 | RTX 4090 (not in N1) | 42 / 27 | 0.446 / 0.350 | 5 | +0.108 [+0.086, +0.126] |
| precision 400 | v2 | original sweep | 30 / 30 | 0.429 / 0.353 | 30 | +0.076 [+0.056, +0.094] |
| precision 400 | v1 | A10 | 81 / 58 | 0.404 / 0.343 | 35 | +0.054 [+0.035, +0.078] |
| precision 400 | v1 | RTX 3090 | 10 / 41 | 0.398 / 0.351 | 3 | +0.036 [-0.031, +0.107] |
| precision 400 | v1 | L4 | 29 / 20 | 0.402 / 0.356 | 2 | +0.068 [+0.049, +0.088] |
| precision 400 | v1 | RTX 4090 (not in N1) | 0 / 1 | - / 0.303 | 0 | - |
| precision 400 | v1 | original sweep | 30 / 30 | 0.412 / 0.361 | 30 | +0.052 [+0.027, +0.077] |
| precision 654 | v2 | A10 | 34 / 49 | 0.337 / 0.284 | 16 | +0.056 [+0.039, +0.075] |
| precision 654 | v2 | RTX 3090 | 40 / 34 | 0.335 / 0.283 | 14 | +0.047 [+0.028, +0.065] |
| precision 654 | v2 | L4 | 7 / 1 | 0.330 / 0.291 | 0 | - |
| precision 654 | v2 | RTX 4090 (not in N1) | 39 / 36 | 0.339 / 0.290 | 13 | +0.046 [+0.020, +0.072] |
| precision 654 | v2 | original sweep | 30 / 30 | 0.325 / 0.303 | 30 | +0.023 [+0.007, +0.040] |
| precision 654 | v1 | A10 | 81 / 54 | 0.302 / 0.296 | 34 | +0.006 [-0.004, +0.017] |
| precision 654 | v1 | RTX 3090 | 6 / 48 | 0.324 / 0.299 | 2 | -0.008 [-0.013, -0.003] |
| precision 654 | v1 | L4 | 32 / 17 | 0.303 / 0.304 | 4 | +0.004 [-0.023, +0.043] |
| precision 654 | v1 | RTX 4090 (not in N1) | 1 / 1 | 0.284 / 0.296 | 1 | -0.012 [-0.012, -0.012] |
| precision 654 | v1 | original sweep | 30 / 30 | 0.307 / 0.303 | 30 | +0.005 [-0.015, +0.026] |
| cv 10 | v2 | A10 | 13 / 9 | 0.289 / 0.276 | 4 | +0.032 [-0.013, +0.060] |
| cv 10 | v2 | RTX 3090 | 17 / 21 | 0.323 / 0.273 | 12 | +0.046 [+0.016, +0.077] |
| cv 10 | v1 | A10 | 15 / 21 | 0.302 / 0.291 | 7 | +0.024 [-0.016, +0.074] |
| cv 10 | v1 | L4 | 15 / 9 | 0.269 / 0.307 | 1 | -0.029 [-0.029, -0.029] |
| cv 20 | v2 | A10 | 6 / 31 | 0.291 / 0.258 | 4 | +0.049 [+0.032, +0.064] |
| cv 20 | v2 | RTX 3090 | 54 / 29 | 0.290 / 0.265 | 27 | +0.029 [+0.004, +0.052] |
| cv 20 | v1 | A10 | 40 / 50 | 0.275 / 0.275 | 32 | -0.006 [-0.021, +0.008] |
| cv 20 | v1 | L4 | 20 / 10 | 0.260 / 0.305 | 2 | -0.029 [-0.051, -0.007] |

### Table 6. Capped (epochs_run ≥ max_epochs = 200) versus uncapped runs (descriptive, no test)

| point | backbone | model | runs | capped | uncapped | mean single-run MAE, capped | uncapped | capped by source |
|---|---|---|---:|---:|---:|---:|---:|---|
| precision 400 | v2 | S | 150 | 4 | 146 | 0.368 | 0.439 | precision 3, sweep 1 |
| precision 400 | v2 | D | 150 | 0 | 150 | - | 0.351 | precision 0, sweep 0 |
| precision 400 | v1 | S | 150 | 20 | 130 | 0.360 | 0.412 | precision 15, sweep 5 |
| precision 400 | v1 | D | 150 | 4 | 146 | 0.324 | 0.351 | precision 4, sweep 0 |
| precision 654 | v2 | S | 150 | 14 | 136 | 0.289 | 0.339 | precision 11, sweep 3 |
| precision 654 | v2 | D | 150 | 6 | 144 | 0.260 | 0.290 | precision 5, sweep 1 |
| precision 654 | v1 | S | 150 | 35 | 115 | 0.280 | 0.311 | precision 27, sweep 8 |
| precision 654 | v1 | D | 150 | 3 | 147 | 0.299 | 0.299 | precision 1, sweep 2 |
| cv 10 | v2 | S | 30 | 4 | 26 | 0.273 | 0.313 | - |
| cv 10 | v2 | D | 30 | 3 | 27 | 0.272 | 0.274 | - |
| cv 10 | v1 | S | 30 | 12 | 18 | 0.269 | 0.296 | - |
| cv 10 | v1 | D | 30 | 2 | 28 | 0.234 | 0.300 | - |
| cv 20 | v2 | S | 60 | 13 | 47 | 0.273 | 0.295 | - |
| cv 20 | v2 | D | 60 | 4 | 56 | 0.259 | 0.262 | - |
| cv 20 | v1 | S | 60 | 30 | 30 | 0.258 | 0.282 | - |
| cv 20 | v1 | D | 60 | 4 | 56 | 0.296 | 0.279 | - |

## What the measurements show

Against the frozen rules:

1. **Extended-budget statement.** The one-sided 95% upper bound on A is below δ at B = 654 (registered G1
   result), at about 736 training hosts (K = 10) and at about 777 (K = 20), for v2 and for v1 (Table 3). No point
   fails. The statement holds for both backbones.
2. **Precision statement at 654.** The pooled 30 x 5 upper bound at B = 654 is below δ for both backbones
   (v2 +0.043, v1 +0.001 eV), so the non-inferiority bound holds at 654 under the precision rule. Every subset
   (10 x 3, 10 x 5, 30 x 3) also lies below δ at 654.
3. **B = 400.** The pooled 30 x 5 upper bound at B = 400 is not below δ for either backbone (v2 +0.079, v1
   +0.052 eV). For v1 it misses δ by 0.002 eV; the 10 x 5 subset is also at +0.052. N* is not moved below 654 by
   the precision extension.
4. **v2: the advantage is positive and below δ.** For v2, A at B = 654 pooled is +0.033 [+0.021, +0.045] eV, and
   with CV +0.024 [+0.005, +0.042] (K = 10) and +0.026 [+0.010, +0.043] (K = 20). The two-sided intervals exclude
   zero at all three points: on the primary backbone the descriptors lower the site error by a small amount that is
   distinguishable from zero and whose upper bound is below the margin.
5. **v1: the sign reverses beyond 654.** For v1, A at B = 654 pooled is -0.009 [-0.020, +0.002] eV; with CV it is
   -0.025 [-0.041, -0.009] (K = 10) and -0.021 [-0.036, -0.006] (K = 20). On the originally registered backbone S
   has the lower site error at about 736 and 777 hosts, with intervals below zero.
6. **More resamples moved the v2 estimate, not the decision.** For v2 at 654, A is +0.015 (10 x 3), +0.020
   (10 x 5), +0.031 (30 x 3) and +0.033 (30 x 5): adding resamples 10-29 raised A more than adding seeds 3-4. Every
   one of these upper bounds is below δ. For v1 the four subsets lie between -0.015 and -0.007.
7. **Within-host.** The one-sided upper bound on A_within is below δ at every point for both backbones (largest
   +0.016 eV). For v1, A_within is negative at every point at or beyond 654 with intervals below zero (D has the
   larger within-host residual). For v2, A_within is +0.010 [+0.004, +0.016] at 654 pooled and +0.005 and +0.009
   with CV.
8. **Fold-level spread.** The sample SD of the per-fold A over folds is 0.029 and 0.039 eV (v2, K = 10 and 20)
   and 0.032 and 0.037 eV (v1).
9. **GPU classes (descriptive).** The precision runs used A10, RTX 3090, L4 and RTX 4090; the CV runs A10 and
   RTX 3090 (v2) and A10 and L4 (v1). RTX 4090 ran 69 (B = 400) and 75 (B = 654) v2 precision runs and 1 and 2 v1
   runs; it was not part of N1. The paired-cell A by class is in Table 5 and the SI figure. GPU class was not
   randomised against resample, fold or seed (for example, the "original sweep" class holds only r = 0..9, seeds
   0-2), so the class differences are not separable from those factors.
10. **Epoch cap (descriptive).** S reaches the 200-epoch cap more often than D: at B = 654, 35 of 150 v1 S runs
    and 14 of 150 v2 S runs against 3 and 6 for D; with CV at K = 20, 30 of 60 v1 S runs and 13 of 60 v2 S runs.
    In every S group with capped runs, their mean single-run MAE is lower than that of the uncapped runs. No capped
    run was replaced or removed.

## What is and is not established

Established, under the frozen rules: the advantage of the DFT electronic descriptors in the D-state model over the
structure-only model is bounded below δ = 0.05 eV at 654, about 736 and about 777 training hosts, for each
backbone, and at 654 over 30 resamples and 5 seeds.

Not established: that the descriptors are useless. On the primary backbone (v2) A is positive at every
extension point with two-sided intervals that exclude zero, so the descriptors do help that model, by less than δ.
Also not established: any bound below δ at B = 400 (it fails for both backbones); anything beyond 777 training hosts;
anything for other architectures or descriptor injections. The CV points test every one of the 818 hosts, including
the 79 hosts that no outer resample tests, so their test population differs from that of the outer resamples, and
their MAEs are not directly comparable with the budget points. Predictions carry a GPU-class component (N1) that is
not separable from seed and resample variation run by run.

## Hypotheses (not tested here)

- **The v1-v2 sign difference sits in S.** At 654 pooled, MAE_D is similar on the two backbones (0.264 v2,
  0.275 v1 eV) while MAE_S differs (0.297 v2, 0.267 v1 eV); with CV, MAE_S is higher on v2 (0.279 and 0.267 against
  0.249 and 0.238 eV) and MAE_D is lower (0.255 and 0.241 against 0.274 and 0.259 eV). The hypothesis is that
  the v2 initialisation makes the structure-only model, not D, worse at large budgets, so A on v2 measures partly a
  weaker S. A per-model comparison on identical cells would test it.
- **The epoch cap may bind on S.** S runs hit the cap far more often than D runs, and capped runs show lower mean
  MAE than uncapped ones. One reading is that S is still improving at 200 epochs, so a higher cap could lower
  MAE_S and make A smaller (more negative for v1). The capped/uncapped split is confounded with resample and fold;
  600-epoch twins of these runs would test it (the registered cap-sensitivity check covered only r = 0..2).
- **Resample composition, not hardware, drives the v2 rise at 654.** The v2 A at 654 rose from 10 to 30 resamples
  while seeds changed it less, and the "original sweep" class (r = 0..9 only) shows the smallest v2 A among
  classes. The hypothesis is that resamples 10-29 contain hosts on which the v2 descriptors help more; a
  per-resample comparison by class on the same resamples would separate it from hardware.
- **More training hosts favour S on v1.** v1 A falls from +0.038 (400) through -0.009 (654) to about -0.02
  (736-777), while MAE_S drops faster than MAE_D; the trend suggests the structure-only model keeps improving with
  data where D has saturated. Not tested.

## Figures

- `figures/main/fig3_advantage_extended.pdf` (`figures/code/fig_extended_budget.py`): A against training hosts,
  registered budgets 25 to 654 with bands, precision points at 400 and 654, CV points at 736.2 and 777.1, δ and
  zero, one-sided bounds in panel (b). New file; `figures/code/fig3_advantage.py` and its PDF are unchanged.
- `figures/si/fig_si_gpu_class.pdf` (`figures/code/fig_si_gpu_class.py`): paired-cell A by GPU class at the four
  design points.
- Both pass `figures/code/qa_figure.py`. The existing scripts `fig2_learning_curves.py`, `fig3_advantage.py`,
  `fig_g1_learning_curves.py` and `fig_within_host.py` pick up the four records `results/precision_g1_v1.json`,
  `results/precision_g1_v2.json`, `results/cv_g1_v1.json` and `results/cv_g1_v2.json` ("optional inputs drawn:
  precision v1, precision v2, cv v1, cv v2"), and their outputs pass QA (checked in a scratch directory; the
  committed main-figure PDFs were not regenerated in A1).

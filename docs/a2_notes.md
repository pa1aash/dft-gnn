# A2: staging analysis C3a (2026-10-14)

The staged model P predicts the 22 pristine-host DFT descriptors from structure (P1: 12 host-electronic, 10
site-electronic) and passes them to the descriptor model D of the same resample, budget and seed. It asks how
much of D's access to DFT electronic structure a structure-only network can supply from the pristine crystal. Two
contrasts at each budget: D − P, the cost of predicting rather than knowing the descriptors, and P − S, staging
against the end-to-end structure-only model S.

**Labels.** v1 (originally registered backbone) is the registered staging analysis: ANALYSIS_PLAN §8, with
P and D paired as clarified on 2026-10-10, before any P result. v2 is the primary backbone and is POST HOC; it
is never pre-registered. The four-outcome TOST rule with δ_P = 0.05 eV is the collaborator rule, ratified on
2026-10-11, and is POST HOC. It replaces the §8 null sentence for both backbones. Every implementation detail
was fixed in the `docs/deviations.md` row of 2026-10-14 (§8, step A2) before any staging number of this step was
computed. The v2 point values were already in `results/c3a_v2.json` (M1) and are disclosed in that row.

**Records.** `results/staging_v1.json`, `results/staging_v2.json` (`analysis/staging_analysis.py`);
`results/staging_eval_table.json` with `results/analysis/staging_{eval_long,p1_desc,runs}.parquet`
(`analysis/staging_eval_table.py`); `results/staging_swapin_check.json` (`analysis/staging_swapin_check.py`);
Figure 4 `figures/main/fig4_staging.pdf` (`figures/code/fig4_staging.py`). Tests:
`analysis/tests/test_staging.py`.

**Estimator.** The G1 estimator (`dftgnn.stats.g1`). The seed-ensemble mean over seeds 0-2 per site, then the
site MAE per resample, then the paired hierarchical bootstrap over the 10 resamples and their test hosts: 2000
replicates, seed 20261008. One draw set serves S, D, P, all budgets, both contrasts and both backbones. Point
values are means over resamples. Intervals: two-sided 95% (2.5th and 97.5th percentiles). The TOST 90%
interval is the 5th to 95th percentiles, i.e. the one-sided 95% lower and upper bounds.

## Integrity and sanity checks

| check | v1 | v2 |
|---|---|---|
| runs: P, P1 (outer + Kiyohara) | 183, 183 (180 + 3 each) | 183, 183 (180 + 3 each) |
| runs: S, D on the outer resamples | 180, 180 | 180, 180 |
| test-site coverage, finiteness, no test host in training, targets = universe, prediction sha256, recorded MAE and P1 per-descriptor metrics = stored predictions | pass (1452 runs over both backbones) | pass |
| P run ids and specs = `specs/peval.jsonl` | 183 of 183 | no spec file (collaborator stage) |
| pairing: every P's P1 and D components carry its split, budget and seed; D component = the D-state run used for D (Kiyohara: the Kiyohara D-state run of the same seed) | 183 of 183 | 183 of 183 |
| true-descriptor swap-in, 3 cells (r 5 B 200 s 1; r 9 B 200 s 2; r 6 B 400 s 2) | pass: max deviation 0.0 eV on 3 of 3 cells | **not run**: the P1-v2 and D-v2 checkpoints are only on the cluster storage (sha256 recorded, files absent on the Mac) |
| S − D through this pipeline vs the G1 records | equals `results/g1_primary.json` (points and 95% intervals to 2e-16) | equals the `results/c1c2_v2.json` points (1e-16) |

The swap-in deviation is exactly zero for v1 because P1 and D of one cell share their training hosts. Their
descriptor standardisations are therefore identical, and StagedP's affine map is the identity
(`affine_identity: true`). The check confirms that the composition feeds the descriptors into D correctly. It
does not test a non-trivial map. On the CPU, D and P differ from their stored GPU predictions by at most
1.4e-4 eV and 6e-6 eV (`results/staging_swapin_check.json`, descriptive).

**Reproduction of the collaborator's staging numbers (v2).** From his stored P-v2, S-v2 and D-v2 predictions,
this estimator gives the point values of `results/c3a_v2.json`. P − S, D − P and the MAEs of S, D and P agree
to 1.1e-16 eV at every budget. They also agree with our M1 recompute (`results/ingest_m1_recompute.json`) to
1.1e-16, including the intervals, because the draws are the same. The four-outcome category agrees at every
budget. Interval endpoints differ from his by at most 0.0031 eV for P − S. For D − P they differ by at most 0.076
eV, at B = 50, where the interval spans 2.1 eV; his bootstrap generator differs from ours. His P1 descriptor
means agree to 2e-15. These are the v2 values (`docs/ingest_report.md` row 37). Against the brief's values
+0.044, +0.123, +0.066, +0.119, +0.024, +0.028 eV: five agree to three decimals. At B = 200 the value is
+0.11846 eV, which rounds to +0.118, so the +0.119 in the M1 report (row 37) is a rounding slip; the point
value itself is identical to his record.

## What the measurements show (facts against the frozen rules)

Rule: the four-outcome TOST of P − S with δ_P = 0.05 eV (POST HOC, ratified). Non-inferiority of P to S means a
one-sided 95% upper bound on P − S below δ_P; it was fixed in the A2 row as the upper half of the TOST.

**v1, registered staging analysis.**

1. No budget has P better than S. The 95% interval of P − S lies above zero at all six budgets, so the outcome
   is "P worse" at every budget. P − S runs from +0.036 eV (B = 200) to +0.173 eV (B = 50) and is +0.098 eV
   [+0.075, +0.119] at B = 654.
2. Non-inferiority holds at no budget. The smallest one-sided upper bound is +0.058 eV (B = 200), above δ_P. No
   budget is "equivalent".
3. D − P is negative, with its 95% interval below zero, at every budget: P is worse than D everywhere. The cost
   of predicting the descriptors shrinks in magnitude from about 0.2 eV at B ≤ 50 to 0.086 eV at B = 654
   (D − P = −0.086 eV [−0.109, −0.064]).
4. Arithmetic: P − S = −A − (D − P), with A = MAE_S − MAE_D the registered C1 advantage. At B = 654 the
   registered A is −0.012 eV (D no better than S). The whole P − S gap at 654 is therefore the cost of
   predicting the descriptors.

**v2, primary backbone, POST HOC.**

1. No budget has P better than S. Outcomes: inconclusive at B = 25; P worse at 50, 100 and 200; equivalent at
   400; P worse at 654, but different only within the equivalence margin (90% interval [+0.011, +0.049]).
2. Non-inferiority holds at B = 400 (upper bound +0.047 eV) and B = 654 (+0.049 eV). Both bounds lie within
   0.003 eV of δ_P. It does not hold at 25-200.
3. D − P has its 95% interval below zero at B = 100-654. Its magnitude shrinks from 0.149 eV at 100 to 0.043
   eV at 654 (D − P = −0.043 eV [−0.063, −0.024]). At B = 25 and 50 the interval spans zero by a wide margin, because D-v2 is itself
   unstable there: MAE_D is 1.275 and 1.468 eV, above S, and its intervals reach 2.7 eV.
4. The same arithmetic: at B = 654, −A = −0.015 eV and −(D − P) = +0.043 eV give P − S = +0.028 eV.

**Both backbones.** P1 recovers the host-electronic descriptors better than the site-electronic ones, at both
budgets. The class-mean test R² at B = 654 is 0.69 and 0.49 (v1) and 0.75 and 0.61 (v2); at B = 200 it is 0.49
and 0.30 (v1) and 0.53 and 0.33 (v2). The worst-predicted descriptors are site-electronic. The neighbour minima
of the Born effective charge and of the Bader charge reach R² 0.14-0.28 at 654 and about 0 at 200; the
vacancy-site Bader charge reaches 0.34-0.39 at 654. The best-predicted is the host formation energy (R² 0.93,
0.97 at 654).

## Tables

### MAE of S, D and P: originally registered backbone (v1), registered staging analysis

| B | MAE_S | MAE_D | MAE_P |
|---:|---|---|---|
| 25 | 1.147 [1.092, 1.201] | 1.049 [0.922, 1.155] | 1.239 [1.192, 1.292] |
| 50 | 1.007 [0.946, 1.081] | 0.975 [0.869, 1.090] | 1.180 [1.126, 1.233] |
| 100 | 0.721 [0.667, 0.778] | 0.613 [0.557, 0.673] | 0.778 [0.721, 0.834] |
| 200 | 0.516 [0.488, 0.550] | 0.421 [0.380, 0.473] | 0.553 [0.524, 0.585] |
| 400 | 0.376 [0.348, 0.407] | 0.336 [0.317, 0.357] | 0.455 [0.427, 0.485] |
| 654 | 0.273 [0.252, 0.300] | 0.284 [0.267, 0.304] | 0.371 [0.346, 0.398] |

### Contrasts: originally registered backbone (v1), registered staging analysis

| B | D − P | 95% CI | P − S | 95% CI | 90% CI (one-sided 95% bounds) | TOST outcome | upper bound < δ_P |
|---:|---:|---|---:|---|---|---|---|
| 25 | -0.191 | [-0.320, -0.079] | +0.092 | [+0.040, +0.143] | [+0.048, +0.134] | P worse | no |
| 50 | -0.205 | [-0.304, -0.103] | +0.173 | [+0.110, +0.239] | [+0.120, +0.228] | P worse | no |
| 100 | -0.165 | [-0.224, -0.095] | +0.057 | [+0.006, +0.109] | [+0.015, +0.100] | P worse | no |
| 200 | -0.131 | [-0.174, -0.083] | +0.036 | [+0.008, +0.063] | [+0.014, +0.058] | P worse | no |
| 400 | -0.119 | [-0.144, -0.094] | +0.079 | [+0.057, +0.099] | [+0.061, +0.096] | P worse | no |
| 654 | -0.086 | [-0.109, -0.064] | +0.098 | [+0.075, +0.119] | [+0.079, +0.116] | P worse | no |

### Arithmetic check: P − S = −A − (D − P), v1

| B | A = MAE_S − MAE_D | −A | −(D − P) | P − S |
|---:|---:|---:|---:|---:|
| 25 | +0.098 | -0.098 | +0.191 | +0.092 |
| 50 | +0.032 | -0.032 | +0.205 | +0.173 |
| 100 | +0.108 | -0.108 | +0.165 | +0.057 |
| 200 | +0.095 | -0.095 | +0.131 | +0.036 |
| 400 | +0.040 | -0.040 | +0.119 | +0.079 |
| 654 | -0.012 | +0.012 | +0.086 | +0.098 |

### MAE of S, D and P: primary backbone (v2), POST HOC

| B | MAE_S | MAE_D | MAE_P |
|---:|---|---|---|
| 25 | 1.133 [1.074, 1.198] | 1.275 [0.882, 1.829] | 1.177 [1.121, 1.240] |
| 50 | 0.959 [0.891, 1.050] | 1.468 [0.696, 2.743] | 1.083 [1.009, 1.159] |
| 100 | 0.657 [0.599, 0.717] | 0.574 [0.513, 0.655] | 0.722 [0.665, 0.786] |
| 200 | 0.456 [0.434, 0.478] | 0.432 [0.407, 0.458] | 0.574 [0.543, 0.607] |
| 400 | 0.382 [0.356, 0.412] | 0.328 [0.308, 0.350] | 0.406 [0.380, 0.433] |
| 654 | 0.296 [0.276, 0.317] | 0.280 [0.263, 0.300] | 0.324 [0.304, 0.346] |

### Contrasts: primary backbone (v2), POST HOC

| B | D − P | 95% CI | P − S | 95% CI | 90% CI (one-sided 95% bounds) | TOST outcome | upper bound < δ_P |
|---:|---:|---|---:|---|---|---|---|
| 25 | +0.098 | [-0.302, +0.647] | +0.044 | [-0.010, +0.094] | [-0.001, +0.085] | inconclusive | no |
| 50 | +0.385 | [-0.395, +1.686] | +0.123 | [+0.045, +0.195] | [+0.058, +0.184] | P worse | no |
| 100 | -0.149 | [-0.213, -0.062] | +0.066 | [+0.010, +0.127] | [+0.018, +0.117] | P worse | no |
| 200 | -0.142 | [-0.170, -0.114] | +0.118 | [+0.089, +0.147] | [+0.093, +0.143] | P worse | no |
| 400 | -0.077 | [-0.103, -0.050] | +0.024 | [-0.005, +0.051] | [+0.001, +0.047] | equivalent | yes |
| 654 | -0.043 | [-0.063, -0.024] | +0.028 | [+0.008, +0.053] | [+0.011, +0.049] | P worse; different but within the equivalence margin | yes |

### Arithmetic check: P − S = −A − (D − P), v2

| B | A = MAE_S − MAE_D | −A | −(D − P) | P − S |
|---:|---:|---:|---:|---:|
| 25 | -0.142 | +0.142 | -0.098 | +0.044 |
| 50 | -0.509 | +0.509 | -0.385 | +0.123 |
| 100 | +0.083 | -0.083 | +0.149 | +0.066 |
| 200 | +0.024 | -0.024 | +0.142 | +0.118 |
| 400 | +0.054 | -0.054 | +0.077 | +0.024 |
| 654 | +0.015 | -0.015 | +0.043 | +0.028 |

### P1 test accuracy per descriptor, B = 654 (mean ± SD over the 30 runs)

| class | descriptor | R² v1 | R² v2 | MAE v1 | MAE v2 |
|---|---|---|---|---|---|
| host-electronic | ave_ele_diele | 0.740 ± 0.057 | 0.813 ± 0.052 | 0.368 | 0.282 |
| host-electronic | ave_ion_diele | 0.309 ± 0.233 | 0.459 ± 0.123 | 3.7 | 3.17 |
| host-electronic | band_gap | 0.744 ± 0.040 | 0.817 ± 0.034 | 0.426 | 0.346 |
| host-electronic | cbm_d | 0.804 ± 0.040 | 0.821 ± 0.039 | 0.0938 | 0.0864 |
| host-electronic | cbm_f | 0.518 ± 0.423 | 0.547 ± 0.460 | 0.0124 | 0.0102 |
| host-electronic | cbm_p | 0.546 ± 0.084 | 0.576 ± 0.086 | 0.0877 | 0.0808 |
| host-electronic | cbm_s | 0.703 ± 0.054 | 0.735 ± 0.052 | 0.105 | 0.0947 |
| host-electronic | formation_energy | 0.931 ± 0.018 | 0.966 ± 0.013 | 0.126 | 0.0848 |
| host-electronic | vbm_d | 0.803 ± 0.085 | 0.870 ± 0.056 | 0.0276 | 0.0222 |
| host-electronic | vbm_f | 0.816 ± 0.093 | 0.841 ± 0.096 | 0.00162 | 0.00131 |
| host-electronic | vbm_p | 0.776 ± 0.069 | 0.852 ± 0.063 | 0.0395 | 0.0309 |
| host-electronic | vbm_s | 0.571 ± 0.111 | 0.719 ± 0.096 | 0.0235 | 0.0184 |
| site-electronic | ave_bec | 0.725 ± 0.066 | 0.852 ± 0.034 | 0.134 | 0.0959 |
| site-electronic | bader_charge | 0.337 ± 0.080 | 0.387 ± 0.087 | 0.124 | 0.119 |
| site-electronic | bader_volume | 0.467 ± 0.065 | 0.669 ± 0.034 | 1.44 | 1.11 |
| site-electronic | nn_ave_ave_bec | 0.604 ± 0.061 | 0.759 ± 0.047 | 0.136 | 0.1 |
| site-electronic | nn_ave_bader_charge | 0.529 ± 0.062 | 0.624 ± 0.069 | 0.112 | 0.0977 |
| site-electronic | nn_max_ave_bec | 0.768 ± 0.068 | 0.867 ± 0.038 | 0.462 | 0.344 |
| site-electronic | nn_max_bader_charge | 0.571 ± 0.091 | 0.642 ± 0.064 | 0.298 | 0.273 |
| site-electronic | nn_min_ave_bec | 0.161 ± 0.070 | 0.282 ± 0.090 | 1.21 | 1.04 |
| site-electronic | nn_min_bader_charge | 0.139 ± 0.068 | 0.250 ± 0.087 | 0.736 | 0.637 |
| site-electronic | o2p_center_from_vbm | 0.607 ± 0.053 | 0.795 ± 0.037 | 0.346 | 0.239 |

| class | class-mean R² v1 | class-mean R² v2 | range of descriptor R² v1 | v2 |
|---|---|---|---|---|
| host-electronic (12) | 0.688 | 0.751 | 0.309 to 0.931 | 0.459 to 0.966 |
| site-electronic (10) | 0.491 | 0.613 | 0.139 to 0.768 | 0.250 to 0.867 |

### P1 test accuracy per descriptor, B = 200 (mean ± SD over the 30 runs)

| class | descriptor | R² v1 | R² v2 | MAE v1 | MAE v2 |
|---|---|---|---|---|---|
| host-electronic | ave_ele_diele | 0.586 ± 0.110 | 0.646 ± 0.087 | 0.492 | 0.443 |
| host-electronic | ave_ion_diele | 0.196 ± 0.254 | 0.131 ± 0.219 | 4.42 | 4.42 |
| host-electronic | band_gap | 0.582 ± 0.045 | 0.633 ± 0.048 | 0.556 | 0.511 |
| host-electronic | cbm_d | 0.657 ± 0.071 | 0.672 ± 0.056 | 0.141 | 0.136 |
| host-electronic | cbm_f | 0.123 ± 0.373 | 0.216 ± 0.289 | 0.0165 | 0.0167 |
| host-electronic | cbm_p | 0.360 ± 0.135 | 0.376 ± 0.137 | 0.117 | 0.113 |
| host-electronic | cbm_s | 0.477 ± 0.123 | 0.516 ± 0.083 | 0.157 | 0.147 |
| host-electronic | formation_energy | 0.848 ± 0.050 | 0.889 ± 0.036 | 0.183 | 0.153 |
| host-electronic | vbm_d | 0.601 ± 0.178 | 0.637 ± 0.133 | 0.0438 | 0.0394 |
| host-electronic | vbm_f | 0.542 ± 0.192 | 0.591 ± 0.198 | 0.00236 | 0.00213 |
| host-electronic | vbm_p | 0.612 ± 0.105 | 0.633 ± 0.095 | 0.0573 | 0.0542 |
| host-electronic | vbm_s | 0.321 ± 0.194 | 0.396 ± 0.177 | 0.0327 | 0.0309 |
| site-electronic | ave_bec | 0.517 ± 0.098 | 0.596 ± 0.096 | 0.185 | 0.164 |
| site-electronic | bader_charge | 0.151 ± 0.084 | 0.086 ± 0.337 | 0.145 | 0.143 |
| site-electronic | bader_volume | 0.286 ± 0.077 | 0.362 ± 0.099 | 1.67 | 1.57 |
| site-electronic | nn_ave_ave_bec | 0.327 ± 0.090 | 0.414 ± 0.111 | 0.182 | 0.168 |
| site-electronic | nn_ave_bader_charge | 0.304 ± 0.087 | 0.330 ± 0.154 | 0.139 | 0.134 |
| site-electronic | nn_max_ave_bec | 0.631 ± 0.083 | 0.646 ± 0.093 | 0.613 | 0.583 |
| site-electronic | nn_max_bader_charge | 0.386 ± 0.122 | 0.402 ± 0.127 | 0.374 | 0.362 |
| site-electronic | nn_min_ave_bec | 0.016 ± 0.115 | -0.052 ± 0.089 | 1.4 | 1.43 |
| site-electronic | nn_min_bader_charge | 0.012 ± 0.095 | -0.050 ± 0.098 | 0.855 | 0.866 |
| site-electronic | o2p_center_from_vbm | 0.387 ± 0.080 | 0.537 ± 0.085 | 0.442 | 0.374 |

| class | class-mean R² v1 | class-mean R² v2 | range of descriptor R² v1 | v2 |
|---|---|---|---|---|
| host-electronic (12) | 0.492 | 0.528 | 0.123 to 0.848 | 0.131 to 0.889 |
| site-electronic (10) | 0.302 | 0.327 | 0.012 to 0.631 | -0.052 to 0.646 |

## Hypotheses (not tested here; each needs its own logged analysis)

- **H1. The descriptor head is the bottleneck of staging.** On both backbones D − P shrinks as P1's descriptor
  R² rises with budget: class-mean R² from B = 200 to 654 rises 0.49→0.69 (host) and 0.30→0.49 (site) on v1,
  and 0.53→0.75 and 0.33→0.61 on v2. Over the same range |D − P| falls 0.131→0.086 eV (v1) and 0.142→0.043 eV
  (v2). The descriptors D leans on most may be the poorly recovered site-electronic ones: the neighbour BEC and
  Bader minima and the vacancy-site Bader charge, which describe the local ionic environment of the removed O.
  If so, the staging cost is set by how far pristine structure determines the local charge state, not by D. A
  test would feed D the true descriptors with noise at P1's per-descriptor test error, class by class, and
  compare with D − P. A simpler correlational check would relate, per resample, D − P to P1's class-mean R².
  Neither is run.
- **H2. Staging cannot beat S where D does not.** P − S = −A − (D − P) is an identity, so P beats S only if
  the descriptor advantage A exceeds the cost of predicting the descriptors. At B = 654, A is about zero on both
  backbones (C1, C2) and D − P is negative, so a P better than S would need a near-perfect descriptor head. The
  hypothesis is that this bounds staging for this target at this data size. It is not a measurement of what a
  better P1 would do.
- **H3. The v1/v2 gap in P − S at B = 654 (+0.098 vs +0.028 eV) reflects descriptor recovery more than D.** D's
  MAE at 654 is close on the two backbones (0.284 and 0.280 eV). P1-v2 recovers every site-electronic
  descriptor better than P1-v1 at 654 (class mean 0.61 vs 0.49), with the same untuned P1 values plus the He
  initialisation. Descriptive only: v1 vs v2 was never set up as a test. P1-v2 reuses P1's v1 tuned values
  without re-tuning (row of 2026-10-09).

## Not done in A2

- The v2 swap-in check (checkpoints on cluster storage only).
- The Kiyohara-split P cells (3 per backbone) are counted and checked, but no Kiyohara staging value is
  reported (the `sensitivity.kiyohara_split` row lists P; no rule for it was logged in A2).
- No within-host staging metric; ANALYSIS_PLAN §8 names site MAE only.

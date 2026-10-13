# A5 notes: high-moment, CGCNN and capped-twin sensitivities

Analysis of the three sensitivity stages merged in N2 (`docs/nrp/n2_ingest.md`). The rules were logged in
`docs/deviations.md` before any number was computed: the designs in the rows of 2026-10-10 (§5, §12) and the
estimators, sanity checks and integrity assertions in the row of 2026-10-14 (§5, §12). Nothing was changed after a
number was seen. Energies are in eV; A = MAE_S − MAE_D, which is positive when the DFT electronic descriptors lower
the error. δ = 0.05 eV.

| sensitivity | label | backbone (from `specs/<stage>.manifest.json`) | runs | record |
|---|---|---|---|---|
| high moment | EXTENSION (the exclusion list was fixed 2026-10-10, before any run) | v1 only (`tuned-v1`, a654 values) | 60 | `results/sens_high_moment_v1.json` |
| CGCNN | EXTENSION, untuned, descriptive | its own architecture; MEGNet v1 and v2 beside it | 18 | `results/sens_cgcnn.json` |
| capped reruns | POST HOC | v1 only | 33 new + 3 capsens twins | `results/sens_capped_post_hoc.json` |

None of the three stages has v2 runs. No `sens_high_moment_v2.json` exists, and the v2 capped-twin version is not
defined. The primary backbone (v2) appears only with its own primary result at B = 654, and as a MEGNet comparator
of CGCNN. v2 is never described as pre-registered.

Code: `analysis/sensitivity_eval_tables.py` (eval tables, integrity record `results/sensitivity_eval_tables.json`)
and `analysis/sensitivity_analysis.py`, with synthetic tests in `analysis/tests/test_sensitivity.py`. The SI figure is
`figures/si/fig_si_sensitivities.pdf`, and the claims are rows SENS1 to SENS3 of `docs/claims.yaml`. The figure
passes `figures/code/qa_figure.py` (vector, Arial embedded, one family, 138.6 × 82.0 mm, no text in the axes), and
its caption names records and keys with no typed numbers.

## Integrity and sanity checks

- **Integrity** (`results/sensitivity_eval_tables.json`, `integrity`): all assertions passed on the first run.
  Checked: run ids equal the spec manifests; each run covers its test sites exactly once; predictions are finite;
  no test host is in training; targets equal the universe; hashes and recorded MAEs match. Twin specs equal their
  originals except the epoch settings. The sweep originals at B = 400 and 654 equal their seed columns in
  `results/analysis/eval_table.parquet`.
- **Counts:** moment 60, cgcnn 18, capped 33 + 3 capsens twins = 36 twins of 36 originals, all finite. The v2
  comparator has 72 runs (resample 0 at B = 50 and 200, and every resample at B = 654; seeds 0–2).
- **Excluded entries:** identified from `defect_moment_muB` of `data/processed/universe_v1.parquet` with
  |moment| > 0.5 μB (read only). They are BaCeO3_Va_O1_0, BaCeO3_Va_O2_0, Cs2CeO3_Va_O1_0, La2Hf2O7_Va_O1_0,
  La2Zr2O7_Va_O1_0, La3SbO3_Va_O2_0, LiY(WO4)2_Va_O1_0, Rb2CeO3_Va_O1_0, Rb2CeO3_Va_O2_0 and Sr2CeO4_Va_O2_0.
  Moments are 1.93–2.00 μB on 8 hosts. This list equals the `exclude_sites` of all 60 moment specs. None of the 10
  entries appears in any moment prediction (0 of 0 allowed). The recorded training plus validation site and host
  counts of every moment run equal those of its budget hosts without them.
- **Primary-side reproduction:** the v1 primary side reproduces `results/g1_primary.json` at B = 654 (high
  moment) and at B = 400 and 654 (capped). This holds for MAE_S, MAE_D, A, per-resample A, the interval and the
  one-sided bound, with a maximum absolute difference of **0.0**.
- **v2 primary at 654 against `results/c1c2_v2.json`:** the point values agree (A to 1.6e-17, per-resample A to
  5.6e-17). The interval does not agree to 1e-6: ci95 differs by 4.2e-4 and the one-sided bound by 9.2e-5. This
  is the known difference in bootstrap implementation recorded in A1 (`docs/a1_notes.md`): that record was written
  by `scripts/analysis_c1c2.py`, not `dftgnn.stats.g1`. The G1-estimator value here equals the A1 10 × 3 v2 value
  in `results/precision_g1_v2.json` (`beside_subsets.10x3.654`) exactly, with difference 0.0. The record flags this
  with `sanity_c1c2_v2_654.passed: false`. It is reported here, not hidden.

## Tables

### (a) High moment, v1, B = 654, 10 resamples × 3 seeds (EXTENSION)

Each resample holds 1 to 5 of the excluded entries in its test set. The common test sites number 333 to 356 per
resample, against 334 to 359 primary sites. Between 161 and 164 test hosts keep a common site.

| version | MAE_S | MAE_D | A [two-sided 95%] | one-sided upper | below δ |
|---|---|---|---|---:|:---:|
| primary, all test sites (= G1) | 0.273 [0.252, 0.300] | 0.284 [0.267, 0.304] | −0.012 [−0.035, +0.014] | +0.009 | yes |
| primary, common sites | 0.272 [0.251, 0.299] | 0.282 [0.265, 0.301] | −0.010 [−0.034, +0.017] | +0.012 | yes |
| high moment, common sites | 0.267 [0.253, 0.285] | 0.282 [0.266, 0.301] | −0.015 [−0.037, +0.005] | +0.002 | yes |
| change, high moment − primary (paired) | −0.004 [−0.026, +0.013] | +0.000 [−0.007, +0.008] | −0.005 [−0.025, +0.013] | | |

Per-resample A on the common sites, r0 to r9:

| version | r0 | r1 | r2 | r3 | r4 | r5 | r6 | r7 | r8 | r9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| primary | −0.013 | +0.013 | −0.033 | +0.072 | −0.012 | −0.004 | −0.076 | −0.020 | −0.008 | −0.019 |
| high moment | −0.029 | −0.015 | −0.010 | +0.006 | −0.003 | +0.018 | −0.078 | +0.011 | −0.019 | −0.026 |

### (b) CGCNN against MEGNet, resample 0, seeds 0–2 (EXTENSION, untuned, descriptive)

Seed-ensemble site MAE with the host-cluster bootstrap over the 164 test hosts of resample 0. The draws are shared
by every column (2000 draws, seed 20261008). The last two columns give the single-run MAE as mean ± SD over the
three seeds.

| family | B | MAE_S | MAE_D | A | within-host S | within-host D | A_within | single-run S | single-run D |
|---|---:|---|---|---|---:|---:|---|---|---|
| MEGNet v2 | 50 | 0.862 [0.763, 0.963] | 0.629 [0.555, 0.712] | +0.232 [+0.137, +0.326] | 0.180 | 0.168 | +0.012 [−0.001, +0.025] | 0.983 ± 0.154 | 0.691 ± 0.060 |
| MEGNet v2 | 200 | 0.468 [0.412, 0.529] | 0.432 [0.377, 0.489] | +0.036 [−0.022, +0.099] | 0.155 | 0.176 | −0.021 [−0.035, −0.008] | 0.532 ± 0.179 | 0.449 ± 0.022 |
| MEGNet v2 | 654 | 0.304 [0.261, 0.352] | 0.273 [0.240, 0.311] | +0.031 [−0.010, +0.075] | 0.128 | 0.139 | −0.011 [−0.031, +0.007] | 0.334 ± 0.034 | 0.290 ± 0.017 |
| MEGNet v1 | 50 | 0.959 [0.851, 1.073] | 0.719 [0.637, 0.805] | +0.241 [+0.144, +0.341] | 0.180 | 0.172 | +0.008 [−0.003, +0.019] | 1.109 ± 0.148 | 0.812 ± 0.170 |
| MEGNet v1 | 200 | 0.506 [0.439, 0.578] | 0.407 [0.360, 0.460] | +0.099 [+0.035, +0.167] | 0.181 | 0.172 | +0.009 [−0.007, +0.023] | 0.570 ± 0.049 | 0.430 ± 0.024 |
| MEGNet v1 | 654 | 0.282 [0.244, 0.320] | 0.296 [0.258, 0.336] | −0.014 [−0.049, +0.020] | 0.136 | 0.151 | −0.015 [−0.039, +0.008] | 0.310 ± 0.048 | 0.320 ± 0.020 |
| CGCNN | 50 | 0.903 [0.798, 1.006] | 0.777 [0.692, 0.861] | +0.125 [+0.050, +0.199] | 0.178 | 0.170 | +0.008 [−0.000, +0.017] | 0.966 ± 0.087 | 0.830 ± 0.052 |
| CGCNN | 200 | 0.542 [0.478, 0.615] | 0.516 [0.460, 0.572] | +0.027 [−0.029, +0.083] | 0.181 | 0.161 | +0.020 [+0.007, +0.033] | 0.608 ± 0.057 | 0.568 ± 0.091 |
| CGCNN | 654 | 0.292 [0.248, 0.339] | 0.288 [0.251, 0.326] | +0.003 [−0.031, +0.035] | 0.136 | 0.139 | −0.003 [−0.016, +0.009] | 0.321 ± 0.048 | 0.324 ± 0.030 |

Paired site-MAE differences, CGCNN − MEGNet, on the same draws:

| B | S − S v1 | D − D v1 | S − S v2 | D − D v2 |
|---:|---|---|---|---|
| 50 | −0.056 [−0.132, +0.016] | +0.059 [−0.024, +0.146] | +0.041 [−0.020, +0.104] | +0.148 [+0.053, +0.243] |
| 200 | +0.036 [−0.020, +0.094] | +0.109 [+0.058, +0.157] | +0.074 [+0.012, +0.136] | +0.084 [+0.025, +0.142] |
| 654 | +0.009 [−0.020, +0.038] | −0.008 [−0.034, +0.018] | −0.013 [−0.047, +0.019] | +0.015 [−0.016, +0.045] |

Trainable parameters were counted from each run spec's hyperparameters on the CPU, without training. MEGNet uses
the tuned values of each budget's anchor, so its size changes with B.

| model | B = 50 | B = 200 | B = 654 |
|---|---:|---:|---:|
| cgcnn-S | 83,009 | 83,009 | 83,009 |
| cgcnn-D | 85,825 | 85,825 | 85,825 |
| MEGNet v1 S | 679,489 | 908,481 | 179,713 |
| MEGNet v1 D-state | 197,761 | 183,297 | 647,105 |
| MEGNet v2 S | 832,065 | 167,297 | 908,481 |
| MEGNet v2 D-state | 181,121 | 181,121 | 647,105 |

No CGCNN run reached the 200-epoch cap. Its epochs run were 36–199 and its best epochs 5–168.

### (c) Capped twins, v1 (POST HOC)

A at B = 400 and 654 with every capped original replaced by its 600-epoch twin. The G1 draws are used throughout,
and the primary result and N* are unchanged by rule. The replaced runs are 5 S runs at B = 400, and 8 S and 2 D
runs at B = 654. Three of the 654 twins are the capsens runs.

| B | version | MAE_S | MAE_D | A [two-sided 95%] | one-sided upper | below δ |
|---:|---|---|---|---|---:|:---:|
| 400 | primary (= G1) | 0.376 [0.348, 0.407] | 0.336 [0.317, 0.357] | +0.040 [+0.010, +0.073] | +0.067 | no |
| 400 | capped twins | 0.377 [0.350, 0.408] | 0.336 [0.317, 0.357] | +0.042 [+0.016, +0.070] | +0.066 | no |
| 400 | change (paired) | +0.001 [−0.008, +0.014] | 0.000 [0.000, 0.000] | +0.001 [−0.008, +0.014] | | |
| 654 | primary (= G1) | 0.273 [0.252, 0.300] | 0.284 [0.267, 0.304] | −0.012 [−0.035, +0.014] | +0.009 | yes |
| 654 | capped twins | 0.277 [0.257, 0.304] | 0.286 [0.268, 0.305] | −0.008 [−0.034, +0.018] | +0.014 | yes |
| 654 | change (paired) | +0.004 [−0.000, +0.011] | +0.001 [−0.000, +0.004] | +0.003 [−0.002, +0.010] | | |
| 654 | v2 primary (no capped twins exist) | 0.296 [0.276, 0.317] | 0.280 [0.263, 0.300] | +0.015 [−0.008, +0.037] | +0.033 | yes |

The record holds the change of A at 400 as +0.0014 eV; it shows as +0.001 because the two rows are rounded
separately. MAE_D at 400 is unchanged because no D run at 400 was capped.

Original against twin, paired by run, single-run test metric. S and D use site MAE in eV; P1 uses its recorded
mean standardised descriptor MAE.

| kind | model | B | n capped | mean original | mean twin | mean change | range of change | twin lower |
|---|---|---:|---:|---:|---:|---:|---|---:|
| Kiyohara split | S | 571 | 2 | 0.308 | 0.323 | +0.015 | −0.060 to +0.091 | 1 |
| sweep | S | 25 | 1 | 1.159 | 1.124 | −0.035 | −0.035 | 1 |
| sweep | S | 400 | 5 | 0.382 | 0.400 | +0.018 | −0.045 to +0.153 | 2 |
| sweep | S | 654 | 8 | 0.261 | 0.275 | +0.014 | −0.004 to +0.040 | 1 |
| sweep | D | 25 | 5 | 0.838 | 0.786 | −0.052 | −0.166 to +0.087 | 4 |
| sweep | D | 50 | 1 | 0.855 | 0.751 | −0.104 | −0.104 | 1 |
| sweep | D | 100 | 1 | 0.484 | 0.481 | −0.003 | −0.003 | 1 |
| sweep | D | 200 | 1 | 0.414 | 0.453 | +0.039 | +0.039 | 0 |
| sweep | D | 654 | 2 | 0.314 | 0.334 | +0.020 | +0.000 to +0.039 | 0 |
| sweep | P1 | 50 | 2 | 0.756 | 0.761 | +0.005 | −0.017 to +0.028 | 1 |
| sweep | P1 | 400 | 1 | 0.426 | 0.452 | +0.025 | +0.025 | 0 |
| sweep | P1 | 654 | 7 | 0.371 | 0.378 | +0.007 | −0.009 to +0.021 | 1 |

Twin epochs against the 600 cap (`descriptive_runs.twin_epochs`, per run in `descriptive_runs.per_run`):

- 1 of 36 twins reached 600 epochs: D, r8, B = 25, seed 1, best epoch 595.
- The median number of epochs run was 193.
- 9 of 36 twins found their best validation epoch after epoch 200.
- Of the 33 new twins, 21 stopped before epoch 200, so they never reached the old cap.
- Among the 12 new twins that enter A, 7 stopped before epoch 200 and 4 have a best epoch after 200.
- The 3 capsens twins match their originals exactly (change 0.000), as recorded in G1.

The 33 new twins ran on the NRP pool (A10 12, L4 12, RTX 3090 9). The originals and capsens twins ran on the sweep
pod.

## What the measurements show

These are facts against the frozen rules. Interpretation is in the next section.

1. **High moment (v1, EXTENSION).** Excluding the 10 high-moment entries from training and test changes A at
   B = 654 on the common test sites from −0.010 to −0.015 eV. The paired change is −0.005 eV, with interval
   [−0.025, +0.013]. MAE_S falls by 0.004 eV and MAE_D does not change (+0.000). The one-sided upper bound on A is
   +0.012 eV with the primary runs and +0.002 eV with the high-moment runs, both below δ. **The non-inferiority
   statement at 654 for v1 does not change.** Restricting the primary runs to the common sites moves A by +0.002 eV
   (−0.012 to −0.010). No statement can be made for v2, because no v2 high-moment runs exist.
2. **Capped twins (v1, POST HOC).** Replacing the capped originals by their 600-epoch twins changes A:
   - at B = 654, from −0.012 to −0.008 eV (paired change +0.003 eV [−0.002, +0.010]);
   - at B = 400, from +0.040 to +0.042 eV (paired change +0.001 eV [−0.008, +0.014]).

   At 654 the one-sided bound rises from +0.009 to +0.014 eV and stays below δ, so **the non-inferiority statement
   at 654 for v1 does not change.** At 400 the bound stays above δ (+0.067 and +0.066 eV), so 400 does not qualify
   under either version. The primary result and N* = 654 stand by rule. On average the twins have a higher
   single-run MAE than their originals for S at B = 400 and 654 and for D at B = 654. They have a lower MAE for D at
   B = 25 to 100. v2 has no capped twins, so its 654 statement rests on the primary result alone (bound +0.033 eV,
   below δ).
3. **CGCNN (EXTENSION, untuned, one resample, no test).** On resample 0, A for CGCNN is +0.125, +0.027 and
   +0.003 eV at B = 50, 200 and 654. MEGNet v1 gives +0.241, +0.099 and −0.014 eV, and MEGNet v2 +0.232, +0.036
   and +0.031 eV. In all three families A is largest at B = 50 and smallest at B = 654. At B = 654 the A intervals
   of all three include zero, and CGCNN's site MAE is within ±0.015 eV of both MEGNets' for S and for D, with every
   paired interval including zero. At B = 200, CGCNN D is worse than both MEGNet D models. Its paired differences
   are +0.109 eV against v1 and +0.084 eV against v2, and neither interval includes zero. CGCNN has 83,009 (S) and
   85,825 (D) trainable parameters, against 167,297 to 908,481 for the tuned MEGNets. The intervals cover test-host
   sampling of one resample only.
4. **Excluded entries and caps are rare in the test sets.** The high-moment entries make up at most 5 of 333 to 359
   test sites per resample. The capped runs replaced in A are 5 of 30 S runs at B = 400, and 10 of 60 S and D runs
   at B = 654.

## Hypotheses (not tested here)

These are offered for the discussion. They are not supported by a test in this analysis, and any follow-up must be
logged in `docs/deviations.md` first and labelled exploratory.

- **High moment.** All 10 excluded vacancies leave about 2 μB on the cell, which is what two localised electrons
  on reducible cations would give (Ce 4f in four of the eight hosts, BaCeO3, Cs2CeO3, Rb2CeO3 and Sr2CeO4; W in LiY(WO4)2; the La2Hf2O7,
  La2Zr2O7 and La3SbO3 hosts otherwise).
  These spin-polarised, polaron-like configurations are the ones a non-magnetic graph target describes worst. Their
  removal lowers MAE_S slightly and leaves MAE_D unchanged. That pattern would fit the descriptors (band edges, O-2p
  centre) already flagging the reducible-cation hosts for D, while S has no such signal. The change is small and its
  interval includes zero, so this is not established.
- **Capped twins.** The cap was not what limited these runs. In 21 of the 33 new twins, early stopping triggered
  before epoch 200, which is not possible if the original trajectory had simply been continued. The twins are better
  read as fresh runs on a different GPU class, as N1 predicts for a GPU-class change, than as the same runs with
  more epochs. The small positive change of MAE_S at 654 would then measure GPU-class and trajectory variation
  rather than the effect of training longer. Only the 3 capsens twins, run on the sweep hardware, isolate the cap,
  and they change nothing.
- **CGCNN.** A falls toward zero with training budget in an architecture that was not tuned, so the vanishing
  advantage of the descriptors at about 650 hosts is unlikely to be specific to MEGNet or to its tuning. This is a
  single resample with untuned optimiser settings, so it can only be consistent with that reading. The larger gap
  of CGCNN D at B = 200 may reflect the untuned learning rate. Most CGCNN runs stopped early, with best epochs as
  low as 5.

## Open points

- `docs/ANALYSIS_PLAN.md` §12 lists (a) high moment and (c) CGCNN among "pre-registered sensitivity analyses", and
  `specs/moment.manifest.json` and `specs/cgcnn.manifest.json` carry `label: registered`. The A5 brief labels both
  EXTENSION, and that label is used throughout. The plan fixed the exclusion and the cross-architecture check
  qualitatively. The comparison estimators, common-site handling and intervals were fixed only in the rows of
  2026-10-10 and 2026-10-14. Whether the SI calls them pre-registered in design but EXTENSION in analysis is the
  author's choice.

# Sweep notes (S09)

Completeness and health record of the pre-registered sweep (ANALYSIS_PLAN §5, §7, §14) and the two sensitivity
runs executed with it. This note reports counts, failures, wall times, epochs against the cap and one sanity
table. It contains no gap, interval, N* or comparison of S with D; those belong to S10 and the G1 gate.
Source: `results/sweep_completeness.json` (script `scripts/sweep_completeness.py`).

## What was run

- Sweep: S, D (D-state) and P1 on 10 resamples x 6 budgets x 3 seeds, 540 trained runs, each with the tuned
  hyperparameters of its budget's anchor (`configs/tuned_v1.yaml`), `max_epochs` 200, patience 30.
- Kiyohara split: S, D and P1 x 3 seeds, 9 runs. The three S runs are the official C0 runs (same run ids,
  recorded at code commit 1e4d634); D and P1 were run at the pod commit f943fdf. All sweep, Kiyohara-D/P1 and
  cap-sensitivity runs record f943fdf.
- Epoch-cap sensitivity: S and D at B = 654, resamples 0-2, seeds 0-2, `max_epochs` 600, 18 runs under
  `results/capsens/`. Not compared with their 200-epoch twins here (S10).
- P evaluation jobs (inference only) were not run. P1 predictions and checkpoints exist for S11.

## Completeness

567 of 567 expected runs (540 sweep, 9 Kiyohara, 18 epoch-cap) have a result JSON, a predictions parquet and a
checkpoint; every hash matches the result record; predictions cover each test site of the run's split exactly
once and are finite (P1: all descriptor predictions finite); no duplicates, no missing or unexpected cells. 583
checkpoint files (1010 MB) are listed with sha256 in `results/checkpoint_manifest.json`. Failures: 0; OOM
requeues: 0; reruns: 0.

## Wall time

Session wall time 18.08 GPU-h (one L40S, four workers under CUDA MPS): T1 8.07 h, T2 1.70 h, T3 1.74 h, T4 6.57 h.
Mean wall time per run (s, four-way sharing):

| model | 25 | 50 | 100 | 200 | 400 | 654 |
|---|---:|---:|---:|---:|---:|---:|
| S | 31 | 57 | 163 | 341 | 515 | 989 |
| D-state | 23 | 35 | 56 | 133 | 674 | 1442 |
| P1 | 16 | 39 | 114 | 234 | 870 | 1810 |

## Runs stopped by the 200-epoch cap (runs that reached epoch 200 / runs)

| model | 25 | 50 | 100 | 200 | 400 | 654 |
|---|---:|---:|---:|---:|---:|---:|
| S | 1/30 | 0/30 | 0/30 | 0/30 | 5/30 | 8/30 |
| D | 5/30 | 1/30 | 1/30 | 1/30 | 0/30 | 2/30 |
| P1 | 0/30 | 2/30 | 0/30 | 0/30 | 1/30 | 7/30 |

Kiyohara split: S 2/3, D 0/3, P1 0/3. The 600-epoch runs: S 0/9 and D 0/9 reached 600. The cap binds mainly for S
at the two largest budgets and for P1 at 654, as the tuning runs indicated.

## Sanity table: mean test MAE over resamples and seeds (eV; P1: mean standardised descriptor MAE)

| model | 25 | 50 | 100 | 200 | 400 | 654 |
|---|---:|---:|---:|---:|---:|---:|
| S | 1.240 | 1.108 | 0.821 | 0.588 | 0.412 | 0.307 |
| D | 1.102 | 1.043 | 0.662 | 0.455 | 0.361 | 0.303 |
| P1 | 0.912 | 0.873 | 0.608 | 0.502 | 0.435 | 0.379 |

Every mean falls with the budget; no step rises. The rule flags S at B = 25, 50 and 100 and D at B = 25 and 50 for
exceeding 0.8 eV. Checked for implementation errors only: the MAE recomputed from the stored predictions equals
the recorded MAE; the B = 654 value agrees with the official C0 (0.283 eV on Kiyohara's split); the constant
predictor at the pooled mean has MAE 1.21 eV on these test sets, and S at B = 25 sits at 1.24 eV. With 22 training hosts
(about 45 sites) the structure-only network early-stops near epoch 28 and has learned little beyond the mean,
which is the data-starved regime the study is built to measure. Nothing was changed.

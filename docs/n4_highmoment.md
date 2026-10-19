# N4 high-moment exclusion on the final network (session I1, 2026-10-19)

Record: `results/derived_n4/high_moment_final_network.json` (script `analysis/n4/high_moment_final.py`, commit
4e2837f). Label: EXTENSION on the final network (POST HOC backbone). Rule: `docs/deviations.md`, row of 2026-10-18
(§12). The exclusion list was fixed on 2026-10-10, before any run.

**Physics.** The hosts are classified as non-magnetic, yet 10 neutral oxygen vacancies end their DFT relaxation with
a defect moment above 0.5 muB. They sit in Ce- and La-containing oxides and one tungstate, where the two electrons
left by the vacancy localise on a reducible cation. This check asks whether the bound on A = MAE_S - MAE_D at 654
training hosts depends on these localised-electron entries, which a structure-only model cannot see as different
from closed-shell vacancies.

**Design.** S and D are retrained on the final network (He initialisation, validation-tuned, `configs/tuned_v2.yaml`)
at 654 training hosts, for outer resamples 0-9 and seeds 0-2 (60 runs, stage moment_v2), with the 10 entries
removed from training and test. They are compared with the final-network sweep at 654 (the 10 x 3 design of
`results/derived_c1/final_network_summary.json`, row B654), restricted to the same test sites: the sweep's test
predictions minus the excluded sites, which are 1 to 5 sites per resample.

**Estimator.** These are the steps of `analysis/sensitivity_analysis.high_moment`, the estimator that produced the
default-initialisation result (`results/sens_high_moment_v1.json`), imported unchanged: seed-ensemble mean;
`common_sites`; `stats_by_r`; `hier_pair` on the G1 hierarchical draws (2000 replicates, seed 20261008); `changes`,
with the same draws on both sides; and `with_bound`. Intervals are two-sided 95%. U is the one-sided 95% upper
bound. delta = 0.05 eV.

## Result (eV, 654 training hosts, 10 resamples x 3 seeds)

| Quantity | Final network, no exclusion, all test sites | Final network, no exclusion, same test sites | Final network, high-moment entries excluded | Change, excluded minus no exclusion (same sites, paired) | Default initialisation, excluded (A5, for reference) |
|---|---|---|---|---|---|
| MAE_S | 0.296 [0.276, 0.317] | 0.294 [0.274, 0.316] | 0.301 [0.282, 0.322] | +0.007 [-0.009, +0.021] | 0.267 [0.253, 0.285] |
| MAE_D | 0.280 [0.263, 0.300] | 0.277 [0.260, 0.299] | 0.274 [0.258, 0.292] | -0.004 [-0.015, +0.006] | 0.282 [0.266, 0.301] |
| A = MAE_S - MAE_D | +0.015 [-0.008, +0.037] | +0.016 [-0.007, +0.038] | +0.027 [+0.001, +0.052] | +0.011 [-0.008, +0.029] | -0.015 [-0.037, +0.005] |
| U (one-sided 95% upper bound on A) | +0.0329 | +0.0342 | +0.0488 | +0.0265 | +0.0024 |
| U < 0.05 | yes | yes | yes (by 0.0012) | n/a | yes |

Per-resample site counts are the same as in A5, because the splits are the same. Between 1 and 5 of the 10 entries
are in each test set, and the other 5 to 9 are in the training pool. The common test sites per resample number 333
to 356.

**Reading.** On the final network, removing the localised-moment entries raises A from +0.016 to +0.027 eV on the
same test sites. S gets slightly worse and D slightly better. The paired change, +0.011 [-0.008, +0.029] eV, has an
interval that contains zero. Its sign is opposite to the default-initialisation change, -0.005 [-0.025, +0.013] eV.

**Is "U < 0.05 eV at 654" unchanged?** Yes. With the exclusion, U = +0.0488 eV, which is below delta =
0.05 eV under the strict rule of `analysis/a1_common.passes`. The non-inferiority statement at 654 therefore holds
on both networks with and without the exclusion. The margin on the final network is thin, 0.0012 eV, against
0.047 eV on the default-initialisation network.

Two further facts follow from the same record and should not be hidden:

1. With the exclusion, the two-sided 95% interval of A, [+0.001, +0.052], lies above zero and its upper end is
   above +0.05 eV. Without the exclusion it is [-0.007, +0.038]. The C1 wording "the two-sided interval lies
   inside +-0.05" (`docs/c1_coverage.md`, headline row) therefore does not carry over to the exclusion sensitivity.
   Only the one-sided statement does.
2. The comparison mixes the exclusion with hardware. The 60 moment_v2 runs ran on the NRP GPU pool (A10 31,
   TITAN RTX 12, L4 10, Quadro RTX 6000 4, RTX 3090 3), while the sweep ran on the sweep pod, and by N1 different
   GPU classes never give identical predictions. The default-initialisation A5 comparison carries the same caveat.
   4 of the 30 S runs stopped at the 200-epoch limit (a7d70fc64d35f0c8, 4f4fcd4874ca44df, 8dd956bdfe4e07c4,
   aee1a01ca0787cad). By Appendix F, such runs tend to lower A rather than raise it. This is descriptive, and no
   correction is made.

## Network-free forest check (quoted from `results/sens_high_moment_rf.json`, not recomputed)

RF-Kumagai at 654 training hosts, the same 10 entries removed from training and test, paired host bootstrap (2000
draws):

| Quantity | Site MAE (eV) |
|---|---|
| Baseline, all test sites | 0.346 [0.328, 0.365] |
| Baseline, test sites without the entries | 0.342 [0.324, 0.361] |
| Refit without the entries | 0.342 [0.325, 0.361] |
| Change, total (refit minus baseline) | -0.004 [-0.008, -0.0002] |
| Change, training only (refit minus baseline on the same sites) | -0.0004 [-0.004, +0.003] |
| Change, evaluation only | -0.004 [-0.006, -0.002] |

The forest error falls by 0.004 eV, almost all of it from dropping the entries from the test set. Dropping them from
training changes nothing measurable.

## Reproduction (tolerance 1e-9 eV; the script stops before writing on any mismatch)

12 comparisons, 21,087 values, maximum absolute difference 0.0:

- `sensitivity_analysis.high_moment` rerun on its own inputs equals `results/sens_high_moment_v1.json`. This covers
  the primary common-site, high-moment, change and full-site blocks and the per-resample counts, and shows that the
  estimator is unchanged.
- `sensitivity_analysis.v2_primary` equals `v2_primary_654` of that record.
- The final-network full-site block equals `v2_primary_654` (A, MAE_S, MAE_D, with per-resample values) and row
  B654 of `results/derived_c1/final_network_summary.json` (point values, intervals, U).
- The v2 sweep predictions of `sens_eval_long.parquet` (S and D, 654, seeds 0-2) equal those of
  `staging_eval_long.parquet`, the C1 input.
- The per-resample exclusion counts on the final network equal those of the A5 record.

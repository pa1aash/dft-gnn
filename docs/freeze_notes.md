# Freeze notes (A6, tag `results-v1`)

Status of each claim at the results freeze (`docs/deviations.md`, AUTHOR DECISION / FREEZE row of 2026-10-14). Every
number below is a row of `results/freeze_table.json` (row id in brackets), read without recomputation from the record
and key named in that row; `paper/tables/freeze_table.tex` prints the same rows. Energies in eV. A = MAE_S − MAE_D
(positive when the DFT electronic descriptors lower the site error); δ = 0.05 eV; intervals are two-sided 95% unless
marked; U is the one-sided 95% upper bound. v2 is the primary backbone and POST HOC (adopted after diagnostics of v1,
never pre-registered); v1 is the originally registered backbone. The checks of the freeze (repeated numbers,
estimator differences, notes, claims, figures) all pass and are in `payload.checks` of the same record.

## Claim status

**C0 (structure-only accuracy against the published 0.29 eV).** Established on v1 for both protocols. On Kiyohara's
released host split the seed-ensemble S reaches 0.283 [0.237, 0.329] (C0-kiyo-v1), below the 0.35 gate (C0-kiyo-gate),
against 0.414 [0.339, 0.499] for RF-Kumagai on the same split (RF-K-kiyo). On the formula-grouped protocol at 654
training hosts S reaches 0.273 [0.252, 0.300] (C0-fg-v1). On v2 the formula-grouped value is 0.296 [0.275, 0.317]
(C0-fg-v2, POST HOC). Not established: a v2 C0 on Kiyohara's split, which exists only as six run records
(`results/v2_kiyohara/`) with no named analysis record. The claims.yaml status moved from planned to measured at the
freeze; no value or label changed.

**C1 (A below δ from N* on).** Established for both backbones with N* = 654, the largest registered budget. v1: A at
654 is −0.012 [−0.035, +0.014], U +0.009 (C1-A654-v1); the bound is above δ at every smaller budget (at 400, A +0.040,
U +0.067; C1-A400-v1), so N* = 654 (C1-Nstar-v1). v2 (POST HOC): A at 654 is +0.015 [−0.008, +0.036], U +0.033
(C1-A654-v2); the bound is also below δ at 200 (U +0.047) but not at 400 (U +0.075), so N* = 654 under the "N* and all
larger budgets" rule (C1-Nstar-v2, C1-Nstar-v2-qual). The extensions bound A below δ beyond 654 on both backbones:
over 30 resamples × 5 seeds at 654, v1 −0.009 [−0.020, +0.002], U +0.001 and v2 +0.033 [+0.021, +0.045], U +0.043
(PR1-A654-v1, PR1-A654-v2); with grouped CV at about 736 and 777 training hosts, v1 −0.025 and −0.021 with intervals
below zero, v2 +0.024 and +0.026 with intervals above zero, all U below δ (CV1-Ak10/Ak20). At 400 the pooled bound
stays above δ on both (U +0.052 v1, +0.079 v2; PR1-A400). Leave-one-cluster-out gives v1 +0.008 [−0.015, +0.031],
U +0.027 and v2 +0.041 [+0.018, +0.064], U +0.060 (LOCO-A; v2 above δ). Within hosts, A_within at 654 is −0.018
[−0.030, −0.007] (v1) and −0.002 [−0.013, +0.009] (v2), with N*_within = 25 on both (WH-Aw654, WH-Nstar). Not
established: that the descriptors carry no information. On v2, A is positive with intervals excluding zero at every
extension point, so the descriptors help that model by less than δ; nothing is established beyond 777 training
hosts, below 654 (400 fails), for other architectures than the CGCNN cross-check, or under LOCO on v2.

**C2 (the D − S gap at maximum budget bounds the value of perfect pristine-host electronic information).** Measured:
v1 −0.012 [−0.035, +0.014] (C2-v1), v2 +0.015 [−0.008, +0.036] (C2-v2, POST HOC). Both intervals include zero and lie
inside ±δ. The refined values over 30 × 5 are those of C1 (PR1-A654). Not established: a sign; the backbones disagree
in sign at 654 and beyond (v1 negative, v2 positive).

**C3a (staging).** Measured on v1 (registered staging analysis; outcome rule POST HOC). P is worse than S at all six
budgets (TOST outcome "P worse" at 25 to 654, C3a-out*-v1), non-inferior at none (C3a-noninf-v1); at 654, P − S =
+0.098 [+0.075, +0.119], U +0.116 (C3a-PS654-v1), and D − P = −0.086 [−0.109, −0.064] (C3a-DP654-v1), so the whole
P − S gap at 654 is the cost of predicting the descriptors. On v2 (POST HOC) no budget has P better than S: inconclusive
at 25, worse at 50 to 200, equivalent at 400, worse within the equivalence margin at 654 (C3a-out*-v2); P is
non-inferior at 400 and 654 only (C3a-noninf-v2); at 654, P − S = +0.028 [+0.008, +0.053], U +0.049 and D − P = −0.043
[−0.063, −0.024] (C3a-PS654-v2, C3a-DP654-v2). P1 recovers host-electronic descriptors better than site-electronic
ones (class-mean test R² at 654: 0.688 and 0.491 on v1, 0.751 and 0.613 on v2; C3a-P1*). Not established: any budget
where staging beats end-to-end S; the v2 true-descriptor swap-in check was not run (checkpoints on cluster storage only).

**C3b (geometry robustness under MACE-MP-0 relaxed hosts).** Measured on v1 at 654 on our 818 relaxations. The null
rule is not met, with neither condition holding (C3b-null): the median internal RMSD is 0.024 Å, above 0.01 Å
(C3b-rmsd), and the ΔMAE intervals of S exclude zero, +0.004 [+0.0003, +0.008] under MLIP and +0.007 [+0.003, +0.012]
under rescaled MLIP geometry (C3b-dS-*), while those of D and P include zero (C3b-dD-*, C3b-dP-*). Removing the 7
non-converged hosts does not change the outcome (C3b-nc-null). The degradations are small: the largest |ΔMAE| is
0.007 eV. Not established: that staged and end-to-end models "degrade differently"; the plan registers no test of
that difference, and the POST HOC TOST gives equivalent under MLIP (−0.003 [−0.008, +0.003]) and P better within the
margin under rescaled MLIP (−0.007 [−0.012, −0.002]; C3b-tost-*). No v2 geometry evaluation on our 818 relaxations
exists; the collaborator's v2 evaluation on his 809 relaxations, largest |dMAE| 0.003 (C3b-809-his), is a POST HOC
cross-check only.

**C4 (latent probe).** Measured on v1 and failed under the registered §10 rule, so C4 moves to the SI
(C4-outcome-v1, C4-holds-v1). The class-mean probe R² rises with budget (Spearman ρ 0.916 [0.854, 0.953] host,
0.945 [0.927, 0.963] site; C4-rho-*-v1) and exceeds the shuffled-label control at 200, 400 and 654, but it does not
exceed the random-init control at any of them. The S-v2 probe (POST HOC, descriptive) shows the same pattern (ρ 0.964
and 0.978; C4-rho-*-v2), and C4 would not hold on v2 either (C4-holds-v2). Not established: that training adds
recoverable electronic information beyond what a random encoder of the same structure already exposes.

**C5 (screening demonstration).** A demonstration, not a test. On the 10 oxygen sites of the 7 named candidate oxides
in the universe, S at 654 has MAE 0.294 [0.195, 0.424] on v1 (pre-registered aggregation) and 0.420 [0.307, 0.553] on
v2 (POST HOC) (C5-mae-v1, C5-mae-v2; intervals from `figures/main/data/screening_demo.json`, row SD1). The claims.yaml
status moved from planned to measured at the freeze. Not established: screening accuracy outside these 10 sites;
candidates outside the deep-vacancy domain (TiO2 O1-O3, BaTiO3, SrTiO3) are absent by the data filter, not by choice.

**Sensitivities (SI).** On v1 at 654, neither the high-moment exclusion (A −0.015, U +0.002; SENS1) nor the 600-epoch
capped twins (A −0.008, U +0.014; paired change +0.003 [−0.002, +0.010]; SENS3) moves the upper bound above δ; at 400
the twins leave it above δ (U +0.066). Untuned CGCNN on resample 0 gives A +0.003 [−0.031, +0.035] at 654 against
−0.014 [−0.049, +0.020] for MEGNet v1 on the same draws (SENS2, descriptive). No v2 sensitivity runs exist.

## Caveats the prose must keep

1. **v2 chronology.** v2 was adopted after test-set diagnostics of v1; every v2 number is POST HOC and is never
   described as pre-registered. v1 is the originally registered backbone and is reported in full beside v2. The
   backbones disagree in the sign of A at and beyond 654 (v1 negative, v2 positive).
2. **GPU classes.** The extension runs used A10, RTX 3090, L4 and RTX 4090 (RTX 4090 was not in N1). Runs are bitwise
   repeatable on one node and across nodes of one class (12 of 12; N1-same-node, N1-cross-node) but not across
   classes. The class shifts the seed-ensemble MAE by −0.017 to +0.000 eV for S and −0.022 to +0.000 eV for D at 654,
   and by up to +0.102 eV for S at 200 (N1-S*, N1-D*). GPU class was not randomised against resample, fold or seed,
   so its effect is not separable from them.
3. **Epoch cap.** max_epochs = 200 with patience 30. The registered cap check (resamples 0-2) found the primary result
   cap-insensitive, but S reaches the cap far more often than D in the extensions (at 654, 35 of 150 v1 S and 14 of
   150 v2 S precision runs, against 3 and 6 for D), and capped S runs have lower mean MAE. The POST HOC capped twins
   change A by +0.003 at 654 (v1 only; no v2 twins).
4. **CV test sets.** The grouped K-fold CV tests every one of the 818 hosts, including the 79 that no outer resample
   tests, so its test population differs from the registered resamples; CV MAEs and A are not directly comparable
   with the budget points, and the CV training sizes (about 736 and 777) are means over folds.
5. **Deep-vacancy domain.** The perturbed-host-state filter removes shallow-donor entries (345 of 2103 completed
   neutral entries in the release). Every result describes deep, localised neutral oxygen vacancies in non-magnetic
   ordered oxides; early-transition-metal d0 oxides (Nb, W, Ti, V, Ta, Mo) are under-represented.
6. **No v2 geometry on our 818 relaxations.** C3b is v1 only. The collaborator's v2 geometry evaluation used his 809
   relaxations and is a POST HOC cross-check; it is not part of C3b.
7. **Estimator differences.** The collaborator's records (`results/c1c2_v1.json`, `results/c1c2_v2.json`,
   `results/c3a_v2.json`) use a different bootstrap; point values are identical to ours, intervals differ by up to
   4.2e-4 eV for A at 654 on v2 (8.7e-4 on v1) and 1.7e-3 eV for P − S at 654 on v2. The registered intervals are
   those of the G1 estimator. The geometry DFT condition is a re-inference and differs from the sweep MAEs by at most
   4.5e-8 eV (`payload.checks.estimators`).
8. **Labels of LOCO.** The LOCO runs are the collaborator's, adopted by the 2026-10-11 row ("EXTENSION, as run");
   `docs/provenance_labels.md` #3 calls the v1 runs pre-registered in design and leaves the choice to the author. The
   freeze table follows the later row (EXTENSION).
9. **Within-host.** The within-host breakdown (WH1) averages each site over the resamples in which its host was
   tested; its pooled site MAE differs from the resample mean of the G1 records by 0.011 (D) and 0.014 (S), as
   recorded in `results/within_host_breakdown.json` (`sanity`).

## After the freeze

No experiment, run or analysis is added after `results-v1`. A later change to a record, rule or label gets its own
dated row in `docs/deviations.md` with its label and is reported beside the frozen value, which is kept.

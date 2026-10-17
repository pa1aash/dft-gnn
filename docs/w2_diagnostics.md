# W2: diagnostics of the final network

Session W2a, 2026-10-17. The final network is the He-initialised, validation-tuned network (v2 in the repository).
Everything below comes from existing predictions with the existing estimators (`analysis/w2/diagnostics.py`);
nothing was trained. The records are in `results/derived_w2/`; the tables after this summary are rendered from them
by `analysis/w2/make_docs.py`, and every number the rewrite may quote has a `\numNet...` macro
(`paper/tools/net_macros.py`). These are diagnoses for the author and for the wording of Results; none of them
replaces a result of the paper, and none is a claim until a claims-table row is added for it.

## Findings

**(a) Descriptor network at 25 and 50 hosts: a few test oxides with f-character conduction bands, not divergence.**
No D run has a non-finite prediction or a non-finite training or validation loss, and every run stopped by early
stopping at a normal validation error (one exception, r2 seed 0 at 50 hosts, whose best validation error is
126 eV: its validation set holds BaCeO3 and LaNbO4 while its training set holds no La or Ce oxide; seed 1 of the
same resample, whose validation split put those two oxides in training instead, reaches 0.672 eV). The large D errors come from a handful of test
sites, all in La- and Ce-containing oxides (LaScO3, Rb2CeO3, BaCeO3, Cs2CeO3, LaAsO3, La2Zr2O7, LaBO3 and others),
where D predicts energies of tens to hundreds of eV, far outside the 1.6 to 8.3 eV range of the targets. At every
one of these sites the descriptor furthest from the training data is the f-orbital fraction of the conduction-band
minimum (`cbm_f`): standardised with the run's own training sites, its |z| is 60 to 300 at those sites against
about 2 at the others. With 25 or 50 training oxides there are almost no f-band hosts in training, so the SD of
`cbm_f` is tiny, and a test oxide with an f-like conduction band is a large extrapolation that the network
amplifies. The extreme sites (78 at 25 hosts, 69 at 50 hosts, under 1% of the predictions) carry a third of the
absolute error at 25 hosts and half at 50 hosts. The Tukey rule flags 2 runs at 25 hosts (r0 s1, r1 s0) and 4 at
50 (r2 s0 and all three seeds of r6, a resample whose test set holds BaCeO3, Cs2CeO3, LaScO3 and LaAsO3), so the
outliers are partly one poor resample and partly single runs; but the same mechanism also inflates runs below the
fence (16 of 30 runs at 25 hosts and 12 of 30 at 50 carry extreme sites). Removing the flagged runs moves A at 50
hosts from -0.509 [-1.823, +0.277] to +0.238 [+0.096, +0.368]: the negative A at 25 and 50 hosts in the C1 table is
produced by these sites, not by S being better than D. This is behaviour of the descriptor input (training-set
standardisation of a nearly constant descriptor, as specified), not a defect in the code, so the paper's
small-budget numbers stand as computed; Results should say that D is unstable below 100 training hosts because a
few f-band oxides lie outside its training range, and quote the median or trimmed D error if a typical value is
needed.

**(b) Training limit.** In the sweep (10 x 3), S reaches the 200-epoch limit in 0 runs up to 200 hosts, 1 at 400
and 3 of 30 at 654; D in 1 of 30 at 654 and none elsewhere; P1 (the trained part of P) in 2, 10 and 20 of 30 runs
at 200, 400 and 654. At 654 in the 30 x 5 set, 14 S and 6 D runs are capped (17 of 150 cells hold a capped run).
Capped S runs are better, not worse, than uncapped ones (single-run MAE lower by 0.051 eV): they are the runs still
improving when the limit stopped them. The cells with a capped run have a smaller paired A (0.006 eV where only S
is capped, against 0.048 where neither is), so including them lowers the mean single-run A by 0.003 eV (30 x 5) and
0.0007 eV (10 x 3); removing the capped runs from the seed ensemble raises the 30 x 5 point estimate of A from
0.033 to 0.037 eV. Training S longer would therefore more likely shrink A than grow it; the effect is small next
to the interval and is descriptive only.

**(c) Crossover with the forest.** D is below RF-Kumagai with a 95% interval from 200 hosts on (-0.046
[-0.066, -0.028] at 200). S is below the forest in point estimate from 200 hosts (-0.023 at 200, -0.017 at 400) but
its interval includes zero at 200 and 400; S is clearly below only at 654 (-0.051 [-0.073, -0.030]). At 100 hosts
both networks are worse than the forest (S +0.089 [+0.027, +0.154]; D +0.006 [-0.044, +0.073]).

**(d) Why the bound passes at 200 and fails at 400.** The intervals are about equally wide at 200, 400 and 654
(bootstrap SD 0.015, 0.013, 0.011 eV; SD of A across resamples 0.034, 0.034, 0.030 eV). What changes is the point
estimate: A is 0.024 at 200, 0.054 at 400 and 0.015 at 654, so the bound is 0.047, 0.075 and 0.033. At 400 no
resample has A below zero and 6 of 10 exceed 0.05; at 200 two resamples are below zero and two above 0.05. The 30 x 5
design confirms 400 (A 0.066, U 0.079, 19 of 30 resamples above 0.05). The 200-host pass is therefore a lower point
estimate with the same resample-to-resample noise, not a more precise one: D at 200 still varies more between
resamples (SD of MAE_D 0.031 against 0.015 for S), and A at 200 sits between zero and δ. The N* rule needs the bound
below δ at every larger size, so N* stays 654; Results can say in one clause that the 200-host bound falls below δ because
the point estimate there is low, and that 400 hosts fail on both designs.

**(e) Screening.** On the 10 screened sites the final network's MAE is 0.420 eV [0.307, 0.553] with no net bias
(+0.003 eV; 5 over, 5 under). The errors are largest on the high-energy group (MgO, Al2O3 under-predicted by about
0.6 eV; ZrO2 over-predicted by 0.5 to 0.6 eV) and smallest on Ga2O3 O1 (+0.13 eV).

## (a) Descriptor network at 25 and 50 training hosts

Record: `results/derived_w2/w2_descriptor_small_budget.json` (git 6a49183). Single-run MAE of every resample x seed run of D (eV). Outlying run: MAE above the Tukey fence Q3 + 1.5 IQR of the 30 runs of the budget. Extreme site: absolute error above 10 eV (the DFT targets lie between 1.6 and 8.3 eV). z: the largest |z| over the 22 descriptors of D, standardised with the training sites of that run (`dftgnn.train.resolve_hosts` on the stored run spec, population SD, as in `Standardiser.fit`).

### 25 training hosts

| Run | MAE | Outlying | Extreme sites | Share of abs. error from them | MAE without them | Median z, extreme sites | Median z, other sites | Descriptor with largest z | Best validation MAE | Epochs |
|---|---|---|---|---|---|---|---|---|---|---|
| r0 s0 | 1.320 | no | 6 | 0.51 | 0.664 | 90 | 2.2 | cbm_f (6) | 0.718 | 65 |
| r0 s1 | 2.849 | yes | 7 | 0.76 | 0.699 | 89 | 2.0 | cbm_f (7) | 0.166 | 48 |
| r0 s2 | 1.735 | no | 7 | 0.60 | 0.710 | 93 | 2.1 | cbm_f (7) | 0.475 | 72 |
| r1 s0 | 3.358 | yes | 8 | 0.60 | 1.373 | 81 | 2.2 | cbm_f (8) | 1.015 | 40 |
| r1 s1 | 1.155 | no | 0 | 0.00 | 1.155 | - | 2.1 | - | 0.713 | 66 |
| r1 s2 | 1.400 | no | 0 | 0.00 | 1.400 | - | 2.1 | - | 0.312 | 33 |
| r2 s0 | 1.606 | no | 4 | 0.29 | 1.152 | 85 | 2.2 | cbm_f (4) | 0.347 | 40 |
| r2 s1 | 1.375 | no | 4 | 0.32 | 0.941 | 87 | 2.2 | cbm_f (4) | 0.110 | 71 |
| r2 s2 | 1.499 | no | 4 | 0.34 | 0.997 | 88 | 2.2 | cbm_f (4) | 0.355 | 37 |
| r3 s0 | 0.774 | no | 0 | 0.00 | 0.774 | - | 2.1 | - | 0.178 | 39 |
| r3 s1 | 0.928 | no | 0 | 0.00 | 0.928 | - | 2.1 | - | 0.314 | 41 |
| r3 s2 | 0.778 | no | 0 | 0.00 | 0.778 | - | 2.1 | - | 0.577 | 65 |
| r4 s0 | 0.621 | no | 0 | 0.00 | 0.621 | - | 2.7 | - | 0.703 | 52 |
| r4 s1 | 0.705 | no | 0 | 0.00 | 0.705 | - | 2.3 | - | 0.325 | 81 |
| r4 s2 | 0.792 | no | 0 | 0.00 | 0.792 | - | 2.4 | - | 0.332 | 38 |
| r5 s0 | 0.782 | no | 0 | 0.00 | 0.782 | - | 2.5 | - | 0.192 | 36 |
| r5 s1 | 0.819 | no | 0 | 0.00 | 0.819 | - | 2.6 | - | 0.511 | 44 |
| r5 s2 | 0.749 | no | 0 | 0.00 | 0.749 | - | 2.4 | - | 0.260 | 46 |
| r6 s0 | 2.500 | no | 8 | 0.63 | 0.955 | 103 | 2.4 | cbm_f (8) | 0.372 | 39 |
| r6 s1 | 2.676 | no | 7 | 0.68 | 0.881 | 104 | 2.4 | cbm_f (7) | 0.606 | 65 |
| r6 s2 | 2.600 | no | 9 | 0.61 | 1.037 | 101 | 2.3 | cbm_f (9) | 0.243 | 31 |
| r7 s0 | 0.743 | no | 1 | 0.10 | 0.670 | 76 | 2.1 | cbm_f (1) | 0.485 | 81 |
| r7 s1 | 1.158 | no | 3 | 0.44 | 0.649 | 114 | 2.1 | cbm_f (3) | 0.625 | 61 |
| r7 s2 | 1.592 | no | 2 | 0.09 | 1.455 | 311 | 2.0 | cbm_f (2) | 0.466 | 31 |
| r8 s0 | 1.086 | no | 2 | 0.08 | 1.003 | 120 | 2.2 | cbm_f (2) | 0.177 | 44 |
| r8 s1 | 1.438 | no | 3 | 0.25 | 1.083 | 123 | 2.1 | cbm_f (3) | 0.189 | 38 |
| r8 s2 | 1.147 | no | 3 | 0.12 | 1.017 | 121 | 2.1 | cbm_f (3) | 0.274 | 89 |
| r9 s0 | 0.830 | no | 0 | 0.00 | 0.830 | - | 2.1 | - | 0.816 | 33 |
| r9 s1 | 0.890 | no | 0 | 0.00 | 0.890 | - | 2.1 | - | 1.033 | 40 |
| r9 s2 | 0.874 | no | 0 | 0.00 | 0.874 | - | 2.2 | - | 0.484 | 48 |

- Tukey fence 2.724 eV; outlying runs: r0 seed 1, r1 seed 0.
- D run MAE: median 1.151, 10% trimmed mean 1.243, mean 1.359, max 3.358 eV (S for reference: median 1.224, trimmed mean 1.214).
- Non-finite predictions in 0 runs; non-finite training or validation loss in 0 runs. 16 of 30 runs carry 78 extreme sites in all, 0.34 of the absolute error of the budget; hosts: Ba2CePtO6, BaCeO3, BaLa2O4, BaLa2PtO5, Cs2CeO3, KLaO2, La2Zr2O7, La3SbO3, LaAsO3, LaBO3, LaScO3, NaLa2TaO6, Rb2CeO3.
- A, all runs: -0.142 [-0.706, +0.259], upper +0.211 (MAE of D 1.275); outlying runs removed: -0.028 [-0.529, +0.290], upper +0.257 (MAE of D 1.162; resamples kept: 10, D runs kept: 28).

### 50 training hosts

| Run | MAE | Outlying | Extreme sites | Share of abs. error from them | MAE without them | Median z, extreme sites | Median z, other sites | Descriptor with largest z | Best validation MAE | Epochs |
|---|---|---|---|---|---|---|---|---|---|---|
| r0 s0 | 0.719 | no | 0 | 0.00 | 0.719 | - | 2.1 | - | 0.318 | 34 |
| r0 s1 | 0.731 | no | 0 | 0.00 | 0.731 | - | 2.0 | - | 0.152 | 38 |
| r0 s2 | 0.622 | no | 0 | 0.00 | 0.622 | - | 1.9 | - | 0.480 | 45 |
| r1 s0 | 0.659 | no | 0 | 0.00 | 0.659 | - | 2.0 | - | 0.417 | 45 |
| r1 s1 | 0.955 | no | 3 | 0.28 | 0.691 | 62 | 2.1 | cbm_f (3) | 0.894 | 38 |
| r1 s2 | 1.240 | no | 4 | 0.44 | 0.708 | 61 | 2.0 | cbm_f (4) | 0.390 | 60 |
| r2 s0 | 10.336 | yes | 16 | 0.91 | 0.965 | 301 | 1.9 | cbm_f (16) | 126.434 | 33 |
| r2 s1 | 0.672 | no | 0 | 0.00 | 0.672 | - | 1.9 | - | 0.568 | 41 |
| r2 s2 | 0.591 | no | 0 | 0.00 | 0.591 | - | 1.8 | - | 0.213 | 71 |
| r3 s0 | 0.617 | no | 0 | 0.00 | 0.617 | - | 2.1 | - | 0.374 | 61 |
| r3 s1 | 0.742 | no | 0 | 0.00 | 0.742 | - | 2.1 | - | 0.240 | 69 |
| r3 s2 | 1.412 | no | 8 | 0.47 | 0.766 | 213 | 2.1 | cbm_f (8) | 1.721 | 31 |
| r4 s0 | 0.604 | no | 0 | 0.00 | 0.604 | - | 2.2 | - | 0.253 | 39 |
| r4 s1 | 0.606 | no | 0 | 0.00 | 0.606 | - | 2.2 | - | 0.131 | 51 |
| r4 s2 | 0.645 | no | 0 | 0.00 | 0.645 | - | 2.4 | - | 0.410 | 77 |
| r5 s0 | 0.610 | no | 0 | 0.00 | 0.610 | - | 2.3 | - | 0.421 | 53 |
| r5 s1 | 0.871 | no | 0 | 0.00 | 0.871 | - | 2.3 | - | 0.644 | 31 |
| r5 s2 | 0.727 | no | 0 | 0.00 | 0.727 | - | 2.2 | - | 0.429 | 36 |
| r6 s0 | 6.179 | yes | 10 | 0.83 | 1.065 | 127 | 2.1 | cbm_f (10) | 0.414 | 33 |
| r6 s1 | 5.541 | yes | 9 | 0.82 | 1.019 | 150 | 2.2 | cbm_f (9) | 0.368 | 45 |
| r6 s2 | 3.419 | yes | 9 | 0.77 | 0.815 | 147 | 2.1 | cbm_f (9) | 0.492 | 87 |
| r7 s0 | 0.821 | no | 1 | 0.08 | 0.761 | 108 | 2.1 | cbm_f (1) | 0.469 | 33 |
| r7 s1 | 0.712 | no | 1 | 0.10 | 0.640 | 109 | 2.1 | cbm_f (1) | 0.356 | 42 |
| r7 s2 | 0.666 | no | 1 | 0.09 | 0.607 | 107 | 2.0 | cbm_f (1) | 0.749 | 71 |
| r8 s0 | 0.910 | no | 0 | 0.00 | 0.910 | - | 2.0 | - | 0.296 | 36 |
| r8 s1 | 0.952 | no | 3 | 0.13 | 0.840 | 94 | 2.0 | cbm_f (3) | 0.513 | 47 |
| r8 s2 | 1.310 | no | 4 | 0.34 | 0.875 | 97 | 2.0 | cbm_f (4) | 0.695 | 33 |
| r9 s0 | 1.002 | no | 0 | 0.00 | 1.002 | - | 2.1 | - | 0.606 | 32 |
| r9 s1 | 0.820 | no | 0 | 0.00 | 0.820 | - | 2.2 | - | 0.828 | 39 |
| r9 s2 | 0.682 | no | 0 | 0.00 | 0.682 | - | 2.1 | - | 0.681 | 33 |

- Tukey fence 1.484 eV; outlying runs: r2 seed 0, r6 seed 0, r6 seed 1, r6 seed 2.
- D run MAE: median 0.737, 10% trimmed mean 0.938, mean 1.546, max 10.336 eV (S for reference: median 1.099, trimmed mean 1.053).
- Non-finite predictions in 0 runs; non-finite training or validation loss in 0 runs. 12 of 30 runs carry 69 extreme sites in all, 0.52 of the absolute error of the budget; hosts: Ba2CePtO6, Ba2LaSbO6, BaCeO3, BaLa2O4, BaLa2PtO5, Cs2CeO3, KLaO2, KNaLaNbO5, KNaLaTaO5, La2Hf2O7, La2Zr2O7, La3SbO3, LaAsO3, LaBO3, LaNbO4, LaScO3, LaTaO4, Rb2CeO3, RbLaO2, Sr2CeO4.
- A, all runs: -0.509 [-1.823, +0.277], upper +0.241 (MAE of D 1.468); outlying runs removed: +0.238 [+0.096, +0.368], upper +0.347 (MAE of D 0.723; resamples kept: 9, D runs kept: 26).

## (b) Training-limit counts

Record: `results/derived_w2/w2_training_limit.json` (git 6a49183). A run is capped when it stopped at the epoch limit (200 epochs) rather than by early stopping. P is P1 then D and has no epochs of its own; a P run counts as capped when its P1 or D component is. Sweep design, 10 resamples x 3 seeds.

| Training hosts | S | D | P1 | P (P1 or D component) |
|---|---|---|---|---|
| 100 | 0 / 30 | 0 / 30 | 0 / 30 | 0 / 30 |
| 200 | 0 / 30 | 0 / 30 | 2 / 30 | 2 / 30 |
| 25 | 0 / 30 | 0 / 30 | 0 / 30 | 0 / 30 |
| 400 | 1 / 30 | 0 / 30 | 10 / 30 | 10 / 30 |
| 50 | 0 / 30 | 0 / 30 | 0 / 30 | 0 / 30 |
| 654 | 3 / 30 | 1 / 30 | 20 / 30 | 21 / 30 |

Paired cells at 654 hosts (same resample and seed; single-run MAE, eV; A_cell = MAE_S - MAE_D):

| Design | Cell type | Cells | Mean MAE S | Mean MAE D | Mean A_cell |
|---|---|---|---|---|---|
| 30 x 5 | S capped, D not | 11 | 0.288 | 0.282 | +0.006 |
| 30 x 5 | D capped, S not | 3 | 0.316 | 0.257 | +0.058 |
| 30 x 5 | all | 150 | 0.334 | 0.289 | +0.045 |
| 30 x 5 | both capped | 3 | 0.295 | 0.262 | +0.033 |
| 30 x 5 | neither capped | 133 | 0.339 | 0.291 | +0.048 |
| 10 x 3 | S capped, D not | 3 | 0.289 | 0.280 | +0.010 |
| 10 x 3 | D capped, S not | 1 | 0.310 | 0.265 | +0.045 |
| 10 x 3 | all | 30 | 0.325 | 0.303 | +0.023 |
| 10 x 3 | both capped | 0 | n/a | n/a | n/a |
| 10 x 3 | neither capped | 26 | 0.330 | 0.307 | +0.024 |

- 30 x 5: mean A_cell +0.045 with all cells, +0.048 without the cells that hold a capped run: the capped cells lowers A by 0.0032 eV. Capped S runs have a lower MAE than uncapped ones by 0.051 eV.
- 10 x 3: +0.023 against +0.024 (lowers A, 0.0007 eV).
- Seed-ensemble A at 654 (30 x 5, point only): +0.033 with all runs, +0.037 with the 20 capped runs removed.

## (c) Crossover with the forest

Record: `results/derived_w2/w2_forest_crossover.json` (git 6a49183). Difference of the seed-ensemble MAE and RF-Kumagai (eV), paired G1 hierarchical bootstrap (the C1 draws). Below = the two-sided 95% interval lies below 0.

| Training hosts | S - RF | 95% | below | D - RF | 95% | below |
|---|---|---|---|---|---|---|
| 25 | +0.374 | [+0.307, +0.438] | no | +0.515 | [+0.134, +1.060] | no |
| 50 | +0.321 | [+0.244, +0.412] | no | +0.830 | [+0.068, +2.094] | no |
| 100 | +0.089 | [+0.027, +0.154] | no | +0.006 | [-0.044, +0.073] | no |
| 200 | -0.023 | [-0.049, +0.002] | no | -0.046 | [-0.066, -0.028] | yes |
| 400 | -0.017 | [-0.041, +0.007] | no | -0.071 | [-0.090, -0.051] | yes |
| 654 | -0.051 | [-0.073, -0.030] | yes | -0.066 | [-0.084, -0.047] | yes |

- S: point below the forest from 200 hosts; below with a 95% interval first at 654 hosts.
- D: point below from 200 hosts; below with a 95% interval from 200 hosts on.

## (d) The bound at 200, 400 and 654 training hosts

Record: `results/derived_w2/w2_bound_spread.json` (git 6a49183). A with its two-sided 95% interval and one-sided upper bound; the spread is that of the per-resample A (seed ensemble) and of single runs.

| Training hosts | Design | A | 95% | upper | bootstrap SD | SD over resamples | min, max over resamples | resamples above 0.05 | resamples below 0 | single-run SD |
|---|---|---|---|---|---|---|---|---|---|---|
| 200 | 10 x 3 (sweep) | +0.024 | [-0.006, +0.052] | +0.047 | 0.015 | 0.034 | -0.042, +0.069 | 2 | 2 | 0.083 |
| 400 | 10 x 3 (sweep) | +0.054 | [+0.027, +0.080] | +0.075 | 0.013 | 0.034 | +0.007, +0.114 | 6 | 0 | 0.054 |
| 654 | 10 x 3 (sweep) | +0.015 | [-0.008, +0.037] | +0.033 | 0.011 | 0.030 | -0.047, +0.058 | 1 | 3 | 0.049 |
| 400 | 30 x 5 (precision extension) | +0.066 | [+0.051, +0.081] | +0.079 | n/a | 0.034 | -0.023, +0.121 | 19 | 1 | n/a |
| 654 | 30 x 5 (precision extension) | +0.033 | [+0.021, +0.045] | +0.043 | n/a | 0.028 | -0.065, +0.094 | 8 | 1 | n/a |

## (e) Screening, final network

Record: `results/derived_w2/w2_screening_sites.json` (git 6a49183). S at 654 training hosts; prediction = seed-ensemble mean averaged over the resamples that hold the host out (N). Cations: the cation elements of the oxide and the number bonded to the removed oxygen (first shell).

| Oxide | Site | Cations (first shell) | DFT (eV) | Prediction (eV) | Error (eV) | N |
|---|---|---|---|---|---|---|
| ZnO | O1 | Zn (4) | 4.965 | 5.324 | +0.358 | 1 |
| TiO2 | O4 | Ti (4) | 5.347 | 5.790 | +0.443 | 2 |
| SnO2 | O1 | Sn (3) | 4.790 | 4.463 | -0.327 | 5 |
| MgO | O1 | Mg (6) | 7.611 | 7.003 | -0.608 | 1 |
| Al2O3 | O1 | Al (4) | 7.694 | 7.118 | -0.576 | 2 |
| ZrO2 | O1 | Zr (3) | 7.013 | 7.550 | +0.537 | 1 |
| ZrO2 | O2 | Zr (4) | 6.925 | 7.570 | +0.645 | 1 |
| Ga2O3 | O1 | Ga (3) | 4.668 | 4.800 | +0.131 | 3 |
| Ga2O3 | O2 | Ga (4) | 5.299 | 4.981 | -0.317 | 3 |
| Ga2O3 | O3 | Ga (3) | 5.068 | 4.809 | -0.259 | 3 |

Pooled MAE 0.420 eV, 95% interval [0.307, 0.553] (host-cluster bootstrap, 7 hosts); bias +0.003 eV; 5 over- and 5 under-predicted; largest error 0.645 eV (ZrO2_Va_O2_0).

## Reproduction

7 comparisons, 430 values shared with earlier records; maximum absolute difference 1.7e-16; all below 1e-9: yes.

| Comparison | Reference | Values | Max abs difference |
|---|---|---|---|
| a.A_all_runs_vs_final_network_summary | results/derived_c1/final_network_summary.json payload.table.rows.B25, B50 | 14 | 0.0e+00 |
| a.single_run_mae_vs_staging_runs_and_run_records | results/analysis/staging_runs.parquet mae; results/v2_sweep/<run_id>.json payload.metrics.mae | 120 | 0.0e+00 |
| b.capped_counts_vs_precision_record | results/precision_a_b400_b654.json payload.descriptive.capped (counts, by source, mean single-run MAE) | 59 | 0.0e+00 |
| c.S_D_RF_marginals_vs_final_network_summary | results/derived_c1/final_network_summary.json payload.table.rows.B* (MAE_S, MAE_D, MAE_RF) | 72 | 0.0e+00 |
| d.A_10x3_vs_final_network_summary_and_c1c2_v2 | results/derived_c1/final_network_summary.json payload.table.rows.B*.A; results/c1c2_v2.json payload.A_mae.*.per_resample, sd_across_resamples | 45 | 1.7e-16 |
| d.A_30x5_vs_precision_record | results/precision_a_b400_b654.json payload.v2.30x5.*.A | 64 | 0.0e+00 |
| e.screening_vs_screening_demo_and_c5 | figures/main/data/screening_demo.json payload.sites.*.v2, summary.v2; results/screening_c5.json | 56 | 0.0e+00 |

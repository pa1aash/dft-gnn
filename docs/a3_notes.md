# A3: geometry robustness (C3b), notes

Rules: `docs/deviations.md`, row of 2026-10-14 (§9, step A3), logged before any number was computed; it restates
ANALYSIS_PLAN §9. Labels:

- **Registered**: the v1 (originally registered backbone) geometry evaluation on our 818 MACE-MP-0 relaxations at
  B = 654.
- **DESCRIPTIVE EXTRA**: the same at B = 200 (row of 2026-10-10, MLIP budgets). Inference only, no test.
- **POST HOC**: the TOST of ΔMAE_P − ΔMAE_S and the slope comparison (the collaborator rule of 2026-10-09, ratified
  2026-10-11), and the descriptive cross-check against the collaborator's 809 relaxations and his v2 evaluation. The v2
  evaluation is never pre-registered. No v2 geometry evaluation on our 818 relaxations exists.

Records: `results/geometry_eval_table.json` (integrity), `results/geometry_c3b.json` (ΔMAE, null rule, regression,
sensitivity, POST HOC item i), `results/geometry_descriptive.json` (component distributions, d-bins, GPU classes,
809 cross-check, sanity checks). Scripts: `analysis/geometry_eval_table.py`, `analysis/geometry_analysis.py` (tests:
`analysis/tests/test_geometry.py`, 23 synthetic checks). Figure: `figures/main/fig5_geometry.pdf`.

Conditions: (i) DFT geometry, (ii) MLIP geometry, (iii) MLIP geometry isotropically rescaled to the DFT volume. D keeps
its DFT descriptors under every condition, so it is a fixed oracle and its change isolates the graph input.

## Inputs and integrity

180 geomeval records (S, D, P × r = 0..9 × seeds 0-2 × B = 654, 200). Their run ids, keys and specs equal
`specs/geomeval.jsonl`, and every prediction sha256 matches its record. Each run covers its test sites once under each
condition, with finite predictions. Targets and hosts equal the universe. No host is flagged `excluded_from_C3b`: 818
tiled, 797 translation-only and 21 with one lattice point operation, which reproduces `data/tiling_summary_v1.csv`. The
vacancy atom of every evaluated site (1561) is O in both the release supercell and the MLIP supercell. 818 relax
records, one per host, and the sha256 of all 1636 MLIP unit-cell and supercell files read match their records. 739
hosts and 1561 sites are evaluated under every condition, 164 test hosts per resample. 7 relaxations did not converge;
they are kept and flagged.

## Tables

### T1. ΔMAE (eV), seed ensemble, paired hierarchical bootstrap (2000 draws, seed 20261008), two-sided 95%

| B | model | MAE (i) | MAE (ii) | MAE (iii) | ΔMAE (ii) | 95% interval | ΔMAE (iii) | 95% interval |
|---|---|---:|---:|---:|---:|---|---:|---|
| 654 | S | 0.2729 | 0.2768 | 0.2802 | +0.00394 | [+0.00034, +0.00754] | +0.00731 | [+0.00297, +0.01240] |
| 654 | D | 0.2845 | 0.2845 | 0.2845 | +0.00002 | [−0.00002, +0.00008] | +0.00001 | [−0.00001, +0.00004] |
| 654 | P | 0.3708 | 0.3717 | 0.3714 | +0.00093 | [−0.00188, +0.00417] | +0.00054 | [−0.00051, +0.00164] |
| 200 (extra) | S | 0.5165 | 0.5165 | 0.5165 | +0.00001 | [−0.00002, +0.00003] | +0.00000 | [−0.00001, +0.00003] |
| 200 (extra) | D | 0.4214 | 0.4214 | 0.4214 | −0.00000 | [−0.00010, +0.00007] | +0.00002 | [−0.00004, +0.00007] |
| 200 (extra) | P | 0.5528 | 0.5529 | 0.5525 | +0.00010 | [−0.00066, +0.00089] | −0.00023 | [−0.00066, +0.00016] |

### T2. Sensitivity without the 7 non-converged hosts (161–164 test hosts per resample; new draw set, same seed)

| B | model | ΔMAE (ii) | 95% interval | ΔMAE (iii) | 95% interval |
|---|---|---:|---|---:|---|
| 654 | S | +0.00411 | [+0.00070, +0.00758] | +0.00785 | [+0.00336, +0.01308] |
| 654 | D | +0.00002 | [−0.00002, +0.00008] | +0.00001 | [−0.00001, +0.00004] |
| 654 | P | +0.00102 | [−0.00170, +0.00430] | +0.00071 | [−0.00036, +0.00191] |
| 200 (extra) | S | +0.00001 | [−0.00002, +0.00003] | +0.00000 | [−0.00001, +0.00003] |
| 200 (extra) | D | −0.00001 | [−0.00011, +0.00008] | +0.00002 | [−0.00004, +0.00007] |
| 200 (extra) | P | +0.00009 | [−0.00068, +0.00081] | −0.00023 | [−0.00068, +0.00014] |

Median internal RMSD over the 811 converged hosts: 0.0239 Å. Null rule outcome unchanged: not met, neither condition
holds.

### T3. Geometry components of the relaxations

eps_v = (V_MLIP / V_DFT)^(1/3) − 1 (positive for every host: smallest 0.0022, so |eps_v| = eps_v); deviatoric strain
= ‖dev U‖_F; internal RMSD in Å (definitions: row of 2026-10-10).

| hosts | component | n | median | Q1 | Q3 | P95 | max |
|---|---|---:|---:|---:|---:|---:|---:|
| all | eps_v | 818 | 0.0157 | 0.0121 | 0.0204 | 0.0293 | 0.0867 |
| all | deviatoric strain | 818 | 0.0057 | 0.0023 | 0.0129 | 0.0335 | 0.2407 |
| all | internal RMSD (Å) | 818 | 0.0242 | 0.0135 | 0.0410 | 0.1009 | 0.6205 |
| evaluated | eps_v | 739 | 0.0158 | 0.0122 | 0.0203 | 0.0286 | 0.0867 |
| evaluated | deviatoric strain | 739 | 0.0056 | 0.0023 | 0.0128 | 0.0333 | 0.2407 |
| evaluated | internal RMSD (Å) | 739 | 0.0244 | 0.0138 | 0.0403 | 0.0993 | 0.6205 |

The 7 non-converged hosts (mp-1211443, mp-30298, mp-3635, mp-504510, mp-557871, mp-561725, mp-562441) have median eps_v
0.0455, deviatoric 0.1277 and internal RMSD 0.2668 Å. Each component's maximum over all 818 hosts belongs to this group.

### T4. Components by d-electron bin (our definition, `data/host_dbins_v1.csv`)

| d-bin | n | eps_v median | P95 | max | deviatoric median | P95 | max | RMSD median (Å) | P95 | max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| d0 | 313 | 0.0151 | 0.0260 | 0.0867 | 0.0055 | 0.0295 | 0.2407 | 0.0214 | 0.0960 | 0.6205 |
| d10 | 428 | 0.0163 | 0.0327 | 0.0614 | 0.0056 | 0.0343 | 0.1478 | 0.0275 | 0.1090 | 0.3469 |
| other | 68 | 0.0172 | 0.0271 | 0.0307 | 0.0077 | 0.0360 | 0.2151 | 0.0181 | 0.0556 | 0.1743 |
| unassigned | 9 | 0.0209 | 0.0316 | 0.0323 | 0.0050 | 0.0183 | 0.0206 | 0.0292 | 0.0600 | 0.0668 |

Evaluated hosts: d0 281, d10 392, other 58, unassigned 8.

### T5. Components by GPU class of the relax run (descriptive)

| GPU | n | eps_v median | P95 | max | deviatoric median | P95 | max | RMSD median (Å) | P95 | max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A10 | 548 | 0.0156 | 0.0293 | 0.0867 | 0.0054 | 0.0342 | 0.2407 | 0.0245 | 0.1087 | 0.6205 |
| TITAN RTX | 239 | 0.0163 | 0.0282 | 0.0614 | 0.0061 | 0.0305 | 0.1168 | 0.0237 | 0.0868 | 0.3469 |
| RTX 4090 | 31 | 0.0132 | 0.0280 | 0.0318 | 0.0069 | 0.0308 | 0.0422 | 0.0206 | 0.0863 | 0.3441 |

Each host was relaxed once, on one card. The classes hold different hosts, so this table compares host sets, not cards.
No relaxation was repeated on a second card, and cross-card reproducibility of the relaxed geometry is not measured.

### T6. Regression of the per-host mean |pred(ii) − pred(i)| on the three components (joint OLS, coefficients in eV per SD, host bootstrap 2000, two-sided 95%)

| stratum | n | model | B | R² | eps_v | deviatoric | internal RMSD |
|---|---:|---|---|---:|---|---|---|
| pooled | 739 | S | 654 | 0.042 | +0.0105 [+0.0066, +0.0146] | −0.0014 [−0.0059, +0.0025] | −0.0021 [−0.0065, +0.0023] |
| pooled | 739 | D | 654 | 0.005 | +0.0001 [−0.0000, +0.0002] | +0.0000 [−0.0001, +0.0002] | −0.0000 [−0.0002, +0.0001] |
| pooled | 739 | P | 654 | 0.070 | +0.0095 [+0.0062, +0.0133] | +0.0003 [−0.0035, +0.0051] | −0.0021 [−0.0063, +0.0013] |
| pooled | 739 | S | 200 | 0.006 | +0.0000 [−0.0000, +0.0001] | +0.0000 [−0.0000, +0.0000] | −0.0000 [−0.0001, +0.0000] |
| pooled | 739 | D | 200 | 0.046 | +0.0004 [+0.0003, +0.0005] | −0.0000 [−0.0002, +0.0001] | −0.0000 [−0.0002, +0.0001] |
| pooled | 739 | P | 200 | 0.045 | +0.0028 [+0.0020, +0.0037] | −0.0009 [−0.0022, +0.0002] | −0.0004 [−0.0014, +0.0005] |
| d0 | 281 | S | 654 | 0.233 | +0.0118 [+0.0070, +0.0169] | −0.0014 [−0.0077, +0.0079] | −0.0003 [−0.0089, +0.0067] |
| d0 | 281 | D | 654 | 0.006 | +0.0001 [−0.0000, +0.0004] | −0.0000 [−0.0001, +0.0001] | −0.0000 [−0.0002, +0.0001] |
| d0 | 281 | P | 654 | 0.119 | +0.0131 [+0.0057, +0.0244] | −0.0030 [−0.0132, +0.0055] | −0.0015 [−0.0098, +0.0038] |
| d10 | 392 | S | 654 | 0.020 | +0.0089 [+0.0032, +0.0152] | −0.0008 [−0.0067, +0.0060] | −0.0054 [−0.0129, +0.0002] |
| d10 | 392 | D | 654 | 0.020 | +0.0000 [−0.0001, +0.0002] | −0.0000 [−0.0001, +0.0001] | +0.0001 [−0.0000, +0.0002] |
| d10 | 392 | P | 654 | 0.057 | +0.0079 [+0.0035, +0.0127] | +0.0036 [−0.0014, +0.0099] | −0.0048 [−0.0109, −0.0004] |
| other | 58 | S | 654 | 0.012 | +0.0028 [−0.0035, +0.0093] | −0.0031 [−0.0369, +0.0071] | +0.0021 [−0.0097, +0.0205] |
| other | 58 | D | 654 | 0.006 | +0.0001 [−0.0004, +0.0005] | +0.0003 [−0.0004, +0.0061] | −0.0001 [−0.0021, +0.0005] |
| other | 58 | P | 654 | 0.189 | +0.0059 [+0.0013, +0.0103] | −0.0140 [−0.0225, +0.0133] | +0.0149 [+0.0056, +0.0283] |
| unassigned | 8 | — | — | — | fewer than 20 hosts: counts only, no fit | | |

The d-bin strata at B = 200 and the single-component fits are in `payload.regression.strata`. Single-component fits,
pooled, B = 654, coefficient per SD [95%] (R²):

| model | eps_v alone | deviatoric alone | internal RMSD alone |
|---|---|---|---|
| S | +0.0083 [+0.0058, +0.0113] (0.039) | +0.0035 [+0.0014, +0.0061] (0.007) | +0.0035 [+0.0012, +0.0061] (0.007) |
| D | +0.0001 [+0.0000, +0.0002] (0.005) | +0.0001 [+0.0000, +0.0002] (0.003) | +0.0001 [+0.0000, +0.0001] (0.002) |
| P | +0.0083 [+0.0056, +0.0116] (0.068) | +0.0045 [+0.0014, +0.0089] (0.020) | +0.0040 [+0.0013, +0.0073] (0.016) |

Without the 7 non-converged hosts (732 hosts, pooled, joint, B = 654): eps_v coefficients S +0.0094 [+0.0061, +0.0134],
P +0.0087 [+0.0057, +0.0121], D +0.0001 [−0.0000, +0.0001]; the deviatoric and internal-RMSD intervals include 0 for
every model.

### T7. POST HOC (ratified rule): ΔMAE_P − ΔMAE_S and slope differences

| B | condition | ΔMAE_P − ΔMAE_S | 95% | 90% | outcome |
|---|---|---:|---|---|---|
| 654 | (ii) MLIP | −0.0030 | [−0.0083, +0.0026] | [−0.0075, +0.0016] | equivalent |
| 654 | (iii) rescaled | −0.0068 | [−0.0121, −0.0021] | [−0.0112, −0.0027] | P better; different but within the equivalence margin |
| 200 (extra) | (ii) MLIP | +0.0001 | [−0.0007, +0.0009] | [−0.0005, +0.0007] | equivalent |
| 200 (extra) | (iii) rescaled | −0.0002 | [−0.0007, +0.0002] | [−0.0006, +0.0001] | equivalent |

Joint-fit slope of P minus that of S, eV per IQR of the component (margin ±0.05 eV): at B = 654, eps_v −0.0011 (90%
[−0.0056, +0.0035]), deviatoric +0.0009 ([−0.0013, +0.0039]) and internal RMSD +0.0000 ([−0.0023, +0.0021]), all
equivalent. At B = 200: eps_v +0.0029 ([+0.0022, +0.0038]), P worse but within the margin; deviatoric and internal RMSD
equivalent.

### T8. POST HOC descriptive cross-check against the collaborator's 809 relaxations

All 809 of his hosts are among our 818. 800 pass the comparability rule; 9 fail it (8 on a lattice length, 1 on a
lattice angle) and are not compared. His components are recomputed with `dftgnn.mlip.geometry.host_metrics` from his
relaxed unit cells against our DFT unit cells.

| component | Spearman | median abs. difference | max abs. difference | median, ours | median, his |
|---|---:|---:|---:|---:|---:|
| eps_v | 0.9999995 | 1.8e-15 | 1.4e-4 | 0.015664 | 0.015664 |
| deviatoric | 0.99991 | 3.9e-15 | 3.4e-4 | 0.005432 | 0.005432 |
| internal RMSD (Å) | 0.9999994 | 3.3e-15 | 3.9e-4 | 0.023904 | 0.023904 |

His record (`results/mlip_eval_v2.json`, v2, his 802 converged hosts): median internal RMSD 0.0239 Å, median isotropic
strain 0.0157, median deviatoric strain 0.0054. His quoted largest |dMAE| is 0.0033 eV (P-v2, B = 654, MLIP geometry).
Ours (v1, our relaxations) is 0.0073 eV at B = 654 (S, rescaled) and 0.0002 eV at B = 200 (P, rescaled). His statement
"MLIP changes predictions by at most 0.003 eV" (`docs/ingest_report.md` row 27) refers to |dMAE|, not to per-host
prediction changes. It does not carry over to v1: S-v1 at B = 654 exceeds it under both conditions.

### T9. Sanity checks

| check | result |
|---|---|
| geomeval records / relax records | 180 / 818 |
| tiling split from `data/tiling_summary_v1.csv` | 797 translation-only + 21 point operation = 818, 0 excluded |
| hosts per condition (i), (ii), (iii) | 739, 739, 739 (1561 sites, 61,992 rows each) |
| S and D condition (i) vs the stored S09 sweep predictions, same checkpoints (120 of 120 runs) | max abs difference 4.8e-4 eV overall; B = 654: S 3.5e-5, D 5.2e-6 eV; B = 200: S 4.0e-4, D 4.8e-4 eV |
| components recomputed for 20 random hosts (`default_rng(20261008)`) | max abs difference 6.3e-16 (deviatoric), 2.2e-16 (eps_v), 0 (RMSD); pass at 1e-6 |

The S09 sweep predictions came from the original sweep GPU. Condition (i) was re-run on NRP A10, TITAN RTX and RTX 4090
cards, so floating-point differences between GPU classes are expected. Per class (`payload.sanity.sweep_condition_i.by`
of `results/geometry_descriptive.json`), the largest difference is 4.8e-4 eV (D, B = 200, TITAN RTX). At B = 654 the
largest is 3.5e-5 eV, about a hundredth of S's ΔMAE there. Conditions (i) to (iii) of one run always share a card. No mismatch
was found in the geometry recomputation or the integrity checks.

## What the measurements show

Against the null rule fixed in ANALYSIS_PLAN §9 and the row of 2026-10-14 (registered budget B = 654):

1. **Condition (1) does not hold.** The median internal RMSD over the 818 relaxations is 0.0242 Å. That is 0.0142 Å
   above the 0.01 Å threshold, 2.4 times the threshold.
2. **Condition (2) does not hold.** Two of the six ΔMAE intervals exclude 0: S under MLIP geometry (+0.0039 eV, 95%
   [+0.0003, +0.0075]) and S under rescaled MLIP geometry (+0.0073 eV, [+0.0030, +0.0124]). The four intervals of D and
   P include 0.
3. **Outcome: "null rule not met; holds: neither".** The result is not reported as "serial fragility not realised in
   this regime". Removing the 7 non-converged hosts leaves the outcome unchanged (S +0.0041 and +0.0079 eV, both
   intervals above 0; median RMSD 0.0239 Å).
4. **Size.** Every ΔMAE is at most 0.0124 eV at its upper bound. S degrades by about 1.4% (ii) and 2.7% (iii) of its
   DFT-geometry MAE, and every interval lies well inside δ = 0.05 eV.
5. **D under MLIP geometry.** D's ΔMAE intervals lie within ±0.0001 eV at both budgets. Because D is a fixed
   oracle, its graph input contributes almost nothing to its prediction change.
6. **P.** Both P intervals include 0. Under the POST HOC ratified TOST, ΔMAE_P − ΔMAE_S is equivalent under MLIP
   geometry and P better, within the margin, under rescaled geometry. The plan registers no test of the S-versus-P
   difference, so "staged and end-to-end models degrade differently" is not established by a registered test.
7. **Rescaled geometry.** Rescaling to the DFT volume does not reduce S's degradation (+0.0073 under (iii) against
   +0.0039 eV under (ii)).
8. **Regression.** In the pooled joint fit, eps_v is the only component whose coefficient interval excludes 0 for S
   and P at B = 654 (S +0.0105, P +0.0095 eV per SD). The deviatoric and internal-RMSD coefficients include 0. The
   joint R² is small (S 0.042, P 0.070). Each component alone has a positive coefficient for S and P. In the d10
   stratum, P's internal-RMSD coefficient is negative (−0.0048 [−0.0109, −0.0004]). In the "other" stratum (58 hosts),
   P's internal-RMSD coefficient is positive (+0.0149 [+0.0056, +0.0283]). The unassigned stratum (8 hosts) has no fit.
9. **B = 200 (DESCRIPTIVE EXTRA).** Every interval includes 0. S at B = 200 is almost insensitive to geometry (|ΔMAE|
   ≤ 0.00003 eV at the bounds).
10. **Cross-check (POST HOC, descriptive).** Our relaxations and the collaborator's agree host by host to about 1e-15
    at the median (the same MACE-MP-0 medium model, float64, FIRE). The geometry regime is the same in both. His v2
    statement of a largest |dMAE| of 0.0033 eV does not hold for v1 S at B = 654.

## Hypotheses (not tested here)

- **H1. The volume change drives S's degradation.** MACE-MP-0 expands every host (eps_v > 0 for all 818, median 1.6%).
  The radius graph has a 5 Å cutoff and Gaussian distance features, so expansion shifts every edge distance and moves
  neighbours across the cutoff. This would explain eps_v's dominance in the regression. It does not explain why
  rescaling to the DFT volume does not reduce the degradation. A rescaled cell keeps the MLIP's shape and internal
  coordinates, and S may be more sensitive to those than to the volume. A per-host comparison of (ii) and (iii)
  changes would test this.
- **H2. D's descriptors carry its prediction.** D is almost insensitive to geometry at both budgets, so it may lean on
  its DFT descriptors and use the graph mainly for site identity. A descriptor-ablation evaluation under MLIP geometry
  would test this.
- **H3. S at B = 200 is site-blind.** S-v1 at B ≤ 200 makes nearly constant predictions within hosts (G1 and S10b
  diagnostics). That may make it insensitive to geometric detail, which would explain the zero ΔMAE at B = 200. The
  sensitivity at B = 654 would then come with learning site and geometry resolution.
- **H4. P's change is dominated by P1's response.** P inherits geometry sensitivity through P1's predicted descriptors.
  Its ΔMAE interval is wider than D's and comparable to S's, consistent with P1 responding to geometry like S does.
  P1's descriptor change under (ii) has not been measured.
- **H5. The stratum-specific internal-RMSD signs are small-sample or collinearity effects.** In the "other" and d10
  strata the joint fits separate correlated components on few hosts or with small R². These are not physical opposite
  responses until replicated.

Any of these would be logged in `docs/deviations.md` first and labelled exploratory.

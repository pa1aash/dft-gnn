# Within-host physics of S and D at B = 654 (M9)

**Label: EXTENSION.** New analysis of existing test predictions; nothing was trained or rerun. Both backbones
are analysed: v2, the primary backbone by author decision of 2026-10-11 (POST HOC: adopted after test-set
diagnostics of v1), and v1, the originally registered backbone. This breakdown was not pre-registered; its
rules (groups, thresholds, metrics, bootstrap) were logged in `docs/deviations.md` (row of 2026-10-11,
"Within-host breakdown") before any of its numbers was computed, and nothing was changed afterwards.

Every number below is read from `results/within_host_breakdown.json` (written by
`analysis/within_host_breakdown.py` from a clean tree; `payload.groups`, `payload.spearman`,
`payload.sanity`). Energies in eV. Figure: `figures/si/fig_si_withinhost_groups.pdf` (caption beside it).
Number macros: `\numWithinHostBreakdown...` (`paper/tools/make_numbers.py`; the group entries are keyed by
`<variable>_<group>`, e.g. `\numWithinHostBreakdownGroupsDClassDZeroVTwoSWithinHostMaePoint`).

## Setup

- Predictions: seed-ensemble mean (seeds 0-2) of S and D (v1: D; v2: D-state) at B = 654 on resamples 0-9,
  averaged per site over the resamples in which its host was tested. 739 hosts and 1561 sites were tested
  at least once; the 79 never-tested hosts of universe v1 (818) are absent. Sites were tested in 1 to 6
  resamples (`payload.sanity.resamples_per_site`).
- Within-host residual MAE: the G1 definition applied to the averaged predictions (hosts with ≥ 2 tested
  sites; residual = (prediction − host mean prediction) − (target − host mean target)). Host means always use
  all tested sites of the host.
- Zero-skill value: mean absolute deviation of the true energies from the host mean over the same sites. It
  is the within-host residual MAE of any predictor that is constant within each host (B0, the host-mean
  oracle, a site-blind network). A model "has within-host skill" in a group when its within-host residual
  MAE is below this value.
- Groups: (a) d-electron class (`data/host_dbins_v1.csv`); (b) cation element (every element other than O,
  elements in ≥ 15 tested hosts, a host counted under each of its cations; 39 elements); (c) hosts with at
  least one of Nb, W, Ti, V, Ta, Mo ("PHS-prone") versus none; (d) stability terciles of
  `desc_formation_energy` (Materials Project formation energy per atom; edges −2.731 and −2.117 eV/atom;
  "lower" = most stable); (e) terciles of the PBEsol(+U) band gap `desc_band_gap` (edges 2.363 and
  3.453 eV); (f) site rank of the vacancy-O Bader charge `desc_bader_charge` within its host (lowest = most
  negative), and the within-host Spearman correlation for hosts with ≥ 3 tested sites.
- Intervals: two-sided 95% percentile intervals of a host-cluster bootstrap within each group (2000 draws,
  `default_rng(SeedSequence([20261012, k]))`), shared by S and D of both backbones, so S − D and v2 − v1 are
  paired on the same hosts. No interval where fewer than 10 hosts contribute to a metric; the d-class
  "unassigned" (8 hosts) is flagged "descriptive, small n". No hypothesis tests and no multiplicity
  correction: the tables hold about 1000 intervals, so some exclude zero by chance alone.

## Sanity checks (Task 3)

| check | result |
|---|---|
| (i) pooled site MAE, v1, resample-mean estimator of G1 on this pipeline's seed ensemble vs `results/g1_primary.json` (`per_budget.654.MAE_S`, `MAE_D`) | S 0.27286 vs 0.27286, D 0.28447 vs 0.28447; abs. differences 1.1e-16 and 5.6e-17: MATCH (≤ 1e-3) |
| (ii) pooled within-host MAE, v1, same estimator vs `results/g1_within_host.json` (`per_budget.654.S`, `D`) | S 0.14259 vs 0.14259, D 0.16092 vs 0.16092; abs. differences 5.6e-17 and 0: MATCH |
| v2 reference: same estimator vs `results/c1c2_v2.json` (`mae.654`) | site MAE and within-host MAE of S and D-state equal to ≤ 2.8e-17: MATCH |
| effect of averaging each site over its resamples (this analysis) instead of averaging per-resample MAEs (G1) | v1 pooled site MAE: S 0.259 (−0.014 vs G1), D 0.274 (−0.011); v1 within-host MAE: S 0.138 (−0.005), D 0.154 (−0.007). The site sets are the same (1561 sites); the difference comes from weighting (G1 weights a site by the number of resamples that tested it) and from averaging predictions of differently trained models, which lowers the error |
| (iii) group sizes | d class, PHS-prone, stability and band-gap terciles each partition 739 hosts and 1561 sites exactly. Bader rank: 463 eligible hosts (≥ 2 sites, charges not all equal), 1285 sites = 463 lowest + 463 highest + 359 middle (260 hosts). Cation: 1686 host memberships over 39 elements (multi-cation hosts counted repeatedly); 1 tested host contains none of the 39 listed elements. Spearman: 260 hosts with ≥ 3 sites, none undefined |

No mismatch was found.

## Tables

### T1. Within-host residual MAE (eV) and zero-skill value

| variable | group | hosts | sites | hosts ≥2 sites | sites in those | zero-skill | S v2 | D v2 | S v1 | D v1 | flag |
|---|---|---:|---:|---:|---:|---|---|---|---|---|---|
| all | all | 739 | 1561 | 463 | 1285 | 0.184 [0.166, 0.203] | 0.146 [0.133, 0.161] | 0.146 [0.133, 0.160] | 0.138 [0.126, 0.151] | 0.154 [0.139, 0.170] |  |
| (a) d class | d0 | 281 | 601 | 191 | 511 | 0.127 [0.110, 0.144] | 0.107 [0.092, 0.123] | 0.104 [0.088, 0.119] | 0.107 [0.093, 0.122] | 0.111 [0.096, 0.127] |  |
| (a) d class | d10 | 392 | 878 | 258 | 744 | 0.219 [0.192, 0.251] | 0.168 [0.148, 0.190] | 0.168 [0.149, 0.190] | 0.155 [0.138, 0.174] | 0.181 [0.158, 0.205] |  |
| (a) d class | other | 58 | 72 | 12 | 26 | 0.284 [0.159, 0.418] | 0.264 [0.144, 0.400] | 0.363 [0.194, 0.558] | 0.254 [0.143, 0.383] | 0.244 [0.102, 0.405] |  |
| (a) d class | unassigned | 8 | 10 | 2 | 4 | 0.067 | 0.066 | 0.049 | 0.063 | 0.029 | descriptive, small n |
| (b) cation | Ag | 25 | 31 | 4 | 10 | 0.429 | 0.371 | 0.288 | 0.375 | 0.327 |  |
| (b) cation | Al | 34 | 87 | 28 | 81 | 0.242 [0.176, 0.320] | 0.116 [0.081, 0.163] | 0.153 [0.103, 0.212] | 0.138 [0.107, 0.178] | 0.180 [0.117, 0.256] |  |
| (b) cation | As | 42 | 109 | 31 | 98 | 0.198 [0.110, 0.326] | 0.187 [0.112, 0.291] | 0.175 [0.108, 0.260] | 0.174 [0.107, 0.260] | 0.172 [0.099, 0.276] |  |
| (b) cation | Au | 19 | 24 | 4 | 9 | 0.228 | 0.248 | 0.214 | 0.249 | 0.203 |  |
| (b) cation | B | 69 | 155 | 50 | 136 | 0.258 [0.173, 0.349] | 0.180 [0.124, 0.250] | 0.191 [0.131, 0.256] | 0.168 [0.117, 0.222] | 0.214 [0.144, 0.292] |  |
| (b) cation | Ba | 94 | 195 | 66 | 167 | 0.217 [0.151, 0.297] | 0.153 [0.105, 0.217] | 0.165 [0.123, 0.217] | 0.140 [0.100, 0.188] | 0.180 [0.130, 0.243] |  |
| (b) cation | Be | 18 | 52 | 17 | 51 | 0.255 [0.112, 0.443] | 0.204 [0.096, 0.346] | 0.163 [0.086, 0.258] | 0.191 [0.101, 0.304] | 0.175 [0.090, 0.280] |  |
| (b) cation | Bi | 43 | 99 | 29 | 85 | 0.273 [0.188, 0.361] | 0.217 [0.160, 0.279] | 0.230 [0.165, 0.293] | 0.194 [0.137, 0.259] | 0.229 [0.158, 0.305] |  |
| (b) cation | Ca | 52 | 117 | 35 | 100 | 0.175 [0.120, 0.234] | 0.150 [0.106, 0.199] | 0.133 [0.087, 0.180] | 0.132 [0.092, 0.174] | 0.138 [0.091, 0.189] |  |
| (b) cation | Cd | 29 | 54 | 17 | 42 | 0.208 [0.106, 0.316] | 0.145 [0.072, 0.234] | 0.200 [0.118, 0.306] | 0.146 [0.073, 0.239] | 0.208 [0.120, 0.314] |  |
| (b) cation | Cs | 57 | 123 | 37 | 103 | 0.182 [0.139, 0.230] | 0.122 [0.093, 0.155] | 0.126 [0.093, 0.166] | 0.126 [0.096, 0.161] | 0.139 [0.104, 0.179] |  |
| (b) cation | Cu | 24 | 30 | 4 | 10 | 0.080 | 0.047 | 0.197 | 0.039 | 0.131 |  |
| (b) cation | Ga | 31 | 85 | 27 | 81 | 0.245 [0.181, 0.316] | 0.160 [0.122, 0.207] | 0.176 [0.129, 0.227] | 0.130 [0.094, 0.168] | 0.215 [0.154, 0.277] |  |
| (b) cation | Ge | 49 | 137 | 43 | 131 | 0.197 [0.142, 0.268] | 0.137 [0.104, 0.182] | 0.153 [0.114, 0.199] | 0.129 [0.097, 0.168] | 0.156 [0.114, 0.206] |  |
| (b) cation | Hf | 16 | 31 | 11 | 26 | 0.159 [0.076, 0.250] | 0.118 [0.059, 0.187] | 0.127 [0.061, 0.195] | 0.111 [0.049, 0.185] | 0.141 [0.076, 0.212] |  |
| (b) cation | In | 23 | 53 | 18 | 48 | 0.192 [0.131, 0.258] | 0.162 [0.117, 0.215] | 0.148 [0.084, 0.224] | 0.148 [0.102, 0.202] | 0.115 [0.073, 0.165] |  |
| (b) cation | K | 81 | 168 | 49 | 136 | 0.136 [0.110, 0.162] | 0.115 [0.090, 0.142] | 0.099 [0.077, 0.121] | 0.108 [0.084, 0.132] | 0.103 [0.079, 0.127] |  |
| (b) cation | La | 43 | 82 | 24 | 63 | 0.192 [0.122, 0.265] | 0.182 [0.121, 0.249] | 0.155 [0.097, 0.221] | 0.166 [0.106, 0.232] | 0.178 [0.116, 0.247] |  |
| (b) cation | Li | 87 | 195 | 58 | 166 | 0.144 [0.113, 0.179] | 0.130 [0.098, 0.165] | 0.117 [0.094, 0.143] | 0.126 [0.097, 0.158] | 0.131 [0.107, 0.157] |  |
| (b) cation | Mg | 46 | 98 | 32 | 84 | 0.144 [0.106, 0.184] | 0.122 [0.091, 0.156] | 0.146 [0.102, 0.197] | 0.116 [0.083, 0.151] | 0.146 [0.104, 0.193] |  |
| (b) cation | Mo | 23 | 42 | 12 | 31 | 0.146 [0.083, 0.213] | 0.089 [0.046, 0.141] | 0.110 [0.068, 0.161] | 0.093 [0.058, 0.144] | 0.106 [0.066, 0.151] |  |
| (b) cation | Na | 116 | 250 | 76 | 210 | 0.133 [0.098, 0.176] | 0.114 [0.085, 0.149] | 0.087 [0.066, 0.112] | 0.103 [0.079, 0.132] | 0.091 [0.069, 0.119] |  |
| (b) cation | Nb | 26 | 52 | 16 | 42 | 0.244 [0.167, 0.326] | 0.212 [0.153, 0.275] | 0.210 [0.136, 0.291] | 0.177 [0.127, 0.234] | 0.230 [0.155, 0.308] |  |
| (b) cation | Pb | 37 | 95 | 25 | 83 | 0.166 [0.122, 0.213] | 0.136 [0.101, 0.172] | 0.168 [0.132, 0.208] | 0.134 [0.096, 0.172] | 0.169 [0.125, 0.218] |  |
| (b) cation | Pt | 21 | 28 | 7 | 14 | 0.362 | 0.307 | 0.509 | 0.294 | 0.309 |  |
| (b) cation | Rb | 65 | 131 | 39 | 105 | 0.141 [0.111, 0.177] | 0.105 [0.081, 0.132] | 0.091 [0.070, 0.117] | 0.110 [0.086, 0.137] | 0.099 [0.075, 0.126] |  |
| (b) cation | Sb | 62 | 130 | 41 | 109 | 0.262 [0.176, 0.364] | 0.203 [0.142, 0.275] | 0.170 [0.122, 0.228] | 0.194 [0.138, 0.256] | 0.188 [0.134, 0.253] |  |
| (b) cation | Sc | 31 | 67 | 19 | 55 | 0.129 [0.077, 0.188] | 0.105 [0.067, 0.150] | 0.109 [0.065, 0.164] | 0.101 [0.067, 0.142] | 0.111 [0.070, 0.162] |  |
| (b) cation | Si | 60 | 173 | 55 | 168 | 0.162 [0.128, 0.204] | 0.116 [0.095, 0.140] | 0.119 [0.091, 0.152] | 0.102 [0.086, 0.121] | 0.131 [0.102, 0.166] |  |
| (b) cation | Sn | 36 | 79 | 26 | 69 | 0.257 [0.166, 0.371] | 0.224 [0.153, 0.310] | 0.169 [0.106, 0.244] | 0.213 [0.147, 0.290] | 0.195 [0.120, 0.293] |  |
| (b) cation | Sr | 67 | 150 | 42 | 125 | 0.124 [0.091, 0.160] | 0.109 [0.085, 0.134] | 0.118 [0.086, 0.151] | 0.093 [0.072, 0.113] | 0.133 [0.097, 0.170] |  |
| (b) cation | Ta | 43 | 93 | 32 | 82 | 0.130 [0.088, 0.174] | 0.123 [0.079, 0.167] | 0.133 [0.089, 0.175] | 0.120 [0.081, 0.159] | 0.149 [0.103, 0.193] |  |
| (b) cation | Ti | 28 | 60 | 18 | 50 | 0.115 [0.072, 0.166] | 0.096 [0.058, 0.143] | 0.082 [0.044, 0.124] | 0.096 [0.059, 0.139] | 0.102 [0.061, 0.152] |  |
| (b) cation | Tl | 26 | 56 | 17 | 47 | 0.205 [0.144, 0.285] | 0.178 [0.129, 0.243] | 0.177 [0.104, 0.295] | 0.179 [0.135, 0.242] | 0.178 [0.119, 0.266] |  |
| (b) cation | V | 34 | 72 | 20 | 58 | 0.176 [0.115, 0.248] | 0.133 [0.091, 0.183] | 0.137 [0.094, 0.187] | 0.133 [0.093, 0.187] | 0.151 [0.110, 0.203] |  |
| (b) cation | W | 34 | 74 | 21 | 61 | 0.190 [0.135, 0.248] | 0.184 [0.136, 0.238] | 0.189 [0.127, 0.254] | 0.170 [0.129, 0.216] | 0.205 [0.144, 0.268] |  |
| (b) cation | Y | 36 | 80 | 25 | 69 | 0.300 [0.158, 0.472] | 0.226 [0.132, 0.337] | 0.207 [0.117, 0.313] | 0.220 [0.129, 0.324] | 0.235 [0.131, 0.363] |  |
| (b) cation | Zn | 40 | 100 | 30 | 90 | 0.154 [0.114, 0.201] | 0.115 [0.084, 0.149] | 0.143 [0.103, 0.192] | 0.110 [0.083, 0.139] | 0.139 [0.099, 0.185] |  |
| (b) cation | Zr | 19 | 35 | 13 | 29 | 0.146 [0.061, 0.261] | 0.119 [0.048, 0.241] | 0.118 [0.045, 0.220] | 0.105 [0.040, 0.220] | 0.111 [0.045, 0.218] |  |
| (c) PHS-prone | phs_prone | 184 | 389 | 119 | 324 | 0.164 [0.139, 0.189] | 0.141 [0.119, 0.162] | 0.144 [0.121, 0.167] | 0.133 [0.114, 0.152] | 0.159 [0.135, 0.183] |  |
| (c) PHS-prone | not_phs_prone | 555 | 1172 | 344 | 961 | 0.190 [0.169, 0.215] | 0.147 [0.131, 0.166] | 0.147 [0.130, 0.165] | 0.140 [0.125, 0.156] | 0.152 [0.134, 0.171] |  |
| (d) stability | lower | 247 | 545 | 176 | 474 | 0.178 [0.148, 0.212] | 0.138 [0.117, 0.162] | 0.141 [0.119, 0.165] | 0.132 [0.112, 0.155] | 0.156 [0.131, 0.183] |  |
| (d) stability | middle | 246 | 548 | 162 | 464 | 0.198 [0.165, 0.235] | 0.153 [0.128, 0.182] | 0.151 [0.127, 0.177] | 0.141 [0.120, 0.165] | 0.162 [0.136, 0.192] |  |
| (d) stability | upper | 246 | 468 | 125 | 347 | 0.172 [0.148, 0.199] | 0.147 [0.126, 0.171] | 0.146 [0.122, 0.172] | 0.141 [0.120, 0.164] | 0.140 [0.117, 0.165] |  |
| (e) band gap | lower | 247 | 427 | 110 | 290 | 0.210 [0.180, 0.244] | 0.184 [0.157, 0.215] | 0.175 [0.147, 0.206] | 0.170 [0.143, 0.198] | 0.167 [0.140, 0.196] |  |
| (e) band gap | middle | 246 | 559 | 171 | 484 | 0.172 [0.146, 0.204] | 0.131 [0.112, 0.153] | 0.141 [0.120, 0.165] | 0.126 [0.107, 0.146] | 0.151 [0.128, 0.178] |  |
| (e) band gap | upper | 246 | 575 | 182 | 511 | 0.180 [0.147, 0.216] | 0.137 [0.114, 0.165] | 0.135 [0.113, 0.159] | 0.131 [0.110, 0.153] | 0.150 [0.125, 0.177] |  |
| (f) Bader rank | lowest | 463 | 463 | 463 | 463 | 0.196 [0.174, 0.219] | 0.156 [0.139, 0.174] | 0.154 [0.138, 0.171] | 0.146 [0.131, 0.163] | 0.162 [0.144, 0.180] |  |
| (f) Bader rank | middle | 260 | 359 | 260 | 359 | 0.174 [0.153, 0.201] | 0.137 [0.120, 0.157] | 0.139 [0.122, 0.158] | 0.131 [0.116, 0.147] | 0.149 [0.130, 0.172] |  |
| (f) Bader rank | highest | 463 | 463 | 463 | 463 | 0.178 [0.160, 0.198] | 0.142 [0.128, 0.158] | 0.144 [0.129, 0.160] | 0.135 [0.121, 0.149] | 0.150 [0.134, 0.168] |  |

### T2. Paired differences in within-host residual MAE (eV)

| variable | group | S − D, v2 | S − D, v1 | v2 − v1, S | v2 − v1, D |
|---|---|---|---|---|---|
| all | all | -0.000 [-0.010, +0.008] | -0.016 [-0.025, -0.007] | +0.008 [+0.003, +0.013] | -0.008 [-0.012, -0.003] |
| (a) d class | d0 | +0.003 [-0.006, +0.013] | -0.004 [-0.013, +0.005] | -0.000 [-0.005, +0.005] | -0.008 [-0.012, -0.003] |
| (a) d class | d10 | +0.000 [-0.014, +0.014] | -0.025 [-0.041, -0.011] | +0.013 [+0.006, +0.021] | -0.012 [-0.019, -0.006] |
| (a) d class | other | -0.099 [-0.221, +0.011] | +0.009 [-0.083, +0.114] | +0.011 [-0.009, +0.032] | +0.119 [+0.046, +0.217] |
| (a) d class | unassigned | +0.017 | +0.034 | +0.003 | +0.020 |
| (b) cation | Ag | +0.083 | +0.048 | -0.005 | -0.039 |
| (b) cation | Al | -0.037 [-0.078, +0.001] | -0.042 [-0.098, +0.008] | -0.022 [-0.041, -0.003] | -0.027 [-0.046, -0.010] |
| (b) cation | As | +0.011 [-0.022, +0.042] | +0.002 [-0.034, +0.035] | +0.013 [-0.004, +0.037] | +0.004 [-0.022, +0.025] |
| (b) cation | Au | +0.034 | +0.046 | -0.001 | +0.011 |
| (b) cation | B | -0.011 [-0.045, +0.020] | -0.046 [-0.092, -0.002] | +0.012 [-0.005, +0.031] | -0.024 [-0.040, -0.007] |
| (b) cation | Ba | -0.013 [-0.046, +0.022] | -0.040 [-0.073, -0.013] | +0.013 [-0.003, +0.032] | -0.015 [-0.032, +0.001] |
| (b) cation | Be | +0.041 [-0.008, +0.105] | +0.017 [-0.015, +0.054] | +0.013 [-0.013, +0.043] | -0.011 [-0.031, +0.005] |
| (b) cation | Bi | -0.013 [-0.060, +0.036] | -0.035 [-0.106, +0.036] | +0.023 [+0.005, +0.043] | +0.001 [-0.023, +0.025] |
| (b) cation | Ca | +0.017 [-0.001, +0.038] | -0.006 [-0.034, +0.021] | +0.019 [+0.004, +0.035] | -0.005 [-0.023, +0.012] |
| (b) cation | Cd | -0.056 [-0.129, -0.001] | -0.062 [-0.129, -0.006] | -0.002 [-0.020, +0.016] | -0.008 [-0.023, +0.008] |
| (b) cation | Cs | -0.004 [-0.039, +0.030] | -0.013 [-0.053, +0.027] | -0.004 [-0.017, +0.011] | -0.013 [-0.027, +0.002] |
| (b) cation | Cu | -0.150 | -0.092 | +0.007 | +0.066 |
| (b) cation | Ga | -0.015 [-0.054, +0.017] | -0.085 [-0.130, -0.045] | +0.031 [+0.015, +0.045] | -0.039 [-0.061, -0.017] |
| (b) cation | Ge | -0.016 [-0.051, +0.017] | -0.028 [-0.065, +0.006] | +0.008 [-0.003, +0.020] | -0.004 [-0.022, +0.019] |
| (b) cation | Hf | -0.009 [-0.056, +0.037] | -0.031 [-0.069, +0.017] | +0.007 [-0.015, +0.032] | -0.014 [-0.034, +0.008] |
| (b) cation | In | +0.013 [-0.040, +0.064] | +0.032 [-0.016, +0.094] | +0.014 [-0.004, +0.032] | +0.033 [-0.005, +0.090] |
| (b) cation | K | +0.016 [-0.002, +0.034] | +0.005 [-0.012, +0.022] | +0.007 [-0.001, +0.016] | -0.004 [-0.012, +0.004] |
| (b) cation | La | +0.026 [-0.005, +0.059] | -0.013 [-0.041, +0.016] | +0.016 [+0.000, +0.033] | -0.023 [-0.034, -0.012] |
| (b) cation | Li | +0.013 [-0.014, +0.043] | -0.005 [-0.030, +0.023] | +0.004 [-0.005, +0.014] | -0.014 [-0.024, -0.004] |
| (b) cation | Mg | -0.024 [-0.061, +0.009] | -0.030 [-0.058, -0.004] | +0.006 [-0.007, +0.017] | +0.000 [-0.012, +0.015] |
| (b) cation | Mo | -0.020 [-0.059, +0.018] | -0.013 [-0.048, +0.019] | -0.004 [-0.031, +0.018] | +0.004 [-0.010, +0.017] |
| (b) cation | Na | +0.027 [+0.009, +0.046] | +0.012 [-0.002, +0.025] | +0.010 [+0.002, +0.020] | -0.005 [-0.013, +0.003] |
| (b) cation | Nb | +0.003 [-0.060, +0.068] | -0.053 [-0.111, +0.005] | +0.036 [+0.011, +0.065] | -0.020 [-0.049, +0.007] |
| (b) cation | Pb | -0.032 [-0.077, +0.007] | -0.036 [-0.089, +0.011] | +0.002 [-0.005, +0.010] | -0.001 [-0.018, +0.015] |
| (b) cation | Pt | -0.202 | -0.015 | +0.013 | +0.200 |
| (b) cation | Rb | +0.013 [-0.008, +0.037] | +0.010 [-0.012, +0.036] | -0.005 [-0.014, +0.004] | -0.008 [-0.015, -0.001] |
| (b) cation | Sb | +0.033 [-0.006, +0.077] | +0.005 [-0.016, +0.028] | +0.009 [-0.014, +0.034] | -0.018 [-0.033, -0.006] |
| (b) cation | Sc | -0.004 [-0.023, +0.015] | -0.010 [-0.027, +0.004] | +0.004 [-0.009, +0.019] | -0.002 [-0.009, +0.005] |
| (b) cation | Si | -0.003 [-0.024, +0.017] | -0.029 [-0.055, -0.006] | +0.014 [+0.000, +0.033] | -0.012 [-0.024, -0.002] |
| (b) cation | Sn | +0.054 [+0.017, +0.097] | +0.017 [-0.022, +0.059] | +0.011 [-0.006, +0.029] | -0.026 [-0.061, +0.004] |
| (b) cation | Sr | -0.008 [-0.028, +0.013] | -0.040 [-0.065, -0.015] | +0.017 [+0.008, +0.026] | -0.015 [-0.026, -0.005] |
| (b) cation | Ta | -0.010 [-0.026, +0.008] | -0.029 [-0.049, -0.006] | +0.003 [-0.014, +0.017] | -0.016 [-0.035, -0.001] |
| (b) cation | Ti | +0.015 [-0.011, +0.041] | -0.006 [-0.032, +0.021] | +0.001 [-0.013, +0.014] | -0.020 [-0.043, +0.004] |
| (b) cation | Tl | +0.001 [-0.066, +0.057] | +0.001 [-0.045, +0.044] | -0.001 [-0.028, +0.023] | -0.001 [-0.031, +0.039] |
| (b) cation | V | -0.004 [-0.026, +0.018] | -0.019 [-0.051, +0.014] | +0.000 [-0.025, +0.027] | -0.014 [-0.028, -0.001] |
| (b) cation | W | -0.005 [-0.042, +0.033] | -0.035 [-0.065, -0.005] | +0.014 [-0.001, +0.030] | -0.016 [-0.030, -0.002] |
| (b) cation | Y | +0.019 [-0.022, +0.062] | -0.015 [-0.055, +0.025] | +0.007 [-0.021, +0.034] | -0.028 [-0.060, -0.004] |
| (b) cation | Zn | -0.029 [-0.064, +0.001] | -0.029 [-0.063, +0.000] | +0.005 [-0.013, +0.021] | +0.004 [-0.007, +0.018] |
| (b) cation | Zr | +0.001 [-0.047, +0.054] | -0.007 [-0.030, +0.019] | +0.015 [-0.007, +0.045] | +0.006 [-0.013, +0.033] |
| (c) PHS-prone | phs_prone | -0.003 [-0.016, +0.010] | -0.026 [-0.041, -0.013] | +0.008 [-0.001, +0.016] | -0.015 [-0.023, -0.008] |
| (c) PHS-prone | not_phs_prone | +0.000 [-0.010, +0.012] | -0.013 [-0.025, +0.000] | +0.008 [+0.002, +0.013] | -0.005 [-0.011, +0.000] |
| (d) stability | lower | -0.003 [-0.014, +0.008] | -0.024 [-0.036, -0.012] | +0.006 [-0.001, +0.012] | -0.015 [-0.022, -0.008] |
| (d) stability | middle | +0.001 [-0.017, +0.019] | -0.021 [-0.039, -0.004] | +0.011 [+0.003, +0.020] | -0.011 [-0.019, -0.003] |
| (d) stability | upper | +0.001 [-0.017, +0.021] | +0.001 [-0.018, +0.022] | +0.006 [-0.002, +0.016] | +0.006 [-0.004, +0.017] |
| (e) band gap | lower | +0.010 [-0.016, +0.034] | +0.003 [-0.018, +0.025] | +0.015 [+0.005, +0.026] | +0.008 [-0.004, +0.021] |
| (e) band gap | middle | -0.010 [-0.024, +0.004] | -0.025 [-0.042, -0.010] | +0.005 [-0.001, +0.012] | -0.010 [-0.018, -0.003] |
| (e) band gap | upper | +0.002 [-0.009, +0.015] | -0.018 [-0.032, -0.006] | +0.006 [-0.001, +0.014] | -0.015 [-0.021, -0.008] |
| (f) Bader rank | lowest | +0.003 [-0.009, +0.014] | -0.015 [-0.027, -0.005] | +0.010 [+0.004, +0.016] | -0.008 [-0.015, -0.001] |
| (f) Bader rank | middle | -0.002 [-0.013, +0.009] | -0.018 [-0.031, -0.006] | +0.006 [-0.000, +0.013] | -0.010 [-0.016, -0.005] |
| (f) Bader rank | highest | -0.003 [-0.014, +0.008] | -0.015 [-0.026, -0.004] | +0.007 [+0.002, +0.012] | -0.006 [-0.011, +0.000] |

### T3. Site-level MAE (eV) and paired S − D

| variable | group | S v2 | D v2 | S v1 | D v1 | S − D, v2 | S − D, v1 |
|---|---|---|---|---|---|---|---|
| all | all | 0.282 [0.263, 0.301] | 0.268 [0.250, 0.288] | 0.259 [0.243, 0.276] | 0.274 [0.255, 0.294] | +0.014 [-0.007, +0.033] | -0.014 [-0.033, +0.004] |
| (a) d class | d0 | 0.211 [0.189, 0.235] | 0.204 [0.183, 0.227] | 0.190 [0.172, 0.210] | 0.200 [0.181, 0.220] | +0.007 [-0.015, +0.030] | -0.009 [-0.027, +0.007] |
| (a) d class | d10 | 0.320 [0.293, 0.349] | 0.300 [0.272, 0.329] | 0.290 [0.267, 0.314] | 0.314 [0.285, 0.344] | +0.021 [-0.011, +0.052] | -0.023 [-0.054, +0.003] |
| (a) d class | other | 0.373 [0.278, 0.488] | 0.385 [0.298, 0.472] | 0.407 [0.319, 0.519] | 0.372 [0.292, 0.450] | -0.012 [-0.124, +0.118] | +0.036 [-0.073, +0.162] |
| (a) d class | unassigned | 0.582 | 0.578 | 0.598 | 0.483 | +0.004 | +0.115 |
| (b) cation | Ag | 0.336 [0.264, 0.413] | 0.308 [0.217, 0.400] | 0.390 [0.317, 0.466] | 0.328 [0.229, 0.429] | +0.028 [-0.063, +0.133] | +0.062 [-0.020, +0.154] |
| (b) cation | Al | 0.215 [0.171, 0.267] | 0.251 [0.187, 0.316] | 0.209 [0.168, 0.252] | 0.280 [0.209, 0.353] | -0.035 [-0.086, +0.016] | -0.072 [-0.127, -0.019] |
| (b) cation | As | 0.358 [0.283, 0.447] | 0.426 [0.314, 0.570] | 0.344 [0.282, 0.414] | 0.416 [0.302, 0.569] | -0.068 [-0.213, +0.037] | -0.072 [-0.219, +0.032] |
| (b) cation | Au | 0.376 [0.241, 0.514] | 0.347 [0.211, 0.509] | 0.334 [0.223, 0.437] | 0.401 [0.264, 0.569] | +0.029 [-0.132, +0.168] | -0.067 [-0.224, +0.046] |
| (b) cation | B | 0.264 [0.208, 0.323] | 0.291 [0.228, 0.363] | 0.261 [0.204, 0.322] | 0.304 [0.242, 0.375] | -0.027 [-0.082, +0.017] | -0.044 [-0.096, +0.012] |
| (b) cation | Ba | 0.220 [0.174, 0.272] | 0.258 [0.212, 0.309] | 0.218 [0.176, 0.268] | 0.269 [0.221, 0.324] | -0.038 [-0.083, +0.003] | -0.050 [-0.088, -0.015] |
| (b) cation | Be | 0.263 [0.152, 0.408] | 0.329 [0.150, 0.597] | 0.241 [0.154, 0.340] | 0.343 [0.149, 0.622] | -0.065 [-0.359, +0.138] | -0.102 [-0.356, +0.052] |
| (b) cation | Bi | 0.458 [0.364, 0.564] | 0.437 [0.351, 0.542] | 0.382 [0.314, 0.451] | 0.436 [0.356, 0.530] | +0.020 [-0.119, +0.149] | -0.054 [-0.169, +0.049] |
| (b) cation | Ca | 0.220 [0.177, 0.268] | 0.245 [0.186, 0.304] | 0.228 [0.185, 0.273] | 0.257 [0.203, 0.316] | -0.025 [-0.070, +0.018] | -0.030 [-0.075, +0.016] |
| (b) cation | Cd | 0.358 [0.254, 0.473] | 0.308 [0.227, 0.403] | 0.325 [0.237, 0.425] | 0.325 [0.243, 0.419] | +0.050 [-0.056, +0.163] | +0.000 [-0.092, +0.091] |
| (b) cation | Cs | 0.260 [0.204, 0.330] | 0.227 [0.184, 0.277] | 0.236 [0.191, 0.288] | 0.234 [0.192, 0.280] | +0.032 [-0.033, +0.105] | +0.002 [-0.052, +0.055] |
| (b) cation | Cu | 0.551 [0.372, 0.793] | 0.332 [0.256, 0.401] | 0.542 [0.356, 0.788] | 0.318 [0.262, 0.379] | +0.219 [+0.038, +0.460] | +0.225 [+0.038, +0.459] |
| (b) cation | Ga | 0.273 [0.222, 0.326] | 0.305 [0.233, 0.389] | 0.205 [0.160, 0.250] | 0.331 [0.259, 0.409] | -0.032 [-0.105, +0.027] | -0.126 [-0.192, -0.069] |
| (b) cation | Ge | 0.192 [0.158, 0.237] | 0.187 [0.149, 0.232] | 0.179 [0.152, 0.215] | 0.208 [0.162, 0.258] | +0.005 [-0.031, +0.041] | -0.028 [-0.069, +0.009] |
| (b) cation | Hf | 0.199 [0.131, 0.272] | 0.212 [0.145, 0.291] | 0.196 [0.121, 0.279] | 0.207 [0.141, 0.288] | -0.014 [-0.095, +0.066] | -0.011 [-0.101, +0.076] |
| (b) cation | In | 0.333 [0.252, 0.434] | 0.368 [0.271, 0.479] | 0.323 [0.246, 0.419] | 0.330 [0.226, 0.446] | -0.035 [-0.116, +0.044] | -0.007 [-0.090, +0.090] |
| (b) cation | K | 0.273 [0.209, 0.343] | 0.182 [0.148, 0.217] | 0.219 [0.173, 0.267] | 0.185 [0.151, 0.221] | +0.091 [+0.037, +0.148] | +0.033 [-0.009, +0.076] |
| (b) cation | La | 0.327 [0.254, 0.416] | 0.381 [0.280, 0.497] | 0.288 [0.216, 0.377] | 0.339 [0.257, 0.441] | -0.054 [-0.142, +0.026] | -0.051 [-0.104, +0.001] |
| (b) cation | Li | 0.211 [0.174, 0.251] | 0.183 [0.158, 0.210] | 0.210 [0.175, 0.248] | 0.191 [0.163, 0.222] | +0.028 [-0.002, +0.058] | +0.019 [-0.012, +0.050] |
| (b) cation | Mg | 0.216 [0.161, 0.288] | 0.191 [0.152, 0.240] | 0.210 [0.158, 0.275] | 0.210 [0.171, 0.257] | +0.024 [-0.026, +0.084] | -0.000 [-0.043, +0.057] |
| (b) cation | Mo | 0.214 [0.137, 0.306] | 0.217 [0.139, 0.316] | 0.172 [0.107, 0.245] | 0.205 [0.143, 0.285] | -0.003 [-0.115, +0.097] | -0.033 [-0.127, +0.058] |
| (b) cation | Na | 0.307 [0.256, 0.357] | 0.221 [0.179, 0.272] | 0.267 [0.225, 0.312] | 0.227 [0.188, 0.273] | +0.086 [+0.025, +0.137] | +0.040 [-0.013, +0.088] |
| (b) cation | Nb | 0.290 [0.238, 0.338] | 0.377 [0.282, 0.463] | 0.262 [0.218, 0.310] | 0.347 [0.265, 0.427] | -0.087 [-0.180, +0.014] | -0.085 [-0.169, +0.006] |
| (b) cation | Pb | 0.408 [0.321, 0.498] | 0.296 [0.234, 0.361] | 0.335 [0.256, 0.414] | 0.302 [0.236, 0.377] | +0.112 [+0.029, +0.207] | +0.033 [-0.049, +0.121] |
| (b) cation | Pt | 0.349 [0.256, 0.443] | 0.489 [0.338, 0.644] | 0.308 [0.225, 0.392] | 0.446 [0.309, 0.583] | -0.139 [-0.288, +0.001] | -0.138 [-0.273, -0.016] |
| (b) cation | Rb | 0.283 [0.224, 0.348] | 0.165 [0.134, 0.201] | 0.274 [0.216, 0.334] | 0.183 [0.153, 0.216] | +0.118 [+0.061, +0.182] | +0.091 [+0.036, +0.147] |
| (b) cation | Sb | 0.264 [0.204, 0.330] | 0.246 [0.202, 0.299] | 0.253 [0.202, 0.308] | 0.259 [0.209, 0.319] | +0.018 [-0.034, +0.072] | -0.006 [-0.042, +0.030] |
| (b) cation | Sc | 0.219 [0.155, 0.301] | 0.266 [0.199, 0.346] | 0.203 [0.158, 0.258] | 0.268 [0.204, 0.338] | -0.046 [-0.114, +0.018] | -0.065 [-0.107, -0.028] |
| (b) cation | Si | 0.164 [0.134, 0.204] | 0.175 [0.144, 0.212] | 0.150 [0.124, 0.180] | 0.172 [0.139, 0.213] | -0.012 [-0.037, +0.014] | -0.022 [-0.045, -0.001] |
| (b) cation | Sn | 0.353 [0.267, 0.438] | 0.276 [0.195, 0.363] | 0.313 [0.239, 0.391] | 0.278 [0.201, 0.364] | +0.077 [-0.001, +0.158] | +0.035 [-0.050, +0.122] |
| (b) cation | Sr | 0.258 [0.203, 0.318] | 0.241 [0.193, 0.295] | 0.206 [0.162, 0.255] | 0.238 [0.194, 0.287] | +0.017 [-0.026, +0.059] | -0.032 [-0.066, +0.007] |
| (b) cation | Ta | 0.267 [0.205, 0.333] | 0.278 [0.202, 0.365] | 0.249 [0.194, 0.309] | 0.286 [0.212, 0.374] | -0.011 [-0.083, +0.062] | -0.037 [-0.099, +0.028] |
| (b) cation | Ti | 0.218 [0.157, 0.287] | 0.256 [0.177, 0.350] | 0.226 [0.165, 0.308] | 0.256 [0.185, 0.344] | -0.038 [-0.115, +0.035] | -0.031 [-0.099, +0.031] |
| (b) cation | Tl | 0.308 [0.221, 0.415] | 0.492 [0.316, 0.738] | 0.317 [0.247, 0.405] | 0.489 [0.312, 0.749] | -0.183 [-0.454, +0.028] | -0.172 [-0.448, +0.040] |
| (b) cation | V | 0.216 [0.151, 0.299] | 0.231 [0.176, 0.294] | 0.212 [0.155, 0.287] | 0.237 [0.182, 0.299] | -0.015 [-0.064, +0.038] | -0.025 [-0.066, +0.020] |
| (b) cation | W | 0.258 [0.202, 0.317] | 0.263 [0.204, 0.329] | 0.265 [0.216, 0.319] | 0.296 [0.236, 0.362] | -0.006 [-0.062, +0.047] | -0.031 [-0.073, +0.012] |
| (b) cation | Y | 0.325 [0.224, 0.448] | 0.302 [0.224, 0.390] | 0.289 [0.209, 0.381] | 0.324 [0.231, 0.435] | +0.023 [-0.050, +0.121] | -0.035 [-0.097, +0.024] |
| (b) cation | Zn | 0.176 [0.143, 0.214] | 0.218 [0.175, 0.267] | 0.178 [0.147, 0.213] | 0.224 [0.182, 0.277] | -0.041 [-0.088, -0.001] | -0.045 [-0.095, +0.002] |
| (b) cation | Zr | 0.247 [0.159, 0.353] | 0.186 [0.126, 0.263] | 0.192 [0.118, 0.286] | 0.192 [0.137, 0.266] | +0.060 [-0.006, +0.132] | +0.000 [-0.043, +0.046] |
| (c) PHS-prone | phs_prone | 0.246 [0.219, 0.274] | 0.269 [0.235, 0.304] | 0.234 [0.209, 0.261] | 0.273 [0.242, 0.307] | -0.023 [-0.054, +0.008] | -0.039 [-0.067, -0.014] |
| (c) PHS-prone | not_phs_prone | 0.294 [0.272, 0.318] | 0.268 [0.246, 0.293] | 0.268 [0.249, 0.287] | 0.274 [0.252, 0.299] | +0.026 [+0.001, +0.049] | -0.006 [-0.029, +0.016] |
| (d) stability | lower | 0.230 [0.206, 0.255] | 0.257 [0.227, 0.288] | 0.220 [0.198, 0.244] | 0.260 [0.230, 0.292] | -0.027 [-0.052, -0.004] | -0.040 [-0.059, -0.022] |
| (d) stability | middle | 0.260 [0.228, 0.293] | 0.250 [0.221, 0.281] | 0.240 [0.214, 0.265] | 0.257 [0.230, 0.286] | +0.009 [-0.018, +0.037] | -0.018 [-0.043, +0.008] |
| (d) stability | upper | 0.370 [0.331, 0.411] | 0.303 [0.266, 0.347] | 0.328 [0.293, 0.363] | 0.308 [0.271, 0.353] | +0.067 [+0.014, +0.114] | +0.020 [-0.031, +0.067] |
| (e) band gap | lower | 0.425 [0.382, 0.467] | 0.370 [0.329, 0.411] | 0.373 [0.335, 0.412] | 0.359 [0.321, 0.400] | +0.056 [+0.007, +0.104] | +0.014 [-0.033, +0.061] |
| (e) band gap | middle | 0.238 [0.213, 0.266] | 0.249 [0.218, 0.285] | 0.225 [0.203, 0.249] | 0.259 [0.227, 0.298] | -0.011 [-0.046, +0.023] | -0.034 [-0.068, -0.005] |
| (e) band gap | upper | 0.219 [0.195, 0.245] | 0.212 [0.189, 0.237] | 0.208 [0.187, 0.230] | 0.224 [0.199, 0.249] | +0.007 [-0.014, +0.027] | -0.016 [-0.033, +0.002] |
| (f) Bader rank | lowest | 0.279 [0.254, 0.305] | 0.273 [0.247, 0.300] | 0.260 [0.237, 0.283] | 0.277 [0.251, 0.302] | +0.007 [-0.019, +0.032] | -0.017 [-0.040, +0.006] |
| (f) Bader rank | middle | 0.250 [0.223, 0.280] | 0.239 [0.209, 0.273] | 0.220 [0.199, 0.244] | 0.258 [0.224, 0.296] | +0.011 [-0.024, +0.042] | -0.038 [-0.072, -0.007] |
| (f) Bader rank | highest | 0.266 [0.242, 0.290] | 0.256 [0.233, 0.279] | 0.250 [0.228, 0.271] | 0.259 [0.238, 0.282] | +0.010 [-0.015, +0.036] | -0.009 [-0.032, +0.013] |

### T4. Mean signed within-host residual by Bader-charge rank (eV)

| rank | S v2 | D v2 | S v1 | D v1 |
|---|---|---|---|---|
| lowest | -0.004 [-0.026, +0.018] | +0.005 [-0.016, +0.026] | -0.008 [-0.029, +0.012] | +0.005 [-0.017, +0.028] |
| middle | +0.014 [-0.009, +0.037] | +0.016 [-0.007, +0.038] | +0.015 [-0.005, +0.035] | +0.012 [-0.014, +0.039] |
| highest | -0.007 [-0.027, +0.012] | -0.017 [-0.037, +0.003] | -0.004 [-0.024, +0.013] | -0.014 [-0.036, +0.007] |

### T5. Within-host Spearman correlation with the true energy (hosts with ≥ 3 tested sites: 260)

| quantity | mean over hosts [95%] | median | hosts used | hosts undefined |
|---|---|---:|---:|---:|
| ρ(prediction, truth), S v2 | 0.353 [0.273, 0.435] | 0.500 | 260 | 0 |
| ρ(prediction, truth), D v2 | 0.395 [0.323, 0.467] | 0.500 | 260 | 0 |
| ρ(prediction, truth), S v1 | 0.434 [0.351, 0.513] | 0.500 | 260 | 0 |
| ρ(prediction, truth), D v1 | 0.328 [0.247, 0.404] | 0.500 | 260 | 0 |
| ρ(Bader charge, truth), reference | 0.043 [-0.036, 0.120] | 0.400 | 260 | 0 |
| S − D, v1 | +0.107 [+0.006, +0.210] | | 260 | |
| S − D, v2 | -0.042 [-0.139, +0.054] | | 260 | |
| v2 − v1, D | +0.068 [+0.012, +0.120] | | 260 | |
| v2 − v1, S | -0.081 [-0.154, -0.005] | | 260 | |

## What the measurements show

Facts only; every value is in the tables above. "Below zero-skill" compares point values; the plan fixed no
interval for the difference between a model and the zero-skill value.

1. **Pooled.** Across the 463 tested hosts with at least two sites, the zero-skill value is 0.184 eV. The
   within-host residual MAE is 0.146 eV for both S and D on v2 (S − D = −0.000 [−0.010, +0.008]), and
   0.138 eV (S) and 0.154 eV (D) on v1 (S − D = −0.016 [−0.025, −0.007]). Pooled, all four model-backbone
   pairs are below zero-skill, but they remove only part of it: about a sixth (D on v1), a fifth (S and D on v2)
   and a quarter (S on v1).
2. **Where a backbone has no within-host skill** (point value at or above zero-skill):
   - d-class "other" (12 hosts with ≥ 2 sites): D on v2, 0.363 against 0.284; the intervals are wide.
   - Mg (32 hosts): D on both backbones, 0.146 against 0.144.
   - Pb (25 hosts): D on both backbones, 0.168 (v2) and 0.169 (v1) against 0.166.
   - Ta (32 hosts): D on both backbones, 0.133 (v2) and 0.149 (v1) against 0.130.
   - Cd (17 hosts): D on v1, 0.2082 against 0.2078 (D on v2 is 0.200).
   - Sr (42 hosts): D on v1, 0.133 against 0.124.
   - W (21 hosts): D on v1, 0.205 against 0.190 (D on v2 is 0.189).
   - Groups with fewer than 10 hosts with ≥ 2 sites (no intervals): Cu (4), D on both backbones;
     Au (4), S on both backbones; Pt (7), D on v2.
   S on v2 is below zero-skill in every group with at least 10 contributing hosts. Its smallest margins below
   zero-skill are in W (0.184 against 0.190) and Ta (0.123 against 0.130; S on v1 0.120), then La, As, Li and
   Sr (0.010 to 0.015 eV).
3. **Where D is worse than S within hosts** (paired interval of S − D entirely below zero):
   - v1: pooled; d10 (−0.025 [−0.041, −0.011]); cations B, Ba, Cd, Ga (−0.085 [−0.130, −0.045]), Mg, Si,
     Sr, Ta, W; PHS-prone hosts (−0.026 [−0.041, −0.013]); the most stable and middle stability thirds; the
     middle and largest-gap thirds; all three Bader-charge ranks.
   - v2: Cd only (−0.056 [−0.129, −0.001]).
   - D is better than S within hosts (interval above zero) only on v2, for Na (+0.027 [+0.009, +0.046]) and
     Sn (+0.054 [+0.017, +0.097]).
4. **Backbone change.** From v1 to v2, D's within-host MAE falls (pooled −0.008 [−0.012, −0.003]; also d0,
   d10, PHS-prone, several cations) and S's rises (pooled +0.008 [+0.003, +0.013]); the v1 S − D gap closes.
   Pooled site MAE of S rises by 0.023 [+0.012, +0.034] from v1 to v2.
5. **d-electron class.** d0 hosts have the smallest within-host spread (zero-skill 0.127) and the smallest
   residuals (0.104 to 0.111); d10 hosts have a larger spread (0.219) and larger residuals (0.155 to 0.181).
   In absolute terms the models remove 0.016 to 0.023 eV of the d0 spread and 0.038 to 0.064 eV of the d10
   spread.
6. **PHS-prone chemistry.** Hosts with Nb, W, Ti, V, Ta or Mo have a smaller within-host spread (zero-skill
   0.164 against 0.190) and a similar residual (0.133 to 0.159 against 0.140 to 0.152). Their site-level MAE
   is not higher than that of the other hosts (S on v2: 0.246 against 0.294).
7. **Stability and gap.** The within-host residual MAE varies little across the stability thirds (0.132 to
   0.162). Site-level MAE is largest in the least stable third (S on v2: 0.370 against 0.230 in the most stable
   third). Across band-gap thirds, the smallest-gap third has the largest within-host residual (0.167 to 0.184)
   with the largest zero-skill value (0.210), and the largest site-level MAE (S on v2: 0.425; D on v2: 0.370).
8. **Bader-charge rank.** The within-host residual is similar for the most negative, intermediate and least
   negative vacancy oxygen of a host; the mean signed residual is within ±0.017 eV with every interval
   containing zero, so no backbone systematically over- or under-predicts the vacancy energy of the most
   ionic or the least ionic oxygen of a host. The sites at the most negative charge have the largest
   deviation from their host mean (zero-skill 0.196 against 0.178 at the least negative).
9. **Within-host ranking.** Over 260 hosts with ≥ 3 tested sites, the mean Spearman correlation between
   predicted and true energies is 0.33 to 0.43 (positive for every model and backbone; medians 0.5). On v1, S
   ranks sites better than D (+0.107 [+0.006, +0.210]); on v2 the two do not differ (−0.042
   [−0.139, +0.054]). The vacancy-O Bader charge alone has a mean within-host correlation with the true energy
   of 0.043 [−0.036, +0.120].

## Hypotheses

Physical interpretations. **Each item is a hypothesis**, not a result of this analysis; none was tested
here, and the measurement that motivates it is named. Testing any of them would need a grouping or variable
logged first as exploratory (`docs/deviations.md`).

- **H1, coordination sets the site-to-site spread in d0 hosts (motivated by fact 5).** *Hypothesis:* in
  closed-shell d0 hosts the two electrons of the neutral vacancy stay in a localised cavity state, and the
  difference between O sites is mostly how many cation–O bonds are broken and how strongly the lattice
  relaxes, which a radius graph of the pristine structure encodes; this would make the spread small and
  learnable. Coordination numbers were not a grouping variable here (the Voronoi weights in the universe
  table would allow it).
- **H2, bond covalency in d10 and lone-pair hosts (facts 2, 3, 5).** *Hypothesis:* in d10 hosts (Zn, Ga, Cd,
  In, Sn) and in hosts with lone-pair cations (Pb, Bi, Sb), the cation–O bonds are more covalent, and the
  energy cost of removing a given O depends on the strength of its specific bonds to soft, polarisable cations
  and on how the vacancy electrons hybridise with the cation s states. Site differences are then larger
  (larger zero-skill value) and depend on electronic detail that neither the graph nor the pristine-host
  site descriptors fully capture: Pb and Cd are where D shows no within-host skill.
- **H3, shallow versus deep vacancy states (facts 6, 7).** *Hypothesis:* the perturbed-host-state filter has
  already removed the shallow-donor vacancies of the early-transition-metal d0 oxides, so the PHS-prone
  hosts that remain in the universe carry deep, localised vacancy states and behave like the other hosts
  within a host. In the smallest-gap third, the vacancy level lies closer to the conduction band, so even
  retained entries may carry partly delocalised electrons, whose energy depends on long-range screening and
  band-edge position rather than on the local environment; this would explain the largest within-host
  residuals and site errors there.
- **H4, host-level offsets versus site resolution (fact 7).** *Hypothesis:* the large site-level error of the
  least stable third is a host-level error (the absolute vacancy energy follows the host's O-binding
  strength, which a less stable host makes harder to predict), not a failure to resolve sites, because the
  within-host residual does not change across stability thirds.
- **H5, site descriptors add variance not aligned with the target (facts 3, 4, 9).** *Hypothesis:* on v1, D's
  within-host predictions follow its site descriptors (the S10b forensic found D's within-host spread vanishes
  when the site descriptors are held at the host mean), and in Ga, Sr, Si, Ta, W, B, Ba, Mg and Cd hosts those
  descriptors vary across sites in ways that do not track the vacancy energy, so D is worse than a model
  without them. The v2 backbone, which builds more site resolution from structure, would then lean less on
  the descriptors; that the S − D gap closes from v1 to v2 is consistent with this but does not establish it.
- **H6, the O charge is not the ordering variable (facts 8, 9).** *Hypothesis:* within a host, the vacancy
  energy is ordered by the local bonding and relaxation (H1, H2) rather than by the ionicity of the O site:
  the Bader charge alone barely ranks the sites, and no backbone shows a bias at either end of the charge
  range.

## Limits

- One budget (B = 654); 10 resamples; per-site averages over 1 to 6 resamples, so sites tested once carry a
  single training set's error.
- About 1000 intervals without multiplicity control; an isolated interval that excludes zero is weak
  evidence.
- The cation groups overlap (multi-cation hosts) and are confounded with each other and with structure type.
- Group summaries are of the filtered universe (deep or localised neutral vacancies only;
  `docs/limitations_notes.md`).

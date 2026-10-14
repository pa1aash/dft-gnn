# A4: latent probe (C4) on the originally registered backbone

Session A4, 2026-10-14. Rules: `docs/deviations.md`, row of 2026-10-14 (§10, step A4), logged and committed (34fbceb)
before any v1 probe number was computed. Scripts: `analysis/probe_fit.py`, `analysis/probe_stats.py` (tests
`analysis/tests/test_probe.py`, 14 synthetic checks). Records (all via `write_result` from a clean tree):
`results/probe_fit_v1.json` (per cell and descriptor; integrity and sanity checks), `results/probe_c4_v1.json` (rule,
class-mean curves), `results/probe_descriptive.json` (per-descriptor, within-host, 22-descriptor mean, alpha edges,
S-v2). Figure: `figures/si/fig6_probe.pdf` (in the SI because the rule fails).

LABELS. The probe on the originally registered backbone (v1; the 60 seed-0 S checkpoints of the sweep) is the
registered C4 analysis. The collaborator's probe on S-v2 (`results/probe_v2_sweep.json`) is POST HOC and
descriptive; v2 is never pre-registered. init1 and init2 are descriptive spread of the random-init control.

Intervals: 95% percentile intervals from 2000 bootstrap draws of the 10 resamples (generator
`default_rng(20261008)`, one index matrix shared by every interval, so all comparisons are paired by resample).

## Integrity and sanity checks (Task 3)

- 240 embedding records (60 cells x trained, init0, init1, init2) and 240 npz + 240 sidecars; every record, sidecar,
  artifact and npz sha256 agree; shapes, per-split counts and block bounds agree; every trained record points at the
  seed-0 v1 S sweep run of its cell. No mismatch.
- Per cell: rows = train + val + test sites of the cell's hosts; train, val and test hosts equal
  `dftgnn.embeddings.site_split` (registered budget order and validation carve-out); test hosts equal
  `splits/outer_r<r>.json`; test sites equal the S sites of `results/analysis/eval_table.parquet`; site and host counts
  equal the S run record; no test host in training; site and host ids equal the universe. All 60 cells pass.
- Readout alignment (r = 0; B = 25, 200, 654). Head replay (checkpoint head applied to the stored embedding, mapped
  back with the checkpoint target statistics, against the stored seed-0 test predictions): max |difference|
  3.1e-5, 1.1e-4, 3.6e-5 eV (mean 1.8e-6, 2.1e-6, 1.2e-6 eV), float32 level: the stored vector is the head's input.
  Linear probe from the trained embedding to the model's own test prediction (grouped 5-fold CV on the 352 test
  sites, out-of-fold R²): 0.9996, 0.9956, **0.9699**. The B = 654 cell is below the 0.99 threshold of the task. The
  head is a nonlinear MLP (softplus), so a linear map need not reproduce it exactly; the exact replay above confirms
  alignment. Reported, not adjusted.
- Alpha grid edges (19-value grid 1e-3 to 1e6): upper edge chosen in 115 of 1320 trained fits, 746 of 1320
  shuffled fits (no signal, maximal shrinkage as expected), 129 / 100 / 86 for init0 / init1 / init2; lower edge in
  88 trained fits. No descriptor had an undefined test R².

## Tables

### Host-electronic class-mean test R² (v1; resample mean [95% interval])

| B | trained | shuffled | init0 | init1 | init2 |
|---|---|---|---|---|---|
| 25 | -0.174 [-0.253, -0.106] | -0.357 [-0.632, -0.176] | -0.219 [-0.347, -0.102] | -0.171 [-0.222, -0.122] | -0.127 [-0.217, -0.047] |
| 50 | -0.014 [-0.052, 0.020] | -0.089 [-0.126, -0.055] | 0.016 [-0.041, 0.054] | -0.014 [-0.069, 0.030] | 0.109 [0.080, 0.142] |
| 100 | 0.139 [0.107, 0.167] | -0.055 [-0.088, -0.032] | 0.259 [0.208, 0.306] | 0.232 [0.165, 0.290] | 0.320 [0.283, 0.349] |
| 200 | 0.229 [0.129, 0.288] | -0.045 [-0.069, -0.027] | 0.471 [0.439, 0.499] | 0.450 [0.416, 0.481] | 0.475 [0.455, 0.495] |
| 400 | 0.425 [0.361, 0.484] | -0.032 [-0.040, -0.025] | 0.398 [0.348, 0.437] | 0.375 [0.347, 0.400] | 0.409 [0.342, 0.458] |
| 654 | 0.446 [0.401, 0.487] | -0.027 [-0.036, -0.017] | 0.440 [0.397, 0.479] | 0.389 [0.356, 0.420] | 0.471 [0.431, 0.508] |

### Site-electronic class-mean test R² (v1)

| B | trained | shuffled | init0 | init1 | init2 |
|---|---|---|---|---|---|
| 25 | -0.199 [-0.348, -0.092] | -0.184 [-0.257, -0.120] | -0.247 [-0.378, -0.138] | -0.039 [-0.063, -0.017] | -0.198 [-0.276, -0.124] |
| 50 | -0.026 [-0.056, -0.001] | -0.082 [-0.114, -0.053] | -0.020 [-0.069, 0.017] | 0.018 [-0.018, 0.048] | 0.031 [-0.004, 0.062] |
| 100 | 0.064 [0.040, 0.080] | -0.046 [-0.057, -0.034] | 0.174 [0.144, 0.202] | 0.185 [0.168, 0.202] | 0.211 [0.195, 0.226] |
| 200 | 0.188 [0.162, 0.211] | -0.032 [-0.042, -0.021] | 0.361 [0.338, 0.380] | 0.354 [0.323, 0.383] | 0.347 [0.321, 0.369] |
| 400 | 0.358 [0.292, 0.404] | -0.019 [-0.027, -0.013] | 0.329 [0.310, 0.347] | 0.362 [0.346, 0.377] | 0.322 [0.303, 0.339] |
| 654 | 0.382 [0.343, 0.417] | -0.017 [-0.023, -0.011] | 0.357 [0.333, 0.376] | 0.394 [0.377, 0.411] | 0.359 [0.340, 0.378] |

### The §10 rule (trained minus control at B ≥ 200; ✓ = lower bound > 0)

| class | Spearman ρ [95%] | trend | T−shuffled at 200 | T−shuffled at 400 | T−shuffled at 654 | T−init0 at 200 | T−init0 at 400 | T−init0 at 654 | C4 for class |
|---|---|---|---|---|---|---|---|---|---|
| host | 0.916 [0.854, 0.953] | holds | +0.274 [+0.168, +0.339] ✓ | +0.457 [+0.396, +0.516] ✓ | +0.472 [+0.423, +0.516] ✓ | -0.242 [-0.339, -0.178] ✗ | +0.027 [-0.027, +0.071] ✗ | +0.005 [-0.035, +0.049] ✗ | fails |
| site | 0.945 [0.927, 0.963] | holds | +0.220 [+0.196, +0.242] ✓ | +0.377 [+0.310, +0.427] ✓ | +0.399 [+0.360, +0.434] ✓ | -0.173 [-0.193, -0.153] ✗ | +0.028 [-0.030, +0.070] ✗ | +0.025 [-0.017, +0.070] ✗ | fails |

### Within-host R², site-electronic class mean (v1; descriptive)

Per cell over test hosts with ≥ 2 test sites (96-109 hosts, 269-301 sites per resample; the same for every budget
because the test hosts of a resample do not change with B).

| B | trained | shuffled | init0 | init1 | init2 | trained − init0 | trained − shuffled |
|---|---|---|---|---|---|---|---|
| 25 | -0.006 [-0.012, -0.001] | -0.001 [-0.006, 0.002] | -0.035 [-0.077, -0.007] | -0.022 [-0.043, -0.009] | -0.020 [-0.030, -0.010] | +0.029 [-0.001, +0.073] | -0.005 [-0.012, +0.002] |
| 50 | -0.036 [-0.077, -0.007] | -0.005 [-0.009, -0.001] | -0.034 [-0.066, -0.011] | -0.022 [-0.046, -0.002] | -0.044 [-0.079, -0.016] | -0.002 [-0.050, +0.046] | -0.031 [-0.072, -0.001] |
| 100 | -0.025 [-0.040, -0.013] | -0.000 [-0.001, 0.001] | -0.083 [-0.139, -0.038] | -0.013 [-0.036, 0.005] | -0.084 [-0.146, -0.041] | +0.058 [+0.013, +0.116] | -0.025 [-0.039, -0.013] |
| 200 | -0.041 [-0.063, -0.022] | 0.000 [-0.000, 0.001] | -0.057 [-0.107, -0.011] | -0.048 [-0.086, -0.013] | -0.037 [-0.085, 0.000] | +0.015 [-0.021, +0.059] | -0.042 [-0.063, -0.023] |
| 400 | 0.001 [-0.036, 0.038] | -0.000 [-0.004, 0.003] | -0.079 [-0.110, -0.049] | -0.078 [-0.134, -0.035] | -0.032 [-0.078, -0.001] | +0.080 [+0.036, +0.119] | +0.001 [-0.036, +0.038] |
| 654 | -0.021 [-0.074, 0.034] | -0.003 [-0.008, 0.001] | -0.068 [-0.106, -0.037] | -0.070 [-0.131, -0.023] | -0.020 [-0.056, 0.010] | +0.046 [+0.007, +0.087] | -0.019 [-0.071, +0.037] |

### Per-descriptor test R² at B = 654 (v1; descriptive)

| descriptor | class | trained | shuffled | init0 | within trained |
|---|---|---|---|---|---|
| ave_ele_diele | host | 0.599 [0.521, 0.656] | -0.025 [-0.054, 0.005] | 0.579 [0.510, 0.645] | — |
| ave_ion_diele | host | 0.291 [0.246, 0.334] | -0.023 [-0.050, -0.005] | 0.248 [0.176, 0.307] | — |
| band_gap | host | 0.632 [0.596, 0.666] | -0.028 [-0.055, -0.004] | 0.584 [0.555, 0.611] | — |
| cbm_d | host | 0.498 [0.403, 0.575] | -0.027 [-0.045, -0.012] | 0.592 [0.565, 0.622] | — |
| cbm_f | host | -0.117 [-0.340, 0.090] | -0.034 [-0.056, -0.013] | -0.347 [-0.853, 0.112] | — |
| cbm_p | host | 0.466 [0.419, 0.516] | -0.012 [-0.021, -0.004] | 0.447 [0.400, 0.497] | — |
| cbm_s | host | 0.307 [0.218, 0.382] | -0.040 [-0.059, -0.023] | 0.321 [0.255, 0.368] | — |
| formation_energy | host | 0.908 [0.868, 0.936] | -0.032 [-0.061, -0.004] | 0.889 [0.864, 0.910] | — |
| vbm_d | host | 0.497 [0.386, 0.601] | -0.053 [-0.076, -0.030] | 0.569 [0.496, 0.637] | — |
| vbm_f | host | 0.288 [0.178, 0.401] | -0.017 [-0.036, -0.002] | 0.428 [0.291, 0.532] | — |
| vbm_p | host | 0.524 [0.446, 0.592] | -0.021 [-0.041, -0.001] | 0.567 [0.510, 0.622] | — |
| vbm_s | host | 0.455 [0.390, 0.513] | -0.007 [-0.015, 0.004] | 0.404 [0.340, 0.473] | — |
| ave_bec | site | 0.596 [0.540, 0.638] | -0.009 [-0.020, 0.001] | 0.495 [0.440, 0.550] | -0.082 [-0.232, 0.055] |
| bader_charge | site | 0.289 [0.231, 0.349] | -0.032 [-0.060, -0.007] | 0.304 [0.258, 0.354] | -0.058 [-0.135, -0.004] |
| bader_volume | site | 0.353 [0.268, 0.423] | -0.005 [-0.011, -0.000] | 0.469 [0.435, 0.499] | 0.074 [0.023, 0.133] |
| nn_ave_ave_bec | site | 0.453 [0.395, 0.514] | -0.014 [-0.028, 0.001] | 0.363 [0.329, 0.396] | 0.053 [-0.018, 0.121] |
| nn_ave_bader_charge | site | 0.390 [0.337, 0.445] | -0.027 [-0.056, -0.003] | 0.317 [0.272, 0.364] | 0.167 [0.112, 0.225] |
| nn_max_ave_bec | site | 0.618 [0.546, 0.680] | -0.015 [-0.024, -0.006] | 0.541 [0.467, 0.590] | -0.505 [-0.969, -0.155] |
| nn_max_bader_charge | site | 0.413 [0.365, 0.462] | -0.035 [-0.063, -0.014] | 0.400 [0.341, 0.455] | -0.301 [-0.519, -0.123] |
| nn_min_ave_bec | site | 0.085 [0.060, 0.113] | -0.014 [-0.028, -0.004] | 0.069 [0.040, 0.097] | 0.017 [0.005, 0.031] |
| nn_min_bader_charge | site | 0.092 [0.069, 0.117] | -0.013 [-0.022, -0.006] | 0.068 [0.038, 0.095] | 0.024 [0.014, 0.034] |
| o2p_center_from_vbm | site | 0.527 [0.459, 0.595] | -0.006 [-0.028, 0.022] | 0.543 [0.505, 0.578] | 0.396 [0.341, 0.448] |

### 22-descriptor mean (descriptive, not the rule)

Spearman ρ 0.941 [0.904, 0.963]; the controls condition fails here too.

| B | trained | shuffled | init0 | init1 | init2 |
|---|---|---|---|---|---|
| 25 | -0.185 [-0.280, -0.108] | -0.279 [-0.440, -0.165] | -0.232 [-0.323, -0.148] | -0.111 [-0.143, -0.079] | -0.159 [-0.241, -0.087] |
| 50 | -0.020 [-0.045, 0.005] | -0.086 [-0.119, -0.058] | -0.001 [-0.036, 0.032] | 0.001 [-0.033, 0.029] | 0.073 [0.046, 0.101] |
| 100 | 0.105 [0.085, 0.123] | -0.051 [-0.072, -0.034] | 0.221 [0.187, 0.253] | 0.211 [0.169, 0.245] | 0.270 [0.248, 0.288] |
| 200 | 0.210 [0.148, 0.250] | -0.039 [-0.054, -0.027] | 0.421 [0.395, 0.441] | 0.407 [0.386, 0.424] | 0.417 [0.403, 0.429] |
| 400 | 0.394 [0.337, 0.444] | -0.026 [-0.033, -0.021] | 0.367 [0.339, 0.392] | 0.369 [0.353, 0.383] | 0.369 [0.334, 0.397] |
| 654 | 0.417 [0.380, 0.450] | -0.022 [-0.028, -0.016] | 0.402 [0.375, 0.427] | 0.391 [0.369, 0.413] | 0.420 [0.397, 0.443] |

### Collaborator's probe on S-v2 (POST HOC, descriptive; recomputed from his stored per-descriptor R²)

Class means recomputed with the A4 definition equal his stored class means (max |difference| 0.0). His single
random-init control is mapped to init0. Within-host values cannot be computed (his predictions are not stored).
Host-electronic: ρ 0.964 [0.949, 0.980]; site-electronic: ρ 0.978 [0.970, 0.987]; 22-descriptor: ρ 0.975
[0.963, 0.985] (his stored value 0.975 [0.963, 0.986]).

Host-electronic:

| B | trained | shuffled | init0 (his random) |
|---|---|---|---|
| 25 | -0.184 [-0.325, -0.080] | -0.280 [-0.442, -0.161] | -0.202 [-0.311, -0.106] |
| 50 | -0.001 [-0.089, 0.066] | -0.095 [-0.125, -0.065] | -0.008 [-0.094, 0.057] |
| 100 | 0.194 [0.137, 0.234] | -2.871 [-8.424, -0.067] | 0.218 [0.163, 0.273] |
| 200 | 0.348 [0.319, 0.381] | -0.042 [-0.062, -0.024] | 0.377 [0.314, 0.436] |
| 400 | 0.510 [0.476, 0.547] | -0.040 [-0.058, -0.020] | 0.556 [0.522, 0.585] |
| 654 | 0.607 [0.572, 0.639] | -0.059 [-0.074, -0.043] | 0.637 [0.618, 0.655] |

Controls: 200|init0 -0.030 [-0.074, +0.016] ✗; 200|shuffled +0.389 [+0.358, +0.428] ✓; 400|init0 -0.046 [-0.080, -0.014] ✗; 400|shuffled +0.550 [+0.510, +0.589] ✓; 654|init0 -0.030 [-0.050, -0.009] ✗; 654|shuffled +0.666 [+0.627, +0.702] ✓

Site-electronic:

| B | trained | shuffled | init0 (his random) |
|---|---|---|---|
| 25 | -0.139 [-0.213, -0.079] | -0.193 [-0.289, -0.109] | -0.156 [-0.213, -0.105] |
| 50 | 0.015 [-0.011, 0.040] | -0.092 [-0.128, -0.057] | 0.015 [-0.014, 0.043] |
| 100 | 0.124 [0.083, 0.158] | -0.058 [-0.083, -0.033] | 0.165 [0.144, 0.186] |
| 200 | 0.265 [0.250, 0.281] | -0.033 [-0.043, -0.022] | 0.299 [0.264, 0.329] |
| 400 | 0.402 [0.384, 0.421] | -0.026 [-0.036, -0.016] | 0.416 [0.398, 0.432] |
| 654 | 0.491 [0.474, 0.508] | -0.029 [-0.039, -0.019] | 0.462 [0.444, 0.478] |

Controls: 200|init0 -0.034 [-0.059, -0.008] ✗; 200|shuffled +0.298 [+0.279, +0.320] ✓; 400|init0 -0.013 [-0.026, +0.000] ✗; 400|shuffled +0.428 [+0.409, +0.448] ✓; 654|init0 +0.030 [+0.019, +0.039] ✓; 654|shuffled +0.520 [+0.501, +0.540] ✓

22-descriptor mean:

| B | trained | shuffled | init0 (his random) |
|---|---|---|---|
| 25 | -0.164 [-0.246, -0.095] | -0.240 [-0.329, -0.165] | -0.181 [-0.248, -0.118] |
| 50 | 0.006 [-0.047, 0.049] | -0.093 [-0.120, -0.065] | 0.002 [-0.051, 0.046] |
| 100 | 0.162 [0.120, 0.198] | -1.592 [-4.622, -0.059] | 0.194 [0.161, 0.226] |
| 200 | 0.310 [0.290, 0.333] | -0.038 [-0.052, -0.024] | 0.342 [0.298, 0.381] |
| 400 | 0.461 [0.441, 0.479] | -0.033 [-0.047, -0.019] | 0.492 [0.474, 0.510] |
| 654 | 0.555 [0.533, 0.575] | -0.045 [-0.056, -0.034] | 0.557 [0.542, 0.572] |

Controls: 200|init0 -0.032 [-0.061, +0.001] ✗; 200|shuffled +0.348 [+0.324, +0.376] ✓; 400|init0 -0.031 [-0.049, -0.013] ✗; 400|shuffled +0.494 [+0.470, +0.517] ✓; 654|init0 -0.003 [-0.015, +0.009] ✗; 654|shuffled +0.599 [+0.575, +0.621] ✓

The shuffled S-v2 value at B = 100 (host class) is dominated by one resample with a very negative R²; it is his
stored value and is not corrected here.

## What the measurements show (against the fixed rule)

1. Trend condition: holds for both classes. Spearman ρ between log budget and the trained class-mean R² is 0.916
   [0.854, 0.953] (host-electronic) and 0.945 [0.927, 0.963] (site-electronic); both intervals exclude 0.
2. Controls condition: fails for both classes. The trained probe exceeds the shuffled-label control at B = 200, 400
   and 654 in both classes (by +0.27 to +0.47 host, +0.22 to +0.40 site; every lower bound > 0). It does not exceed
   the registered random-init control (init0) at any of the three budgets: at B = 200 the trained probe is below
   init0 (host −0.242 [−0.339, −0.178]; site −0.173 [−0.193, −0.153]); at B = 400 and 654 the differences are
   +0.027 [−0.027, +0.071] and +0.005 [−0.035, +0.049] (host), +0.028 [−0.030, +0.070] and +0.025 [−0.017, +0.070]
   (site), intervals including 0.
3. Outcome: C4 does not hold; under the §10 rule C4 moves to the SI. Fig 6 is built as `figures/si/fig6_probe.pdf`.
4. init1 and init2 (descriptive) lie close to init0 at B ≥ 200 in both classes (table above), so init0 is not an
   unusually favourable draw.
5. Within-host (site-electronic, descriptive): the trained class-mean within-host R² is between −0.041 and +0.001 at
   every budget; it is above init0 at B = 100, 400 and 654 (intervals excluding 0) and not above shuffled at any
   budget. Per descriptor at B = 654 the trained within-host R² is positive with interval excluding 0 for
   o2p_center_from_vbm (0.396), nn_ave_bader_charge (0.167), bader_volume (0.074), nn_min_ave_bec and
   nn_min_bader_charge, and negative for nn_max_ave_bec (−0.505), nn_max_bader_charge (−0.301) and bader_charge.
6. S-v2 (POST HOC): the same pattern. Trend holds in both classes; shuffled is exceeded at every B ≥ 200; init0 is
   not exceeded except site-electronic at B = 654 (+0.030 [+0.019, +0.039]); C4 would not hold under the A4 rule on
   v2 either.

## Hypotheses (not tested here; labelled as interpretation)

- H1. The readout input of an untrained MEGNet already encodes composition and local geometry (element embeddings,
  distance expansions, set2set pooling), and the host-electronic descriptors (formation energy, band gap,
  dielectric constants, band-edge orbital character) are largely functions of composition and structure. A linear
  probe on a random but injective featurisation can then reach the same R² as on a trained encoder. The control
  therefore measures what the architecture's input featurisation already exposes, and training on E_f does not add
  linearly decodable descriptor information beyond it at B ≥ 400.
- H2. The deficit of the trained probe at B = 200 (and B = 100) relative to init0 may reflect the budget-specific
  hyperparameters of the v1 checkpoints (each init<k> encoder uses its cell's hyperparameters) together with the
  site-blind collapse of the registered backbone at small budgets (`docs/s_site_resolution.md`,
  `docs/diagnostics_sweep.md`): training compresses the representation towards the E_f direction, discarding
  descriptor variance that the untrained encoder still carries.
- H3. The rising trend of the trained probe with budget may be partly a property of the probe's training-set size
  (more training hosts per cell), not only of the encoder: the init0 curve rises with budget too.
- H4. The near-zero within-host class mean, with positive within-host R² only for o2p_center_from_vbm and the
  nearest-neighbour Bader averages, suggests the readout input resolves a few site-level electronic quantities
  within a host but not the extreme-neighbour ones.

Any analysis of these hypotheses would be new, logged first in `docs/deviations.md` and labelled exploratory.

## Not done / limits

- `docs/provenance_labels.md` and the pending-figure table of `docs/figure_style.md` still describe Fig 6 and C4 as
  pending; both are outside this session's edit scope.
- The S-v2 probe is reproduced only from stored R² values; his embeddings and checkpoints are on NRP.

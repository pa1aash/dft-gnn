# Sweep diagnostics before the C1/C2 figures

Response to the review of 2026-10-07. Numbers come from `scripts/diagnostics_sweep.py`
(`results/diagnostics_sweep.json`), which reads only the committed sweep, capsens, C0 and baseline
results. Every model value uses the seed-ensemble-mean prediction of a (model, resample, budget), the
estimand of ANALYSIS_PLAN §7. Intervals are the hierarchical bootstrap of `dftgnn.stats.metrics`
(resamples, then test hosts; 2000 draws, two-sided 95%). The review quoted single-seed means, so some
values below differ from it: for example, A at 654 is +0.005 eV over single seeds and −0.012 eV on the
ensemble.

The C1/C2 intervals and N* are deliberately not computed here; item 5 asks for their reporting rules to
be fixed first.

## Summary

| Item | Finding | Status |
|---|---|---|
| 1 | Real, not a reporting artefact, and not an indexing bug. At B ≤ 200, S gives (nearly) every site of a host the same prediction. Root cause: the pre-registered backbone cannot see O-site geometry at initialisation; S learns it only at B ≥ 400. | Pipeline verified; mechanism identified; crossing runs show the small-budget tuned values keep S site-blind even at 654 hosts. v2 backbone arm logged and screening (deviations, 2026-10-08) |
| 2 | At 25 and 50 hosts both GNNs beat the training-mean predictor but are 0.23–0.39 eV worse than B0 and RF-Kumagai. S reaches B0 at 100 and passes RF-Kumagai only at 654. | Reported; figure requirement below |
| 3 | Descriptors are clean and standardised on training sites only. D does not beat S at 654 (A = −0.012 eV, D ahead in 2 of 10 resamples) and ties on the Kiyohara split. D cannot be called an upper bound. Ablation: host descriptors add nothing; without site descriptors D is site-blind; descriptors displace geometry. | Done (permutation importances in `results/diag_checkpoints.json`) |
| 6 | The epoch cap does not bind. All 18 capsens runs reproduce their 200-epoch twins bit for bit; ΔA = 0. | Done; one caveat |
| 8 | 97 of 126 Kiyohara test hosts were in a tuning set. On the other 29, S scores 0.285 eV, no better than on the 97. | Done |
| 4, 5, 7 | 7 logged and run: D-late gives the same A pattern as D-state. 4 and 5 proposed below for sign-off. | 7 done |
| 9 | The two planning documents are outside the repository; each now carries a superseded banner. | Done |

## 1. Within-host skill at B ≤ 200

### What the predictions show

| Model | B | Pooling | Constant hosts (of ~102 multi-site) | Within-host prediction spread (eV) | Corr. with true within-host deviation | Within-host MAE | Within-host skill |
|---|---:|---|---:|---:|---:|---|---|
| S | 25 | set2set | 95.7 | 0.0001 | −0.02 | 0.187 | 0.000 [−0.000, 0.000] |
| S | 50 | set2set | 77.1 | 0.0007 | 0.04 | 0.187 | 0.000 [−0.000, 0.000] |
| S | 100 | set2set | 102.2 | 0.0000 | 0.00 | 0.187 | 0.000 [−0.000, 0.000] |
| S | 200 | set2set | 93.1 | 0.0002 | 0.01 | 0.187 | 0.000 [−0.000, 0.000] |
| S | 400 | mean | 0.5 | 0.051 | 0.55 | 0.170 | 0.017 [0.011, 0.022] |
| S | 654 | mean | 0.3 | 0.085 | 0.72 | 0.143 | 0.045 [0.033, 0.056] |
| D | 25 | set2set | 11.3 | 0.032 | 0.15 | 0.184 | 0.003 [−0.000, 0.009] |
| D | 50 | set2set | 13.3 | 0.028 | 0.18 | 0.184 | 0.004 [0.000, 0.007] |
| D | 100 | set2set | 0.0 | 0.091 | 0.35 | 0.183 | 0.004 [−0.008, 0.015] |
| D | 200 | set2set | 0.4 | 0.095 | 0.34 | 0.185 | 0.003 [−0.007, 0.012] |
| D | 400 | mean | 0.2 | 0.087 | 0.44 | 0.174 | 0.013 [0.006, 0.021] |
| D | 654 | mean | 0.7 | 0.088 | 0.55 | 0.161 | 0.026 [0.019, 0.034] |

"Constant" means the range of a host's ensemble predictions is below 1 meV. Within-host skill is the
zero-skill value (the within-host residual MAE of any host-constant predictor, 0.187 eV) minus the
model's, paired on the same hosts. The true within-host spread is 0.187 eV.

- **S at B ≤ 200 is a host-ranking model.** Its predictions vary within a host by about 0.1 meV, against
  0.19 eV in the targets.
- **D at B ≤ 200 varies within hosts but without skill.** Its within-host variation is about half the
  true spread, yet correlates only weakly with it.

### Pipeline checks (all pass)

- The graph store rebuilt from the release matches `data/graphs_v1_manifest.sha256` file for file. The
  graphs used in training are therefore the graphs checked here.
- In collated test batches, the flag sits on exactly one node per graph. That node is
  `vacancy_index`, it is an O atom, and it belongs to the right graph after batching
  (`tests/test_graphs.py::test_sites_of_one_host_share_the_graph_and_differ_only_in_the_flag`,
  `tests/test_models.py::test_readout_gathers_the_flagged_node_after_batching`).
- Sites of one host produce graphs that are identical except for the flag. The vacancy atoms of every
  multi-site host are distinct
  (`tests/test_models.py::test_site_graphs_of_one_host_differ_only_in_the_flag`, and the store test above).

### Mechanism: the backbone is site-blind at initialisation

Two inequivalent O sites of one host give the same output from an **untrained** S, to float precision.
On a randomly distorted MgO supercell, the relative spread of the output across O sites is about 2e-7,
under the tuned values of every anchor (a50, a200 and a654 alike). The flag survives to the readout, but
the geometry does not. After each MEGNet block the unflagged O nodes are identical to about 1e-6, even
though their mean edge RBF features differ by 0.02. With matgl's PyTorch default `nn.Linear`
initialisation and the slope-0.5 softplus2, the distance signal is attenuated through the stacked MLPs
(encoder, edge MLP, scatter-mean, node MLP) to float noise. The gradient of the output is 2e-7 with
respect to all edge distances combined, against 7e-4 with respect to the flag.

Since every vacancy node carries the same flag, an untrained S distinguishes hosts only by composition.
It must learn to amplify the geometric pathway, and the predictions show that it does so only with more
data and longer training: S's best epoch averages 103 at B = 400 and 128 at 654 (a654 values), against 28–31
at B ≤ 200. D varies within hosts at small budgets for the reason the flag survives: its site
descriptors enter at the vacancy node, before any distance-dependent layer.

Glorot initialisation, used by the original Keras MEGNet, raises the untrained relative spread only to
3e-4, and Kaiming(relu) to 6e-3. A re-initialisation alone is therefore not a clean fix.

This is recorded in the test suite as a strict expected failure
(`test_untrained_s_distinguishes_inequivalent_o_sites`). The test will flag the change if the backbone
is altered.

### Diagnostic runs (NRP, logged 2026-10-07)

Budget and tuned values are confounded: anchors 50 and 200 use set2set pooling, anchor 654 uses mean.
The `diag_cross` stage trains S at (B, anchor) = (200, 200), (200, 654), (654, 200) and (654, 654), on
resamples 0–2 with 3 seeds (36 runs, `results/diag_cross/`, NRP).

| B | Tuned values of anchor | Pooling | Mean best epoch | Test MAE | Within-host skill | Constant hosts (of ~102) | Corr. within |
|---:|---:|---|---:|---|---|---:|---:|
| 200 | 200 | set2set | 34 | 0.509 [0.465, 0.557] | 0.000 [−0.000, 0.000] | 99.0 | 0.03 |
| 200 | 654 | mean | 60 | 0.537 [0.440, 0.640] | 0.007 [−0.000, 0.017] | 25.7 | 0.23 |
| 654 | 200 | set2set | 33 | 0.417 [0.363, 0.471] | 0.000 [−0.000, 0.000] | 102.7 | −0.01 |
| 654 | 654 | mean | 168 | 0.263 [0.239, 0.288] | 0.059 [0.041, 0.079] | 1.0 | 0.78 |

The collapse follows the tuned values, not the budget. With the a200 values, S is site-blind even when
trained on 654 hosts. Those values reach their best validation MAE after about 33 epochs and stop,
before the geometric pathway has grown. With the a654 values, S at 200 hosts starts to separate sites
(26 constant hosts instead of 99) but has almost no skill, so budget matters as well. The a50 and a200
values were selected on 5 and 20 validation hosts, whose objective is dominated by host placement.

Single runs are noisy. Retraining the (200, 200) and (654, 654) cells on NRP changed individual site
predictions by 0.21–0.47 eV on average per run relative to the sweep's twin runs on the L40S, while
aggregate MAEs stayed close (0.509 on resamples 0–2 here; 0.516 over all ten resamples in the sweep). Only seed-ensemble, multi-resample numbers should be
reported.

`scripts/diag_checkpoints.py` adds the geometry and flag gradients of trained against untrained networks
(`results/diag_checkpoints.json`).

### Reporting consequence

If the backbone stays as pre-registered, the paper should state that at ≤ 200 hosts S learns host
ranking only (within-host skill 0.000 eV), and treat within-host skill against budget as a headline
result, not a footnote. Separately, the authors should decide whether the site-blind initialisation is an
implementation error under §14 (fix, re-tune, re-sweep) or a property of the pre-registered design
(report, with a logged sensitivity arm). The diagnostic runs above inform that choice.

## 2. Trivial references at every budget

Site-level test MAE, eV, 10 resamples.

| B | Training mean | B0 | RF-Kumagai | S | D |
|---:|---|---|---|---|---|
| 25 | 1.243 [1.194, 1.295] | 0.769 [0.726, 0.821] | 0.760 [0.712, 0.812] | 1.147 [1.088, 1.201] | 1.049 [0.925, 1.149] |
| 50 | 1.226 [1.182, 1.271] | 0.742 [0.710, 0.777] | 0.638 [0.597, 0.679] | 1.007 [0.945, 1.074] | 0.975 [0.865, 1.084] |
| 100 | 1.213 [1.172, 1.258] | 0.731 [0.699, 0.767] | 0.568 [0.536, 0.600] | 0.721 [0.666, 0.779] | 0.613 [0.557, 0.669] |
| 200 | 1.209 [1.168, 1.253] | 0.726 [0.695, 0.758] | 0.478 [0.453, 0.504] | 0.516 [0.485, 0.548] | 0.421 [0.379, 0.469] |
| 400 | 1.208 [1.168, 1.253] | 0.724 [0.694, 0.756] | 0.399 [0.376, 0.423] | 0.376 [0.345, 0.409] | 0.336 [0.316, 0.354] |
| 654 | 1.209 [1.168, 1.254] | 0.722 [0.693, 0.754] | 0.346 [0.328, 0.365] | 0.273 [0.251, 0.300] | 0.284 [0.267, 0.304] |

The training mean is the mean target of the B training hosts' sites, validation hosts included (the
median gives the same picture). Paired differences, from `results/diagnostics_sweep.json`:

| B | S − B0 | S − RF-Kumagai | D − B0 | D − RF-Kumagai |
|---:|---|---|---|---|
| 25 | +0.378 [0.314, 0.444] | +0.387 [0.331, 0.445] | +0.279 [0.143, 0.398] | +0.289 [0.172, 0.395] |
| 50 | +0.265 [0.196, 0.338] | +0.369 [0.313, 0.435] | +0.233 [0.118, 0.343] | +0.337 [0.237, 0.436] |
| 100 | −0.011 [−0.064, 0.047] | +0.153 [0.094, 0.215] | −0.118 [−0.178, −0.057] | +0.045 [0.002, 0.089] |
| 200 | −0.209 [−0.246, −0.173] | +0.038 [0.012, 0.066] | −0.304 [−0.357, −0.243] | −0.057 [−0.097, −0.012] |
| 400 | −0.348 [−0.380, −0.315] | −0.023 [−0.051, 0.008] | −0.388 [−0.419, −0.358] | −0.063 [−0.083, −0.045] |
| 654 | −0.449 [−0.481, −0.419] | −0.073 [−0.095, −0.052] | −0.438 [−0.470, −0.407] | −0.062 [−0.080, −0.043] |

At 25 and 50 hosts, S and D are two models without useful skill. Both are better than predicting the
mean, but worse than a two-descriptor linear fit. The D−S gap there is not evidence about descriptors.
Fig 2 must therefore show B0, RF-Kumagai and the training-mean predictor at every budget. N* and the gap
curve must be read against them.

**Limitation to state.** The a50 values, used at B = 25 and 50, were tuned on 5 validation hosts
(9 sites). The objective is noisy at that size (`docs/tuning.md`), and the a50 configurations may be part
of why the small-budget GNNs underperform. Combined with item 1, the small-budget networks stop after
about 30 epochs with a composition-level representation.

## 3. D against S

### Gap and within-host comparison

A = MAE_S − MAE_D (positive: D better), point values only:

| B | mean A | min | max | resamples with A > 0 |
|---:|---:|---:|---:|---:|
| 25 | +0.098 | −0.061 | +0.440 | 7/10 |
| 50 | +0.032 | −0.195 | +0.241 | 7/10 |
| 100 | +0.108 | −0.083 | +0.287 | 8/10 |
| 200 | +0.095 | −0.057 | +0.166 | 9/10 |
| 400 | +0.040 | −0.034 | +0.113 | 8/10 |
| 654 | −0.012 | −0.076 | +0.067 | 2/10 |

- **Within-host MAE at 654:** S 0.143, D 0.161 (ensemble).
- **Kiyohara split:** S 0.283 and D 0.284. D's within-host MAE there is lower (0.134 against 0.147).

### Descriptor checks (all pass)

- **No missing values.** No descriptor has non-finite values.
- **Zeros are physical.** Exact zeros occur only in the f-orbital band-edge characters (`cbm_f`, `vbm_f`:
  1545 sites) and the d-orbital ones (`cbm_d`, `vbm_d`: 59 and 48 sites), which are zero in hosts
  without those orbitals at the band edges.
- **Standardisation uses training sites only.** `train_run` fits on the training sites, with validation
  hosts excluded. Recomputed for the D runs at 654 on resample 0: no constant columns, all test z-scores
  finite, maximum |z| 14.7 (heavy tails, mostly dielectric constants).
- **Injection matches §4.** Host descriptors are appended to the initial global state. Site descriptors
  are multiplied by the flag, so they appear only on the vacancy node (code and
  `test_descriptor_injection_wired`).
- **Classes behave as expected.** The 12 host descriptors are constant within a host, and the 10 site
  descriptors vary within it.

### Within-host signal in the site descriptors

The site descriptors carry little within-host signal. Pooled within-host correlations with E_f:

| Descriptor | r |
|---|---:|
| O site's own Bader charge | 0.002 |
| Neighbour-averaged Bader charge | 0.25 |
| Neighbour-averaged Born effective charge | 0.26 |
| Site Born effective charge | −0.21 |
| Bader volume | −0.14 |

S's learned geometry reaches a within-host correlation of 0.72 at 654.

### Interpretation

A plausible reading: the descriptors give D an easy route to host placement and a weak within-host
signal, so D learns less from geometry than S. That would explain why D's within-host MAE is worse.
The class ablations test this (`d_ablation`, 27 runs, NRP). D-state at B = 654, resamples 0–2, 3 seeds,
seed-ensemble:

| Model | Test MAE | Within-host MAE | Within-host skill | Constant hosts |
|---|---|---:|---|---:|
| S (sweep) | 0.283 [0.260, 0.307] | 0.139 | 0.051 [0.035, 0.071] | 0.7 |
| D, all descriptors (retrained) | 0.300 [0.268, 0.331] | 0.166 | 0.024 [0.009, 0.038] | 0.0 |
| D, host descriptors at training mean | 0.297 [0.268, 0.329] | 0.160 | 0.031 [0.017, 0.044] | 0.0 |
| D, site descriptors at training mean | 0.341 [0.310, 0.376] | 0.190 | 0.000 [0.000, 0.000] | 102.7 |

- **The 12 host-electronic descriptors add nothing over structure.** Removing them leaves MAE unchanged
  (0.297 against 0.300).
- **D's within-host signal comes from the site descriptors, not from geometry.** Without them, D gives
  every site of a host the same prediction, even at 654 hosts and with the a654 values that let S learn
  geometry.
- **The shortcut costs D accuracy.** With descriptors available, the network does not grow the geometric
  pathway. The weak site descriptors replace the stronger geometric signal that S learns, so D ends up
  below S.

Per-descriptor permutation importances on the unablated checkpoints are in
`results/diag_checkpoints.json`.

### Wording consequence

D is not an upper bound in practice. The paper should call D the "descriptor-augmented reference", not an
"oracle upper bound". C2 should read: "At the maximum budget, the advantage A = MAE_S − MAE_D, with its
95% CI, measures what pristine-host DFT descriptors add to this architecture", rather than claiming it
bounds the improvement that perfect electronic information can provide.

## 6. Epoch cap

Pre-specified rule (deviations, 2026-10-07): S and D at 654, resamples 0–2, seeds 0–2, with a 600-epoch
cap.

- **Paired difference, 600 minus 200 epochs:** 0.000 eV for S and 0.000 eV for D. ΔA = 0.000. The cap is
  insensitive under the logged rule (|ΔA| ≤ 0.02 eV), and C2 does not depend on it.
- **Why exactly zero:** all 18 pairs give bit-identical predictions. No 600-epoch run found a better
  validation MAE after epoch 200. The runs that used all 200 epochs (S r0 s0, S r2 s0, D r1 s1) had best
  epochs at 174, 196 and 177, and early-stopped at epochs 204–226 with the same weights.
- **Caveat:** 10 of the 60 sweep runs at 654 used all 200 epochs, and only 3 of them fall in resamples
  0–2. The other 7 (S r5 s0, r5 s2, r6 s0, r7 s2, r9 s0, r9 s2; D r6 s0) were not rerun. One of them,
  S r9 s0, had its best epoch at 200. The S tuning anchor's best trial also ran to the cap; that affects
  hyperparameter choice and is not tested by capsens.

## 8. C0 and the tuning overlap

The tuning sets are nested (a50 ⊂ a200 ⊂ a654), so "in any tuning training or validation set" equals the
a654 set: 97 of the 126 Kiyohara test hosts (9 in a50, 30 in a200).

| Test hosts | n hosts (sites) | S | D | RF-Kumagai |
|---|---|---|---|---|
| All | 126 (272) | 0.283 [0.237, 0.329] | 0.284 [0.239, 0.331] | 0.414 [0.339, 0.499] |
| Not in any tuning set | 29 (68) | 0.285 [0.191, 0.401] | 0.270 [0.164, 0.403] | 0.346 [0.222, 0.513] |
| In a tuning set | 97 (204) | 0.282 [0.237, 0.335] | 0.289 [0.244, 0.336] | 0.436 [0.355, 0.536] |

There is no sign that the overlap improved C0, but the non-overlap interval is wide (29 hosts). Both rows
should be reported.

## Proposed deviation rows

Item 7 and the diagnostic runs are logged in `docs/deviations.md` (2026-10-07), because they run now.
Items 4 and 5 are proposed here. They must be signed off and copied to `docs/deviations.md` before any P
evaluation and before the C1/C2 analysis.

**Item 4 (§8, §9; C3a, C3b). Equivalence standard for staging and geometry.**
Proposed row: "DEVIATION. The staging contrast P − S (MAE_P − MAE_S, negative: P better) is reported with
an equivalence margin δ_P = 0.05 eV (TOST, α = 0.05 each side) and one of four outcomes, decided in this
order from the paired hierarchical bootstrap:
- **P better:** the 95% two-sided interval lies below 0.
- **P worse:** the 95% two-sided interval lies above 0.
- **Equivalent:** the 90% two-sided interval lies inside (−δ_P, δ_P).
- **Inconclusive:** otherwise.

'Better' or 'worse' with the 90% interval inside the margin is reported as 'different but within the
equivalence margin'. The sentence 'if the two-sided 95% interval of P − S includes 0, the result is a
null' is withdrawn. For C3b the same rule applies to the difference in degradation, ΔMAE_P − ΔMAE_S with
ΔMAE = MAE(MLIP geometry) − MAE(DFT geometry), at δ = 0.05 eV. The per-component slopes are compared with
the margin δ / IQR(component), where IQR is the interquartile range of that geometry component over the
hosts: a slope difference smaller than this moves |Δerror| by less than δ across the middle half of the
hosts."

Reason: failure to reject is not evidence of no difference. N* already uses an equivalence logic.

**Item 5 (§7; C1, C2). N* reporting rules.**
Proposed row: "CLARIFICATION.
(a) The abstract reports N* from the primary formula-grouped protocol (10 outer resamples). LOCO (§11)
runs only at the maximum feasible training size, so it gives no N*. Its A and interval are reported next
to N*. If the LOCO upper bound is ≥ δ while the grouped N* ≤ 654, the abstract says so in the same
sentence.
(b) If the first qualifying budget is 654, N* is reported as 'reached only at the maximum budget (654
hosts)', with no extrapolation and no fitted learning curve. If none qualifies, 'N* > 654'.
(c) The gap is A = MAE_S − MAE_D, positive when D is better, in every table, figure and sentence. The
phrase 'D minus S gap' in the C1/C2 statements is replaced by 'the advantage A = MAE_S − MAE_D'.
(d) The rule 'remains below δ at every larger tested budget' is binding: A is not monotone in B (point
values +0.032 at 50, +0.108 at 100), so a qualifying budget followed by a non-qualifying one does not
count."

**Item 7 (§12d; logged).** D-late is trained in the sweep protocol at B = 200, 400 and 654 (10 resamples,
3 seeds), and C1/C2 are reported with D-late in place of D-state as a sensitivity check. Result (90 runs,
`results/dlate/`; point values, A = MAE_S − MAE_D):

| B | D-state MAE | D-late MAE | A with D-state (resamples A > 0) | A with D-late (range; resamples A > 0) |
|---:|---:|---:|---:|---:|
| 200 | 0.421 | 0.441 | +0.095 (9/10) | +0.075 [−0.010, +0.155] (9/10) |
| 400 | 0.336 | 0.337 | +0.040 (8/10) | +0.039 [−0.039, +0.116] (8/10) |
| 654 | 0.284 | 0.291 | −0.012 (2/10) | −0.018 [−0.115, +0.075] (4/10) |

The choice between the two injection variants does not change the picture: D helps at 200 and 400 hosts
and not at 654.

## 9. Planning documents

`SCIENCE_BRIEF_v3.md` and `PLAN_v3.md` are not in this repository; the copies found are in the author's
Downloads folder. Each now opens with a banner marking it superseded by `docs/ANALYSIS_PLAN.md`
(818 hosts, 1726 sites, budgets to 654, Bader descriptors in D, seven figures per `docs/claims.yaml`).
Any other copy (shared drive, earlier drafts) should be marked the same way.

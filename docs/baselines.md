# Non-GNN baselines (S04)

Every number is read from `results/*.json` by `scripts/summarize_baselines.py`. Intervals are 95%:
hierarchical bootstrap over outer resamples and test hosts for the 10-resample rows, test-host cluster
bootstrap for the single Kiyohara split. Energies are in eV; targets are the neutral O-vacancy formation
energies of universe v1 (1726 sites, 818 hosts).

## Full budget (654 training hosts), 10 outer resamples

| Predictor | MAE | within-host residual MAE | RMSE | R2 |
|---|---|---|---|---|
| B0 physics floor | 0.722 [0.693, 0.754] | 0.187 [0.172, 0.203] | 0.904 | 0.591 |
| RF-Kumagai (70 descriptors) | 0.346 [0.328, 0.365] | 0.151 [0.140, 0.161] | 0.476 | 0.887 |
| RF-electronic (22) | 0.423 [0.402, 0.445] | 0.169 [0.154, 0.182] | 0.577 | 0.834 |
| RF-structural (48) | 0.386 [0.366, 0.406] | 0.157 [0.146, 0.169] | 0.556 | 0.845 |
| Host-mean oracle (descriptive, not a model) | 0.153 [0.140, 0.167] | 0.187 [0.172, 0.203] | 0.279 | 0.961 |

The host-mean oracle predicts each test site with the true mean over its host's sites. No predictor that
cannot tell the O sites of one host apart can beat its MAE.
Within-host residual MAE is the zero-skill value for any predictor that is constant within a host: the oracle and B0 (both host-level) share it by construction, so it is the reference for within-host skill, not a lower bound.

Within-host spread of the site energies (mean sd over hosts with two or more sites): 0.252 eV; mean range 0.439 eV.

## Kiyohara split (train on their 571 train hosts, test on their 126 test hosts)

| Predictor | MAE | within-host residual MAE | RMSE | R2 |
|---|---|---|---|---|
| B0 physics floor | 0.779 [0.678, 0.889] | 0.170 [0.136, 0.203] | 0.984 | 0.578 |
| RF-Kumagai (70 descriptors) | 0.414 [0.339, 0.499] | 0.130 [0.107, 0.155] | 0.605 | 0.841 |
| RF-electronic (22) | 0.484 [0.406, 0.571] | 0.147 [0.119, 0.176] | 0.670 | 0.804 |
| RF-structural (48) | 0.446 [0.373, 0.523] | 0.148 [0.122, 0.175] | 0.640 | 0.821 |
| Host-mean oracle (descriptive, not a model) | 0.143 [0.112, 0.171] | 0.170 [0.136, 0.203] | 0.228 | 0.977 |

Baselines need no validation set, so the 121 validation hosts are left unused.

## Comparison with published values

| Reference | Value | Ours |
|---|---|---|
| Kumagai 2021 RF, q = 0, 700 training oxides (K21 abstract, Fig. 5(a), Sec. III D) | 0.34 eV | RF-Kumagai at 654 hosts: 0.346 [0.328, 0.365] eV; difference +0.006 eV, **PASS** (tolerance 0.05 eV) |
| Kiyohara 2025 CGCNN, q = 0, their split (PRL 135, 246101) | 0.29 eV | RF-Kumagai on their split: 0.414 [0.339, 0.499] eV; B0: 0.779 eV; host-mean oracle: 0.143 eV |

Differences between our setting and K21's: universe v1 (1726 sites / 818 hosts) vs K21's 1745 / 824 before our D1-D3 filters; test set of 164 hosts (20%) vs 48 hosts; training pool of 654 hosts vs 700; MAE over our test sites; K21 evaluates site errors of its 48 test oxides; scikit-learn 1.9.1 vs 0.24.1.

## Learning curve (MAE by training hosts, 10 outer resamples)

| Training hosts | B0 physics floor | RF-Kumagai (70 descriptors) | RF-electronic (22) | RF-structural (48) |
|---|---|---|---|---|
| 25 | 0.769 | 0.760 | 0.767 | 1.016 |
| 50 | 0.742 | 0.638 | 0.658 | 0.849 |
| 100 | 0.731 | 0.568 | 0.596 | 0.659 |
| 200 | 0.726 | 0.478 | 0.532 | 0.528 |
| 400 | 0.724 | 0.399 | 0.469 | 0.439 |
| 654 | 0.722 | 0.346 | 0.423 | 0.386 |

## Kumagai-style RF learning curve (100 resamples per size)

| Training hosts | MAE (mean over 100 resamples) | sd across resamples | 95% interval |
|---|---|---|---|
| 22 | 0.756 | 0.100 | [0.730, 0.784] |
| 70 | 0.591 | 0.076 | [0.572, 0.613] |
| 220 | 0.457 | 0.058 | [0.441, 0.475] |
| 654 | 0.342 | 0.045 | [0.330, 0.355] |

Fit a N^-0.5 + b through N = 220 and 654: b = 0.183 eV (K21 reports 0.19 eV). Published values at N = 22, 70 and 220 appear only in Fig. 5(a) and are not used.

## Descriptor-class characterisation (SI; no model is altered)

| Contrast at full budget | MAE difference | 95% interval | within-host MAE difference |
|---|---|---|---|
| rf-electronic minus rf-structural | +0.037 | [+0.012, +0.065] | +0.011 |
| rf-kumagai minus b0 | -0.376 | [-0.404, -0.348] | -0.036 |
| rf-electronic minus rf-kumagai | +0.077 | [+0.065, +0.090] | +0.018 |
| rf-structural minus rf-kumagai | +0.039 | [+0.017, +0.062] | +0.007 |

## Sensitivity: high-moment entries

Removing the 10 entries with |defect moment| > 0.5 muB (pre-registered) from RF-Kumagai at 654 hosts changes the MAE by -0.004 eV, 95% interval [-0.008, -0.000] (paired over the same test hosts).

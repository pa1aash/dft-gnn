# Pre-registered analysis plan

Status: frozen before any graph network is trained (tag `prereg-v1`). Every decision below was signed
off by the author. Departures are handled only through Section 15. Config values that implement each
decision live in `configs/config.yaml`; `scripts/check_prereg.py` checks the numeric decisions against the
machine-readable block at the end of this document.

## Preamble

The study asks how much a graph network that sees only the pristine crystal structure of an oxide, with
the oxygen site to be removed marked, loses against the same network given the DFT electronic
descriptors of the pristine host and site. The physical quantity is the neutral oxygen-vacancy formation
energy E_f, evaluated at the reference oxygen chemical potential, in non-magnetic oxides. No new DFT is
performed: all targets, descriptors and structures come from the Kumagai et al. (Phys. Rev. Materials 5,
123803, 2021) database.

The data universe (universe v1) contains 1726 neutral oxygen-vacancy sites in 818 non-magnetic oxide
hosts. It is the Kumagai et al. 2021 machine-learning subset after the D1-D3 filters described in
Section 2.

Formation energies are dominated by the host. The one-way random-effects intraclass correlation of E_f
grouped by host is ICC_host = 0.930 (95% interval 0.909-0.947; `results/variance_decomposition.json`):
93% of the variance lies between hosts and 7% between the oxygen sites of one host. A site-level MAE is
therefore governed mostly by how well a model places each host, and could hide whether the model
distinguishes sites within a host. Within-host residual MAE is for this reason a mandatory secondary
metric throughout.

The non-GNN baselines at 654 training hosts, averaged over the ten outer resamples (`docs/baselines.md`),
set the scale against which the graph networks are judged. In site-level test MAE (eV): the
two-descriptor physics floor B0 reaches 0.722; the random forest on the 70 Kumagai descriptors
(RF-Kumagai) reaches 0.346, reproducing the published 0.34; the random forest restricted to electronic
descriptors (RF-electronic) reaches 0.423; the random forest restricted to structural and compositional
descriptors (RF-structural) reaches 0.386; and the host-mean oracle, which predicts each site with the
true mean of its host and is a descriptive bound rather than a model, reaches 0.153.

The splits are ten grouped 20% host hold-outs with nested training budgets of 25, 50, 100, 200, 400 and
654 hosts, plus the split released by Kiyohara et al. All are tracked in `splits/` and are immutable.

## 1. Hypotheses and claims

The claims register is `docs/claims.yaml`, reproduced here. Two statements were updated in this
session, in both this document and `docs/claims.yaml`: B0 now names its two descriptors and its
intercept explicitly, and C3a now defines the staged model P as a descriptor predictor feeding the
trained oracle D. B0 keeps the status "measured". No other claim was changed.

| ID | Statement | Tested by | Figure | Falsifiable how | Status |
|---|---|---|---|---|---|
| B0 | A linear model in two descriptors (oxide stability and PBEsol+U band gap) with intercept provides the thermodynamic floor against which all learned models are measured. | M1 | Fig2 | Descriptive baseline; reported, not tested. | measured (`results/b0_physics_floor.json`) |
| C0 | A structure-only MEGNet on pristine host supercells with a marked vacancy site reproduces the published structure-only accuracy for neutral oxygen vacancies (0.29 eV; Kiyohara et al., Phys. Rev. Lett. 135, 246101, 2025), on both our formula-grouped protocol and Kiyohara's released host split. | M3 | Fig2 reference line; SI parity | MAE on Kiyohara's split materially worse than 0.29 eV triggers debugging before any further claim. | planned |
| C1 | The MAE advantage of explicit DFT electronic descriptors over structure alone (D minus S) falls below delta = 0.05 eV, with the upper 95% bootstrap bound below delta at budget N* and all larger budgets; extends the descriptor-only learning curve of Kumagai et al. (2021) to the structure-versus-descriptor gap. | M5 | Fig2, Fig3 | If the upper bound never falls below delta within available data, N* is reported as a lower bound. | planned |
| C2 | At maximum training budget, the D minus S gap, with 95% CI, bounds the improvement perfect pristine-host electronic information can provide. | M5 | Fig3 | Measurement; reported with CI. | planned |
| C3a | A staged model P, which predicts the pristine-host electronic descriptors (host-level and pristine-site Bader) from structure and passes the predictions to the trained oracle D, is compared with end-to-end S and oracle D at matched budgets; the D-minus-P gap is the cost of predicting rather than knowing the descriptors. | M6 | Fig4 | P minus S indistinguishable from zero is reported as a null. | planned |
| C3b | Under MACE-MP-0 relaxed host geometry, staged and end-to-end models degrade differently; degradation is decomposed into volumetric strain and internal displacement. | M7 | Fig5 | Statistically indistinguishable degradation slopes, or negligible geometry change, are reported as a null. | planned |
| C4 | Linear-probe recovery of electronic descriptors from the structure-only model's embeddings increases with training budget and exceeds shuffled-label and random-encoder controls. | M8 | Fig6 | Flat trend or failure to beat both controls moves C4 to SI. | planned |
| C5 | Screening demonstration on named oxide crystals. | M10 | Fig7 | Demonstration, not a claim. | planned |

## 2. Data and splits

The analysis uses universe v1 and nothing else. It is built by a fixed filter cascade
(`results/filter_cascade.json`). The release holds 2103 completed neutral calculations in 935 hosts.
Kumagai et al.'s neutral machine-learning subset (`charge0.csv`) keeps 1745 of them in 824 hosts, having
already removed perturbed-host-state entries, entries with undetermined band edges and dynamically
unstable hosts. Three further filters then apply, in order. D1 removes the 15 entries flagged as vacancy
split, unknown defect type or not the same configuration as the initial one (1730 sites, 819 hosts). D2
removes the host Sr2Zr7O16, whose machine-learning site labels do not match the release targets (1726
sites, 818 hosts). D3 keeps an entry of the two hosts with inconsistent cell metadata (Ba4Nb2WO12 and
Sr2SnO4) only if its vacancy site maps to an oxygen atom with a matching first cation shell; it removes
nothing (Ba4Nb2WO12 is no longer present and Sr2SnO4 passes). The final universe is 1726 sites in 818
hosts.

The splits are used exactly as tracked in `splits/`, whose integrity is fixed by the sha256 manifest
`splits/MANIFEST.sha256` (the manifest file itself has sha256
`dd0986ef7667a0158cdf4bcfb5a7d41ba7fde3ae572b0691c975ea903ee9175a`). Each of the ten outer resamples holds
out 164 hosts (20%) as test hosts, stratified by host-mean E_f, and orders the remaining 654-host pool so
that the training set at budget B is the first B hosts of that order; budgets are therefore nested.
Grouping is by formula, which in this release is identical to grouping by host.

Independent 20% hold-outs do not test every host: 79 of the 818 hosts never fall in a test set across
the ten resamples. These 79 hosts are excluded from every per-host analysis, because no out-of-sample
prediction exists for them.

On the Kiyohara split, the graph networks train on Kiyohara's train hosts, early-stop on Kiyohara's
validation hosts and are tested on Kiyohara's test hosts (571, 121 and 126 hosts of universe v1).

## 3. Graph representation

Each example is the pristine host supercell from the release. The oxygen atom to be removed stays in the
graph and carries a binary vacancy flag in its node features. The graph is a periodic radius graph with a
cutoff of 5.0 Å. Node features are a learned element embedding plus the vacancy flag. Edge features are a
Gaussian expansion of the interatomic distance, with the MEGNet default number of centres and width.

The rationale is physical. At deployment the site to be removed is known, but the relaxed defect
geometry is not. The supercell matches the DFT defect cell, so the periodic images of the vacancy are
separated as in the reference calculation.

## 4. Models

All graph networks share a backbone of MEGNet blocks from matgl 4.1.0, using its PyG implementation.

The structure-only model S reads out the concatenation of three vectors: the embedding of the vacancy
node, a global pooling of all node embeddings (Set2Set or mean pooling) and the global state. A
multilayer perceptron maps this vector to E_f. The pooling choice is a tuned hyperparameter. The
physical rationale for this readout is that E_f decomposes into a host-level thermodynamic term and a
local-environment term, which matches the measured variance structure (Preamble).

The descriptor model D is S plus the descriptor classes listed in `models.D.descriptor_classes`
(host-electronic DFT and site-electronic DFT, as defined in `docs/descriptor_taxonomy.csv`),
standardised with training-set statistics. Two injection variants are defined. In D-state, the
host-electronic descriptors are appended to the initial global state and the site-electronic
descriptors are appended to the initial features of the vacancy node. In D-late, all descriptors are concatenated to the readout vector before the multilayer
perceptron. The variant with the lower mean validation MAE across the three tuning anchors becomes D for
the whole study. The other variant is reported only from its tuning runs, in the SI.

The descriptor predictor P1 has the backbone and readout of S, with a multi-output head that predicts
all standardised D descriptors. It is trained with a mean-squared-error loss with equal weights on the
descriptors.

The staged model P is the composition of P1 and D: at inference, D receives the descriptors predicted by
P1 instead of the true ones. D itself is trained on true descriptors, as in serial charge-then-energy
pipelines. P is evaluated against D on identical test hosts, so D acts as the true-descriptor swap-in for
P, and the difference between them isolates the cost of predicting the descriptors. P1's per-descriptor
test R² and MAE are reported.

The non-GNN baselines (B0, RF-Kumagai, RF-electronic and RF-structural) are used as defined and run in
S04 and are frozen.

## 5. Training

The E_f loss is L1 on the target, standardised with the training-set mean and standard deviation. The
optimiser is AdamW, with a ReduceLROnPlateau schedule (factor 0.5, patience 15).

The maximum number of epochs and the early-stopping patience are not fixed in this plan. S07 sets them
from the benchmark, and they are frozen before tuning begins; the config holds the placeholder
`TBD-S07` for both. Early stopping monitors validation MAE and restores the best weights.

The validation set is carved out of the training hosts with `val_split` (fraction 0.1, at least 3 hosts),
with its seed derived from the resample r, the budget B and the training seed. Every (resample, budget)
pair is trained with seeds 0, 1 and 2.

Checkpoints are saved for every S run, because the latent probe of Section 10 needs them, and for every D
and P1 run.

## 6. Hyperparameter tuning

Hyperparameters are tuned with Optuna's TPE sampler, 30 trials per model per anchor. The tuned models are
S, D-state, D-late and P1. The anchors are training budgets of 50, 200 and 654 hosts, using the nested
training sets of resample 0. The objective is the inner validation MAE only; test hosts are never seen
during tuning.

The search space is identical for all tuned models: learning rate log-uniform on [1e-4, 3e-3]; weight
decay log-uniform on [1e-6, 1e-3]; hidden width in {64, 128}; number of MEGNet blocks in {2, 3, 4};
dropout uniform on [0, 0.3]; batch size in {16, 32, 64}; readout MLP width in {64, 128}; and pooling in
{set2set, mean}.

Each training budget takes its hyperparameters from one anchor: budgets 25 and 50 use the 50-host anchor,
budgets 100 and 200 the 200-host anchor, and budgets 400 and 654 the 654-host anchor.

One limitation is disclosed. Hosts in resample 0's training pool appear in the test sets of other
resamples, so the tuned hyperparameters carry mild cross-resample information. This is standard practice
and is stated in Methods.

## 7. Primary analysis (C1, C2)

The primary metric is site-level test MAE in eV. The secondary metrics are within-host residual MAE and
host-mean MAE.

For each resample r and budget B, the advantage of descriptors over structure is A_rB = MAE_S − MAE_D,
computed on the same test hosts from the seed-ensemble-mean prediction of each model. A positive A means
that the DFT electronic descriptors help.

Uncertainty comes from a paired hierarchical bootstrap with 2000 draws: resamples are drawn with
replacement, then test hosts are drawn with replacement within each drawn resample, and the mean A is
recomputed on each draw. Pairing keeps S and D on the same hosts in every draw.

The margin is δ = 0.05 eV. It is one-sixth of the published structure-only error (0.29 eV) and well
below the spread between DFT and experiment for defect formation energies.

N* is the smallest budget B whose one-sided 95% upper bound on A, the 95th percentile of the bootstrap
distribution, is below δ, and remains below δ for every larger tested budget. This is a non-inferiority
test of S against D with margin δ, equivalent to one arm of a TOST at α = 0.05. If no budget qualifies,
N* > 654 is reported as a lower bound.

The C2 ceiling is A at B = 654 with its two-sided 95% interval: bounding the improvement that perfect
pristine-host electronic information can provide (claim C2).

Intervals displayed in figures are two-sided 95%. The same analysis is repeated for the within-host
residual MAE and reported as secondary. On multiplicity, the requirement that the bound hold at N* and
at all larger budgets is the stated protection; no further correction is applied.

## 8. Staging analysis (C3a)

At every budget the analysis reports the MAE of S, D and P, together with two paired contrasts computed
with the same paired hierarchical bootstrap as Section 7: D − P, the cost of predicting rather than
knowing the descriptors, and P − S, staging against end-to-end learning. If the two-sided 95% interval of
P − S includes 0, the result is a null and is reported as such.

## 9. Geometry robustness (C3b, M7)

The alternative host geometry comes from MACE-MP-0, medium model, in
float64. Each pristine host unit cell is relaxed (cell and positions; FIRE; fmax 0.01 eV/Å; at most 500
steps) and then tiled with the release's supercell matrix, so that vacancy atom indices map one to one
onto the DFT supercell. The model version and its hash are recorded.

The geometry change of each host is decomposed into three parts. The isotropic strain is
ε_v = (V_MLIP / V_DFT)^(1/3) − 1. The deviatoric strain is the Frobenius norm of the deviatoric part of
the deformation gradient between the DFT and MLIP lattices. The internal RMSD is the RMSD between the DFT
Cartesian positions and the Cartesian positions obtained by placing the MLIP fractional coordinates on
the DFT lattice, with fixed atom correspondence.

Models trained on DFT geometry are evaluated without retraining under three inference conditions: (i)
DFT geometry; (ii) MLIP geometry; and (iii) a control, MLIP geometry isotropically rescaled to the DFT
volume. ΔMAE is each condition minus condition (i), for S, D and P at B = 654 and at N* (or at B = 200 if
no N* exists).

Per-host |Δerror| is regressed on the three geometry components, and the analysis is stratified by
cation d-electron count, with formal oxidation states taken from pymatgen's oxidation-state guess and
binned as d0, d10 and other.

Under MLIP geometry, D keeps its DFT descriptors. It is therefore a fixed oracle, and its degradation
isolates the contribution of the graph input alone. This is stated explicitly in the text of the paper.

The null outcome is defined in advance: if the median internal RMSD is below 0.01 Å and the |ΔMAE|
intervals include 0, the result is reported as "serial fragility not realised in this regime".

## 10. Latent probe (C4, M8)

From the frozen S checkpoints (seed 0, all resamples, all budgets), the readout input
vector is extracted for each test site. A ridge regression maps these embeddings to each D descriptor,
with the regularisation strength α chosen by an inner 5-fold grouped cross-validation on the training
sites. Test R² is reported per descriptor, together with its mean over each descriptor class.

Two controls are run: (a) the same probe on shuffled descriptor labels; and (b) a randomly initialised,
untrained S encoder of the same architecture.

C4 holds if the class-mean R² increases with budget (Spearman ρ > 0 with a bootstrap interval excluding
0) and exceeds both controls at B ≥ 200. Otherwise C4 moves to the SI.

## 11. Robustness and uncertainty (M9)

Leave-one-chemistry-out evaluation: hosts are grouped by
their periodic-group cation pattern (definition ii of the S02 data audit). GroupKFold with k = 5 runs
over these families at the maximum feasible training size, for S and D with 3 seeds. The advantage A is
reported with a host bootstrap.

Ensemble uncertainty is the spread of the seed predictions for each site. Its calibration is reported as
the Spearman correlation between the ensemble standard deviation and the absolute error.

Seed-variance and resample-variance tables are reported.

## 12. Pre-registered sensitivity analyses

Four sensitivity analyses are fixed now. (a) The 10 entries whose defect magnetic moment exceeds 0.5 μB
in magnitude are excluded, and S and D are rerun at B = 654. (b) S, D and P are run on the Kiyohara
split. (c) A cross-architecture check replaces the backbone with CGCNN for S and D at B = 50, 200 and
654, on resample 0 only, with 3 seeds; it is reported in the SI. (d) The D injection variant that was not
selected is reported from its tuning runs only, in the SI.

## 13. Screening demonstration (C5, M10)

The candidate list is fixed now: ZnO, TiO2 (all polymorphs present), SnO2, In2O3, CeO2, MgO, Al2O3,
ZrO2, SrTiO3, BaTiO3, Ga2O3, WO3, MoO3, Nb2O5 and LaAlO3. Only candidates present in universe v1 and
tested in at least one resample are kept. For each kept host, the out-of-sample S prediction at B = 654,
averaged over every resample in which the host was tested, is reported against the DFT value, per site.
The chemical discussion of these oxides is written after G2.

## 14. Gates and stopping rules

G1 requires a learning-curve figure with error bands for RF, B0, S and D to exist before any staging,
MLIP or probe work starts.

The C0 check: if S's MAE on the Kiyohara split exceeds 0.35 eV, the implementation is debugged before
the sweep. Debugging may change implementation errors only, never pre-registered design choices.

G2 is the results freeze, marked by the tag `results-v1`.

The cost gate: S07 reports runtime and memory, and the author approves the pod before S09.

## 15. Deviations policy

Any departure from this plan is logged in `docs/deviations.md` with the date, the reason and the impact,
before the affected run. All deviations are reported in the SI. Results generated before a deviation are
retained and reported.

## Machine-readable decisions

The block below is parsed by `scripts/check_prereg.py`, which fails if any value differs from
`configs/config.yaml`. Keys are dotted config paths.

```yaml prereg
stats.delta_eV: 0.05
stats.ci: 0.95
analysis.bootstrap.draws: 2000
analysis.n_star.upper_quantile: 0.95
analysis.n_star.alpha: 0.05
analysis.c2_ceiling_budget: 654
analysis.c2_ceiling_ci: 0.95
analysis.display_ci: 0.95
analysis.staging_null_ci: 0.95
budgets.hosts: [25, 50, 100, 200, 400, 654]
budgets.max: 654
split.n_outer_resamples: 10
split.test_fraction: 0.2
tuning.optuna_trials_per_model_per_anchor: 30
tuning.anchors: [50, 200, 654]
tuning.anchor_resample: 0
tuning.budget_to_anchor: {25: 50, 50: 50, 100: 200, 200: 200, 400: 654, 654: 654}
tuning.search_space.learning_rate.low: 1.0e-4
tuning.search_space.learning_rate.high: 3.0e-3
tuning.search_space.weight_decay.low: 1.0e-6
tuning.search_space.weight_decay.high: 1.0e-3
tuning.search_space.hidden_width.choices: [64, 128]
tuning.search_space.megnet_blocks.choices: [2, 3, 4]
tuning.search_space.dropout.low: 0.0
tuning.search_space.dropout.high: 0.3
tuning.search_space.batch_size.choices: [16, 32, 64]
tuning.search_space.readout_mlp_width.choices: [64, 128]
training.seeds: [0, 1, 2]
training.scheduler.factor: 0.5
training.scheduler.patience: 15
training.validation.frac: 0.1
training.validation.min_hosts: 3
training.max_epochs: TBD-S07
training.early_stopping.patience: TBD-S07
graph.cutoff_A: 5.0
mlip.relax.fmax_eV_per_A: 0.01
mlip.relax.max_steps: 500
mlip.budget_if_no_n_star: 200
mlip.null_rule.median_internal_rmsd_A_below: 0.01
probe.checkpoints.seeds: [0]
probe.alpha_cv.folds: 5
probe.pass_rule.beats_controls_min_budget: 200
robustness.loco.k: 5
robustness.loco.seeds: [0, 1, 2]
sensitivity.exclude_high_moment.threshold_muB: 0.5
sensitivity.exclude_high_moment.budget: 654
sensitivity.cgcnn_check.budgets: [50, 200, 654]
sensitivity.cgcnn_check.resamples: [0]
sensitivity.cgcnn_check.seeds: [0, 1, 2]
screening.budget: 654
screening.min_resamples_tested: 1
gates.C0_kiyohara_max_mae_eV: 0.35
```

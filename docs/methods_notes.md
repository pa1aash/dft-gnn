# Methods notes

Seed material for the Methods section and the SI of the manuscript. Each item states a fact of the
protocol as run, with the file that records it. Items are added as the study proceeds.

## Training budget and the validation carve-out

The training budget B counts training hosts including the validation hosts used for early stopping.
The validation set is carved out of the B hosts by `dftgnn.split.val_split` (10%, at least 3 hosts;
ANALYSIS_PLAN §5), so the number of hosts whose sites enter the loss is about 0.9 B: 22 of 25, 45 of
50, 180 of 200 and 589 of 654. Learning curves are plotted against B, the number of hosts with DFT
labels that a model consumes, which is the quantity a practitioner pays for.

## Epoch cap and early stopping

The maximum number of epochs (200) and the early-stopping patience (30) were set by a rule logged
before the calibration pilot ran (`docs/deviations.md`, 2026-10-06 and 2026-10-07): the cap is the
smallest multiple of 50 at or above 1.5 times the slowest convergence epoch over the piloted budgets
(133 epochs at B = 654), and the patience is max(30, 0.15 x cap). Early stopping monitors the
validation MAE and restores the weights of the best epoch.

Sensitivity: in the untuned C0 pilot, two of three seeds reached their best validation MAE near the
cap (best epoch 198 and 189 of 200, counted from 1). Rerunning those two seeds with a 600-epoch cap changed their test MAE by
-0.015 and +0.014 eV (`results/c0_cap_check/`), with no systematic direction. This is reported in the
SI.

## GPU throughput settings

Training ran on one NVIDIA L40S. Several training processes shared the card through CUDA MPS, and a
process started a run only when the summed benchmarked peak memory of the running jobs, times a safety
factor of 1.25, stayed within 85% of the device memory (`dftgnn.train.admission`,
`dftgnn.jobqueue`). These settings affect wall time only. They do not change any hyperparameter,
split, seed or stopping rule. In the 18 epoch-cap pairs (S and D at B = 654, resamples 0-2, seeds
0-2, 200- and 600-epoch caps), every 600-epoch run reproduced its 200-epoch twin bitwise: the prediction
files have equal sha256 (`results/g1_diagnostics.json`). This was observed for 18 pairs on one GPU class
(NVIDIA L40S). It is not a general guarantee: the scatter-add aggregations of PyTorch Geometric have no
deterministic CUDA kernel, and GPU floating-point summation order is not guaranteed to be bitwise
reproducible. Runs on the CPU with the same seed and thread count are bit-identical.

## Limitation: tuning hosts that are Kiyohara test hosts

The hyperparameters were tuned on resample 0's nested training sets (ANALYSIS_PLAN §6), and the tuning
objective was the validation MAE on hosts carved out of those sets. Kiyohara's released split was drawn
independently, so many of these hosts are Kiyohara test hosts. Of the 126 Kiyohara test hosts, 97 lie in
the 654-host anchor set (8 of them among its 65 validation hosts), 30 in the 200-host anchor set (1 of 20
validation hosts) and 9 in the 50-host anchor set (1 of 5 validation hosts). The official C0, which uses
the 654-host anchor's hyperparameters, is therefore not a fully held-out evaluation on Kiyohara's split: the
hyperparameters were chosen with the labels of 97 of its 126 test hosts in the training data and 8 of them
in the objective. Model weights never saw those hosts' labels in the C0 runs themselves (they train only
on Kiyohara's training hosts). The counts are recorded in `results/c0_official.json`
(`tuning_overlap_with_kiyohara_test`).

## G1 primary analysis: bootstrap procedure

The advantage of the DFT descriptors at budget B is A = MAE_S − MAE_D, where each MAE is the site-level test MAE
of the seed-ensemble mean prediction (three seeds) over the 164 test hosts of an outer resample, averaged over the
10 resamples. Uncertainty comes from a paired hierarchical bootstrap with 2000 replicates
(`dftgnn.stats.g1.HierDraws`). In each replicate, 10 resamples are drawn with replacement; within each drawn
resample its test hosts are drawn with replacement, every site of a drawn host is kept, and the metric of each
model is recomputed on the draw; the replicate value is the mean over the 10 draws. The generator is
`numpy.random.default_rng(20261008)`, and one set of draws is applied to every model, budget and metric, so all
differences are paired and budgets share their host draws (test hosts are identical across budgets within a
resample). Two-sided 95% intervals are the 2.5th and 97.5th percentiles; the one-sided 95% upper bound used for
N* is the 95th percentile. N* is the smallest tested budget whose upper bound is below δ = 0.05 eV and stays below
δ at every larger tested budget (`scripts/analysis/g1_analysis.py`; `results/g1_primary.json`). The bootstrap
resamples test-host composition and outer-split variability; retraining noise enters only through the
differences between resamples.

## G1 clarifications

Logged in `docs/deviations.md` on 2026-10-08 before any analysis code ran on the sweep predictions; none alters a
pre-registered decision: (1) the seed ensemble is the arithmetic mean of the three seed predictions per site;
(2) the bootstrap design, seed and percentile convention above, with draws shared across models, budgets and
metrics; (3) budgets are paired within resample; (4) N* is evaluated over {25, 50, 100, 200, 400, 654} with a
strict comparison and reported as ">654" if no budget qualifies; (5) negative A is reported as computed, without
truncation; (6) the within-host residual MAE uses hosts with at least two sites and the same δ and rule, and
host-mean MAE is descriptive; (7) the epoch-cap comparison uses the seed ensembles of resamples 0-2 at B = 654
with the sweep runs as the 200-epoch comparator; (8) the S09 sanity table is reproduced from single-seed
predictions; (9) baselines are the frozen S04 predictions and the host-mean oracle, descriptive only; (10) the
seed- and resample-variance tables are sample SDs as defined in the log.

## G1 epoch-cap sensitivity outcome

At B = 654 on resamples 0-2, A(200) = A(600) = −0.013 eV (two-sided 95% interval [−0.044, +0.017]); the
difference is 0.000 eV, within the pre-specified 0.02 eV, so the primary result is cap-insensitive
(`results/g1_cap_sensitivity.json`). In all 18 pairs the 600-epoch run reached its best validation MAE at the
same epoch as the 200-epoch run and produced byte-identical predictions (`results/g1_diagnostics.json`): no run's
best epoch lay beyond epoch 200. The bootstrap for this comparison draws from only three resamples.

## CGCNN cross-check (sensitivity c)

Architecture defaults fetched headlessly from the original repository, https://github.com/txie-93/cgcnn,
commit f42ab233c4ee0c416879d6bc2d22a264418413ad (`main.py`, `cgcnn/model.py`, `cgcnn/data.py` via
raw.githubusercontent.com): `--atom-fea-len 64`, `--n-conv 3`, `--h-fea-len 128`, `--n-h 1`; Gaussian
distance filter `dmin 0`, `step 0.2`, `var = step`; softplus activations; batch norm in each convolution.
The repository's optimiser defaults (SGD, lr 0.01, momentum 0.9, weight decay 0, batch 256, 30 epochs) are
not used: the cross-check fixes AdamW, lr 1e-3, weight decay 1e-5 and batch 32 at every budget, with the
section 5 protocol otherwise (docs/deviations.md, 2026-10-10). Graphs are the 5.0 A radius graphs of the
main models (the original uses the 12 nearest neighbours within 8 A). Convolutions are
`torch_geometric.nn.CGConv` (sum aggregation, batch norm on the aggregated message, residual) each followed
by a softplus; PyG's layer lacks the original's batch norm on the gated pre-activation. Parameter counts:
cgcnn-S 83,009, cgcnn-D 85,825 (22 descriptors x 128 extra first-layer weights).

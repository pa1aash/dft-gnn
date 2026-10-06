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
split, seed or stopping rule. GPU runs are reproducible up to floating-point summation order: the
scatter-add aggregations of PyTorch Geometric have no deterministic CUDA kernel, so two runs with the
same seed agree closely but not bitwise. Runs on the CPU with the same seed and thread count are
bit-identical.

**Figure G1. Learning curves of the neutral oxygen-vacancy formation energy.** (**a**) Site-level test mean
absolute error (MAE, eV) against the number of training hosts B (25, 50, 100, 200, 400 and 654; logarithmic
axis) for the two-descriptor physics floor B0, the random forest on the 70 Kumagai descriptors (RF-Kumagai),
the structure-only MEGNet S and the descriptor model D (S given the host-electronic and site-electronic DFT
descriptors of the pristine host, D-state injection). The thin dashed lines mark published values: the
random-forest MAE of Kumagai et al. (Phys. Rev. Materials 5, 123803, 2021; 0.34 eV, 700 training oxides) and
the structure-only CGCNN MAE of Kiyohara et al. (Phys. Rev. Lett. 135, 246101, 2025; 0.29 eV, their split).
(**b**) The advantage of the DFT descriptors, A = MAE_S − MAE_D, against B; the dashed line marks the
pre-registered margin δ = 0.05 eV and the dotted line marks zero. Each point is the mean over 10 outer
resamples, each holding out 164 test hosts (20% of 818; 1726 sites in universe v1) with nested training
budgets drawn from the remaining 654 hosts and grouped by formula. S and D predictions are the mean of three
training seeds (0, 1, 2) per test site; B0 and the random forest are single fits. Shaded bands are two-sided
95% intervals from a paired hierarchical bootstrap (2000 replicates: resamples drawn with replacement, then
test hosts drawn with replacement within each drawn resample, all sites of a drawn host kept; one set of
draws shared by all models and budgets; seed 20261008). N* is defined, before any result was seen, as the
smallest tested budget at which the one-sided 95% upper bound of A (the 95th bootstrap percentile) is below δ
and stays below δ at every larger tested budget; if no budget qualifies, N* > 654 is reported. Source:
`results/g1_primary.json`.

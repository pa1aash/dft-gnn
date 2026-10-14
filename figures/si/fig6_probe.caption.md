**Figure 6. Latent probe: linear recovery of the DFT electronic descriptors from the structure-only model's readout
input.** For every resample r and budget B, a ridge regression maps the readout input vector of the seed-0 S
checkpoint ([vacancy-node embedding, pooled node embeddings, global state]) to each descriptor given to D, with
the regularisation chosen by cross-validation grouped by host on the training sites, and is scored by
test R² on the test sites (implementation and rule: `docs/deviations.md`, the latent-probe row of the A4 step;
`docs/ANALYSIS_PLAN.md`, latent-probe section). Originally registered backbone (v1), the registered analysis:
dashed line, open markers and hatched band for the trained probe (dashed bars in (**c**)). Controls in grey: the same probe with descriptor
rows permuted among training hosts (shuffled labels; squares) and the probe on an untrained encoder of the same
architecture (init0, the registered random-init control; triangles); the encoders init1 and init2 (light grey,
dotted, no band) show the spread of the random-init control and are descriptive. (**a**)
Host-electronic and (**b**) site-electronic class-mean test R² (unweighted mean over the descriptors of the class)
against training hosts on a logarithmic axis: `results/probe_c4_v1.json`, keys
`payload.curves.<host|site>.<trained|shuffled|init0|init1|init2>.<B>` (`mean` over the resamples, two-sided
interval `ci95` of the resample bootstrap; per-resample values `per_resample`). The dotted line is zero. (**c**)
Test R² per descriptor at the largest budget, host-electronic descriptors above the grey rule and site-electronic
below: `results/probe_descriptive.json`, keys `payload.per_descriptor_r2.<trained|shuffled|init0>.<descriptor>.654`
(`mean`, `ci95`). The rule of the latent-probe section is evaluated in `payload.rule.<host|site>` of
`results/probe_c4_v1.json`: `trend` (Spearman ρ of log budget against the trained class mean over all resample-budget cells,
`rho`, `ci95`, `holds`) and `controls.<B>|<shuffled|init0>` (trained minus control, `mean`, `ci95`, `exceeds`) at
the budgets the rule names. The rule does not hold (`results/probe_c4_v1.json`, `payload.C4_holds` false; `payload.outcome`), so C4 moves to the Supplementary Information and this figure is placed there (`figures/si/`). Panel letters (a) and (b) together form the class-mean panel of the analysis plan and (c) its
per-descriptor panel. The collaborator's probe on the primary backbone (v2) is POST HOC and is not drawn; its
quantities are in `results/probe_descriptive.json`, key `payload.s_v2`. Within-host R² of the site-electronic
descriptors: `payload.within_host_site`. Script: `figures/code/fig6_probe.py`.

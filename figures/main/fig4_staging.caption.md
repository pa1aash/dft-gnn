**Figure 4. Staging: predicting the DFT descriptors from structure and passing them to the descriptor model.** The
staged model P feeds the descriptors predicted by P1 from the pristine host structure into the trained descriptor
model D of the same resample, budget and seed (pairing in `docs/deviations.md`: the staging-pairing
clarification and the A2 implementation row); S is the structure-only model. Training hosts on a logarithmic axis. (**a**) Seed-ensemble test MAE
of S, D and P (eV): `payload.budgets.<B>.mae.<S|D|P>` (`mean`, two-sided interval `ci95`). (**b**) The two staging
contrasts of the staging section of `docs/ANALYSIS_PLAN.md`: D − P, the cost of predicting rather than knowing the descriptors (negative:
P worse than D), key `payload.budgets.<B>.D_minus_P`; and P − S, staging against end-to-end learning (negative: P
better than S), key `payload.budgets.<B>.P_minus_S` (`mean`, `ci95`; the TOST interval `ci90`, the one-sided
bounds `lower_one_sided_95` and `upper_one_sided_95`, the outcome `report` and `noninferior`). The dashed lines
are the equivalence margins plus and minus δ_P (`payload.delta_P_eV`), the dotted line zero. The outcome of P − S
at every budget follows the TOST rule of the collaborator (`docs/deviations.md`: the TOST row and its ratification;
POST HOC) and is listed in `payload.summary.outcome_by_budget`. Records: `results/staging_v2.json`
(solid lines, filled markers, filled bands: primary backbone (v2), adopted after diagnostics of the originally
registered backbone, POST HOC) and `results/staging_v1.json` (dashed lines, open markers, hatched bands:
originally registered backbone (v1), the registered staging analysis). Bands are the two-sided intervals of the
paired hierarchical bootstrap over resamples and test hosts named in `payload.estimator` (one draw set for S, D,
P, every budget and both backbones). The axes span the point estimates and the P − S intervals; the bands of D in
(a) and of D − P in (b) at the smallest budgets reach beyond them and are clipped (full intervals under the keys
above). Integrity checks (counts, pairing, true-descriptor swap-in): `payload.integrity`; P1 descriptor accuracy:
`payload.p1_descriptors`. Script: `figures/code/fig4_staging.py`.

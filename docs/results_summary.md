# Results summary

For the authors writing the paper. Every number below comes from a committed result record (paths given),
computed by the scripts named, with the rules of `docs/ANALYSIS_PLAN.md` and `docs/deviations.md`. Unless noted,
values are site-level test MAE in eV on ten formula-grouped 20% host hold-outs, from the seed-ensemble mean
(3 seeds), with 95% hierarchical bootstrap intervals (resamples, then test hosts; 2000 draws). A = MAE_S − MAE_D,
positive when the DFT descriptors help; δ = 0.05 eV.

Two arms are reported:

- **Pre-registered.** The backbone and tuned values of the plan; this is the primary analysis.
- **v2.** A post-hoc backbone with He initialisation, chosen on validation hosts and re-tuned
  (deviations of 2026-10-08/09). It is used for the staged model, the probe and the MLIP analysis, and is
  reported as a post-hoc model chosen on validation data.

## Headline results

| Claim | Pre-registered arm | v2 arm | Record |
|---|---|---|---|
| C0, Kiyohara split, S | 0.283 [0.237, 0.329] (published 0.29); 0.285 [0.191, 0.401] on the 29 hosts outside every tuning set | S-v2 0.325 [0.272, 0.379]; D-v2 0.277 [0.232, 0.327] | `c0_official.json`, `diagnostics_sweep.json`, `v2_kiyohara/` |
| C1, N* | Reached only at the maximum budget (654); upper bounds +0.188, +0.100, +0.171, +0.133, +0.067, +0.010 at 25–654 | Reached only at the maximum budget (654); 200 qualifies (+0.047) but 400 does not (+0.075), so the binding rule decides | `c1c2_v1.json`, `c1c2_v2.json` |
| C2, A at 654 | −0.012 [−0.036, +0.014] | +0.015 [−0.008, +0.036] | same |
| LOCO A (unseen cation families, 654–655 training hosts) | +0.008 [−0.015, +0.031], upper bound 0.027 < δ | +0.041 [+0.016, +0.066], upper bound 0.061 ≥ δ, which the abstract must state in the sentence giving N* (deviation 2026-10-09, rule a) | `c1c2_v1.json`, `c1c2_v2.json` |
| C3a, P − S | — (pre-registered staged model not run) | Inconclusive at 25; P worse at 50, 100, 200; equivalent at 400 (+0.024 [−0.003, +0.050]); P worse but within the equivalence margin at 654 (+0.028 [+0.008, +0.052]) | `c3a_v2.json` |
| C3a, D − P (cost of predicting the descriptors) | — | −0.149, −0.142, −0.077, −0.043 eV at 100, 200, 400, 654 (D better); unstable at 25–50 (see limitations) | same |
| C3b, MLIP geometry | — | *pending* (`mlip_eval_v2.json`) | |
| C4, latent probe | — | **Fails its rule; moves to the SI.** Class-mean test R² rises with budget (Spearman ρ 0.975 [0.963, 0.986]) and beats shuffled labels at every B ≥ 200 (+0.35 to +0.60), but not the untrained encoder (trained − random: −0.032 [−0.062, −0.000] at 200, −0.031 at 400, −0.003 [−0.015, +0.009] at 654) | `probe_v2_sweep.json` |

### Learning curves (site MAE, eV)

| B | Training mean | B0 | RF-Kumagai | S | D | S-v2 | D-v2 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 25 | 1.243 | 0.769 | 0.760 | 1.147 | 1.049 | 1.133 | 1.275 |
| 50 | 1.226 | 0.742 | 0.638 | 1.007 | 0.975 | 0.959 | 1.468 |
| 100 | 1.213 | 0.731 | 0.568 | 0.721 | 0.613 | 0.657 | 0.574 |
| 200 | 1.209 | 0.726 | 0.478 | 0.516 | 0.421 | 0.456 | 0.432 |
| 400 | 1.208 | 0.724 | 0.399 | 0.376 | 0.336 | 0.382 | 0.328 |
| 654 | 1.209 | 0.722 | 0.346 | 0.273 | 0.284 | 0.296 | 0.280 |

## Findings to report

1. **Electronic descriptors add nothing measurable at full budget.** C2 is consistent with zero in both arms.
   The host-electronic descriptors are redundant with structure: removing them from D costs nothing
   (0.297 vs 0.300 eV), although a trained D leans on them (permuting them costs 0.81 eV, mostly oxide
   stability and band gap). `docs/diagnostics_sweep.md` §3, `diag_checkpoints.json`.
2. **Below 400 hosts the pre-registered networks rank hosts but not sites.** Within-host skill of S is
   0.000 eV at 25–200 and 0.045 [0.033, 0.056] at 654. S-v2 reaches 0.016 [0.010, 0.022] at 200 and
   0.038 [0.028, 0.048] at 654. Cause: the backbone is site-blind at initialisation, and the small-budget
   tuned values stop training before the geometric pathway grows. Training with the 654 values raises the
   geometry gradient by seven orders of magnitude; with the small-budget values it does not grow, even on
   654 hosts. `docs/diagnostics_sweep.md` §1, Fig. within-host skill.
3. **Small-budget networks lose to simple baselines.** At 25–50 hosts both networks beat the training mean
   but are 0.2–0.4 eV worse than B0 and RF-Kumagai. S passes RF-Kumagai only at 654 (pre-registered) and is
   level with it at 200–400 (v2).
4. **On unseen chemistry the structure-only network beats the descriptor forest.** Pre-registered S scores
   0.313 under LOCO against 0.414 for RF-Kumagai (−0.101 [−0.129, −0.074]); RF loses 0.068 eV going from
   random to chemistry hold-outs, S 0.040.
5. **v2 trades large-budget accuracy for small-budget accuracy.** S-v2 improves at 100–200 hosts but is worse
   at 654 (0.296 vs 0.273), on the Kiyohara split (0.325 vs 0.283) and under LOCO (0.347 vs 0.313). D-v2's
   descriptor advantage under LOCO (+0.041) comes mostly from that weaker S-v2.
6. **Staging (predict descriptors, then energy) never beats end-to-end learning.** P is worse than S from 50
   to 200 hosts and at most equivalent at 400–654.
7. **Training does not put extra electronic information into the structural representation.** A linear probe
   recovers the 22 descriptors from the trained S-v2 readout as well as, not better than, from an untrained
   network of the same architecture (mean R² 0.555 against 0.557 at 654 hosts). The rise with budget reflects
   the probe's growing training set. This fits finding 1: the information the descriptors carry is already in
   the structure.

## Limitations to state

- **D-v2 is unstable at 25–50 hosts.** A few seeds reach test MAE of 3–10 eV while their validation MAE is
  normal (about 0.4 eV, on 5 validation hosts). The pre-registered seed-ensemble mean is reported unchanged;
  medians are 0.74 eV at 50.
- **Tuning values at small anchors rest on 5 and 20 validation hosts.** They drive the site-blindness of item 2.
- **P1-v2 was not re-tuned for the v2 backbone** (deadline; deviation 2026-10-09).
- **Single runs are noisy.** Retraining one configuration changes site predictions by 0.2–0.5 eV on average.
  Only ensemble, multi-resample numbers are reported.
- **The pre-registered sweep checkpoints were lost.** The staged model, the probe and the MLIP analysis exist
  only for v2.
- **Scope.** All claims are about reproducing one DFT dataset (PBEsol+U, neutral O vacancies, non-magnetic
  oxides; Kumagai et al. 2021) on held-out hosts and held-out cation families, not about experiment or other
  functionals.

## Figures

All figures are vector PDFs at printed width in `figures/main/`, generated by `scripts/make_figures.py` from the
records above, with captions printed by the script:

- `fig2_learning_curves.pdf`: both arms with baselines.
- `fig3_advantage.pdf`: A with intervals, one-sided bounds and δ.
- `fig_within_host.pdf`: within-host skill.

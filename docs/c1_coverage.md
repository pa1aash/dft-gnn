# C1: claim coverage for the final network

Final network = the He-initialised, validation-tuned network (v2 in the repository, `configs/tuned_v2.yaml`).
Ablation = the default-initialisation network (v1, the originally registered backbone). Energies in eV;
intervals are two-sided 95% unless marked; delta = 0.05 eV. New C1 records are in `results/derived_c1/`;
their tables are `docs/c1_final_network_table.md` and `docs/c1_ablation_table.md`.

Status key: **final** = a record on the final network exists; **network-free** = the quantity does not depend on
the network; **v1 only** = the claim currently rests on the default-initialisation network alone;
**PENDING** = being rerun separately on the final network.

| Claim | Status | Final-network record | Key final-network number | Default-init (v1) record and number |
|---|---|---|---|---|
| Headline: A = MAE_S - MAE_D at 654 training hosts | final | `results/derived_c1/final_network_summary.json` (`table.rows.B654`, `B654_30x5`); `results/c1c2_v2.json`; `results/precision_a_b400_b654.json` (`v2`) | sweep 10 x 3: A = +0.015 [-0.008, +0.037], upper +0.033; pooled 30 x 5: A = +0.033 [+0.021, +0.045], upper +0.043; both intervals inside +-0.05 | `results/g1_primary.json`: A = -0.012 [-0.035, +0.014], upper +0.009 |
| Headline: N* (upper bound below delta at N* and beyond) | final | `results/c1c2_v2.json` (`N_star`); upper bounds per budget recomputed with the G1 estimator in `final_network_summary.json` | N* = 654; the upper bound is also below delta at 200 (+0.047) but not at 400 (+0.075), so not monotone | `results/g1_primary.json`: N* = 654 |
| Extended budget: about 736 and 777 training hosts (grouped CV) | final | `results/cv_extended_budget.json` (`v2.k10`, `v2.k20`); `final_network_summary.json` (`CV_k10`, `CV_k20`) | K = 10: +0.024 [+0.005, +0.042], upper +0.039; K = 20: +0.026 [+0.010, +0.043], upper +0.040; inside +-0.05 | K = 10: -0.025 [-0.041, -0.009]; K = 20: -0.021 [-0.036, -0.006] |
| Unseen chemistry (leave-one-family-out, 5 folds) | final | `results/ingest_m1_recompute.json` (`loco_v2`); `results/derived_c1/loco_family.json` | A = +0.041 [+0.018, +0.064], upper +0.060 (exceeds delta by 0.010); not inside +-0.05 | `loco_v1`: +0.008 [-0.015, +0.031], upper +0.027 |
| Between-host variance (ICC 0.930) | network-free | `results/variance_decomposition.json` (`host`) | ICC = 0.930 [0.909, 0.947] (1726 sites, 818 hosts) | same record |
| Within-host site resolution: A_within | final | `results/c1c2_v2.json` (`A_within_host`, `N_star_within_host`) | A_within at 654 = -0.002 [-0.013, +0.009], upper +0.007; N*_within = 25 | `results/g1_within_host.json`: A_within at 654 = -0.018 |
| Within-host site resolution: pooled within-host MAE, zero-skill reference | final | `results/within_host_breakdown.json` (`groups[variable=pooled].v2`) | S 0.146 [0.133, 0.161], D 0.146 [0.133, 0.160]; zero-skill 0.184 [0.166, 0.203] (network-free) | v1 block of the same record |
| Within-host site resolution: prediction spread relative to the data | final (new) | `final_network_summary.json` (`table.within_host_prediction_spread`); `default_init_ablation.json` (`site_resolution`) | S spread / target spread: 0.012 at 25, 0.017 at 50, 0.123 at 100, 0.265 at 200, 0.412 at 654 | v1: 0.001, 0.004, 0.000, 0.001 at 25-200; 0.454 at 654 (`results/g1_diagnostics.json`) |
| Staging: P - S, D - P per budget | final | `results/staging_v2.json` | P - S at 654 = +0.028 [+0.008, +0.053], upper +0.049: P worse, within the margin; P non-inferior at 400 and 654 only; P never better | `results/staging_v1.json` |
| Staging: swap-in check (P with true descriptors reproduces D) | **PENDING** | `results/staging_swapin_check.json` lists v2 as "not run" | being rerun separately | v1: 3 of 3 cells passed, max deviation 0.0 |
| Geometry (n = 809 relaxations) | v1 only for the registered analysis; final network descriptive only | `results/mlip_eval_v2.json` (collaborator's v2 evaluation, his estimator); `results/geometry_descriptive.json` (`cross_check_809`) | largest abs Delta-MAE 0.003 (P, MLIP geometry, 654); S at 654: +0.000 [-0.003, +0.003] | `results/geometry_c3b.json` (our 818 relaxations, 739 evaluated hosts, null rule, TOST) exists for v1 only |
| Latent probe (C4) | final, descriptive | `results/probe_descriptive.json` (`s_v2`) | C4 does not hold under the A4 rule; trend rho host 0.964 [0.949, 0.980], site 0.978 [0.970, 0.987] | `results/probe_c4_v1.json`: C4 does not hold (moved to SI) |
| Screening (10 sites, 7 hosts) | final | `results/screening_c5.json` (`mae_S_v2`); `figures/main/data/screening_demo.json` (`summary.v2`) | MAE of S = 0.420 [0.307, 0.553] | v1: 0.294 [0.195, 0.424] |
| High-moment exclusion (A5) | **PENDING** | none (`results/sens_high_moment_v1.json` states that no v2 runs exist) | being rerun separately | A at 654 without 10 entries: -0.015 [-0.037, +0.005], upper +0.002 |
| Capped runs (600-epoch twins, A5) | **v1 only** | none (`results/sens_capped_post_hoc.json` `v2`: no capped reruns exist); descriptive capped-vs-uncapped counts for v2 in `results/precision_a_b400_b654.json` and `results/cv_extended_budget.json` (`descriptive.capped`) | n/a | A at 654 with twins: -0.008, upper +0.014 |
| CGCNN cross-check (A5) | final comparator exists | `results/sens_cgcnn.json` (`table.megnet_v2`) | resample 0, 654: MEGNet-v2 A = +0.031 [-0.010, +0.075], upper +0.069; CGCNN A = +0.003 [-0.031, +0.035] (CGCNN untuned, network-free) | `table.megnet_v1`: -0.014 [-0.049, +0.020] |
| Baselines (B0, RF) at every budget | network-free | `results/g1_primary.json` (`descriptive_curves`); `final_network_summary.json` | RF 0.346 [0.329, 0.365], B0 0.722 [0.691, 0.754] at 654 | same |

## Claims that currently rest only on the default-initialisation network

1. **Capped-run rule (600-epoch twins).** No capped reruns exist for the final network.
2. **Registered geometry analysis C3b** (null rule, TOST, d-bin strata, non-converged sensitivity, our 818
   relaxations). The final network has only the collaborator's descriptive evaluation on his 809 relaxations
   (`results/mlip_eval_v2.json`), with his estimator.
3. **The registered C4 rule application** (`results/probe_c4_v1.json`). The final-network probe is descriptive
   (`results/probe_descriptive.json`).
4. **S10b checkpoint forensic** (flag sweep, readout decomposition): run on v1 checkpoints only. The
   prediction-level spread statistic now exists for the final network (row above).
5. **High-moment exclusion** and **staging swap-in check**: PENDING (being rerun separately).

## Unseen chemistry: which families drive the bound

Source: `results/derived_c1/loco_family.json`. Families are the S02 keys: the sorted periodic-table groups of a
host's non-oxygen elements (lanthanides and actinides count as group 3); 131 families in 5 grouped folds.
"Contribution" is the family's share of the pooled A (the sum of |e_S| - |e_D| over its sites divided by all
1726 sites; the contributions add up to the pooled A). Leave-one-family-out bounds use the same estimator on
the remaining hosts (descriptive).

Final network: pooled A = +0.041 [+0.018, +0.064], upper +0.060, i.e. 0.010 above delta.

| Fold | Hosts | A | two-sided 95% | upper | Contribution | Pooled upper without this fold |
|---|---|---|---|---|---|---|
| 0 | 164 | +0.132 | [+0.065, +0.203] | +0.194 | +0.028 | +0.036 |
| 1 | 164 | +0.041 | [-0.009, +0.092] | +0.084 | +0.007 | +0.064 |
| 2 | 164 | +0.009 | [-0.040, +0.052] | +0.046 | +0.002 | +0.072 |
| 3 | 163 | +0.052 | [+0.009, +0.101] | +0.091 | +0.011 | +0.061 |
| 4 | 163 | -0.032 | [-0.075, +0.007] | +0.002 | -0.007 | +0.085 |

| Family (groups) | Fold | Hosts | Sites | A within family | Contribution | Pooled upper without it | Example hosts |
|---|---|---|---|---|---|---|---|
| 1-14 | 0 | 48 | 132 | +0.301 | +0.023 | +0.037 | Cs2Li2GeO4, Cs2Li2SiO4, Cs2Pb2O3, Cs2PbO2 |
| 1-13 | 3 | 38 | 79 | +0.197 | +0.009 | +0.054 | Cs2Li3GaO4, Cs3AlO3, Cs3GaO3, Cs3InO3 |
| 1-2-15 | 1 | 11 | 21 | +0.272 | +0.003 | +0.059 | Ba3NaBiO6, Ba3NaSbO6 |
| 1-15 | 2 | 40 | 77 | +0.074 | +0.003 | +0.060 | Cs2LiAsO4, Cs3BiO3 |
| 1-12 | 0 | 20 | 32 | +0.165 | +0.003 | +0.058 | Cs2HgO2, K2CdO2, K2Zn3O4 |

The excess over delta is carried by one family: the alkali group-14 oxides (Cs, K and Rb germanates,
silicates and plumbates; 48 hosts, 132 sites, all in fold 0). Within that family S errs by 0.30 eV more
than D per site, and it alone contributes +0.023 of the pooled +0.041. Without it the pooled upper bound is
+0.037, below delta; removing any one of the other nine largest contributors instead leaves it at +0.054 to
+0.060, above delta. The alkali group-13
family (aluminates, gallates, indates) is second (+0.009). Both are alkali-rich oxides whose vacancy energies
the structure-only model, trained without that chemistry, places poorly and the DFT electronic descriptors
correct. The default-initialisation network shows the same two families at the top (+0.022, +0.009), but its
pooled bound (+0.027) stays below delta because fold 4 offsets them (A = -0.052 there).

So the paper may say for unseen chemistry only that the upper bound on A is 0.060 eV, above 0.05 eV, with the
excess traced to the alkali group-14 family; it may not say "within 0.05 eV" or "below 0.05 eV" there.

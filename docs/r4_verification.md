# R4 verification: read-only answers from the repository's records

Session R4, 2026-10-17. Nothing was computed. Each answer names the file and the key (JSON pointer, YAML path, CSV
column or document section) it rests on. K21 = Kumagai et al., Phys. Rev. Materials 5, 123803 (2021); K25 =
Kiyohara et al., Phys. Rev. Lett. 135, 246101 (2025), as tagged in `docs/provenance.md`.

## (a) Number of oxides in the Kumagai release

**The record's number is 937.** It counts the oxides (hosts) of the release.

| Number | What it counts | Record and key |
|---|---|---|
| 937 | Hosts of the release: distinct formulas, distinct MP IDs, per-host archives and `site_info/` folders | `results/structure_audit.json#/payload/polymorph/release_hosts` (937; also `unique_formula_strings`, `unique_mp_id`); `results/data_inventory.json#/payload/file_classes/unpacked/oxygen_vacancies_db/oxygen_vacancies_db_data/<formula>.tar.gz/files` (937); `docs/data_audit.md` set (c), "937 (935 with a completed neutral entry; Cs2HfO3 and KBa4Sb3O have none)"; `docs/provenance.md` verification row 1 ("K21 reports **937** oxides with completed vacancy calculations; DB ships 937 per-formula tarballs") |
| 935 | Hosts with at least one completed neutral calculation (2103 entries); the first step of the filter cascade | `results/filter_cascade.json#/payload/steps/0/hosts` (step `release`, criterion "Completed neutral entries in the release"); macro `\numFilterCascadeStepsReleaseHosts`; `docs/data_audit.md` set (a) |
| 932 | Kiyohara et al.'s working count of non-magnetic oxides ("non-magnetic 932 oxides with 2090 inequivalent sites", K25 Methods p. 10) | `docs/provenance.md` verification row 1 and Discrepancy 1; `docs/data_audit.md` section 3.1: 932 equals 937 minus the 3 dynamically unstable hosts minus the 2 hosts with no completed neutral entry, "a coincidence of arithmetic that K25 does not confirm"; K25's code ships 924 host files |

R3 printed 935 (`\numFilterCascadeStepsReleaseHosts`) as the size of the database, which is the completed-neutral
count. R4 prints 937 through the new curated macro `\numNetReleaseOxides` (`results/structure_audit.json#/payload/polymorph/release_hosts`)
in the Introduction and the first sentence of Methods 2.1. Methods 2.1 now reads "The release covers 937 oxides and
holds 2103 completed neutral calculations in 935 of them". 932 does not appear in the paper.

## (b) Kiyohara et al.'s published structure-only MAE

**0.29 eV at q = 0, two decimals, the precision of the source.**

- `results/c0_official.json#/payload/comparison_eV/kiyohara_published` = 0.29 (the record behind `\numNetPublishedMae`).
- `results/k25_split.json#/payload/reported/q0_test_MAE_eV` = 0.29. Its `source` field reads "K25 p. 2, p. 6, Fig. 3(a)",
  and `q1_test_MAE_eV` = 0.22 and `q2_test_MAE_eV` = 0.37.
- `docs/claim_check.md` section (b) quotes the source text (arXiv:2510.00513v2): "we achieved improved accuracies of
  0.29, 0.22, and 0.37 eV for the neutral, +1, and +2 charge states". `docs/data_audit.md` (line 247) agrees: "q = 0
  test MAE 0.29 eV".

R3 printed it as 0.290, because the house rule of `make_numbers.fmt` gives three decimals. R4 gives
`\numNetPublishedMae` the curated format `trim` (three decimals, trailing zeros dropped), so it prints 0.29 in the
Introduction, Methods 2.5, Results 3.1 and Discussion 4.3. The macro is used nowhere outside the main-text sections.

## (c) Did Kumagai et al. 2021 report error against training-set size?

**Yes, and the repository holds the source text.** `docs/claim_check.md` section (a) quotes K21:

- Sec. III D: "22, 70, 220, and 700 oxides were selected for the training sets, and 48 oxides for the test sets".
- Fig. 5 caption: "(a) RF model convergence against the number of oxides in the training set. The model creation
  process was repeated 100 times with a different training set."

`results/baselines_summary.json#/payload/rf_kumagai_vs_published/curve_endpoint_check/published_at_700_eV` (0.34)
records the endpoint of that curve. The text was extracted in S01 from the publisher PDF into a local cache, which is
not tracked. The tracked quotation in `docs/claim_check.md` is the repository's record of it.

The Introduction ("Kumagai et al. trained random forests on such descriptors and followed their error as the number
of training oxides grew") and Discussion 4.3 ("with a learning curve over the number of training oxides") say what
these lines support. Neither sentence was changed. Because the repository can show the source, this is not a NEEDS
PALAASH item.

## (d) Tuning of S, D, P1 and P under He initialisation

Protocol: tree-structured Parzen estimator, 30 trials per model per anchor (`configs/config.yaml#/tuning/optuna/trials_per_model_per_anchor`),
anchors 50, 200 and 654 hosts, validation hosts of resample 0. The objective is the validation MAE of E_f in eV for S
and D, and for P1 the MAE over the 22 standardised descriptors (dimensionless), as `docs/tuning.md` line 5 states.

| Model | Initialisation of the tuning | Trials (50 / 200 / 654) | Best validation MAE (50 / 200 / 654) | Record |
|---|---|---|---|---|
| S | He (re-tuned) | 30 / 30 / 30 | 0.490 / 0.361 / 0.263 eV | `results/tuning_v2_summary.json#/payload/best/S|50/best_value` (and `S|200`, `S|654`); `results/tuning/tuning_v2_S_a*.json#/payload/n_complete` = 30 |
| D (D-state) | He (re-tuned) | 30 / 30 / 30 | 0.318 / 0.258 / 0.197 eV | `results/tuning_v2_summary.json#/payload/best/D-state|50/best_value` (and `|200`, `|654`); `results/tuning/tuning_v2_D-state_a*.json` |
| P1 | default only; **not re-tuned** | 30 / 30 / 30 under the default initialisation; **0 under He** | 0.706 / 0.426 / 0.340 (standardised descriptors, default initialisation) | `results/tuning_summary.json#/payload/studies/P1_a50/best_value` (and `P1_a200`, `P1_a654`); `configs/tuned_v2.yaml#/models` holds S, D-state and D only |
| P | not tuned (P1 composed with the trained D) | none | none | `docs/deviations.md` row 2026-10-10 §8 (staging pairing) |
| S, default (for reference) | default | 30 / 30 / 30 | 0.721 / 0.465 / 0.253 eV | `results/tuning_summary.json#/payload/studies/S_a*/best_value` |
| D-state, default (for reference) | default | 30 / 30 / 30 | 0.419 / 0.285 / 0.218 eV | `results/tuning_summary.json#/payload/studies/D-state_a*/best_value` |

What the deviations log says about P1. `docs/deviations.md`, row 2026-10-09 §4, §8, §9, §10: "P1-v2 is P1 with P1's
pre-registered tuned values (`configs/tuned_v1.yaml`, P1 at each budget's anchor) plus the v2 option `init: kaiming`;
it is not re-tuned (deadline)". Its consequence column reads: "P1-v2's hyperparameters are not tuned for the v2
backbone." The choice of He initialisation itself came from a 36-run design screen on validation hosts
(`docs/deviations.md` row 2026-10-08 §6).

**Plain statement.** Under He initialisation, S and D were each re-tuned with 90 trials (30 at each of three anchors).
P1 was not re-tuned: it carries the values from its 90 default-initialisation trials. The staged model P therefore
did **not** receive the same tuning budget as S and D under He initialisation. In addition, P1 reaches the 200-epoch
limit in 2, 10 and 20 of 30 sweep runs at 200, 400 and 654 hosts
(`results/derived_w2/w2_training_limit.json#/payload/counts_sweep_10x3/<B>/P1/n_capped`). The staging conclusion is
therefore stated "at the tuning and training length used" (Part 2 item 9; `docs/r4_changes.md`).

## (e) The descriptor set given to D

D receives the 22 electronic descriptors of the pristine cell, 12 host-level and 10 site-level. The 48 structural
and compositional descriptors of the release are withheld from D.

Records:
- the list of 22: `results/rf_electronic.json#/payload/features` (`n_features` = 22);
- level and class: `docs/descriptor_taxonomy.csv`, columns `name`, `level`, `class`;
- the split: `results/staging_v2.json#/payload/p1_descriptors/654/by_class/host_electronic/n_descriptors` = 12 and
  `.../site_electronic/n_descriptors` = 10, and `docs/deviations.md` row 2026-10-10 §8 ("P1 predicts all 22 D
  descriptors (12 host-electronic DFT, 10 site-electronic DFT)").

| Level | Class (taxonomy) | Descriptors (`name` in docs/descriptor_taxonomy.csv) |
|---|---|---|
| host (12) | host-electronic DFT | `band_gap` (PBEsol(+U) gap); `formation_energy` (per atom, the Materials Project value, a tabulated pristine-DFT quantity); `ave_ele_diele`, `ave_ion_diele` (electronic and ionic dielectric constants); `vbm_s`, `vbm_p`, `vbm_d`, `vbm_f`, `cbm_s`, `cbm_p`, `cbm_d`, `cbm_f` (orbital character of the band edges) |
| site (10) | site-electronic DFT | `bader_charge`, `bader_volume` (Bader charge and volume of the oxygen to be removed); `ave_bec` (its Born effective charge); `nn_ave_bader_charge`, `nn_max_bader_charge`, `nn_min_bader_charge`, `nn_ave_ave_bec`, `nn_max_ave_bec`, `nn_min_ave_bec` (solid-angle-weighted mean, maximum and minimum over the periodic Voronoi neighbours of the O site); `o2p_center_from_vbm` (centre of the O 2p band of the site below the VBM) |
| site (48), withheld from D | structural/compositional | 3 neighbour-electronegativity statistics and 45 Voronoi solid-angle fractions by element |

Every descriptor of D comes from the pristine unit cell, and none needs a defect calculation (`deployment_cost`
column). The text before R4 described D's input three ways: "all pristine-host descriptors" in the Abstract, "every
pristine-host and pristine-site electronic descriptor" in the Introduction and "every pristine-host descriptor" in
the Conclusions. The first and third were inaccurate, because ten of the descriptors are site-level. R4 uses one
description, "the 22 pristine-cell electronic descriptors, 12 host-level and 10 site-level". It appears in the
Abstract (in short form), the Introduction, Methods 2.1 and 2.2, and the Conclusions.

The taxonomy defines the six neighbour statistics over the Voronoi neighbours of the O site, not over its cation
neighbours. Methods 2.1 said "cation neighbours" and now says "Voronoi neighbours".

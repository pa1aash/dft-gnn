# Provenance labels for the collaborator NRP analysis (M1)

One label per analysis or result group on the collaborator branch `origin/review-diagnostics` (tip
`f658823`), with the matching main-side group where one exists.

- **PRE-REGISTERED**: v1 (the registered backbone and `tuned-v1` values), with the deciding rule
  committed before the results.
- **POST HOC**: the v2 backbone, or any rule committed after the results it decides.
- **EXTENSION**: new compute or analysis beyond the plan.

Labels describe chronology. They do not grade the results. All times are UTC commit times
(`git blame` of `docs/deviations.md`, first commit of each result file), or the first `timestamp_utc`
among a group's run records. Reference points:

| event | time (UTC) | ref |
|---|---|---|
| plan frozen, tag `prereg-v1` | 2026-10-06 09:03 | 2d2c19a |
| tuned values frozen, tag `tuned-v1` | 2026-10-07 11:24 | 1e4d634 |
| official C0 (Kiyohara split) | 2026-10-07 11:59 | 8e832f9 |
| sweep T1 (B = 654, 400; Kiyohara D) and T2 (B = 200–25) test predictions committed | 2026-10-07 20:50, 22:32 | 2829f74, 2f818da |
| fork point of all collaborator branches | 2026-10-08 00:15 | 9ec3af5 |
| his sweep diagnostics on test predictions ("review of 2026-10-07"; within-host spread at B ≤ 200) | 2026-10-08 02:40 | d58b1cc, `results/diagnostics_sweep.json` |
| our G1 clarifications / G1 results / tag `g1-v1` | 2026-10-08 08:49 / 08:55 / 08:57 | main |
| our S10b site-resolution forensic (test hosts) | 2026-10-08 13:40 | ac0af6c |
| his v2 deviation row (design screen and selection rule) | 2026-10-08 16:55 | 44cf16b |

## Labels

| # | group | records | backbone | rule (row or plan section) and commit time | first result | label |
|---|---|---|---|---|---|---|
| 1 | G1 primary (C1, C2), pre-registered arm | main `results/g1_primary.json`; his `results/c1c2_v1.json` (same inputs, identical point values) | v1 | ANALYSIS_PLAN §7 in `prereg-v1` (2026-10-06 09:03); main clarifications 2026-10-08 08:49; his reporting rules (deviations 2026-10-09 §7) 2026-10-09 16:55 | test predictions 2026-10-07 20:50; main analysis 2026-10-08 08:55; his 2026-10-09 18:03 | PRE-REGISTERED |
| 2 | G1 on the v2 arm | `results/c1c2_v2.json` | v2 | same estimand; v2 arm rows 2026-10-08 16:55 and 2026-10-09 16:24 | 2026-10-10 04:43 | POST HOC |
| 3 | LOCO, S and D (§11) | `results/loco/` (30 runs), A in `results/c1c2_v1.json` | v1 (a654 values) | ANALYSIS_PLAN §11 in `prereg-v1`; his fold row 2026-10-08 16:55 | first run 2026-10-08 19:16 | PRE-REGISTERED |
| 4 | LOCO baselines B0 and RF-Kumagai on the folds | `results/loco_baselines.json`, `results/predictions/loco_*.parquet` | none | his LOCO row 2026-10-08 16:55 ("for reference"); not in §11 | 2026-10-08 17:04 | EXTENSION |
| 5 | LOCO on the v2 arm | `results/loco_v2/` (30 runs) | v2 | v2 production row 2026-10-09 16:24 | 2026-10-09 17:27 | POST HOC |
| 6 | staging (C3a): P1-v2 training and P-v2 evaluation | `results/p1_v2/` (183), `results/p_v2/` (183), `results/c3a_v2.json` | v2 (P1-v2 = `tuned-v1` P1 values + `init: kaiming`, not re-tuned) | rows 2026-10-09 16:55 (v2 for staging; TOST rule replacing the §8 null sentence) | P1-v2 2026-10-09 19:49; P-v2 21:35 | POST HOC |
| 7 | geometry evaluation (C3b) | `results/mlip_eval_v2.json` | v2 (S-v2, D-v2, P-v2 at B = 654 and 200) | rows 2026-10-09 16:55 (v2 for MLIP; TOST on the degradation difference) | 2026-10-10 05:27 | POST HOC |
| 8 | MLIP relaxations | `results/mlip/relaxed_shard{0-3}.json.gz` (809 hosts, 802 converged), `results/mlip_inputs.json` | none | ANALYSIS_PLAN §9 in `prereg-v1` (MACE-MP-0 medium, float64, FIRE, fmax 0.01, 500 steps) | inputs 2026-10-09 18:00; relaxations committed 18:39 | PRE-REGISTERED |
| 9 | latent probe (C4) | `results/probe_v2_sweep.json` (60 S-v2 checkpoints) | v2 | §10 rule (pre-registered) applied to v2 checkpoints; row 2026-10-09 16:55 | 2026-10-10 05:02 | POST HOC |
| 10 | screening (C5), pre-registered S | `results/screening_c5.json` (`mae_S`, 0.294 eV) | v1 (sweep S at B = 654) | ANALYSIS_PLAN §13 candidate list and aggregation in `prereg-v1` | 2026-10-10 05:29 | PRE-REGISTERED |
| 11 | screening (C5), S-v2 column | `results/screening_c5.json` (`mae_S_v2`, 0.420 eV) | v2 | none beyond §13 | 2026-10-10 05:29 | POST HOC |
| 12 | descriptor ablations and permutation importances | `results/d_ablation/` (27), `results/diag_checkpoints.json` | v1 | his diagnostics row 2026-10-08 02:39 | 2026-10-08 03:31 | EXTENSION |
| 13 | D-late trained in the sweep protocol | `results/dlate/` (90) | v1 (D-late `tuned-v1` values) | his row 2026-10-08 02:39 (§12(d) registered D-late from tuning runs only) | 2026-10-08 07:43 | EXTENSION |
| 14 | budget × tuned-setting crossing | `results/diag_cross/` (36) | v1 | his diagnostics row 2026-10-08 02:39 | 2026-10-08 06:53 | EXTENSION |
| 15 | checkpoint gradient and flag diagnostics | `results/diag_checkpoints.json` | v1 (retrained diagnostic checkpoints) | his diagnostics row 2026-10-08 02:39 | 2026-10-08 20:28 | EXTENSION |
| 16 | C0 tuning-overlap check | `results/diagnostics_sweep.json` (`c0_overlap`) | v1 (official C0 predictions) | none (analysis of existing predictions) | 2026-10-08 02:40 | EXTENSION |
| 17 | v2 design screen | `results/v2_screen/` (36 runs) | v2 candidates | v2 row 2026-10-08 16:55 (variants and selection rule) | 2026-10-08 19:24 | POST HOC |
| 18 | v2 retuning | `results/tuning/tuning_v2_*.json` (6 studies × 30) | v2 | row recording the selection 2026-10-09 00:36 (§6 protocol unchanged) | 2026-10-09 03:02 | POST HOC |
| 19 | v2 production | `results/v2_sweep/` (360), `results/v2_kiyohara/` (6), `results/loco_v2/` (30) | v2 (`configs/tuned_v2.yaml`) | freeze and production row 2026-10-09 16:24 | 2026-10-09 17:02 | POST HOC |

Counts over the 19 groups: PRE-REGISTERED 4 (#1, #3, #8, #10); POST HOC 9 (#2, #5, #6, #7, #9, #11,
#17, #18, #19); EXTENSION 6 (#4, #12, #13, #14, #15, #16).

For every group, the rows of his that set its design were committed before its first run record. The
v2 arm's design screen, selection rule, tuning and freeze each preceded the next step.

## Why v2 is POST HOC at the level of model choice

The v2 deviation row (committed 2026-10-08 16:55) gives its reason as "the review of 2026-10-07 found that
the S results at B <= 200 measure a site-blind network". It cites `docs/diagnostics_sweep.md` item 1. That
item's numbers come from `scripts/diagnostics_sweep.py`, which reads the committed sweep predictions. Those
predictions are the test-site predictions of the pre-registered S and D (`results/diagnostics_sweep.json`,
2026-10-08 02:40). The diagnostics behind them are: constant predictions within hosts, within-host spread,
and within-host skill per budget. On main, the same pattern was recorded by the G1 diagnostics
(`results/g1_diagnostics.json`, 08:55) and by the S10b site-resolution check (`results/
s_site_resolution_forensic.json`, 13:40). Both used test hosts, and both predate his v2 row. His branch,
forked at 00:15, does not contain them. The decision to build a second backbone therefore followed test-set
diagnostics of v1, and v2 is labelled POST HOC whatever the later steps did.

The later steps never loaded test hosts, verified from code and payloads:

- **Design screen.** All 36 `results/v2_screen/` records have `spec.eval_test = False`,
  `n_hosts.test = 0` and 0 prediction rows. In `train_run`, `eval_test = False` makes the test-host list
  empty (`src/dftgnn/train/__init__.py`, the split block). The queue worker's graph store holds every host's
  graph in memory, as it does for every run, but no test host enters training, validation or prediction.
- **Retuning.** `scripts/tune/run_study.py` builds a `TuningStore(resample=0)`, which sets resample 0's
  test-host graphs to None, sets their targets and descriptors to NaN, and raises if any test host is
  requested. Trials are built with `eval_test = False` (`trial_spec`). All six study records report
  `test_hosts_loaded: false` and 30 COMPLETE trials.
- **Selection.** The selection used mean validation MAE over the anchors (0.492 pre-registered, 0.382 init,
  0.489 local, 0.419 init_local; his row of 2026-10-08 recording the outcome). It was committed
  2026-10-09 00:36, after the screen and before any tuning record (first 03:02).

## Ambiguities

1. **G1 primary (#1).** The §7 rule predates every result. The detailed clarifications on main
   (2026-10-08 08:49) and his N* reporting rules (2026-10-09 16:55) were committed after the sweep test
   predictions existed. The S09 completeness record (single-seed mean test MAE per model and budget,
   06:52) and his diagnostics (A at B = 654 on the ensemble, 02:40) also came first. Neither changes a
   number: the recomputation is exact. The label stays PRE-REGISTERED; the timing should be disclosed.
2. **LOCO (#3).** The folds equal `splits/loco_v1.json`. His validation carve-out seeds `val_split` with
   r = k. Our 2026-10-10 clarification, committed 2026-10-09 18:42 after his runs, uses r = "loco{k}". His
   30 runs are therefore pre-registered in design, but they are not the runs our clarified rule specifies.
   Which set is the registered LOCO result is the author's choice.
3. **MLIP relaxations (#8).** The relaxation settings are those of §9, and they match our 2026-10-10
   clarification. The tiling and atom mapping were not logged in a deviations row on his side: 0.05 Å
   tolerance, shifted-origin recovery, 9 hosts excluded. Our clarification and tiling rule were committed
   2026-10-09 18:42, three minutes after his relaxations were committed (18:39), on a separate branch. The
   two host sets differ (797 vs 809; `docs/ingest_report.md` row 24). No backbone is involved.
4. **D-late (#13).** His row calls it a DEVIATION adding a sensitivity analysis, motivated by the D-variant
   tie in tuning (validation data). It was committed after the sweep test predictions existed.
   EXTENSION is assigned because the compute is new; it could also be read as POST HOC.
5. **Screening (#10, #11).** One record holds both a pre-registered value and a post-hoc value. They are
   labelled separately.
6. **Staging (#6).** Besides the backbone, two choices are post hoc: P1-v2 reuses P1's v1 tuned values
   without re-tuning, and the §8 null sentence is replaced by a TOST rule. The TOST rule was logged before
   any P evaluation.
7. **C0 tuning-overlap check (#16).** It uses no new compute, only a new analysis of existing official
   predictions. EXTENSION is used for "beyond the plan".
8. **Epoch-cap statements.** His "the cap does not bind" (diagnostics item 6) restates the pre-registered
   capsens result (rule 2026-10-07, results 2026-10-08). It is not a separate group. The post-hoc capped
   reruns logged on main (2026-10-08 09:16 and 2026-10-10) have no counterpart on his branch.

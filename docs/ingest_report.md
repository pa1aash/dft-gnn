# Ingest report: collaborator NRP analysis branch (M1)

Audit of the analysis branch `origin/review-diagnostics` (tip `f658823`) and the four provenance branches
pushed by the collaborator (Aiden Lee, commit identity `aidenlee <aiden.lee.sd@gmail.com>`), against `main`
at `e6d1a84`. Audited from a read-only detached worktree; none of his code was run except his own test
suite (read-only, no data). Every recomputed number is in `results/ingest_m1_recompute.json`, written by
`scripts/analysis/ingest_m1_recompute.py` from a clean tree. That script uses our G1 estimator
(`dftgnn.stats.g1`: seed-ensemble mean, paired hierarchical bootstrap, 2000 replicates, seed 20261008). It
reads his stored prediction files only after checking each against the sha256 in its run record. The record
lists all 2003 inputs with their sha256.

**Outcome: merge not performed.** Hygiene is clean (one identity, no banned strings, every recorded hash
verifies). The trial merge conflicts in three code files that affect v1 behaviour or v1 inputs:
`src/dftgnn/train/__init__.py`, `src/dftgnn/train/stages.py` and `scripts/make_loco_splits.py`. Those are
outside the conflicts this session was authorised to resolve, so the merge was aborted and `main` was left
untouched.

Status convention in §4. MATCH: the point estimate is identical to his (to 1e-9 for every estimate
recomputed from his prediction files), and so is every decision that depends on it (below or above δ, N*,
outcome category). Intervals differ only because the bootstrap generators differ: his use seed 0 with
`dftgnn.stats.metrics._draw_weights`, ours seed 20261008 with `HierDraws`. The largest such difference is
quoted. MISMATCH: a point value, a count or a definition differs. UNVERIFIABLE: the inputs needed to
recompute are not in git (checkpoints, embeddings, predictions under MLIP geometry, scheduler logs).

## 1. Branch inventory

All five branches fork from `main` at `9ec3af5` (2026-10-08 00:15 UTC, the epoch-cap sensitivity commit).
`main` is 74 commits ahead of that point. `origin/main` equals local `main` (`e6d1a84`). Tags `prereg-v1`
(`dd730b8`), `tuned-v1` (`c0ac0b5`) and `g1-v1` (`8a19d34`) are identical on origin and locally.

| branch | role | tip | commits ahead of main | first, last commit (UTC) | tracked files / size at tip | directories touched (files) |
|---|---|---|---:|---|---|---|
| review-diagnostics | analysis | f658823 | 64 | 2026-10-08 02:39, 2026-10-10 05:29 | 3080 / 106.6 MiB | results (1997: v2_sweep 720, p_v2 366, p1_v2 366, dlate 180, v2_screen 72, diag_cross 72, loco 60, loco_v2 60, d_ablation 54, tuning 18, v2_kiyohara 12, mlip 4, predictions 2, 11 top-level), scripts (35, of which scripts/nrp 18), src/dftgnn (7), tests (8), splits/loco (6), figures/main (3), docs (4), configs (2), .gitattributes |
| ckpt-fix | provenance | e6b7e33 | 3 | 2026-10-08 02:39, 19:37 | 1044 / 41.5 MiB | scripts/diag_checkpoints.py (+ shared base) |
| tune-v2 | provenance | 738d5ad | 7 | 2026-10-08 02:39, 2026-10-09 00:36 | 1344 / 47.6 MiB | tuning code and config for v2 (+ shared base) |
| prod-v2 | provenance | 1f3a136 | 9 | 2026-10-08 02:39, 2026-10-09 16:24 | 1349 / 47.6 MiB | v2 freeze, production stage, NRP watchdog (+ shared base) |
| mlip-run | provenance | 96c4ef4 | 6 | 2026-10-08 02:39, 2026-10-09 18:01 | 1047 / 41.5 MiB | MLIP preparation and relaxation code (+ shared base) |

The diff of the analysis branch against the merge base covers 2062 files (+1,215,603 / −29 lines). He
modified no existing result file. He modified 18 existing files: `configs/config.yaml`, `docs/claims.yaml`,
`docs/deviations.md`, `scripts/queue/enqueue.py`, `scripts/tune/run_study.py`, `src/dftgnn/{config,
mlip/__init__, models/__init__, probe/__init__, train/__init__, train/stages, tune/__init__}.py` and six test
files.

### Provenance branches (kept as remote refs, not merged)

Every unique commit on the four provenance branches is patch-equivalent to a commit on the analysis branch
(`git cherry`: all "−"). The branches exist because result records name their code SHAs, and three of those
SHAs are reachable only from these branches:

| branch | unique commits (not on review-diagnostics) | recorded SHA reachable only here | records naming it |
|---|---|---|---|
| ckpt-fix | e6b7e33 fix(diag_checkpoints): disable cuDNN for the gradient probe | e6b7e33 (also on mlip-run) | `results/diag_checkpoints.json` |
| tune-v2 | 738d5ad feat(tune): tune the v2 backbone | 738d5ad (also on prod-v2) | 12 fields in the six v2 tuning records |
| prod-v2 | 738d5ad, 8bbd2f3 feat(v2): production stage, 1f3a136 feat(config): freeze v2 tuned hyperparameters | 1f3a136 | 1524 fields: every v2_sweep, v2_kiyohara, loco_v2, p1_v2 and p_v2 record |
| mlip-run | e6b7e33, 620f4a0 / 0faf85a / 96c4ef4 feat(mlip): tiling, shifted-origin recovery, sharded relaxation | none (the relaxation shards carry no code SHA) | — |

Every other recorded SHA (`656b1d6`, `d58b1cc`, `93a2830`, `3e2815d`, `3ae2274`, `063ed64`, `38cf715`,
`6952e9f`, `4987ef8`, `2af8133`) is on the analysis branch. If the analysis branch is ever merged, these
four refs must stay on origin, or `1f3a136`, `738d5ad` and `e6b7e33` must be tagged, for the records to stay
resolvable.

## 2. Hygiene (blocking checks)

| check | result |
|---|---|
| author and committer identities, all 71 unique commits on the five branches | one identity, `aidenlee <aiden.lee.sd@gmail.com>`, as both author and committer on every commit; no other identity |
| banned pattern (the three project-banned strings of the local hooks, case-insensitive) in commit messages | 0 hits |
| banned pattern in every tracked file at each of the five tips, text and binary, and in paths | 0 hits |
| banned pattern in any added or removed line of any commit on the branches | 0 hits |
| `git notes` | none |
| secrets (cloud keys, tokens, private keys, passwords, kubeconfig, .env, credential files) | none found |
| absolute personal paths (`/Users/`, `/home/`, `/root/`) in tracked text | none |
| other personal metadata | result records carry `hostname`: his laptop (`Aidens-MacBook-Air.local`) on 11 analysis records, NRP pod names on run records; `scripts/nrp/*.yaml` name the NRP namespace `cms-ml` and node `hcc-nrp-shor-c6017.unl.edu`; not secrets |
| files over 5 MB added by him | none (largest blob he added: 0.30 MB, `results/probe_v2_sweep.json`; the two > 5 MB files at his tip, `data/MANIFEST.sha256` and `results/data_inventory.json`, are ours from before the fork) |
| recorded prediction hashes | 981 of 981 run records verify (`pred sha256 == record`); the 2 LOCO baseline prediction files verify; `git_dirty` is false on every record |
| local audit hook with both identities allowed | all five branches pass `.git/hooks/_audit.sh` over their full history |

No blocking hygiene finding. Nothing needs remediating on his side before a merge.

### Where large artefacts live

| artefact | location | hash recorded |
|---|---|---|
| test predictions of every run (parquet) | in git, beside each record | yes, sha256 in each record; all verified |
| result records (JSON), tuning studies (Optuna db, trials CSV) | in git | db/CSV in the tuning record's `artefacts` |
| MLIP relaxed unit cells | in git, `results/mlip/relaxed_shard{0-3}.json.gz` (0.8 MiB) | input file sha256 `76bae07e…` in `results/mlip_inputs.json`; shards themselves not hashed in a record |
| MLIP inputs (tiled unit cells) | NRP only (`data/processed/mlip_inputs.json.gz`, gitignored) | sha256 recorded |
| checkpoints (diag_cross, d_ablation, dlate, loco, v2_screen, v2_sweep, v2_kiyohara, loco_v2, p1_v2; 798 runs) | NRP storage only (`checkpoints/`, gitignored) | sha256 in each run record; not verifiable here |
| P-v2 | no checkpoint (composition of P1-v2 and D-v2) | component run ids recorded |
| probe embeddings (S-v2 readout vectors), predictions under MLIP / rescaled geometry | NRP only | not recorded |

## 3. Code differences and v1 behaviour

Changes to `src/` and `scripts/` relative to the merge base:

| module | change | can v1 outputs change? |
|---|---|---|
| `models/__init__.py` | `HParams.init` ("default" or "kaiming"), `HParams.local_readout`; Kaiming re-initialisation and a local-environment readout branch, each only when set | No: with the defaults no module is added, no extra random draw is made and the readout is unchanged; v1 tuned values (`configs/tuned_v1.yaml`) carry neither key |
| `train/__init__.py` | `apply_ablation` (vacancy_flag, desc_host, desc_site); `val_metrics` from an extra validation pass after the best weights are restored | No: ablation is None for v1; the extra pass is in eval mode under `no_grad` with unshuffled batches, after training, so test predictions are unaffected |
| `train/stages.py` | new builders (diag_cross, d_ablation, dlate, review, loco, v2_screen, v2, p_v2); `tuned_hparams` merges `tuned["arch"]` | No: `tuned_v1.yaml` has no `arch`; existing builders unchanged |
| `tune/__init__.py`, `scripts/tune/run_study.py` | fixed `arch` options per trial; `v2_` study prefix | No: `arch` defaults to None |
| `config.py`, `configs/config.yaml` | new required sections `diagnostics`, `v2`; optional `analysis.equivalence_*`, `sensitivity.unselected_variant_sweep` | No numeric v1 value changes; written records' `config` dump gains keys. `check_prereg` keys untouched |
| `mlip/__init__.py`, `probe/__init__.py` | new tiling/geometry/relaxation helpers; probe helpers | Not used by v1 training or the G1 analysis |
| `scripts/queue/enqueue.py` | `--code` override; new stage dispatch | No for existing stages |
| `scripts/make_loco_splits.py` (new on both sides) | his writes `splits/loco/loco_f<k>.json` + own manifest; ours writes `splits/loco_v1.json` and appends to `splits/MANIFEST.sha256` | Affects which LOCO split files exist; folds are identical (§4) |

Manifests: his records carry graph-store manifest sha256 `be5e5cfd…` in all 1038 such fields, equal to the
sha256 of our `data/graphs_v1_manifest.sha256`, whose tracked blob is identical on both sides (`c4fbb8a`).
`data/MANIFEST.sha256` and `data/universe_v1_ids.csv` are identical blobs. His `splits/MANIFEST.sha256`
is the frozen file (sha256 `dd0986ef…`, as in ANALYSIS_PLAN §2). Ours differs from it only by the appended
`loco_v1.json` line (S11). `splits/outer_r*.json` and `kiyohara.json` are identical.

His test suite, run read-only in the ingest worktree with his `src/` on the path and no caches written:
167 passed, 46 skipped (tests that need the gitignored data store), 1 xfailed. The worktree was unchanged
afterwards.

## 4. Claim-by-claim reconciliation

Our recomputation is from `results/ingest_m1_recompute.json` unless another file is named. Energies are in
eV; intervals are two-sided 95%.

| # | claim | his number | his source | our recomputation | status |
|---|---|---|---|---|---|
| 1 | universe rebuilt bit-identically | stated | `docs/diagnostics_sweep.md` §1 | no hash of a rebuilt universe file is recorded; tracked `universe_v1_ids.csv` identical | UNVERIFIABLE |
| 2 | graph store rebuilt bit-identically | manifest sha256 `be5e5cfd…` in every run record | run records | equals ours (`data/graphs_v1_manifest.sha256`) | MATCH |
| 3 | splits unchanged | `splits/MANIFEST.sha256` = `dd0986ef…` | branch tip | equals the frozen manifest; outer and Kiyohara splits identical | MATCH |
| 4 | G1 v1: A per budget 25…654 | +0.098, +0.032, +0.108, +0.095, +0.040, −0.012 | `results/c1c2_v1.json` | identical points (max abs diff 0.0); our recomputation from his copies of the 360 prediction files (all byte-identical to main) equals `results/g1_primary.json` exactly | MATCH |
| 5 | G1 v1: one-sided upper bounds | +0.188, +0.100, +0.171, +0.133, +0.067, +0.010 | `results/c1c2_v1.json` | +0.189, +0.097, +0.168, +0.132, +0.067, +0.009 (max diff 0.0035, bootstrap generator); same side of δ at every budget | MATCH |
| 6 | N* (v1) | 654, "reached only at the maximum budget" | `results/c1c2_v1.json` | 654 | MATCH |
| 7 | C2 ceiling (v1) | −0.012 [−0.036, +0.014] | `results/c1c2_v1.json` | −0.012 [−0.035, +0.014] (endpoints differ ≤ 0.0008) | MATCH |
| 8 | G1 v2 arm: A per budget, N*, C2 | A −0.142, −0.509, +0.083, +0.024, +0.054, +0.015; N* 654 (200 qualifies, 400 does not); C2 +0.015 [−0.008, +0.036] | `results/c1c2_v2.json` | identical points; upper bounds +0.211, +0.241, +0.156, +0.047, +0.075, +0.033 (his +0.206, +0.246, +0.160, +0.048, +0.075, +0.033); N* 654; C2 +0.015 [−0.008, +0.037]. Largest interval-endpoint difference 0.052 at B = 50, where the interval spans 2.1 eV | MATCH |
| 9 | 363 S and D sweep runs | 363 | branch records | his tree holds 363 top-level S and D-state records, byte-identical to main: 360 outer-resample runs and the 3 Kiyohara-split D runs. The 3 official C0 runs (`results/c0_official/`) are the Kiyohara-split S runs, so our count "360 plus 3 official C0" counts the same Kiyohara slot with the S model; his 363 counts it with the D model | MATCH (same files) |
| 10 | 396 v2 production runs | 396 | `results/v2_sweep`, `v2_kiyohara`, `loco_v2` | 360 + 6 + 30 records; 132 cells, each with seeds 0–2; unique run ids | MATCH |
| 11 | 183 P1-v2 | 183 | `results/p1_v2` | 183 records, 61 cells × 3 seeds (60 outer + Kiyohara) | MATCH |
| 12 | 183 P-v2 | 183 | `results/p_v2` | 183 records, 61 cells × 3 seeds | MATCH |
| 13 | 153 diagnostics | 36 crossing + 27 ablation + 90 D-late | `results/diag_cross`, `d_ablation`, `dlate` | 36 + 27 + 90 records; all cells have 3 seeds | MATCH |
| 14 | gradient and permutation analyses of checkpoints | values in `results/diag_checkpoints.json` | same | checkpoints are on NRP only | UNVERIFIABLE |
| 15 | 30 LOCO runs | 30 | `results/loco` | 30 records, 5 folds × {S, D} × 3 seeds | MATCH |
| 16 | LOCO folds vs `splits/loco_v1.json` | 131 families, 5 folds | `splits/loco/loco_f<k>.json` | per fold the test hosts, training hosts and families are identical to ours (164/654, 164/654, 164/654, 163/655, 163/655; 26, 26, 27, 26, 26 families) | MATCH |
| 17 | LOCO validation carve-out | `val_split` seeded with r = k, B = training size | his deviations row 2026-10-08 §11, `src/dftgnn/train/__init__.py` | our clarification (2026-10-10 §11) seeds with r = "loco{k}"; the seeds differ, so his validation hosts are not those our rule specifies | MISMATCH |
| 18 | LOCO A (v1) | +0.008 [−0.015, +0.031], upper 0.027 | `results/c1c2_v1.json` | +0.008 [−0.015, +0.031], upper 0.027 (pooled 818 hosts, host bootstrap) | MATCH |
| 19 | S beats RF-Kumagai on unseen chemistry by 0.10 eV | S − RF = −0.101 [−0.129, −0.074]; S 0.313, RF 0.414 | `docs/diagnostics_sweep.md` (prose only; no result record holds the contrast) | −0.101 [−0.129, −0.076]; S 0.313, RF 0.414 (RF predictions hash-verified against `results/loco_baselines.json`) | MATCH |
| 20 | LOCO A (v2) | +0.041 [+0.016, +0.066], upper 0.061 | `results/c1c2_v2.json` | +0.041 [+0.018, +0.064], upper 0.061 | MATCH |
| 21 | 36-run v2 design screen, validation only | 36 runs, test hosts never loaded | `results/v2_screen`, deviations 2026-10-08 | 36 records, all `eval_test = False`, 0 test hosts, 0 prediction rows; with `eval_test = False` the code sets the test-host list to empty | MATCH |
| 22 | v2 re-tuned in 6 studies | 6 × 30 trials | `results/tuning/tuning_v2_*.json` | 6 studies, 30 COMPLETE each, `test_hosts_loaded: false`; `run_study.py` uses `TuningStore`, which removes resample 0's test-host graphs and targets and raises if one is requested | MATCH |
| 23 | MLIP: 809 unit cells relaxed | 809 | `results/mlip/relaxed_shard*.json.gz`, `results/mlip_inputs.json` | 809 hosts in the shards | MATCH |
| 24 | MLIP host set vs our tiling map | 809 mapped, 9 excluded | `results/mlip_inputs.json` | ours: 797 ok, 21 failed (one-operation extension → 818). 809 = 797 + 13 − 1. +13: our inversion-class failures (Ba2MgGe2O7, Ba2ZnGe2O7, Sr2ZnSi2O7, NaBi(MoO4)2, Ba2CdGe2O7, NaLa(MoO4)2, Sr2ZnGe2O7, La2Be2GeO7, Y2Be2GeO7, Sr2MgSi2O7, Y2Be2SiO7, Ba2MgSi2O7, Sr2MgGe2O7), which he mapped with shifted-origin matching at 0.05 Å. −1: Sr2SnO4, ok in ours, excluded in his. His other 8 exclusions are exactly our 8 two-fold-rotation failures (NaNbO3, Ba2Cd(BO2)6, CaSn(BO3)2, NaBiO3, TiNb3O6, MgTiO3, CaSnO3, Li8SnO6). The 9 hosts with unassigned oxidation states (RbAuO, B6O, Na3AuO2, Rb5Au3O2, RbNa2AuO2, CsK2AuO2, KNa2AuO2, CdAuO2, CsAuO) are all in his relaxed set and none is excluded, so they play no part in the difference | MISMATCH (host set; explained host by host) |
| 25 | MLIP: 802 converged | 802 | shards | 802 converged; not converged: KLa(MoO4)2, KAsO2, LiBO2, MgV2O6, CuAsPbO4, CsBO2, Cs3AlO3 | MATCH |
| 26 | MLIP relaxation protocol | MACE-MP-0 medium, mace 0.3.16, float64, FIRE on FrechetCellFilter, fmax 0.01, 500 steps | shard `meta` | same as ANALYSIS_PLAN §9 and our 2026-10-10 clarification | MATCH |
| 27 | MLIP changes predictions by at most 0.003 eV | ≤ 0.003 | `results/mlip_eval_v2.json` | recorded max abs dMAE 0.0033 (P, B = 654, MLIP geometry); the predictions under MLIP and rescaled geometry, and the v2 checkpoints, are not in git | UNVERIFIABLE |
| 28 | backbone of the geometry evaluation | v2 (S-v2, D-v2, P-v2 at B = 654 and 200) | deviations 2026-10-09, `scripts/mlip_eval.py` | v2; no v1 geometry evaluation exists | MATCH |
| 29 | MLIP d-electron strata | d0 249, d10 86, other 388 (723 hosts) | `results/mlip_eval_v2.json` | our bins on the same 723 hosts (converged and tested at least once): d0 274, d10 384, other 57, unassigned 8. His `d_class` uses `oxi_state_guesses` only, counts only d-block cations, and puts hosts without a d-block cation or without a guess in "other"; ours follows the 2026-10-10 clarification | MISMATCH (definition) |
| 30 | MLIP null-rule geometry (median internal RMSD 0.024 Å > 0.01 Å) | 0.024 | `results/mlip_eval_v2.json` | not recomputed this session (needs the geometry module run on his shards and the gitignored inputs) | UNVERIFIABLE |
| 31 | epoch cap: capsens rule | ΔA = 0, 18 pairs bit-identical | `docs/diagnostics_sweep.md` §6 | `results/g1_cap_sensitivity.json`: A(600) − A(200) = 0.000 | MATCH |
| 32 | "the epoch cap never binds" | does not bind | `docs/diagnostics_sweep.md` summary item 6 | in our sweep records the cap was reached by 8 of 30 S runs at B = 654 (r0 s0, r2 s0, r5 s0, r5 s2, r6 s0, r7 s2, r9 s0, r9 s2) and 2 D runs (r1 s1, r6 s0); his §6 lists the same 10. Totals at the cap in our v1 sweep: S 1/5/8 at B = 25/400/654; D 5/1/1/1/2 at B = 25/50/100/200/654. In his own runs: v2_sweep 5/360, v2_kiyohara 1/6, p1_v2 34/183, loco 5/30, diag_cross 6/36, d_ablation 2/27, dlate 3/90, v2_screen 3/36; v2 tuning trials at the cap: S a654 5, S a50 1, D-state a200 1 | MISMATCH (true of ΔA in capsens, not of epochs run) |
| 33 | epochs run, runs both of us have | — | `results/diag_cross` (S, B = 654, a654 values, r0–2, s0–2), `results/d_ablation` (D-state, no ablation, B = 654, r0–2, s0–2) vs our sweep twins | 18 twins; hyperparameters (hp, lr, weight decay, batch size) identical in all 18. epochs_run equal in 2 of 18 (S r0 s0 and S r2 s0, both 200). Per twin, his/ours epochs_run: S r0 s0 200/200, r0 s1 142/195, r0 s2 173/105, r1 s0 200/158, r1 s1 200/72, r1 s2 200/164, r2 s0 200/200, r2 s1 200/184, r2 s2 172/167; D r0 s0 153/151, r0 s1 157/155, r0 s2 83/55, r1 s0 101/135, r1 s1 42/200, r1 s2 60/86, r2 s0 73/70, r2 s1 120/106, r2 s2 80/95. They differ in code SHA (d58b1cc vs the sweep's) and GPU type (NRP cards vs L40S). The 363 shared records are byte-identical | MISMATCH (run by run) |
| 34 | tuning overlap did not flatter C0 | 97 of 126 Kiyohara test hosts in a tuning set; on the other 29 (68 sites) S 0.285 [0.191, 0.401]; on the 97, 0.282 | `docs/diagnostics_sweep.md` §8, `results/diagnostics_sweep.json` | 29 hosts / 68 sites: 0.285 [0.192, 0.403]; 97 hosts: 0.282 [0.233, 0.333]; all: 0.283 | MATCH |
| 35 | faulty GPU node failed 8 runs | 8 reruns | commit 694224d, `scripts/nrp/worker-job.yaml` | node `hcc-nrp-shor-c6017.unl.edu` (NVIDIA A10, CUDA illegal-address errors, 2026-10-08), excluded by node affinity from then on. The 8 reruns: diag_cross 3114048400697597, 5635e81a8f9183e4, 814e08c4cfedc889 (S, r2, B = 654, s2/s0/s1; pod zh7mj); dlate 65e27140190f1c39, d1ce5ca488f8ec50, d297e74451e71c16, e3289c3cd549e6e4, f1e39c857335b469 (pods gdp5z, zh7mj). Count 8 confirmed | MATCH (count) |
| 36 | no other run from that node is in his results | not stated | — | the other 145 review-stage runs ran on pods bcnd4 (48), hzcnt (47) and k9l7j (50); records carry the pod name only, and the repository holds no pod-to-node log, so whether any of them ran on that node is not established. Nothing on the branch rules it out | UNVERIFIABLE |
| 37 | staging never beats end-to-end (C3a) | P − S: inconclusive at 25; P worse at 50, 100, 200; equivalent at 400; P worse within the margin at 654 | `results/c3a_v2.json` | P − S +0.044 [−0.010, +0.094], +0.123 [+0.045, +0.195], +0.066 [+0.010, +0.127], +0.119 [+0.089, +0.147], +0.024 [−0.005, +0.051], +0.028 [+0.008, +0.053]; no budget has an interval below 0; his four-outcome categories reproduce at every budget with our draws | MATCH |
| 38 | D − P (C3a) | −0.149, −0.142, −0.077, −0.043 at 100–654 | `results/c3a_v2.json` | identical points | MATCH |
| 39 | staging backbone | v2 | deviations 2026-10-09 | v2; no v1 P evaluation exists (the 183 v1 P1 runs and their checkpoints are on main) | MATCH |
| 40 | probe fails its control rule (C4) | ρ 0.975 [0.963, 0.986]; trained − untrained −0.032, −0.031, −0.003 at 200, 400, 654 | `results/probe_v2_sweep.json` | recomputed from his stored per-run class-mean R²: ρ 0.975; trained − untrained −0.032, −0.031, −0.003; trained − shuffled +0.348, +0.494, +0.599; identical to his values | MATCH (rule applied to stored R²) |
| 41 | probe R² values themselves | 60 S-v2 checkpoints, ridge with grouped CV | `results/probe_v2_sweep.json` | embeddings and checkpoints are on NRP only | UNVERIFIABLE |
| 42 | probe backbone | S-v2 | deviations 2026-10-09 | v2; no v1 probe exists (v1 S checkpoints are on main) | MATCH |
| 43 | screening demo: MAE 0.294 eV, 10 sites, 7 oxides | 0.294; ZnO, TiO2, SnO2, MgO, Al2O3, ZrO2, Ga2O3 | `results/screening_c5.json` | 0.294 on the same 10 sites of the same 7 hosts; the same 8 candidates absent from universe v1 | MATCH |
| 44 | screening backbone | pre-registered S at B = 654 (S-v2 0.420 reported beside it) | `results/screening_c5.json` | v1: 0.294; S-v2: 0.420 | MATCH |
| 45 | D-late and ablation outputs: location and design timing | 90 + 27 runs | `results/dlate`, `results/d_ablation` | records and test predictions in git (hash-verified), checkpoints on NRP only. Design rows committed 2026-10-08 02:39 UTC; first run record 03:31 UTC (ablation) and 07:43 UTC (D-late), all built against d58b1cc (02:40 UTC) | MATCH (logged before the runs) |

Counts over the 45 rows: MATCH 34; MISMATCH 5 (#17, #24, #29, #32, #33); UNVERIFIABLE 6 (#1, #14, #27,
#30, #36, #41).

### Points the table does not settle

- Our G1 numbers, including the 2026-10-08 clarifications, are reproduced exactly from his files. His
  reporting rules for N* (deviation row 2026-10-09 §7, rules (a)–(d)) were committed 2026-10-09 16:55 UTC.
  His sweep diagnostics had already computed A at B = 654 on the seed ensemble (2026-10-08 02:40 UTC). The
  rules do not change any number.
- His deviations table carries rows that conflict with rows on main: LOCO validation seeding (#17), and
  the staging null sentence of §8 (withdrawn on his side in favour of a TOST rule with δ_P = 0.05 eV; kept
  on main). A union of the two tables would hold both versions.
- His `docs/claims.yaml` marks C3a, C3b, C4 and C5 as measured on the v2 arm. On main they are planned.

## 5. Merge attempt

On `merge/aiden-analysis` from `main`, `git merge --no-ff origin/review-diagnostics` stopped with five
conflicts:

| file | kind | content of the conflict |
|---|---|---|
| `docs/claims.yaml` | content | statuses and result refs (text; resolvable by the union rule) |
| `docs/deviations.md` | content | both sides appended rows after 2026-10-07 (text; resolvable by the union rule) |
| `scripts/make_loco_splits.py` | add/add | two different LOCO split generators (ours → `splits/loco_v1.json`; his → `splits/loco/`) |
| `src/dftgnn/train/__init__.py` | content | `TRAINED` (ours adds cgcnn-S/cgcnn-D and `LOCO_PREFIX`; his adds `ABLATIONS` and `apply_ablation`) |
| `src/dftgnn/train/stages.py` | content | the `STAGES` tuple (ours adds the S12 stages; his adds the review and v2 stages) |

The three code conflicts are in the training loop, the stage registry and the LOCO split generator. All
three affect v1 runs or v1 inputs. Under this session's rules only `docs/deviations.md` and
`docs/claims.yaml` may be resolved, so the merge was aborted. `merge/aiden-analysis` was deleted (it had no
commits), `main` is unchanged at `e6d1a84`, and nothing was pushed. Both code hunks are additive on each
side (registry entries and one helper), but resolving them means writing code in a merge commit. That is
for the author to decide (`handoff/M1.md`, NEEDS PALAASH).

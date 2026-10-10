# Gap list after the M1 ingest

For each analysis: whether a v1 version (the registered backbone, `tuned-v1`) exists, whether a v2 version
(the collaborator's post-hoc backbone, `configs/tuned_v2.yaml` on `origin/review-diagnostics`) exists, both
or neither, with file pointers. "His" files are on `origin/review-diagnostics` (tip `f658823`) and are not
on main. The collaborator branch is not merged (`docs/ingest_report.md` §5). Nothing was run to fill a gap.
The last column names the S12 stage on main that would produce the missing v1 version
(`src/dftgnn/train/s12.py`, job counts as built in S11). Labels follow `docs/provenance_labels.md`.

| analysis | v1 | v2 | exists | v1 pointers | v2 pointers | missing v1 work (S12 stage, jobs) |
|---|---|---|---|---|---|---|
| C1 (A per budget, N*) | yes | yes | both | main `results/g1_primary.json`, `results/g1_within_host.json`, `docs/g1_notes.md`; his `results/c1c2_v1.json` (identical point values) | his `results/c1c2_v2.json`; recomputed in `results/ingest_m1_recompute.json` (`v2_arm`) | none |
| C2 (A at B = 654) | yes | yes | both | as C1 (`c2_ceiling`) | as C1 | none |
| C3a (staging P vs S, D − P) | no | yes | v2 only | inputs on main: 183 P1 runs (180 outer + 3 Kiyohara; top-level `results/*.json` with model P1) and the D-state runs, checkpoints local and listed in `results/checkpoint_manifest.json`; pairing rule: deviations 2026-10-10 §8 | his `results/p1_v2/` (183), `results/p_v2/` (183), `results/c3a_v2.json` | `peval`, 183 |
| C3b (MLIP geometry robustness) | no | yes | v2 only | main tiling map `data/tiling_summary_v1.csv` (797 ok, 21 failed), MACE identity `results/mace_model.json`, relaxation protocol (deviations 2026-10-10 §9); no v1 relaxations or condition predictions | his `results/mlip/relaxed_shard{0-3}.json.gz` (809 relaxed, 802 converged; backbone-independent, different tiling rule), `results/mlip_inputs.json`, `results/mlip_eval_v2.json` | `relax`, 818; `geomeval`, 180 (B = 654 and 200 as a descriptive extra) |
| C4 (latent probe) | no | yes | v2 only | v1 S checkpoints, seed 0, all 60 (r, B), local (`results/checkpoint_manifest.json`); embedding rule: deviations 2026-10-10 §10 | his `results/probe_v2_sweep.json` (embeddings on NRP only) | `embed`, 240; probe fit (S13) |
| LOCO (§11) | yes, with caveat | yes | both | his `results/loco/` (30 runs, v1, a654 values; folds identical to `splits/loco_v1.json`, validation seeds per his rule r = k, not our r = "loco{k}"); A in his `results/c1c2_v1.json`; main `splits/loco_v1.json` | his `results/loco_v2/` (30), A in `results/c1c2_v2.json` | `loco`, 30, under our validation-seed rule, only if his 30 runs are not accepted as the registered LOCO (author's decision) |
| LOCO baselines (B0, RF-Kumagai on the folds) | yes | n/a | v1 only (EXTENSION) | his `results/loco_baselines.json`, `results/predictions/loco_{b0_physics_floor,rf_kumagai}.parquet` | — | none |
| Sensitivity (a): high defect moment excluded | no | no | neither | rule: deviations 2026-10-10 §12; config `sensitivity.exclude_high_moment` | — | `moment`, 60 |
| Sensitivity (b): Kiyohara split, S, D, P | S and D yes; P no | S, D, P yes | both for S and D; P v2 only | main `results/c0_official.json` and `results/c0_official/` (S), the 3 Kiyohara D-state records in `results/`, 3 Kiyohara P1 records (P evaluation not run) | his `results/v2_kiyohara/` (6), the 3 Kiyohara records in `results/p_v2/` | P on the Kiyohara split is part of `peval` (3 of 183) |
| Sensitivity (c): CGCNN cross-check | no | no | neither | `src/dftgnn/models/cgcnn.py`, rule: deviations 2026-10-10 §12; smoke only (`results/smoke/`, excluded from analysis) | — | `cgcnn`, 18 |
| Sensitivity (d): unselected injection variant D-late | yes (tuning runs, as registered); sweep-protocol D-late is EXTENSION | no | v1 only | main `results/tuning/` (D-late studies); his `results/dlate/` (90 runs at B = 200, 400, 654; EXTENSION) | — | none |
| Epoch-cap sensitivity (pre-registered, B = 654, r0–2) | yes | no | v1 only | main `results/g1_cap_sensitivity.json`, `results/capsens/` | — | none |
| Capped reruns (POST HOC, 600-epoch twins of every capped run) | no | no | neither | spec `scripts/queue/capped_rerun_v1.json`; rule: deviations 2026-10-08 and 2026-10-10 §5 | — (5 v2 sweep runs and 34 P1-v2 runs also reached the cap, `docs/ingest_report.md` row 32) | `capped`, 33 |
| Screening (C5) | yes | yes | both | his `results/screening_c5.json` (`mae_S` 0.294 eV from the v1 sweep S at B = 654; recomputed in `results/ingest_m1_recompute.json`, `screening`); main `results/screening_absence.json` | his `results/screening_c5.json` (`mae_S_v2` 0.420 eV) | none |
| Diagnostics: budget × tuned-setting crossing, descriptor ablation, checkpoint gradients and permutations | yes | n/a | v1 only (EXTENSION) | his `results/diag_cross/` (36), `results/d_ablation/` (27), `results/diag_checkpoints.json`, `docs/diagnostics_sweep.md` | — | none |

## Summary for the cluster stage lists

- **v1 work still to run** (all built on main in S11, none run):
  - `peval` 183, which covers C3a and P on the Kiyohara split;
  - `relax` 818 and `geomeval` 180, which cover C3b;
  - `embed` 240 plus the probe fit, which cover C4;
  - `moment` 60;
  - `cgcnn` 18;
  - `capped` 33 (POST HOC);
  - `loco` 30, only if his LOCO runs are not adopted.
- **Exists for both arms:** C1, C2, LOCO, screening, and S and D on the Kiyohara split.
- **v2 only:** C3a, C3b, C4. Each would need its v1 counterpart before v1-to-v2 comparisons can be made.
- **Neither arm:** high-moment sensitivity, CGCNN cross-check, capped reruns.
- **Decisions that change the stage lists** (`handoff/M1.md`, NEEDS PALAASH):
  - Is his LOCO (v1) accepted as the registered LOCO run? If so, drop `loco`.
  - Can his 809 relaxations stand in for `relax`? They use a different tiling rule and a different host set
    from our map.
  - Should the tiling extension be applied (recovers 21 hosts, 818)? This is the S11 open question.

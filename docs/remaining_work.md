# Remaining work (after tag nrp-code-v1; rerun at nrp-code-v2)

State on 2026-10-11: code and specs are pinned at `nrp-code-v1` (commit ffd86ce). The cluster runbook is
`docs/nrp_runbook.md`. All analysis rules for the new stages are logged in `docs/deviations.md` (rows of
2026-10-11).

## Status at the results freeze (A6, 2026-10-14, tag `results-v1`)

Every cluster stage, ingest and Mac analysis item below is done or closed; the Status columns were updated at the
freeze (`docs/deviations.md`, AUTHOR DECISION / FREEZE row of 2026-10-14). No new experiment runs after the tag;
the items marked "closed by the freeze" will not be run for this manuscript. The frozen headline numbers are in
`results/freeze_table.json` and `paper/tables/freeze_table.tex`; the claim-by-claim status is in
`docs/freeze_notes.md`. Of the open decisions at the end of this file, 1 to 4 and 6 concerned runs that are now
complete; 5 (retention of the cluster-only checkpoints and embeddings) remains open. The text below is kept as
written on 2026-10-11 and 2026-10-14.

## Update of 2026-10-14: rerun of relax, geomeval and embed at `nrp-code-v2`

The cluster finished moment, cgcnn, capped, cv, cv_v2, precision and precision_v2 (1,431 training runs) and peval
(183 runs); all are merged on main (`docs/nrp/n2_ingest.md`). Two implementation bugs in `nrp-code-v1` blocked relax,
geomeval and embed. They are fixed under the annotated tag `nrp-code-v2` (deviations row of 2026-10-14). Run ids,
spec files and completed results are unchanged; the 5 relax records written by the buggy code are discarded.

| ID | What runs | Where | Spec file and count | Depends on | Status |
|---|---|---|---|---|---|
| R-1 | relax: MACE-MP-0 relaxation + tiling | cluster, checkout of `nrp-code-v2` | `relax.jsonl` 818 | inputs-v1 bundles | done: 818 relaxations in `results/mlip_v1/` (`docs/nrp/n3_ingest.md`) |
| R-2 | embed: S readout embeddings | cluster, checkout of `nrp-code-v2` | `embed.jsonl` 240 | S09 checkpoints | done: 240 in `results/embeddings_v1/` (`docs/nrp/n3_ingest.md`) |
| R-3 | geomeval: S, D, P under DFT, MLIP, rescaled geometry | cluster, checkout of `nrp-code-v2` | `geomeval.jsonl` 180 | R-1 (relax of its test hosts) | done: 180 in `results/geomeval/` (`docs/nrp/n3_ingest.md`) |
| R-4 | Ingest `nrp/relax`, `nrp/embed`, `nrp/geomeval` | Mac | per stage | R-1 to R-3 | done (`docs/nrp/n3_ingest.md`, `docs/nrp/n3_artefacts_local.md`) |

Commands (full text and checks in `docs/nrp_runbook.md`, section 9). `N` is the number of GPU pods; pod `i` uses
the queue `/workspace/dft-gnn-v2/jobs_s<i>`, because admission is queue-wide (runbook section 4).

```bash
# 9.1 fresh checkout of the tag, inputs from /workspace/bundles, spec check
cd /tmp && rm -rf dft-gnn-v2 && git clone https://github.com/pa1aash/dft-gnn.git dft-gnn-v2 && cd dft-gnn-v2
git fetch --tags && git checkout --detach nrp-code-v2 && git merge-base --is-ancestor nrp-code-v1 HEAD
cp -a /tmp/dft-gnn-v2 /workspace/dft-gnn-v2 && cd /workspace/dft-gnn-v2
git config user.name aidenlee && git config user.email aiden.lee.sd@gmail.com
for b in inputs checkpoints mace; do
  tar -xf /workspace/bundles/nrp_$b.tar && bash scripts/nrp/verify_bundle.sh nrp_$b.sha256; done
DFTGNN_CHECKOUT=/workspace/dft-gnn-v2 bash scripts/nrp/stage_pod.sh env
export PYTHONPATH=$PWD/src; PY=/tmp/venv/bin/python; N=<number of GPU pods>
for s in relax embed geomeval; do $PY scripts/queue/make_specs.py --stage $s --check; done
# 9.2 phase A: relax (818) and embed (240)
for i in $(seq 0 $((N-1))); do
  $PY scripts/queue/enqueue.py specs --queue /workspace/dft-gnn-v2/jobs_s$i --shard $i/$N \
      --specs specs/relax.jsonl specs/embed.jsonl; done
#   supervisors per queue (runbook 9.2), then GPU pod i: DFTGNN_CHECKOUT=/workspace/dft-gnn-v2
#   DFTGNN_QUEUE=/workspace/dft-gnn-v2/jobs_s<i> DFTGNN_CHAIN=/workspace/chain-v2 bash .../stage_pod.sh
# 9.3 phase B, once ls results/mlip_v1/*.json | wc -l prints 818: geomeval (180)
for i in $(seq 0 $((N-1))); do
  $PY scripts/queue/enqueue.py specs --queue /workspace/dft-gnn-v2/jobs_s$i --shard $i/$N --specs specs/geomeval.jsonl; done
# 9.4 export, one branch per stage
for s in relax embed geomeval; do
  for i in $(seq 0 $((N-1))); do bash scripts/nrp/export_stage.sh $s --queue /workspace/dft-gnn-v2/jobs_s$i --no-push; done
  git -C ../dft-gnn-v2-nrp-$s push origin nrp/$s:nrp/$s; done
```

**How the estimates were made.**
- **Cluster training stages:** N1's measured per-class mean wall times per run, with the same tuned-v1 cells on
  A10, RTX 3090, L4 and RTX A4000 (`results/nrp/n1_recompute.json`). At B = 654 these are S 757–1171 s and D-state
  934–1543 s; at B = 200, S 265–358 s and D-state 136–196 s.
  - The range runs from the fastest class mean to the slowest.
  - Other budgets are scaled linearly in training hosts (for example cv × 736/654 or × 777/654, precision B = 400
    × 400/654), which is an **assumption**.
  - v2 is **assumed** to cost the same as v1 (no v2 timing on NRP).
  - capped runs are 200 to 600 epochs × N1's seconds per epoch.
- **relax, peval, embed, geomeval:** no NRP measurement. These use the S12 cost model built from the S11 CPU
  smoke timings (3 threads), an **assumption**; a GPU is expected to be faster.
- **Wall times:** the time at n concurrent GPUs is card-hours / n, assuming ideal packing. No single training job
  is longer than about 0.43 h (D-state, B = 654, slowest class), so packing is close to ideal for n ≤ 16.
- **Mac items:** session hours are estimates of the work needed, not measurements.

## Plan

| ID | What runs | Where | Spec file and count | Depends on | Status | Estimated hours (card-h, or session-h on the Mac) | Purpose |
|---|---|---|---|---|---|---|---|
| D0 | Build and place the input bundles (inputs, checkpoints, mace) in the shared folder | Mac, then shared folder | - | tag nrp-code-v1 | done | 0.5 session-h | Inputs for every cluster stage |
| D1 | Volume setup, bundle verification, spec `--check` on the cluster | cluster | all 11 files | D0 | done | about 0.5 card-h (setup pod) | Proves the clone computes the same run ids |
| N2a-1 | relax: MACE-MP-0 relaxation + tiling (one-operation rule) | cluster | `relax.jsonl` 818 | D1 | done (as R-1, at `nrp-code-v2`) | 1.8–30.1 card-h (assumption) | Geometry inputs of C3b |
| N2a-2 | peval: P = P1 then D | cluster | `peval.jsonl` 183 | D1 (S09 checkpoints) | done: 183 in `results/peval/` (`docs/nrp/n2_ingest.md`) | 6.0–12.7 card-h (assumption) | C3a staging |
| N2a-3 | embed: S readout embeddings | cluster | `embed.jsonl` 240 | D1 (S09 checkpoints) | done (as R-2, at `nrp-code-v2`) | 9.7–20.6 card-h (assumption) | C4 latent probe |
| N2a-4 | geomeval: S, D, P under DFT, MLIP, rescaled geometry | cluster | `geomeval.jsonl` 180 | N2a-1 (relax of its test hosts) | done (as R-3, at `nrp-code-v2`) | 11.8–25.1 card-h (assumption) | C3b geometry robustness |
| N2b-1 | moment: high-moment exclusion | cluster | `moment.jsonl` 60 | D1 | done: 60 in `results/moment/` | 14.1–22.6 card-h | SI sensitivity (a) |
| N2b-2 | cgcnn: CGCNN cross-check | cluster | `cgcnn.jsonl` 18 | D1 | done: 18 in `results/cgcnn/` | 1.8–2.8 card-h (MEGNet times; assumption for CGCNN) | SI sensitivity (c) |
| N2b-3 | capped: 600-epoch twins | cluster | `capped.jsonl` 33 | D1 | done: 33 in `results/capped_rerun_v1/` | 5.9–23.0 card-h | POST HOC capped rule |
| N3-1 | cv v1: S and D, K in {10, 20}, seeds 0-2 | cluster | `cv.jsonl` 180 | D1 | done: 180 in `results/cv/` | 49.3–79.2 card-h | Extended-budget statement at 736 and 777 hosts; every host tested |
| N3-2 | cv v2: the same with the v2 backbone | cluster | `cv_v2.jsonl` 180 | D1 | done: 180 in `results/cv_v2/` | 49.3–79.2 card-h (v2 = v1 assumed) | v1 vs v2, descriptive |
| N4-1 | precision v1: 30 resamples x 5 seeds at B = 400, 654 | cluster | `precision.jsonl` 480 | D1 | done: 480 in `results/precision/` | 90.8–145.8 card-h | Non-inferiority bound at 654 with 30 x 5 |
| N4-2 | precision v2: the same with the v2 backbone (tuned-v2 has the a654 set, used at both budgets) | cluster | `precision_v2.jsonl` 480 | D1 | done: 480 in `results/precision_v2/` | 90.8–145.8 card-h (v2 = v1 assumed) | v1 vs v2, descriptive |
| I-1 | Ingest each `nrp/<stage>` branch (`ingest_batch.sh`), merge, push | Mac | per stage | each cluster stage | done (`docs/nrp/n2_ingest.md`, `docs/nrp/n3_ingest.md`) | 0.25 session-h per branch (about 3 h total) | Verified results on main |
| A-1 | v1 staging C3a (D − P, P − S; TOST of the ratified rule) | Mac | - | N2a-2, I-1 | done (A2): `results/staging_v1.json`, `results/staging_v2.json`, `docs/a2_notes.md` | 2 session-h | Claim C3a |
| A-2 | v1 geometry C3b (MLIP and rescaled conditions, d-bin strata, non-converged sensitivity) | Mac | - | N2a-1, N2a-4, I-1 | done (A3): `results/geometry_c3b.json`, `docs/a3_notes.md` | 3 session-h | Claim C3b |
| A-3 | Latent probe C4 (ridge, controls, trend rule) | Mac | - | N2a-3, I-1 | done (A4): `results/probe_c4_v1.json`, `docs/a4_notes.md` | 3 session-h | Claim C4 |
| A-4 | High-moment and CGCNN SI | Mac | - | N2b-1, N2b-2, I-1 | done (A5): `results/sens_high_moment_v1.json`, `results/sens_cgcnn.json`, `docs/a5_notes.md` | 1.5 session-h | SI sensitivities (a), (c) |
| A-5 | Capped post-hoc rule (A at 400 and 654 with 600-epoch twins) | Mac | - | N2b-3, I-1 | done (A5): `results/sens_capped_post_hoc.json` | 1 session-h | POST HOC sensitivity |
| A-6 | Grouped CV analysis with the fixed rule (pooled OOF MAE, host bootstrap, fold SD, within-host) | Mac | - | N3-1 (N3-2 for the v2 column), I-1 | done (A1): `results/cv_extended_budget.json`, `docs/a1_notes.md` | 2 session-h | Extended-budget statement |
| A-7 | Precision analysis with the fixed rule (30 x 5 beside 10 x 3, 10 x 5, 30 x 3; within-host) | Mac | - | N4-1 (N4-2 for v2), I-1 | done (A1): `results/precision_a_b400_b654.json`, `docs/a1_notes.md` | 2 session-h | Non-inferiority at 654 |
| A-8 | Within-host breakdowns by d-bin, element and PHS-prone chemistry | Mac | - | sweep predictions (now); cv OOF (N3-1) for the all-host version | done at B = 654 (M9): `results/within_host_breakdown.json`; the all-host version on CV out-of-fold predictions was not run and is closed by the freeze | 2 session-h | Where site resolution fails, physically |
| A-9 | LOCO adoption analysis (collaborator runs, our estimator, A_LOCO and families) | Mac | - | none (runs merged) | closed by the freeze without a separate analysis: LOCO A of the adopted runs is in `results/ingest_m1_recompute.json` (G1 estimator) and `results/c1c2_v1.json`, `results/c1c2_v2.json` (collaborator estimator); no family breakdown | 1 session-h | Chemistry transfer (M9) |
| A-10 | v1 vs v2 comparison table (sweep, LOCO now; cv and precision later) | Mac | - | v2 sweep (now); N3-2, N4-2 | closed by the freeze: both backbones side by side in `results/freeze_table.json`; no separate record | 1.5 session-h | Descriptive backbone comparison |
| A-11 | Screening reconciliation (B = 654 resamples; CV OOF gives every host) | Mac | - | sweep (now); N3-1 | done for the B = 654 resamples (M8): `figures/main/data/screening_demo.json`; the CV out-of-fold part was not run and is closed by the freeze | 1.5 session-h | Screening demonstration C5 |
| W-1 | Figure style (rcParams, palette, no in-plot text) | Mac | - | none | done (`docs/figure_style.md`) | 2 session-h | Consistent figures |
| W-2 | Blender ZnO render (vacancy site) | Mac | - | none | done (`figures/main/fig1_zno_vacancy.png`) | 3 session-h | Graphical abstract or Fig. 1 |
| W-3 | TikZ schematics (models S, D, P; pipeline) | Mac | - | none | done (`schematics/`) | 3 session-h | Methods figures |
| W-4 | Manuscript skeleton (Crystals template) with the AI-disclosure hook | Mac | - | none | done (`paper/main.tex`) | 2 session-h | Writing frame |
| W-5 | Methods and data prose (universe, splits, training, extensions, hardware policy) | Mac | - | none | done (`paper/sections/`) | 4 session-h | Methods section |
| W-6 | Claims table rows and number macros (generated from results JSONs) | Mac | - | none for the existing claims; each A-item adds rows | done (`docs/claims.yaml`, `paper/tools/make_numbers.py`) | 2 session-h | No claim without a claims row |

## Cluster wall time by stage (card-h / n concurrent GPUs)

| Stage | Card-h | 4 GPUs (h) | 8 GPUs (h) | 16 GPUs (h) |
|---|---:|---:|---:|---:|
| N2a relax (assumption) | 1.8–30.1 | 0.5–7.5 | 0.2–3.8 | 0.1–1.9 |
| N2a peval (assumption) | 6.0–12.7 | 1.5–3.2 | 0.7–1.6 | 0.4–0.8 |
| N2a embed (assumption) | 9.7–20.6 | 2.4–5.2 | 1.2–2.6 | 0.6–1.3 |
| N2a geomeval (assumption; after relax) | 11.8–25.1 | 2.9–6.3 | 1.5–3.1 | 0.7–1.6 |
| N2b moment | 14.1–22.6 | 3.5–5.7 | 1.8–2.8 | 0.9–1.4 |
| N2b cgcnn | 1.8–2.8 | 0.5–0.7 | 0.2–0.4 | 0.1–0.2 |
| N2b capped | 5.9–23.0 | 1.5–5.8 | 0.7–2.9 | 0.4–1.4 |
| N3 cv v1 | 49.3–79.2 | 12.3–19.8 | 6.2–9.9 | 3.1–4.9 |
| N3 cv v2 | 49.3–79.2 | 12.3–19.8 | 6.2–9.9 | 3.1–4.9 |
| N4 precision v1 | 90.8–145.8 | 22.7–36.4 | 11.4–18.2 | 5.7–9.1 |
| N4 precision v2 | 90.8–145.8 | 22.7–36.4 | 11.4–18.2 | 5.7–9.1 |
| **All stages** | **331–587** | **83–147** | **41–73** | **21–37** |

## Concurrency and critical path

- **Cluster:** all eleven spec files can sit in one queue. Every stage is independent except geomeval, which waits
  on relax of its test hosts, so all can run concurrently on separate GPUs. Priorities make N2a go first, then N2b,
  N3 and N4, with v1 ahead of v2 within a stage.
- **Mac, while the cluster works:** A-8, A-9, A-10 (sweep and LOCO part), A-11 (sweep part) and W-1 to W-6 need no
  new results.
- **Critical path:** D0 → D1 → N4-1 precision v1 (the largest stage; 23–36 h at 4 GPUs, 6–9 h at 16) → I-1 →
  A-7 → W-6 numbers into the manuscript. With all stages queued together, the cluster part ends after about
  83–147 h at 4 GPUs, 41–73 h at 8, or 21–37 h at 16. The Mac analyses add about 2 session-h after the last branch
  arrives.

## Decisions still open for Palaash

1. How many GPUs to target at once. The namespace pod quota is 200, shared with other groups, and the practical GPU
   concurrency is not recorded. This sets the wall time above.
2. Whether to admit GPU classes below 16 GB. N0 ran on an RTX 2080 Ti (11 GB), and training peaks at 4.65 GB, but
   inference memory is unmeasured.
3. Whether to run the v2 variants of cv (180 runs) and precision (480 runs) now, later, or not at all. Together they
   are 140–225 card-h.
4. Whether our runs should also exclude `nautilus-ext-gpu01.fullerton.edu`. The collaborator excluded it in N1
   after CUDA unknown errors; the logged policy names only `hcc-nrp-shor-c6017.unl.edu`.
5. How long Aiden keeps the NRP-kept checkpoints and embeddings, whose hashes are in `results/nrp/artefacts/`.
6. If the peval canary runs out of memory on 24 GB cards, which large-card class to use for the jobs_big queue.

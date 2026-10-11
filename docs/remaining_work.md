# Remaining work (after tag nrp-code-v1)

State on 2026-10-11: code and specs are pinned at `nrp-code-v1` (commit ffd86ce). The cluster runbook is
`docs/nrp_runbook.md`. All analysis rules for the new stages are logged in `docs/deviations.md` (rows of
2026-10-11).

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
| D0 | Build and place the input bundles (inputs, checkpoints, mace) in the shared folder | Mac, then shared folder | - | tag nrp-code-v1 | ready | 0.5 session-h | Inputs for every cluster stage |
| D1 | Volume setup, bundle verification, spec `--check` on the cluster | cluster | all 11 files | D0 | waiting | about 0.5 card-h (setup pod) | Proves the clone computes the same run ids |
| N2a-1 | relax: MACE-MP-0 relaxation + tiling (one-operation rule) | cluster | `relax.jsonl` 818 | D1 | waiting | 1.8–30.1 card-h (assumption) | Geometry inputs of C3b |
| N2a-2 | peval: P = P1 then D | cluster | `peval.jsonl` 183 | D1 (S09 checkpoints) | waiting | 6.0–12.7 card-h (assumption) | C3a staging |
| N2a-3 | embed: S readout embeddings | cluster | `embed.jsonl` 240 | D1 (S09 checkpoints) | waiting | 9.7–20.6 card-h (assumption) | C4 latent probe |
| N2a-4 | geomeval: S, D, P under DFT, MLIP, rescaled geometry | cluster | `geomeval.jsonl` 180 | N2a-1 (relax of its test hosts) | waiting | 11.8–25.1 card-h (assumption) | C3b geometry robustness |
| N2b-1 | moment: high-moment exclusion | cluster | `moment.jsonl` 60 | D1 | waiting | 14.1–22.6 card-h | SI sensitivity (a) |
| N2b-2 | cgcnn: CGCNN cross-check | cluster | `cgcnn.jsonl` 18 | D1 | waiting | 1.8–2.8 card-h (MEGNet times; assumption for CGCNN) | SI sensitivity (c) |
| N2b-3 | capped: 600-epoch twins | cluster | `capped.jsonl` 33 | D1 | waiting | 5.9–23.0 card-h | POST HOC capped rule |
| N3-1 | cv v1: S and D, K in {10, 20}, seeds 0-2 | cluster | `cv.jsonl` 180 | D1 | waiting | 49.3–79.2 card-h | Extended-budget statement at 736 and 777 hosts; every host tested |
| N3-2 | cv v2: the same with the v2 backbone | cluster | `cv_v2.jsonl` 180 | D1 | waiting | 49.3–79.2 card-h (v2 = v1 assumed) | v1 vs v2, descriptive |
| N4-1 | precision v1: 30 resamples x 5 seeds at B = 400, 654 | cluster | `precision.jsonl` 480 | D1 | waiting | 90.8–145.8 card-h | Non-inferiority bound at 654 with 30 x 5 |
| N4-2 | precision v2: the same with the v2 backbone (tuned-v2 has the a654 set, used at both budgets) | cluster | `precision_v2.jsonl` 480 | D1 | waiting | 90.8–145.8 card-h (v2 = v1 assumed) | v1 vs v2, descriptive |
| I-1 | Ingest each `nrp/<stage>` branch (`ingest_batch.sh`), merge, push | Mac | per stage | each cluster stage | waiting | 0.25 session-h per branch (about 3 h total) | Verified results on main |
| A-1 | v1 staging C3a (D − P, P − S; TOST of the ratified rule) | Mac | - | N2a-2, I-1 | waiting | 2 session-h | Claim C3a |
| A-2 | v1 geometry C3b (MLIP and rescaled conditions, d-bin strata, non-converged sensitivity) | Mac | - | N2a-1, N2a-4, I-1 | waiting | 3 session-h | Claim C3b |
| A-3 | Latent probe C4 (ridge, controls, trend rule) | Mac | - | N2a-3, I-1 | waiting | 3 session-h | Claim C4 |
| A-4 | High-moment and CGCNN SI | Mac | - | N2b-1, N2b-2, I-1 | waiting | 1.5 session-h | SI sensitivities (a), (c) |
| A-5 | Capped post-hoc rule (A at 400 and 654 with 600-epoch twins) | Mac | - | N2b-3, I-1 | waiting | 1 session-h | POST HOC sensitivity |
| A-6 | Grouped CV analysis with the fixed rule (pooled OOF MAE, host bootstrap, fold SD, within-host) | Mac | - | N3-1 (N3-2 for the v2 column), I-1 | waiting | 2 session-h | Extended-budget statement |
| A-7 | Precision analysis with the fixed rule (30 x 5 beside 10 x 3, 10 x 5, 30 x 3; within-host) | Mac | - | N4-1 (N4-2 for v2), I-1 | waiting | 2 session-h | Non-inferiority at 654 |
| A-8 | Within-host breakdowns by d-bin, element and PHS-prone chemistry | Mac | - | sweep predictions (now); cv OOF (N3-1) for the all-host version | can start now | 2 session-h | Where site resolution fails, physically |
| A-9 | LOCO adoption analysis (collaborator runs, our estimator, A_LOCO and families) | Mac | - | none (runs merged) | can start now | 1 session-h | Chemistry transfer (M9) |
| A-10 | v1 vs v2 comparison table (sweep, LOCO now; cv and precision later) | Mac | - | v2 sweep (now); N3-2, N4-2 | partly now | 1.5 session-h | Descriptive backbone comparison |
| A-11 | Screening reconciliation (B = 654 resamples; CV OOF gives every host) | Mac | - | sweep (now); N3-1 | partly now | 1.5 session-h | Screening demonstration C5 |
| W-1 | Figure style (rcParams, palette, no in-plot text) | Mac | - | none | can start now | 2 session-h | Consistent figures |
| W-2 | Blender ZnO render (vacancy site) | Mac | - | none | can start now | 3 session-h | Graphical abstract or Fig. 1 |
| W-3 | TikZ schematics (models S, D, P; pipeline) | Mac | - | none | can start now | 3 session-h | Methods figures |
| W-4 | Manuscript skeleton (Crystals template) with the AI-disclosure hook | Mac | - | none | can start now | 2 session-h | Writing frame |
| W-5 | Methods and data prose (universe, splits, training, extensions, hardware policy) | Mac | - | none | can start now | 4 session-h | Methods section |
| W-6 | Claims table rows and number macros (generated from results JSONs) | Mac | - | none for the existing claims; each A-item adds rows | can start now | 2 session-h | No claim without a claims row |

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

# National Research Platform runbook

This runbook covers the remaining GPU work, run on the National Research Platform (NRP) by the second author from
his own clone. Each card runs one GPU worker, on 24 GB cards or larger, with no job-time limit. The Mac has already
written every job. Each stage is a spec file `specs/<stage>.jsonl` with a manifest. Run ids are computed with the
pinned code reference `nrp-code-v1`, so the cluster reproduces them exactly and the results merge on the Mac by id.
Rules and labels are in `docs/deviations.md` (rows of 2026-10-11).

Steps marked **[MAC]** run on Palaash's Mac. Everything else runs on the cluster.

## 0. What is fixed

| item | value |
|---|---|
| code | annotated tag `nrp-code-v1` (merge of `m2-specs` into main). Workers refuse a job if `src/ scripts/ configs/ splits/ specs/` differ from the tag (`dftgnn.train.check_code_ref`) |
| specs | `specs/<stage>.jsonl` plus `specs/<stage>.manifest.json` (count and sha256). `make_specs.py --check` must reproduce them on the cluster |
| splits | `splits/MANIFEST.sha256` (append-only); `resamples_10_29.json` and `cv_v1.json` are the EXTENSION splits |
| graphs | `data/graphs_v1_manifest.sha256` (graphs manifest sha256 `be5e5cfd…6d3713`; it enters every training run id) |
| identity | every commit you push: `aidenlee <aiden.lee.sd@gmail.com>`. Commit messages and files must not contain the project's banned words (the Mac rejects the branch otherwise) |

## 1. Stages, order and concurrency

| group | stage | jobs | label | depends on | inputs set | results (tracked) | large artefacts (gitignored, outbox) |
|---|---|---:|---|---|---|---|---|
| N2a | relax | 818 minus already relaxed | registered | - | infer | `results/mlip_v1/` | `data/processed/mlip_v1/` |
| N2a | peval | 183 | registered | S09 checkpoints | infer | `results/peval/` + predictions | - |
| N2a | embed | 240 | registered | S09 checkpoints | infer | `results/embeddings_v1/` | `data/processed/embeddings_v1/` |
| N2a | geomeval | 180 | registered (B = 200 descriptive extra) | relax of its test hosts | infer | `results/geomeval/` + predictions | - |
| N2b | loco | 30 | registered | - | train | `results/loco/` + predictions | `checkpoints/` |
| N2b | moment | 60 | registered | - | train | `results/moment/` + predictions | `checkpoints/` |
| N2b | cgcnn | 18 | registered | - | train | `results/cgcnn/` + predictions | `checkpoints/` |
| N2b | capped | 33 | POST HOC | - | train | `results/capped_rerun_v1/` + predictions | `checkpoints/` |
| N3 | cv | 180 per backbone | EXTENSION | - | train | `results/cv/` + predictions | `checkpoints/` |
| N4 | precision | 480 | EXTENSION | - | train | `results/precision/` + predictions | `checkpoints/` |

Priority: every job carries a global `priority`: relax 0…, peval 100000…, …, cv 800000…, precision 900000…. In one
queue a free worker always takes the ready job with the lowest priority. So N2a runs first, then N2b, N3 and N4.

Concurrency:
- All stages can be queued at once in one shared queue. A worker that finds no ready N2a job (for example, geomeval
  waiting on relax) backfills from N2b, N3 or N4.
- relax, peval and embed are independent of one another. A geomeval job becomes ready once the relax jobs of its
  test hosts are done. Hosts that were already relaxed and ingested earlier are not dependencies, because their
  geometry is already in `data/processed/mlip_v1/`.
- loco, moment, cgcnn, capped, cv and precision are independent of everything.
- The v2 versions of cv and precision (`specs/cv_v2.jsonl`, `specs/precision_v2.jsonl`) exist only after the Mac
  wires in the v2 backbone. The manifest of each spec file records its `backbone`.

Memory: training jobs need at most 7.8 GB (`est_peak_gb`). The peval and geomeval estimates go up to 26.3 GB, but
they come from the training benchmark, and inference holds no gradients. Run one of these jobs on a 24 GB card as a
canary (step 4). If it runs out of memory twice, route the heavy jobs to a larger card class with
`--min-est-gb 20` / `--max-est-gb 20` (step 4).

## 2. One-time setup

Use one persistent volume that every GPU pod mounts read-write (on NRP, a CephFS-backed PVC), mounted at
`/workspace`. The checkout, the queue (`jobs/`), the halt file and the outputs all live on it. The file queue claims a
job by `rename`, which is atomic on that filesystem. Without a shared volume, see section 7 (shards).

```bash
cd /workspace
git clone https://github.com/pa1aash/dft-gnn.git && cd dft-gnn
git fetch --tags && git checkout --detach nrp-code-v1
git config user.name aidenlee && git config user.email aiden.lee.sd@gmail.com
mamba env create -y -f env/environment-gpu.yml        # env name dftgnn-gpu
mamba run -n dftgnn-gpu pip install --no-deps -e .
```

**[MAC]** Build the input bundles and hand them over. They are not in git:
`bash scripts/nrp/make_inputs_bundle.sh train` builds the graph shards and the universe table (about 130 MB).
`bash scripts/nrp/make_inputs_bundle.sh infer` adds the 583 S09 checkpoints, the unit cells, the tiling map, the
MACE-MP-0 medium weights and the 818 release supercells. Each bundle is a tar with a `.tar.sha256` and an inner
sha256 list. The script checks every file against its tracked manifest before packing.

On the cluster, from the checkout root:

```bash
shasum -a 256 -c nrp_inputs_infer.tar.sha256           # or sha256sum -c
tar -xf nrp_inputs_infer.tar && sha256sum -c --quiet nrp_inputs_infer.sha256 && echo INPUTS OK
mamba run -n dftgnn-gpu python -c "from dftgnn.graphs import store; b = store.verify_store(); print('graphs', 'OK' if not b else b)"
(cd splits && sha256sum -c --quiet MANIFEST.sha256) && echo "splits OK"
```

## 3. Generate (verify) the specs

The spec files are committed at the tag. Regenerating them proves that the clone computes the same run ids. The
command writes nothing; it compares bytes:

```bash
for s in relax peval embed geomeval loco moment cgcnn capped cv precision; do
  mamba run -n dftgnn-gpu python scripts/queue/make_specs.py --stage $s --code-ref nrp-code-v1 --backbone v1 --check \
      $( [ $s = relax ] || [ $s = geomeval ] && [ -f specs/relax_hosts.txt ] && echo --hosts-file specs/relax_hosts.txt )
done
```

Each line must end in `files match`. If any line differs, stop and report it to Palaash: the run ids would not
merge. The generator is pure: it uses no GPU and no network.

## 4. Enqueue and start the workers (MPS off)

Enqueue once, from any pod. Enqueueing is idempotent by run id, and the code reference is checked first:

```bash
cd /workspace/dft-gnn
Q=/workspace/dft-gnn/jobs
mamba run -n dftgnn-gpu python scripts/queue/enqueue.py specs --queue $Q \
    --specs specs/relax.jsonl specs/peval.jsonl specs/embed.jsonl specs/geomeval.jsonl \
            specs/loco.jsonl specs/moment.jsonl specs/cgcnn.jsonl specs/capped.jsonl \
            specs/cv.jsonl specs/precision.jsonl
```

If 24 GB cards run out of memory on peval or geomeval, give the heavy jobs a queue of their own on a larger card
class. Use two queues, both on the shared volume:
`--max-est-gb 20 --queue $Q` (24 GB cards) and `--min-est-gb 20 --queue /workspace/dft-gnn/jobs_big` (larger cards).

Each GPU pod runs exactly one worker on its card. Do not start CUDA MPS (`scripts/pod/mps.sh` is for RunPod only):

```bash
cd /workspace/dft-gnn
mkdir -p /workspace/chain/logs
CUDA_VISIBLE_DEVICES=0 nohup mamba run -n dftgnn-gpu python scripts/queue/worker.py --max-concurrent 1 \
    --device cuda --threads 4 --queue /workspace/dft-gnn/jobs --halt-file /workspace/chain/HALT \
    >> /workspace/chain/logs/worker_$(hostname).log 2>&1 &
```

On a pod with several GPUs, start one such line per card with `CUDA_VISIBLE_DEVICES=<i>`. Exactly one pod (a small
CPU pod is enough) runs the supervisor without launching workers. It requeues orphaned jobs, retries a failed job
once, packs each finished group (N2a, N2b, N3, N4) into `outbox/` and writes the end state:

```bash
cp scripts/queue/supervisor.py /workspace/chain/
nohup mamba run -n dftgnn-gpu python /workspace/chain/supervisor.py --checkout /workspace/dft-gnn \
    --chain /workspace/chain --no-launch --workers <number of GPU workers> --guard 1e9 --stage nrp \
    --specs specs/relax.jsonl specs/peval.jsonl specs/embed.jsonl specs/geomeval.jsonl specs/loco.jsonl \
            specs/moment.jsonl specs/cgcnn.jsonl specs/capped.jsonl specs/cv.jsonl specs/precision.jsonl \
    --tranches N2a,N2b,N3,N4 >> /workspace/chain/supervisor.log 2>&1 &
```

`--guard 1e9` turns the RunPod spending guard off: the cluster has no hourly price. Monitor with
`mamba run -n dftgnn-gpu python scripts/queue/status.py --queue /workspace/dft-gnn/jobs`, `supervisor.log` and the
`PACKED_<group>` files. End states: `ALL_DONE`, or `DRAINED_WITH_FAILURES` (failed jobs stay in `jobs/failed/` with
their traceback). To stop cleanly, `touch /workspace/chain/HALT`: workers finish their current job and exit.

Canary: before the large wave, check that one peval job with `est_peak_gb` above 20 finishes on a 24 GB card
(`ls jobs/done | head`, then `jobs/failed/`).

Never edit, delete or `git add` tracked files in the live checkout while workers run. `write_result` refuses a dirty
tree, and a changed file under the pinned paths stops every later job.

## 5. Where results go, and how to push them

Training runs write `results/<subdir>/<run_id>.json`, `results/<subdir>/predictions/<run_id>.parquet` and
`checkpoints/<run_id>.pt`. Task stages write `results/mlip_v1/`, `results/embeddings_v1/` and `results/geomeval/`,
plus their large files under `data/processed/`. Every record is written by `write_result` with its git SHA and its
artefact hashes.

Export a stage whenever you like (for example after its group is packed, or daily for long stages). Re-running the
export adds the runs finished since the last one:

```bash
bash scripts/nrp/export_stage.sh cv          # or any stage name
```

The script commits the stage's result JSONs and prediction parquets. It commits in a separate worktree
(`../dft-gnn-nrp-<stage>`, branch `nrp/<stage>`, started at `nrp-code-v1`) under your identity, and pushes
`nrp/<stage>`. It never switches the live checkout. It then packs every artefact of the stage, including the
gitignored checkpoints and structures, into `outbox/outbox_<stage>_<time>.tar.gz` with a `.sha256`. Hand both files
to Palaash, for example through the shared storage you already use. The tarball is needed for every stage that has
large artefacts (section 1).

## 6. Preemption and resume

Run ids are deterministic and every runner is idempotent, so a preempted pod is restarted with the same command:
- A job whose pod died stays in `jobs/running/` until its heartbeat is 10 minutes old. The supervisor, or the next
  worker, then returns it to pending, and it reruns from the start. Training runs are short; no partial state is
  kept.
- A finished run is never redone. Its result verifies by hash (`verify_result`, `tasks.verified`) and is skipped.
  Re-enqueueing the same spec files adds nothing ("already known").
- A failed job is retried once by the supervisor. A second failure stays in `jobs/failed/` with its traceback, and
  its dependants wait. Report these failures; do not edit code on the cluster.
- If the volume itself is lost, re-clone at `nrp-code-v1` and re-enqueue. Runs already exported are on `nrp/<stage>`
  and in the outbox tarballs, and can be placed back before re-enqueueing.

## 7. Without a shared volume: shards

Give each pod its own clone and queue, and split the jobs by run id. With N pods, pod i enqueues:

```bash
mamba run -n dftgnn-gpu python scripts/queue/enqueue.py specs --shard i/N --queue jobs --specs specs/<stage>.jsonl ...
```

The shards are disjoint and their union is the full stage. Each pod exports its own runs with `bash scripts/nrp/export_stage.sh <stage> --no-push` and pushes them to a branch
of its own, `git -C ../dft-gnn-nrp-<stage> push origin nrp/<stage>:nrp/<stage>-s<i>`. The Mac ingests each shard
branch separately. geomeval needs every relax result present, so run it after the relax
shards have been merged and their outbox tarballs placed. Enqueue refuses a geomeval job whose relax dependency is
neither queued nor already verified.

## 8. What the Mac does when a branch arrives **[MAC]**

```bash
cd ~/Desktop/dft-gnn && git switch main && git pull --ff-only
bash scripts/nrp/ingest_batch.sh nrp/<stage> --outbox ~/Downloads/outbox_<stage>_<time>.tar.gz
```

The ingest check fetches the branch. It checks the author set and the banned pattern (commit messages, added lines,
paths), and that the branch contains `nrp-code-v1` and changes nothing under the pinned paths. It places the
tarball's gitignored artefacts only after verifying them. It then checks that every results JSON names its run id,
that the id is listed in `specs/` and that every recorded artefact hash matches. Finally it prints the counts per
stage against the spec totals. It merges nothing. If it passes:

```bash
git merge --no-ff origin/nrp/<stage> -m "merge(nrp): <stage> results from the cluster"
make audit-history && gtimeout 120 git push origin main
```

Back up the gitignored artefacts as for S09. Analyses run from the merged files on the Mac, under the rules logged in
`docs/deviations.md`. The EXTENSION analysis rules are logged before any of their results is read.

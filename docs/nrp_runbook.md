# National Research Platform runbook

This runbook covers the remaining GPU work, run on the National Research Platform (NRP) by Aiden Lee, the second
author, from his own clone. Each card runs one GPU worker, on a mixed pool of GPU classes, with no job-time limit.
The Mac has written every job. Each stage is a spec file `specs/<stage>.jsonl` (with `<stage>.manifest.json`). Run
ids are computed with the pinned code reference `nrp-code-v1`, so the cluster reproduces them exactly and the results
merge on the Mac by id. Rules and labels are in `docs/deviations.md` (rows of 2026-10-11).

Steps marked **[MAC]** run on Palaash's Mac. Everything else runs on NRP.

## 0. What is fixed

| item | value |
|---|---|
| code | annotated tag `nrp-code-v1` on main. `scripts/queue/worker.py` (through `dftgnn.train.check_code_ref`) refuses a job unless `nrp-code-v1` is an ancestor of HEAD and `src/`, `scripts/`, `configs/`, `splits/` and `specs/` are unchanged since that tag. Commits that only add results on top are allowed. The rerun of relax, embed and geomeval uses the bug-fix tag `nrp-code-v2` (section 9): the worker also accepts a checkout whose pinned paths equal `nrp-code-v2`, as long as `nrp-code-v1` is an ancestor. Run ids keep the string `nrp-code-v1` |
| specs | 11 spec files (section 1). `make_specs.py --check` must reproduce each one byte-for-byte on the cluster |
| identity | every commit you push uses exactly `user.name` = `aidenlee` and `user.email` = `aiden.lee.sd@gmail.com` (`export_stage.sh` refuses any other identity). Commit messages and files must not contain the project's banned words; the Mac rejects the branch otherwise |
| hardware | mixed pool. Every result records GPU model, UUID, driver, node (`NODE_NAME`) and pod hostname (`dftgnn.hardware`). Node `hcc-nrp-shor-c6017.unl.edu` is excluded (N1 row of 2026-10-11) |
| inputs | three bundles in the GitHub release `inputs-v1`, each with a sha256 manifest (section 2) |
| outputs | result JSONs and prediction parquets come back as git branches `nrp/<stage>`. Checkpoints, relaxed structures and embeddings stay on NRP storage; their hashes go in the tracked manifest `results/nrp/artefacts/<stage>.sha256` |

## 1. Stages, order and concurrency

| group | spec file | stage | jobs | backbone | label | depends on | results (tracked) | kept on NRP |
|---|---|---|---:|---|---|---|---|---|
| N2a | `relax.jsonl` | MACE-MP-0 relaxation of every host | 818 | - | registered | - | `results/mlip_v1/` | `data/processed/mlip_v1/` |
| N2a | `peval.jsonl` | P = P1 then D on the test hosts | 183 | v1 | registered | S09 checkpoints | `results/peval/` | - |
| N2a | `embed.jsonl` | S readout embeddings | 240 | v1 | registered | S09 checkpoints | `results/embeddings_v1/` | `data/processed/embeddings_v1/` |
| N2a | `geomeval.jsonl` | S, D, P under DFT, MLIP and rescaled geometry | 180 | v1 | registered (B = 200 descriptive extra) | relax of its test hosts | `results/geomeval/` | - |
| N2b | `moment.jsonl` | high-moment exclusion | 60 | v1 | registered | - | `results/moment/` | `checkpoints/` |
| N2b | `cgcnn.jsonl` | CGCNN cross-check | 18 | v1 | registered | - | `results/cgcnn/` | `checkpoints/` |
| N2b | `capped.jsonl` | 600-epoch twins of capped runs | 33 | v1 | POST HOC | - | `results/capped_rerun_v1/` | `checkpoints/` |
| N3 | `cv.jsonl` | grouped CV, K = 10 and 20 | 180 | v1 | EXTENSION | - | `results/cv/` | `checkpoints/` |
| N3 | `cv_v2.jsonl` | grouped CV, K = 10 and 20 | 180 | v2 | EXTENSION, v2 backbone (POST HOC) | - | `results/cv_v2/` | `checkpoints/` |
| N4 | `precision.jsonl` | 30 resamples x 5 seeds at B = 400, 654 | 480 | v1 | EXTENSION | - | `results/precision/` | `checkpoints/` |
| N4 | `precision_v2.jsonl` | the same with the v2 backbone | 480 | v2 | EXTENSION, v2 backbone (POST HOC) | - | `results/precision_v2/` | `checkpoints/` |

Total: 2852 jobs. LOCO is not a stage: your 30 v1 LOCO runs are adopted (deviations row of 2026-10-11).

Priority: every job carries a global `priority`: relax from 0, peval from 100000, and so on to precision from
800000; a v2 file adds 50000 to its stage base. In one queue a free worker always takes the ready job with the
lowest priority, so N2a goes first, then N2b, N3 and N4, and the v1 jobs of a stage go before its v2 jobs.

Concurrency:
- All eleven files can be queued at once in one shared queue. A worker that finds no ready N2a job (for example
  geomeval waiting on relax) backfills from N2b, N3 or N4.
- relax, peval and embed are independent. A geomeval job is ready once the relax jobs of its test hosts are done.
- moment, cgcnn, capped, cv, cv_v2, precision and precision_v2 are independent of everything.

Measured in N1, for training at B = 654 on one GPU: peak GPU memory was 4.65 GB on every class. Mean wall time per
654-host run was 1171-1543 s on A10, 859-1197 s on RTX 3090, 757-934 s on L4 and 1036-1182 s on RTX A4000 (S-D
range; `results/nrp/n1_recompute.json`). Inference memory (peval, embed, geomeval) was not measured. Their
estimates, from the training benchmark, reach 26.3 GB; run one peval job with `est_peak_gb` above 20 first
(section 4).

## 2. One-time setup

**Release `inputs-v1` [MAC → NRP].** Palaash builds three bundles and publishes them as assets of the GitHub
release `inputs-v1` (https://github.com/pa1aash/dft-gnn/releases/tag/inputs-v1). Each bundle is a `.tar`, its
member manifest `.sha256` and a `.tar.sha256`; `INPUTS_MANIFEST.txt` lists every asset with its sha256 and size:
- `nrp_inputs`: graph shards, universe table, DFT unit cells, the tiling map (one-operation rule, 818 of 818
  hosts) and the 818 release supercell CIFs;
- `nrp_checkpoints`: the 583 S09 checkpoints, about 964 MB;
- `nrp_mace`: the MACE-MP-0 medium weights.

**[MAC]** `bash scripts/nrp/make_inputs_bundle.sh all`. It checks every file against its tracked record before
packing, writes the bundles to `.local/nrp_inputs/`, and uploads nothing.

**Project volume.** Use one CephFS-backed PVC that every pod mounts read-write at `/workspace`. It holds the shared
checkout, the queue, the halt file and every output. The file queue claims a job by `rename`, which is atomic on
that filesystem. Clone onto local disk first and then copy: a direct clone onto CephFS broke off in N0.

```bash
cd /tmp && git clone https://github.com/pa1aash/dft-gnn.git && cd dft-gnn
git fetch --tags && git checkout --detach nrp-code-v1
cp -a /tmp/dft-gnn /workspace/dft-gnn && cd /workspace/dft-gnn
git config user.name aidenlee && git config user.email aiden.lee.sd@gmail.com
# download the release inputs-v1 into /workspace/bundles: gh release download inputs-v1 -R pa1aash/dft-gnn \
#   -D /workspace/bundles, or curl each browser_download_url listed by
#   https://api.github.com/repos/pa1aash/dft-gnn/releases/tags/inputs-v1
# then verify every bundle with scripts/nrp/verify_bundle.sh; for each <b> in inputs checkpoints mace:
bash scripts/nrp/verify_bundle.sh /workspace/bundles/nrp_<b>.tar.sha256 /workspace/bundles
tar -xf /workspace/bundles/nrp_<b>.tar && bash scripts/nrp/verify_bundle.sh nrp_<b>.sha256
(cd splits && sha256sum -c --quiet MANIFEST.sha256) && echo "splits OK"
```

`verify_bundle.sh` checks every sha256 in a manifest and nothing else. Each call must print `OK: n of n`.

## 3. Verify the specs on the cluster

From any pod with the environment (section 4, `stage_pod.sh env`):

```bash
cd /workspace/dft-gnn && export PYTHONPATH=$PWD/src
for s in relax peval embed geomeval moment cgcnn capped cv precision; do
  /tmp/venv/bin/python scripts/queue/make_specs.py --stage $s --check; done
for s in cv precision; do /tmp/venv/bin/python scripts/queue/make_specs.py --stage $s --backbone v2 --check; done
```

Each line must end in `files match`. If any line differs, stop and tell Palaash: the run ids would not merge.

## 4. Enqueue, workers and supervisor (MPS off)

Every pod runs `scripts/nrp/stage_pod.sh`, which builds the venv from `env/lock-nrp-rtx2080ti.txt` on local disk.
Give each GPU pod 1 GPU, 2 CPU, 8 GiB memory and a 4 GiB `/dev/shm`, as in N1, plus `NODE_NAME` from the downward
API (`spec.nodeName`). Use this node affinity:
`nvidia.com/gpu.product Exists` and `kubernetes.io/hostname NotIn [hcc-nrp-shor-c6017.unl.edu]`. Do not pin a GPU
class: the pool is mixed by policy. `docs/nrp/n1_submit_template.md` has the YAML pattern.

Enqueue once, from any pod, after `bash scripts/nrp/stage_pod.sh env`. Enqueueing is idempotent by run id, and the
code reference and each file's manifest are checked first.

```bash
cd /workspace/dft-gnn && export PYTHONPATH=$PWD/src; PY=/tmp/venv/bin/python
N2A="specs/relax.jsonl specs/peval.jsonl specs/embed.jsonl specs/geomeval.jsonl"
N2B="specs/moment.jsonl specs/cgcnn.jsonl specs/capped.jsonl"
N3="specs/cv.jsonl specs/cv_v2.jsonl"
N4="specs/precision.jsonl specs/precision_v2.jsonl"
$PY scripts/queue/enqueue.py specs --queue /workspace/dft-gnn/jobs --specs $N2A $N2B $N3 $N4
```

Each GPU pod runs one worker on its card: `bash /workspace/dft-gnn/scripts/nrp/stage_pod.sh` (worker mode). Run as
many GPU pods as the namespace allows.

One CPU pod runs the supervisor without launching workers. It requeues orphaned jobs, retries a failed job once,
packs nothing (`--tranches` only marks group completion) and writes the end state:

```bash
mkdir -p /workspace/chain && cp scripts/queue/supervisor.py /workspace/chain/
nohup $PY /workspace/chain/supervisor.py --checkout /workspace/dft-gnn --chain /workspace/chain --python $PY \
    --no-launch --workers <number of GPU pods> --guard 1e9 --stage nrp --specs $N2A $N2B $N3 $N4 \
    --tranches N2a,N2b,N3,N4 >> /workspace/chain/supervisor.log 2>&1 &
```

The supervisor packs each finished group into `outbox/` as before. Those tarballs are a local convenience and are
not sent anywhere. Monitor with `$PY scripts/queue/status.py --queue /workspace/dft-gnn/jobs`, `supervisor.log` and
`ls jobs/failed`. End states: `ALL_DONE`, or `DRAINED_WITH_FAILURES`. To stop cleanly, `touch /workspace/chain/HALT`.

To run one group at a time instead, enqueue only that group's files (for example `--specs $N3`).

Admission is queue-wide. A worker admits a job only if the `est_peak_gb` of every running job in its queue, on any
card, plus the new one fits in 0.85 of its own card's memory. On one shared queue the whole cluster therefore holds
about one card's worth of estimated memory at a time: jobs with large estimates (embed and geomeval at 6.8-26.3 GB,
peval and the v2-size training jobs at up to 17-26 GB) run one or two at a time however many GPUs are up. This
accounting is left unchanged. For such jobs give every GPU worker its own queue: the sharded per-worker queues of
section 7 (`enqueue.py specs --shard i/N --queue <checkout>/jobs_s<i>`, and `DFTGNN_QUEUE` set per pod), which may
share one checkout on the shared volume. Section 9 uses this layout.

Canary: before the large wave, check that one peval job with `est_peak_gb` above 20 finishes on a 24 GB card. If
it runs out of memory twice, use two queues: enqueue with `--max-est-gb 20 --queue /workspace/dft-gnn/jobs` for
cards under 40 GB and `--min-est-gb 20 --queue /workspace/dft-gnn/jobs_big` for larger cards, and give the large-card
pods `DFTGNN_QUEUE=/workspace/dft-gnn/jobs_big`.

Never edit, delete or `git add` tracked files in `/workspace/dft-gnn` while workers run. `write_result` refuses a
dirty tree, and a change under the pinned paths stops every later job.

## 5. Push results: one branch per stage

```bash
cd /workspace/dft-gnn && bash scripts/nrp/export_stage.sh <stage>     # relax, peval, ..., cv, precision
```

The script commits the stage's result JSONs and prediction parquets, plus `results/nrp/artefacts/<stage>.sha256`
with one line per gitignored artefact (sha256, size, path; each hash recomputed and compared with its record). It
commits in a separate worktree (`../dft-gnn-nrp-<stage>`, branch `nrp/<stage>`, started at `nrp-code-v1`) under
your identity, and pushes. The live checkout never changes branch. Run it again later to add newer runs; an export
from another pod continues the pushed branch. The v2 files share their stage name: cv and cv_v2 both export as
`nrp/cv`, and precision and precision_v2 as `nrp/precision`. Checkpoints and other large artefacts stay on the
volume; keep it until Palaash says the analyses are done.

## 6. Preemption and resume

Run ids are deterministic and every runner is idempotent, so a preempted pod is restarted with the same command.
- A job whose pod died returns to pending after its heartbeat is 10 minutes old, and reruns from the start.
- A finished run whose result verifies by hash is never redone. Re-enqueueing adds nothing ("already known").
- A failed job is retried once by the supervisor. A second failure stays in `jobs/failed/` with its traceback, and
  its dependants wait. Report these failures; do not edit code on the cluster.

## 7. Without a shared volume: shards

Give each pod its own checkout and queue, and split the jobs by run id with `enqueue.py specs --shard i/N`. The
shards are disjoint and their union is the full stage. Each pod exports with
`export_stage.sh <stage> --no-push` and pushes to its own branch:
`git -C ../dft-gnn-nrp-<stage> push origin nrp/<stage>:nrp/<stage>-s<i>`. geomeval needs every relax output on the
same storage, so run it where the relax outputs are.

## 8. On the Mac when a branch arrives **[MAC]**

```bash
cd ~/Desktop/dft-gnn && git switch main && git pull --ff-only
bash scripts/nrp/ingest_batch.sh nrp/<stage>
```

The ingest check fetches the branch. It checks the author set and the banned pattern (commit messages, added lines,
paths), and that the branch contains `nrp-code-v1` and changes nothing under the pinned paths. It then checks that
every results JSON names its run id, that the id is listed in `specs/`, that every committed artefact matches its
recorded sha256, and that every NRP-kept artefact is listed with the same sha256 in `results/nrp/artefacts/`.
Finally it prints the counts per stage against the spec totals. It merges nothing. If it passes:

```bash
git merge --no-ff origin/nrp/<stage> -m "merge(nrp): <stage> results from the cluster"
make audit-history && perl -e 'alarm 120; exec @ARGV' -- git push origin main
```

The analyses run on the Mac from the merged files, under the rules logged in `docs/deviations.md`. The cv and
precision rules were logged on 2026-10-11, before any result.

## 9. Rerun of relax, embed and geomeval at `nrp-code-v2` (2026-10-14)

Two implementation bugs in `nrp-code-v1` stopped these three stages: a translation-only host's point operation read
as NaN in `relax_host`, and checkpoints were loaded onto the CPU while the batches were on the GPU (`readout_vector`).
Both are fixed under the annotated tag `nrp-code-v2` (deviations row of 2026-10-14). No spec file, run id or
completed result changes: the specs still carry `code_ref` = `nrp-code-v1`, and the worker accepts a checkout of
`nrp-code-v2` because `nrp-code-v1` is its ancestor and nothing under `src/`, `scripts/`, `configs/`, `splits/` or
`specs/` has changed since `nrp-code-v2`.

Leave `/workspace/dft-gnn` untouched: it holds the checkpoints of the finished stages. The 5 relax records the buggy
code wrote there (`results/mlip_v1/`, `data/processed/mlip_v1/`) are discarded: never export relax, embed or
geomeval from that checkout. The rerun uses a fresh checkout, `/workspace/dft-gnn-v2`, with its own queues and chain
directory.

| stage | spec file | jobs | depends on | est_peak_gb | results (tracked) | kept on NRP |
|---|---|---:|---|---|---|---|
| relax | `relax.jsonl` | 818 | - | 0.8-2.4 | `results/mlip_v1/` | `data/processed/mlip_v1/` |
| embed | `embed.jsonl` | 240 | S09 checkpoints | 6.8-17.2 | `results/embeddings_v1/` | `data/processed/embeddings_v1/` |
| geomeval | `geomeval.jsonl` | 180 | relax of its test hosts | 6.8-26.3 | `results/geomeval/` | - |

**9.1 Checkout and inputs (CPU pod).** The bundles of release `inputs-v1` are already in `/workspace/bundles`.

```bash
cd /tmp && rm -rf dft-gnn-v2 && git clone https://github.com/pa1aash/dft-gnn.git dft-gnn-v2 && cd dft-gnn-v2
git fetch --tags && git checkout --detach nrp-code-v2
git merge-base --is-ancestor nrp-code-v1 HEAD && echo "nrp-code-v1 is an ancestor"
cp -a /tmp/dft-gnn-v2 /workspace/dft-gnn-v2 && cd /workspace/dft-gnn-v2
git config user.name aidenlee && git config user.email aiden.lee.sd@gmail.com
for b in inputs checkpoints mace; do
  tar -xf /workspace/bundles/nrp_$b.tar && bash scripts/nrp/verify_bundle.sh nrp_$b.sha256; done
(cd splits && sha256sum -c --quiet MANIFEST.sha256) && echo "splits OK"
DFTGNN_CHECKOUT=/workspace/dft-gnn-v2 bash scripts/nrp/stage_pod.sh env      # prints nrp-code-v1 -> <nrp-code-v2 commit>
export PYTHONPATH=$PWD/src; PY=/tmp/venv/bin/python
for s in relax embed geomeval; do $PY scripts/queue/make_specs.py --stage $s --check; done   # each: files match
```

Each `verify_bundle.sh` call must print `OK: n of n`; each `--check` line must end in `files match`.

**9.2 Phase A: relax and embed, one queue per GPU pod.** Set `N` to the number of GPU pods. Pod `i` (0 to N - 1)
gets queue `jobs_s<i>`. Enqueue and start the supervisors (one per queue, on the CPU pod) before any GPU pod, because
a worker that finds its queue empty exits.

```bash
cd /workspace/dft-gnn-v2 && export PYTHONPATH=$PWD/src; PY=/tmp/venv/bin/python; N=<number of GPU pods>
for i in $(seq 0 $((N-1))); do
  $PY scripts/queue/enqueue.py specs --queue /workspace/dft-gnn-v2/jobs_s$i --shard $i/$N \
      --specs specs/relax.jsonl specs/embed.jsonl; done
mkdir -p /workspace/chain-v2 && cp scripts/queue/supervisor.py /workspace/chain-v2/
for i in $(seq 0 $((N-1))); do mkdir -p /workspace/chain-v2/a$i
  nohup $PY /workspace/chain-v2/supervisor.py --checkout /workspace/dft-gnn-v2 --queue /workspace/dft-gnn-v2/jobs_s$i \
      --chain /workspace/chain-v2/a$i --python $PY --no-launch --workers 1 --guard 1e9 --stage nrp \
      --specs specs/relax.jsonl specs/embed.jsonl --shard $i/$N --tranches N2a \
      >> /workspace/chain-v2/a$i/supervisor.log 2>&1 & done
```

GPU pod `i` runs `bash /workspace/dft-gnn-v2/scripts/nrp/stage_pod.sh` with `DFTGNN_CHECKOUT=/workspace/dft-gnn-v2`,
`DFTGNN_QUEUE=/workspace/dft-gnn-v2/jobs_s<i>` and `DFTGNN_CHAIN=/workspace/chain-v2` (pod spec, node affinity and
resources as in section 4). Monitor with
`for i in $(seq 0 $((N-1))); do $PY scripts/queue/status.py --queue /workspace/dft-gnn-v2/jobs_s$i; done` and
`ls /workspace/dft-gnn-v2/jobs_s*/failed`. Phase A ends when every `/workspace/chain-v2/a<i>/` holds `ALL_DONE`.

**9.3 Phase B: geomeval, after all 818 relax jobs.** A geomeval job waits on the relax jobs of its test hosts, which
lie in other shards; once their results verify in the checkout, the enqueue drops those dependencies.

```bash
cd /workspace/dft-gnn-v2 && export PYTHONPATH=$PWD/src; PY=/tmp/venv/bin/python; N=<number of GPU pods>
ls results/mlip_v1/*.json | wc -l                                                     # must print 818
for i in $(seq 0 $((N-1))); do mkdir -p /workspace/chain-v2/b$i
  $PY scripts/queue/enqueue.py specs --queue /workspace/dft-gnn-v2/jobs_s$i --shard $i/$N --specs specs/geomeval.jsonl
  nohup $PY /workspace/chain-v2/supervisor.py --checkout /workspace/dft-gnn-v2 --queue /workspace/dft-gnn-v2/jobs_s$i \
      --chain /workspace/chain-v2/b$i --python $PY --no-launch --workers 1 --guard 1e9 --stage nrp \
      --specs specs/geomeval.jsonl --shard $i/$N --tranches N2a \
      >> /workspace/chain-v2/b$i/supervisor.log 2>&1 & done
```

Then start the GPU pods again with the same settings as phase A. Phase B ends when every `/workspace/chain-v2/b<i>/`
holds `ALL_DONE`. To stop cleanly at any time, `touch /workspace/chain-v2/HALT`.

**9.4 Export.** Each stage collects its done jobs from every shard queue into one branch, then pushes once. The
branches start at `nrp-code-v1` and add results only, as in section 5.

```bash
cd /workspace/dft-gnn-v2; N=<number of GPU pods>
for s in relax embed geomeval; do
  for i in $(seq 0 $((N-1))); do bash scripts/nrp/export_stage.sh $s --queue /workspace/dft-gnn-v2/jobs_s$i --no-push; done
  git -C ../dft-gnn-v2-nrp-$s push origin nrp/$s:nrp/$s
done
```

**[MAC]** Ingest each branch with `bash scripts/nrp/ingest_batch.sh nrp/<stage>` (section 8); the counts must be
relax 818, embed 240 and geomeval 180.

## 10. moment_v2 and the code tags from `nrp-code-v4` (2026-10-18)

The stage `moment_v2` (N2b, v2 backbone only, 60 jobs, `specs/moment_v2.jsonl`, results to `results/moment_v2/`)
reruns the high-moment exclusion on the final network; it is code tagged `nrp-code-v4` (deviations row of
2026-10-18). Its specs keep `code_ref` = `nrp-code-v1`; the worker accepts a checkout whose pinned paths equal
`nrp-code-v4` because the tag is listed in `CODE_REF_SUCCESSORS` (`src/dftgnn/train/__init__.py`). Run it from
`git checkout --detach nrp-code-v4`.

- Scope gates (`git diff --stat <tag> -- src scripts configs splits specs`) compare against `nrp-code-v4` from now on.
- A new stage needs a code commit under the pinned paths, an annotated tag on that commit, and an entry for the tag
  in `CODE_REF_SUCCESSORS` for the code reference its specs carry (`nrp-code-v5` is already listed for N5); without
  the entry the worker refuses the job at the code-reference check.

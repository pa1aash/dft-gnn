#!/usr/bin/env bash
# One GPU pod per queue: pod k drains <queue root>/q<k> (scripts/nrp/partition_queue.py), so each pod's VRAM
# admission sees only its own jobs.  Usage: bash scripts/nrp/launch_indexed_workers.sh <checkout> <queue root> <n> <job>
set -euo pipefail
cd "$(dirname "$0")/../.."
REMOTE=$1; QROOT=$2; N=$3; JOB=$4
kubectl --request-timeout=60s -n cms-ml delete job "$JOB" --ignore-not-found >/dev/null
sed -e "s/name: dftgnn-workers$/name: $JOB/" -e "s|workingDir: /workspace/dft-gnn$|workingDir: $REMOTE|" \
    -e "s/parallelism: [0-9]*/parallelism: $N/" -e "s/completions: [0-9]*/completions: $N\n  completionMode: Indexed/" \
    -e "s|scripts/queue/worker.py --max-concurrent 3 --device cuda|scripts/queue/worker.py --max-concurrent 3 --device cuda --queue $QROOT/q\$JOB_COMPLETION_INDEX|" \
    -e "s/backoffLimit: [0-9]*/backoffLimit: 40/" scripts/nrp/worker-job.yaml \
  | kubectl --request-timeout=60s -n cms-ml apply -f -

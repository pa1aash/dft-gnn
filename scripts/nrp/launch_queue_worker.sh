#!/usr/bin/env bash
# One GPU worker pod for one existing per-pod queue (e.g. a queue whose indexed pod exited before held jobs returned).
#   bash scripts/nrp/launch_queue_worker.sh <checkout> <queue dir> <job name>
set -euo pipefail
cd "$(dirname "$0")/../.."
REMOTE=$1; Q=$2; JOB=$3
kubectl --request-timeout=60s -n cms-ml delete job "$JOB" --ignore-not-found >/dev/null
sed -e "s/name: dftgnn-workers$/name: $JOB/" -e "s|workingDir: /workspace/dft-gnn$|workingDir: $REMOTE|" \
    -e "s/parallelism: [0-9]*/parallelism: 1/" -e "s/completions: [0-9]*/completions: 1/" \
    -e "s|scripts/queue/worker.py --max-concurrent 3 --device cuda|scripts/queue/worker.py --max-concurrent 3 --device cuda --queue $Q|" \
    -e "s/role: worker}/role: worker, group: pq}/" scripts/nrp/worker-job.yaml \
  | kubectl --request-timeout=60s -n cms-ml apply -f -

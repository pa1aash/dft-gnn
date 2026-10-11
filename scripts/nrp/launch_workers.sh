#!/usr/bin/env bash
# (Re)launch the GPU worker Job for a checkout on the volume.
#   bash scripts/nrp/launch_workers.sh <remote checkout> <job name> <parallelism>
set -euo pipefail
cd "$(dirname "$0")/../.."
REMOTE=$1; JOB=$2; N=$3
kubectl --request-timeout=60s -n cms-ml delete job "$JOB" --ignore-not-found >/dev/null
sed -e "s/name: dftgnn-workers$/name: $JOB/" -e "s|workingDir: /workspace/dft-gnn$|workingDir: $REMOTE|" \
    -e "s/parallelism: [0-9]*/parallelism: $N/" -e "s/completions: [0-9]*/completions: $N/" scripts/nrp/worker-job.yaml \
  | kubectl --request-timeout=60s -n cms-ml apply -f -

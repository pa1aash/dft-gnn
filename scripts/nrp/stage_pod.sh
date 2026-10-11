#!/usr/bin/env bash
# One GPU worker on one NRP pod for the cluster stages (docs/nrp_runbook.md, section 4).
#   bash /workspace/dft-gnn/scripts/nrp/stage_pod.sh [worker|env]
# The shared checkout /workspace/dft-gnn (on the project volume, at the tag nrp-code-v1) holds the code, the inputs,
# the queue and every output. This script builds the N0 environment lock (env/lock-nrp-rtx2080ti.txt) in a venv on
# the pod's local disk (importing torch from the CephFS volume took over 20 minutes in N0 and N1), checks that the
# checkout still matches the tag (dftgnn.train.check_code_ref), and runs one queue worker on the pod's GPU with
# MPS off. "env" stops after the environment (for enqueue, supervisor or export pods). Environment variables:
# DFTGNN_CHECKOUT (default /workspace/dft-gnn), DFTGNN_QUEUE (default <checkout>/jobs), DFTGNN_CHAIN (default
# /workspace/chain), NODE_NAME (set from the downward API; recorded in every result).
set -uo pipefail
MODE="${1:-worker}"
C="${DFTGNN_CHECKOUT:-/workspace/dft-gnn}"
Q="${DFTGNN_QUEUE:-$C/jobs}"
CH="${DFTGNN_CHAIN:-/workspace/chain}"
V=/tmp/venv
log() { echo "[stage-pod $(date -u +%H:%M:%S)] $*"; }
git config --global --add safe.directory '*'
log "node ${NODE_NAME:-unknown}, checkout $C, queue $Q"
cd "$C" || exit 2
log "environment (N0 lock) on local disk"
if [ ! -x "$V/bin/python" ]; then
  python3.11 -m venv "$V" && "$V/bin/python" -m pip install -q --upgrade pip || exit 3
  "$V/bin/python" -m pip install -q -r env/lock-nrp-rtx2080ti.txt || exit 3
fi
export PYTHONPATH="$C/src" OMP_NUM_THREADS="${OMP_NUM_THREADS:-2}"
"$V/bin/python" -c "from dftgnn.train import check_code_ref; print('nrp-code-v1 ->', check_code_ref('nrp-code-v1'))" || exit 2
[ "$MODE" = env ] && { log "environment ready: $V/bin/python, PYTHONPATH=$PYTHONPATH"; exit 0; }
nvidia-smi --query-gpu=name,uuid,driver_version,memory.total --format=csv,noheader || exit 4
mkdir -p "$CH/logs"
log "worker (one process on this GPU, MPS off)"
exec "$V/bin/python" scripts/queue/worker.py --max-concurrent 1 --device cuda --threads 2 --queue "$Q" \
    --halt-file "$CH/HALT"

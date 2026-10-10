#!/usr/bin/env bash
# N1 on one NRP GPU pod (Jobs created by scripts/nrp/n1_launch.sh).
#   bash /workspace/n1/n1_pod.sh [pass-label]
# Clones main at $N1_BASE onto the pod's local disk (a clone onto the CephFS volume broke off mid-transfer in N0) and
# applies the N1 commit from /workspace/n1/n1.patch with its recorded dates and committer, so HEAD is exactly $N1_SHA;
# stops if it is not. Installs the N0 environment lock (/workspace/n0/lock-nrp.txt) on local disk, links the verified
# graph store and results/nrp/n1 to the volume (records survive the pod, so a rerun skips finished runs), and runs
# scripts/nrp/run_n1.sh. Exit status is run_n1.sh's.
set -uo pipefail
W=/workspace/n1
R=/tmp/dft-gnn
PASS=${1:-}
log() { echo "[n1 $(date -u +%H:%M:%S)] $*"; }
git config --global --add safe.directory '*'

log "node ${NODE_NAME:-unknown} pass ${PASS:-pass1}"
nvidia-smi --query-gpu=name,uuid,driver_version,memory.total --format=csv,noheader || exit 4
for i in 1 2 3; do
  rm -rf $R && git clone -q https://github.com/pa1aash/dft-gnn.git $R && break
  log "clone attempt $i failed"; sleep 20
done
cd $R && git checkout -q -B nrp/n1-gpu-repeat "${N1_BASE:?}" || exit 2
GIT_COMMITTER_NAME="Aiden Lee" GIT_COMMITTER_EMAIL="${N1_EMAIL:?}" git am -q --committer-date-is-author-date $W/n1.patch || exit 2
test "$(git rev-parse HEAD)" = "${N1_SHA:?}" || { log "HEAD $(git rev-parse HEAD) is not $N1_SHA"; exit 2; }
log "checkout $N1_SHA"

log "environment (N0 lock)"
python3.11 -m venv /tmp/venv && /tmp/venv/bin/python -m pip install -q --upgrade pip || exit 3
/tmp/venv/bin/python -m pip install -q -r /workspace/n0/lock-nrp.txt || exit 3
/tmp/venv/bin/python -m pip install -q -e . --no-deps || exit 3

mkdir -p data/processed results/nrp $W/results/nrp/n1
ln -sfn /workspace/dft-gnn/data/processed/graphs_v1 data/processed/graphs_v1
cp /workspace/n0/universe_v1.parquet data/processed/universe_v1.parquet
ln -sfn $W/results/nrp/n1 results/nrp/n1

log "runs"
N1_PYTHON=/tmp/venv/bin/python bash scripts/nrp/run_n1.sh $PASS
rc=$?
log "exit $rc"
exit $rc

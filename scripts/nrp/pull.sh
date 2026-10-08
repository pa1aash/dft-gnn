#!/usr/bin/env bash
# On the Mac: pack the finished runs of a stage on NRP, copy the tarball back and unpack it with hash
# verification into results/ and checkpoints/. Needs the dftgnn-loader pod (scripts/nrp/loader-pod.yaml).
#
#   bash scripts/nrp/pull.sh <stage>            e.g. diag_cross, d_ablation, dlate
#   bash scripts/nrp/pull.sh --files <name> <repo-relative files...>
set -euo pipefail
cd "$(dirname "$0")/../.."
NS=${NRP_NAMESPACE:-cms-ml}
POD=${NRP_POD:-dftgnn-loader}
PY=/workspace/venv/bin/python
REMOTE=/workspace/dft-gnn
if [[ "${1:-}" == "--files" ]]; then
  name=${2:?name}; shift 2
  line=$(kubectl exec -n "$NS" "$POD" -- bash -c "cd $REMOTE && $PY scripts/queue/outbox.py pack-files --name $name $*" | tail -1)
else
  stage=${1:?stage}
  line=$(kubectl exec -n "$NS" "$POD" -- bash -c "cd $REMOTE && $PY scripts/queue/outbox.py pack --stage $stage" | tail -1)
fi
tarball=${line%% (*}
name=$(basename "$tarball")
mkdir -p outbox
kubectl cp -n "$NS" "$POD:$tarball" "outbox/$name"
kubectl cp -n "$NS" "$POD:$tarball.sha256" "outbox/$name.sha256"
python3 - "outbox/$name" <<'EOF'
import hashlib, sys
p = sys.argv[1]
want = open(p + ".sha256").read().split()[0]
h = hashlib.sha256(open(p, "rb").read()).hexdigest()
sys.exit(f"tarball hash mismatch {p}" if h != want else 0)
EOF
"${DFTGNN_PY:-python}" scripts/queue/outbox.py unpack "outbox/$name"

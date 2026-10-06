#!/usr/bin/env bash
# Runs on the Mac: fetch the pod's outbox, verify every tarball, unpack into results/ and checkpoints/.
#   bash scripts/pod/pull_results.sh --host <ip> --port <port> --key <ssh key> [--dest /workspace/dft-gnn]
set -euo pipefail
HOST=""; PORT=""; KEY=""; DEST="/workspace/dft-gnn"; USER_="root"
while [ $# -gt 0 ]; do
  case "$1" in
    --host) HOST="$2"; shift 2 ;;
    --port) PORT="$2"; shift 2 ;;
    --key) KEY="$2"; shift 2 ;;
    --dest) DEST="$2"; shift 2 ;;
    --user) USER_="$2"; shift 2 ;;
    *) echo "unknown arg $1" >&2; exit 2 ;;
  esac
done
: "${HOST:?--host required}" "${PORT:?--port required}" "${KEY:?--key required}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p outbox
rsync -az -e "ssh -p $PORT -i $KEY -o StrictHostKeyChecking=accept-new" "$USER_@$HOST:$DEST/outbox/" outbox/
for t in outbox/*.tar.gz; do
  [ -e "$t" ] || continue
  [ -e "$t.unpacked" ] && continue
  mamba run -n dftgnn python scripts/queue/outbox.py unpack "$t"
  touch "$t.unpacked"
done
[ -e outbox/lock-gpu.txt ] && echo "outbox/lock-gpu.txt present: copy to env/lock-gpu.txt and commit"
echo "done; review results/ and commit from a clean tree"

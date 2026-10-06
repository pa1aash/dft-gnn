#!/usr/bin/env bash
# Runs on the Mac: copy the graph shards and the splits to the pod.
#   bash scripts/pod/push_data.sh [--host <ip> --port <port> --key <ssh key>]  (or env POD_HOST POD_PORT POD_KEY POD_DEST) [--dest /workspace/dft-gnn]
set -euo pipefail
HOST="${POD_HOST:-}"; PORT="${POD_PORT:-}"; KEY="${POD_KEY:-$HOME/.ssh/id_ed25519}"; DEST="${POD_DEST:-/workspace/dft-gnn}"; USER_="${POD_USER:-root}"
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
: "${HOST:?--host or POD_HOST required}" "${PORT:?--port or POD_PORT required}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SSH="ssh -p $PORT -i $KEY -o StrictHostKeyChecking=accept-new"
cd "$ROOT"
python3 - <<'PY'
import hashlib, pathlib
m = pathlib.Path("data/graphs_v1_manifest.sha256").read_text().splitlines()
d = pathlib.Path("data/processed/graphs_v1")
bad = [n for s, n in (l.split("  ", 1) for l in m if l and not l.startswith("#"))
       if hashlib.sha256((d / n).read_bytes()).hexdigest() != s]
raise SystemExit(f"local shards do not match the manifest: {bad}" if bad else 0)
PY
$SSH "$USER_@$HOST" "mkdir -p $DEST/data/processed/graphs_v1 $DEST/splits"
rsync -az --info=progress2 -e "$SSH" data/processed/graphs_v1/ "$USER_@$HOST:$DEST/data/processed/graphs_v1/"
rsync -az -e "$SSH" splits/ "$USER_@$HOST:$DEST/splits/"
echo "pushed graphs_v1 and splits to $HOST:$DEST; now run on the pod: bash scripts/pod/setup.sh verify $DEST"

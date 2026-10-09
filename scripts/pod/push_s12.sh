#!/usr/bin/env bash
# Runs on the Mac after push_data.sh: copy the S12 inputs to the pod and verify them there.
#   bash scripts/pod/push_s12.sh [--host <ip> --port <port> --key <ssh key>] (or env POD_HOST POD_PORT POD_KEY) [--dest /workspace/dft-gnn]
# Sends: checkpoints/ (583 S09 checkpoints, checked against results/checkpoint_manifest.json), the DFT unit-cell
# cache, the tiling map, the MACE-MP-0 medium checkpoint (.cache/mace/) and the 818 release supercell CIFs of
# universe v1. A sha256 list of every sent file (s12_push.sha256) is checked on the pod with sha256sum -c.
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
LIST=.local/s12_push_files.txt
mkdir -p .local
python3 - "$LIST" <<'PY'
import csv, hashlib, json, pathlib, sys
out = pathlib.Path(sys.argv[1])
man = json.loads(pathlib.Path("results/checkpoint_manifest.json").read_text())["payload"]["files"]
files = [f"checkpoints/{n}" for n in sorted(man)]
mace = json.loads(pathlib.Path("results/mace_model.json").read_text())["payload"]
files += ["data/processed/unit_cells_v1.json", "data/processed/tiling_map_v1.parquet", mace["cache_path"]]
db = "data/raw/unpacked/oxygen_vacancies_db/site_info"      # release directory = formula (checked in S11)
files += sorted(f"{db}/{r['formula']}/supercell.cif" for r in csv.DictReader(open("data/tiling_summary_v1.csv")))
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
bad = [f for f in files[: len(man)] if sha(f) != man[f.split("/", 1)[1]]["sha256"]]
if bad:
    raise SystemExit(f"checkpoints differ from the manifest: {bad[:5]}")
if sha(mace["cache_path"]) != mace["sha256"]:
    raise SystemExit("MACE checkpoint differs from results/mace_model.json")
out.write_text("\n".join(files) + "\n")
pathlib.Path("s12_push.sha256").write_text("".join(f"{sha(f)}  {f}\n" for f in files))
total = sum(pathlib.Path(f).stat().st_size for f in files)
print(f"{len(files)} files, {total / 2**20:.1f} MiB")
PY
rsync -az --no-owner --no-group --info=progress2 --files-from="$LIST" -e "$SSH" ./ "$USER_@$HOST:$DEST/"
rsync -az --no-owner --no-group -e "$SSH" s12_push.sha256 "$USER_@$HOST:$DEST/"
rm -f s12_push.sha256
$SSH "$USER_@$HOST" "cd $DEST && sha256sum -c --quiet s12_push.sha256 && echo 'S12 inputs: OK'"

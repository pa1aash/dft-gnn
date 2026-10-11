#!/usr/bin/env bash
# Runs on the Mac: pack the untracked inputs of the cluster stages into bundles for the shared file folder
# (docs/nrp_runbook.md, section 2). Nothing is uploaded by this script; Palaash places the files in the folder.
#   bash scripts/nrp/make_inputs_bundle.sh inputs|checkpoints|mace|all [outdir]   (default outdir .local/nrp_inputs)
# inputs:      graph shards (checked against data/graphs_v1_manifest.sha256), the universe table, the DFT unit
#              cells, the tiling map (one-operation rule) and the 818 release supercell CIFs.
# checkpoints: the S09 checkpoints (checked against results/checkpoint_manifest.json), about 964 MB.
# mace:        the MACE-MP-0 medium weights (checked against results/mace_model.json).
# Each bundle <name> gives three files: nrp_<name>.tar (members at repo-relative paths), nrp_<name>.sha256 (the
# manifest: one "sha256  path" line per member, also inside the tar) and nrp_<name>.tar.sha256 (the tar itself).
# Aiden, from the checkout root after downloading:
#   bash scripts/nrp/verify_bundle.sh nrp_<name>.tar.sha256 <download dir>
#   tar -xf <download dir>/nrp_<name>.tar && bash scripts/nrp/verify_bundle.sh nrp_<name>.sha256
set -euo pipefail
WHAT="${1:?usage: make_inputs_bundle.sh inputs|checkpoints|mace|all [outdir]}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${2:-$ROOT/.local/nrp_inputs}"
case "$WHAT" in inputs|checkpoints|mace) SETS="$WHAT" ;; all) SETS="inputs checkpoints mace" ;;
  *) echo "bundle must be inputs, checkpoints, mace or all" >&2; exit 2 ;; esac
cd "$ROOT"
mkdir -p "$OUT"
for SET in $SETS; do
  LIST="$OUT/nrp_$SET.files"
  SUMS="$OUT/nrp_$SET.sha256"
  python3 - "$SET" "$LIST" "$SUMS" <<'PY'
import csv, hashlib, json, pathlib, sys
kind, list_path, sums_path = sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
files, bad = [], []
if kind == "inputs":
    for line in pathlib.Path("data/graphs_v1_manifest.sha256").read_text().splitlines():
        if line and not line.startswith("#"):
            s, n = line.split("  ", 1)
            f = f"data/processed/graphs_v1/{n}"
            files.append(f)
            bad += [f] if sha(f) != s else []
    files += ["data/processed/universe_v1.parquet", "data/processed/unit_cells_v1.json",
              "data/processed/tiling_map_v1.parquet"]
    tiling = json.loads(pathlib.Path("results/tiling_v1.json").read_text())["payload"]["map"]
    bad += ["data/processed/tiling_map_v1.parquet"] if sha("data/processed/tiling_map_v1.parquet") != tiling["sha256"] else []
    db = "data/raw/unpacked/oxygen_vacancies_db/site_info"      # release directory = formula (checked in S11)
    files += sorted(f"{db}/{r['formula']}/supercell.cif" for r in csv.DictReader(open("data/tiling_summary_v1.csv")))
elif kind == "checkpoints":
    man = json.loads(pathlib.Path("results/checkpoint_manifest.json").read_text())
    man = man.get("payload", man)["files"]
    for n in sorted(man):
        f = f"checkpoints/{n}"
        files.append(f)
        bad += [f] if sha(f) != man[n]["sha256"] else []
else:
    mace = json.loads(pathlib.Path("results/mace_model.json").read_text())["payload"]
    files.append(mace["cache_path"])
    bad += [mace["cache_path"]] if sha(mace["cache_path"]) != mace["sha256"] else []
if bad:
    raise SystemExit(f"{len(bad)} files differ from their tracked records, e.g. {bad[:3]}")
list_path.write_text("\n".join(files) + "\n")
sums_path.write_text("".join(f"{sha(f)}  {f}\n" for f in files))
total = sum(pathlib.Path(f).stat().st_size for f in files)
print(f"{kind}: {len(files)} files, {total / 2**20:.1f} MiB, every file matches its tracked record")
PY
  # -h follows the symlinks of a worktree; members keep their repo-relative paths
  tar -chf "$OUT/nrp_$SET.tar" -T "$LIST"
  tar -rf "$OUT/nrp_$SET.tar" -C "$OUT" "$(basename "$SUMS")"
  shasum -a 256 "$OUT/nrp_$SET.tar" | sed "s#  .*#  nrp_$SET.tar#" > "$OUT/nrp_$SET.tar.sha256"
  rm -f "$LIST"
  echo "wrote $OUT/nrp_$SET.tar ($(du -h "$OUT/nrp_$SET.tar" | cut -f1)), nrp_$SET.sha256 and nrp_$SET.tar.sha256"
done

#!/usr/bin/env bash
# Runs on the Mac: pack the untracked inputs of the cluster stages into one tarball with a sha256 list
# (docs/nrp_runbook.md, section 2). Nothing is sent anywhere; the tarball is handed to the second author.
#   bash scripts/nrp/make_inputs_bundle.sh train|infer [outdir]      (default outdir .local/nrp_inputs)
# train: graph shards (checked against data/graphs_v1_manifest.sha256) and the universe table; enough for loco,
#        moment, cgcnn, capped, cv and precision.
# infer: train plus the S09 checkpoints (checked against results/checkpoint_manifest.json), the DFT unit cells, the
#        tiling map, the MACE-MP-0 medium weights (checked against results/mace_model.json) and the 818 release
#        supercell CIFs; needed by relax, peval, embed and geomeval.
# On the cluster, from the checkout root: tar -xf nrp_inputs_<set>.tar && sha256sum -c --quiet nrp_inputs_<set>.sha256
set -euo pipefail
SET="${1:?usage: make_inputs_bundle.sh train|infer [outdir]}"
case "$SET" in train|infer) ;; *) echo "set must be train or infer" >&2; exit 2 ;; esac
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${2:-$ROOT/.local/nrp_inputs}"
cd "$ROOT"
mkdir -p "$OUT"
LIST="$OUT/nrp_inputs_$SET.files"
SUMS="$OUT/nrp_inputs_$SET.sha256"
python3 - "$SET" "$LIST" "$SUMS" <<'PY'
import csv, hashlib, json, pathlib, sys
kind, list_path, sums_path = sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
files, bad = [], []
for line in pathlib.Path("data/graphs_v1_manifest.sha256").read_text().splitlines():
    if line and not line.startswith("#"):
        s, n = line.split("  ", 1)
        f = f"data/processed/graphs_v1/{n}"
        files.append(f)
        bad += [f] if sha(f) != s else []
files.append("data/processed/universe_v1.parquet")
if kind == "infer":
    man = json.loads(pathlib.Path("results/checkpoint_manifest.json").read_text())
    man = man.get("payload", man)["files"]
    for n in sorted(man):
        f = f"checkpoints/{n}"
        files.append(f)
        bad += [f] if sha(f) != man[n]["sha256"] else []
    mace = json.loads(pathlib.Path("results/mace_model.json").read_text())["payload"]
    bad += [mace["cache_path"]] if sha(mace["cache_path"]) != mace["sha256"] else []
    files += ["data/processed/unit_cells_v1.json", "data/processed/tiling_map_v1.parquet", mace["cache_path"]]
    db = "data/raw/unpacked/oxygen_vacancies_db/site_info"      # release directory = formula (checked in S11)
    files += sorted(f"{db}/{r['formula']}/supercell.cif" for r in csv.DictReader(open("data/tiling_summary_v1.csv")))
if bad:
    raise SystemExit(f"{len(bad)} inputs differ from their tracked manifests, e.g. {bad[:3]}")
list_path.write_text("\n".join(files) + "\n")
sums_path.write_text("".join(f"{sha(f)}  {f}\n" for f in files))
total = sum(pathlib.Path(f).stat().st_size for f in files)
print(f"{kind}: {len(files)} files, {total / 2**20:.1f} MiB, every file matches its tracked manifest")
PY
# -h follows the symlinks of a worktree; members keep their repo-relative paths
tar -chf "$OUT/nrp_inputs_$SET.tar" -T "$LIST"
tar -rf "$OUT/nrp_inputs_$SET.tar" -C "$OUT" "$(basename "$SUMS")"
shasum -a 256 "$OUT/nrp_inputs_$SET.tar" | sed "s#  .*#  nrp_inputs_$SET.tar#" > "$OUT/nrp_inputs_$SET.tar.sha256"
echo "wrote $OUT/nrp_inputs_$SET.tar ($(du -h "$OUT/nrp_inputs_$SET.tar" | cut -f1)) and its .sha256"

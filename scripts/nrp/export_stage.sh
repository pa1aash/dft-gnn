#!/usr/bin/env bash
# Runs on the cluster, in a checkout whose results are on the shared volume: commit the finished runs of one stage
# to the branch nrp/<stage> (docs/nrp_runbook.md, section 5). The live checkout never changes branch: the commit is
# made in a separate worktree (../<checkout>-nrp-<stage>) that starts at the tag nrp-code-v1.
#   bash scripts/nrp/export_stage.sh <stage> [--queue jobs] [--no-push]
# Re-running adds the runs finished since the last export (a new commit on the same branch).
# Committed: the result JSONs and the tracked artefacts (prediction parquets) of the stage's done jobs, plus
#            results/nrp/artefacts/<stage>.sha256: one "sha256  size  path" line per gitignored artefact
#            (checkpoints, relaxed structures, embeddings), which stay on NRP storage. Each hash is recomputed from
#            the file and must equal the hash in its result record, or nothing is committed.
set -euo pipefail
STAGE="${1:?usage: export_stage.sh <stage> [--queue jobs] [--no-push]}"; shift
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
QUEUE="$ROOT/jobs"; PUSH=1
while [ $# -gt 0 ]; do
  case "$1" in
    --queue) QUEUE="$2"; shift 2 ;;
    --no-push) PUSH=0; shift ;;
    *) echo "unknown arg $1" >&2; exit 2 ;;
  esac
done
cd "$ROOT"
NAME="$(git config user.name || true)"; EMAIL="$(git config user.email || true)"
[ "$NAME" = "aidenlee" ] && [ "$EMAIL" = "aiden.lee.sd@gmail.com" ] || {
  echo "git identity is '$NAME <$EMAIL>'; set: git config user.name aidenlee; git config user.email aiden.lee.sd@gmail.com" >&2
  exit 2; }
git rev-parse --verify -q "nrp-code-v1^{commit}" >/dev/null || { echo "tag nrp-code-v1 missing (git fetch --tags)" >&2; exit 2; }
BR="nrp/$STAGE"
WT="$ROOT/../$(basename "$ROOT")-nrp-$STAGE"
LIST="$(mktemp)"
ARTS="$(mktemp)"
python3 - "$QUEUE" "$STAGE" "$LIST" "$ARTS" <<'PY'
import hashlib, json, pathlib, subprocess, sys
queue, stage, out, arts_out = pathlib.Path(sys.argv[1]), sys.argv[2], pathlib.Path(sys.argv[3]), pathlib.Path(sys.argv[4])
root = pathlib.Path.cwd()
files, recorded = [], {}
for f in sorted((queue / "done").glob("*.json")):
    job = json.loads(f.read_text())
    if job.get("stage") != stage:
        continue
    res = pathlib.Path(job["result"])
    res = res if res.is_absolute() else root / res
    pay = json.loads(res.read_text())["payload"]
    files.append(str(res.resolve().relative_to(root.resolve())))
    arts = [pay[k] for k in ("predictions", "checkpoint") if isinstance(pay.get(k), dict)] + list(pay.get("artifacts", []))
    files += [a["path"] for a in arts]
    recorded.update({a["path"]: a["sha256"] for a in arts})
ignored = set(subprocess.run(["git", "check-ignore", "--stdin"], input="\n".join(files), capture_output=True,
                             text=True).stdout.split())
keep = sorted(set(f for f in files if f not in ignored))
out.write_text("\n".join(keep) + ("\n" if keep else ""))
lines, bad = [], []
for path in sorted(set(files) & ignored):
    p = root / path
    h = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    if h != recorded[path]:
        bad.append(path)
    else:
        lines.append(f"{h}  {p.stat().st_size}  {path}")
if bad:
    raise SystemExit(f"{len(bad)} gitignored artefacts are missing or differ from their records, e.g. {bad[:3]}")
arts_out.write_text("\n".join(lines) + ("\n" if lines else ""))
print(f"{stage}: {len(keep)} tracked files to commit, {len(lines)} gitignored artefacts recorded (they stay on NRP)")
PY
[ -s "$LIST" ] || { echo "no done jobs of stage $STAGE"; rm -f "$LIST" "$ARTS"; exit 1; }
if [ ! -d "$WT" ]; then
  # an export made earlier from another pod: continue the pushed branch instead of restarting at the tag
  git rev-parse --verify -q "refs/heads/$BR" >/dev/null || git fetch -q origin "refs/heads/$BR:refs/heads/$BR" 2>/dev/null || true
  if git rev-parse --verify -q "refs/heads/$BR" >/dev/null; then git worktree add -q "$WT" "$BR"
  else git worktree add -q -b "$BR" "$WT" nrp-code-v1; fi
fi
rsync -aL --files-from="$LIST" "$ROOT/" "$WT/"
mkdir -p "$WT/results/nrp/artefacts"
MANI="$WT/results/nrp/artefacts/$STAGE.sha256"
touch "$MANI"
cat "$ARTS" "$MANI" | sed '/^$/d' | sort -u -k3,3 -k1,1 > "$MANI.tmp"
mv "$MANI.tmp" "$MANI"
[ -s "$MANI" ] || rm -f "$MANI"
rm -f "$LIST" "$ARTS"
cd "$WT"
git add results
if git diff --cached --quiet; then echo "nothing new to commit on $BR"
else
  N=$(git diff --cached --name-only --diff-filter=A -- 'results/*.json' 'results/*/*.json' | grep -vc '/predictions/' || true)
  git commit -q -m "results(nrp): $STAGE, $N new run records from the cluster"
  echo "committed on $BR: $(git log -1 --format='%h %s')"
fi
if [ "$PUSH" = 1 ]; then git push -q origin "$BR" && echo "pushed $BR"; fi
echo "checkpoints and other gitignored artefacts stay on NRP storage; their hashes are in results/nrp/artefacts/$STAGE.sha256"

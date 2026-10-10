#!/usr/bin/env bash
# Runs on the cluster, in the shared checkout: commit the finished runs of one stage to the branch nrp/<stage> and
# pack their gitignored artefacts (docs/nrp_runbook.md, section 5). The live checkout never changes branch: the
# commit is made in a separate worktree (../<checkout>-nrp-<stage>) that starts at the tag nrp-code-v1.
#   bash scripts/nrp/export_stage.sh <stage> [--queue jobs] [--no-push]
# Re-running adds the runs finished since the last export (a new commit on the same branch).
# Committed: the result JSONs and the tracked artefacts (prediction parquets) of the stage's done jobs.
# Packed:    every member, including checkpoints and the relaxed-structure / embedding files, into outbox/ via
#            scripts/queue/outbox.py pack --stage <stage>; hand the tarball and its .sha256 to the Mac.
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
python3 - "$QUEUE" "$STAGE" "$LIST" <<'PY'
import json, pathlib, subprocess, sys
queue, stage, out = pathlib.Path(sys.argv[1]), sys.argv[2], pathlib.Path(sys.argv[3])
root = pathlib.Path.cwd()
files = []
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
ignored = set(subprocess.run(["git", "check-ignore", "--stdin"], input="\n".join(files), capture_output=True,
                             text=True).stdout.split())
keep = sorted(set(f for f in files if f not in ignored))
out.write_text("\n".join(keep) + ("\n" if keep else ""))
print(f"{stage}: {len(keep)} tracked files to commit, {len(set(files) & ignored)} gitignored artefacts to pack")
PY
[ -s "$LIST" ] || { echo "no done jobs of stage $STAGE"; rm -f "$LIST"; exit 1; }
if [ ! -d "$WT" ]; then
  if git rev-parse --verify -q "refs/heads/$BR" >/dev/null; then git worktree add -q "$WT" "$BR"
  else git worktree add -q -b "$BR" "$WT" nrp-code-v1; fi
fi
rsync -a --files-from="$LIST" "$ROOT/" "$WT/"
rm -f "$LIST"
cd "$WT"
git add results
if git diff --cached --quiet; then echo "nothing new to commit on $BR"
else
  N=$(git diff --cached --name-only --diff-filter=A -- 'results/*.json' 'results/*/*.json' | grep -vc '/predictions/' || true)
  git commit -q -m "results(nrp): $STAGE, $N new run records from the cluster"
  echo "committed on $BR: $(git log -1 --format='%h %s')"
fi
if [ "$PUSH" = 1 ]; then git push -q origin "$BR" && echo "pushed $BR"; fi
cd "$ROOT"
python3 scripts/queue/outbox.py pack --stage "$STAGE" --queue "$QUEUE"
echo "hand the outbox/outbox_${STAGE}_*.tar.gz just written and its .sha256 to the Mac (see docs/nrp_runbook.md)"

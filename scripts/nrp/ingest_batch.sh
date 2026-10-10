#!/usr/bin/env bash
# Runs on the Mac: check a results branch pushed from the cluster before anything is merged (docs/nrp_runbook.md, 6).
#   bash scripts/nrp/ingest_batch.sh nrp/<stage> [--outbox outbox_<stage>_<time>.tar.gz] [--base main] [--tracked-only]
#                                                [--no-fetch]
# Checks, over the commits of origin/<branch> that are not in <base>:
#   1. identities: every author and committer is an allowed identity, and no commit message holds a banned string
#      (the local hook .git/hooks/_audit.sh, which also defines the banned pattern; this tracked file never names it);
#   2. content: no added line and no added path matches the banned pattern;
#   3. code: the branch contains the tag nrp-code-v1 and changes nothing under src/ scripts/ configs/ splits/ specs/
#      relative to it (results only);
#   4. artefacts: every results JSON added or changed on the branch names its run id as its file name, its run id is
#      listed in specs/*.jsonl (ids computed with nrp-code-v1; a recorded code_ref must name that tag), and every
#      artefact it records (predictions, checkpoint, task artifacts) has the recorded
#      sha256: committed artefacts are hashed from the branch, gitignored ones (checkpoints, relaxed structures,
#      embeddings) from the local files unpacked from the outbox tarball (--tracked-only skips those);
#   5. counts: results per stage, by matching run ids against specs/*.jsonl, against the stage totals.
# --outbox: before step 4, check the tarball against its .sha256 and its inner manifest and place only its gitignored
# members (checkpoints, relaxed structures, embeddings; never a tracked path, never overwriting a different file), so
# the later merge cannot collide with untracked copies of tracked files.
# It merges nothing and changes no tracked file. Exit status 0 only if every check passes.
set -euo pipefail
BRANCH="${1:?usage: ingest_batch.sh nrp/<stage> [--outbox <tar.gz>] [--base main] [--tracked-only] [--no-fetch]}"; shift
BASE=main; TRACKED_ONLY=0; FETCH=1; OUTBOX=""
while [ $# -gt 0 ]; do
  case "$1" in
    --base) BASE="$2"; shift 2 ;;
    --tracked-only) TRACKED_ONLY=1; shift ;;
    --no-fetch) FETCH=0; shift ;;
    --outbox) OUTBOX="$2"; shift 2 ;;
    *) echo "unknown arg $1" >&2; exit 2 ;;
  esac
done
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
HOOKS="$(git rev-parse --git-common-dir)/hooks"
[ -x "$HOOKS/_audit.sh" ] || { echo "missing $HOOKS/_audit.sh (local hook)" >&2; exit 2; }
PAT="$(sed -n "s/^PAT='\(.*\)'$/\1/p" "$HOOKS/_audit.sh")"
[ -n "$PAT" ] || { echo "could not read the banned pattern from $HOOKS/_audit.sh" >&2; exit 2; }
REF="origin/$BRANCH"
if [ "$FETCH" = 1 ]; then
  if command -v gtimeout >/dev/null 2>&1; then gtimeout 120 git fetch -q origin "$BRANCH" --tags; else git fetch -q origin "$BRANCH" --tags; fi
fi
git rev-parse --verify -q "$REF" >/dev/null || { echo "no ref $REF" >&2; exit 2; }
RANGE="$BASE..$REF"
FAIL=0
N=$(git rev-list --count "$RANGE")
echo "branch $REF: $N commits not in $BASE"
[ "$N" -gt 0 ] || { echo "nothing to ingest"; exit 1; }

# 1. identities and messages
if "$HOOKS/_audit.sh" "$RANGE"; then echo "1 identities and messages: OK"; else echo "1 identities and messages: FAIL"; FAIL=1; fi
echo "  author set: $(git log --format='%an <%ae>' "$RANGE" | sort -u | paste -sd ';' -)"

# 2. added lines and paths
MB="$(git merge-base "$BASE" "$REF")"
HITS="$( { git diff --no-color -U0 "$MB" "$REF" | grep -E '^\+' | grep -Ev '^\+\+\+ ' | grep -Eic "$PAT" ; } || true)"
PHITS="$( { git diff --name-only "$MB" "$REF" | grep -Eic "$PAT" ; } || true)"
if [ "${HITS:-0}" = 0 ] && [ "${PHITS:-0}" = 0 ]; then echo "2 banned pattern in added lines and paths: OK"
else echo "2 banned pattern: FAIL ($HITS lines, $PHITS paths)"; FAIL=1; fi

# 3. code unchanged since the pinned tag
TAG=nrp-code-v1
if ! git rev-parse --verify -q "$TAG^{commit}" >/dev/null; then echo "3 code: FAIL (tag $TAG missing locally)"; FAIL=1
elif ! git merge-base --is-ancestor "$TAG" "$REF"; then echo "3 code: FAIL ($REF does not contain $TAG)"; FAIL=1
else
  CH="$(git diff --name-only "$TAG" "$REF" -- src scripts configs splits specs)"
  if [ -z "$CH" ]; then echo "3 code unchanged since $TAG: OK"; else echo "3 code: FAIL, changed since $TAG:"; echo "$CH" | head -20; FAIL=1; fi
fi

# outbox: place the gitignored artefacts
if [ -n "$OUTBOX" ]; then
  if python3 - "$OUTBOX" <<'PY'
import hashlib, pathlib, subprocess, sys, tarfile
tar_path = pathlib.Path(sys.argv[1])
sha = lambda b: hashlib.sha256(b).hexdigest()
side = tar_path.with_name(tar_path.name + ".sha256")
if not side.is_file() or side.read_text().split()[0] != sha(tar_path.read_bytes()):
    raise SystemExit(f"{tar_path}: missing or mismatching .sha256")
placed = same = 0
with tarfile.open(tar_path, "r:gz") as tar:
    man = dict(reversed(ln.split("  ", 1)) for ln in tar.extractfile("OUTBOX_MANIFEST.sha256").read().decode().splitlines())
    names = [n for n in man if not n.startswith("/") and ".." not in pathlib.Path(n).parts]
    if len(names) != len(man):
        raise SystemExit("unsafe member paths")
    ignored = set(subprocess.run(["git", "check-ignore", "--stdin"], input="\n".join(names), capture_output=True,
                                 text=True).stdout.split())
    for n in sorted(ignored):
        data = tar.extractfile(n).read()
        if sha(data) != man[n]:
            raise SystemExit(f"{n}: member differs from the inner manifest")
        dst = pathlib.Path(n)
        if dst.exists():
            if sha(dst.read_bytes()) != man[n]:
                raise SystemExit(f"{n}: a different file already exists; refusing to overwrite")
            same += 1
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        placed += 1
print(f"outbox {tar_path.name}: {len(man)} members verified; {placed} gitignored artefacts placed, {same} already present, "
      f"{len(man) - len(ignored)} tracked members left to the branch")
PY
  then echo "outbox: OK"; else echo "outbox: FAIL"; FAIL=1; fi
fi

# 4-5. artefact hashes and counts per stage
if python3 - "$MB" "$REF" "$TRACKED_ONLY" "$TAG" <<'PY'
import collections, hashlib, json, pathlib, subprocess, sys
mb, ref, tracked_only, tag = sys.argv[1], sys.argv[2], sys.argv[3] == "1", sys.argv[4]
git = lambda *a: subprocess.run(["git", *a], check=True, capture_output=True).stdout
changed = [p for p in git("diff", "--name-only", "--diff-filter=AM", mb, ref, "--", "results").decode().split()
           if p.endswith(".json")]
tree = set(git("ls-tree", "-r", "--name-only", ref, "--", "results").decode().split())
stage_of, expected = {}, collections.Counter()
for f in sorted(pathlib.Path("specs").glob("*.jsonl")):
    for line in f.read_text().splitlines():
        j = json.loads(line)
        stage_of[j["run_id"]] = j["stage"]
        expected[j["stage"]] += 1
def blob_sha(path):
    return hashlib.sha256(git("show", f"{ref}:{path}")).hexdigest()
bad, missing, found, unknown, n = [], [], collections.Counter(), [], 0
for p in changed:
    try:
        pay = json.loads(git("show", f"{ref}:{p}"))["payload"]
    except (KeyError, json.JSONDecodeError, TypeError):
        continue                                    # not a write_result record (e.g. a manifest)
    if not isinstance(pay, dict) or "run_id" not in pay:
        continue
    n += 1
    rid = pay["run_id"]
    if pathlib.Path(p).stem != rid:
        bad.append(f"{p}: file name differs from run_id {rid}")
    # a run id listed in specs/ was computed with the tag; a recorded code_ref must also name it
    ref_used = pay.get("code_ref") or (pay.get("spec") or {}).get("code_ref")
    if ref_used is not None and ref_used != tag:
        bad.append(f"{p}: code_ref {ref_used!r} is not {tag}")
    arts = [pay[k] for k in ("predictions", "checkpoint") if isinstance(pay.get(k), dict)] + list(pay.get("artifacts", []))
    for a in arts:
        path = a["path"]
        if path in tree:
            if blob_sha(path) != a["sha256"]:
                bad.append(f"{p}: {path} sha256 differs (branch)")
        elif tracked_only:
            continue
        elif pathlib.Path(path).is_file():
            if hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest() != a["sha256"]:
                bad.append(f"{p}: {path} sha256 differs (local, from the outbox tarball)")
        else:
            missing.append(path)
    if rid in stage_of:
        found[stage_of[rid]] += 1
    else:
        unknown.append(rid)
print(f"4 artefacts: {n} result records checked, {len(bad)} problems, {len(missing)} gitignored artefacts not present")
for b in bad[:20]:
    print("  BAD", b)
for m in missing[:10]:
    print("  MISSING", m, "(unpack the stage's outbox tarball with scripts/queue/outbox.py unpack)")
print("5 counts per stage (results on this branch / specs):")
for st in sorted(set(found) | set(expected), key=lambda s: list(expected).index(s) if s in expected else 99):
    print(f"  {st:10s} {found.get(st, 0):5d} / {expected.get(st, 0)}")
if unknown:
    print(f"  {len(unknown)} result run ids are in no spec file, e.g. {unknown[:5]}")
sys.exit(1 if bad or missing or unknown or n == 0 else 0)
PY
then echo "4-5 artefacts and counts: OK"; else echo "4-5 artefacts and counts: FAIL"; FAIL=1; fi

if [ "$FAIL" = 0 ]; then
  echo "INGEST CHECK PASSED for $REF. Nothing was merged. To merge: git merge --no-ff $REF -m 'merge(nrp): <stage> results'"
else
  echo "INGEST CHECK FAILED for $REF. Nothing was merged."; exit 1
fi

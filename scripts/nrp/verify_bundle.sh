#!/usr/bin/env bash
# Verify every sha256 in a bundle manifest and nothing else (docs/nrp_runbook.md, section 2).
#   bash scripts/nrp/verify_bundle.sh <manifest.sha256> [root]
# Each manifest line is "<sha256>  <path>"; <path> is resolved against [root] (default: the current directory).
# Prints one line per mismatch or missing file and a summary; exit status 0 only if every line verifies.
set -euo pipefail
MAN="${1:?usage: verify_bundle.sh <manifest.sha256> [root]}"
ROOT="${2:-.}"
[ -f "$MAN" ] || { echo "no manifest $MAN" >&2; exit 2; }
if command -v sha256sum >/dev/null 2>&1; then HASH="sha256sum"; else HASH="shasum -a 256"; fi
n=0; bad=0
while IFS= read -r line || [ -n "$line" ]; do
  [ -z "$line" ] && continue
  want="${line%%  *}"; path="${line#*  }"
  n=$((n + 1))
  if [ ! -f "$ROOT/$path" ]; then echo "MISSING $path"; bad=$((bad + 1)); continue; fi
  got="$($HASH "$ROOT/$path" | cut -d' ' -f1)"
  if [ "$got" != "$want" ]; then echo "MISMATCH $path"; bad=$((bad + 1)); fi
done < "$MAN"
if [ "$bad" -eq 0 ] && [ "$n" -gt 0 ]; then echo "OK: $n of $n files verify ($MAN)"; exit 0; fi
echo "FAIL: $bad of $n files do not verify ($MAN)"; exit 1

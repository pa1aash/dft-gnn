#!/bin/sh
# Download the current MDPI LaTeX template (ACS style, used by Crystals) into paper/template/.
# The URL is the one recorded in docs/venue.md (section C). The zip carries no licence and MDPI
# restricts it to journal submission, so paper/template/ is listed in .git/info/exclude and the
# template is never committed. Retrieval is headless (curl only).
set -eu
URL="${MDPI_TEMPLATE_URL:-https://res.mdpi.com/data/MDPI_template_ACS.zip?v=20260911}"
here=$(cd "$(dirname "$0")/.." && pwd)
dest="$here/template"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

curl -sSfL --retry 3 -A "Mozilla/5.0" -o "$tmp/template.zip" "$URL"
rm -rf "$dest"
mkdir -p "$dest"
unzip -q "$tmp/template.zip" -d "$tmp/unz"
# the zip may wrap its contents in one top-level folder
src="$tmp/unz"
if [ ! -f "$src/template.tex" ]; then
  src=$(dirname "$(find "$tmp/unz" -name template.tex | head -1)")
fi
cp -R "$src"/. "$dest"/
# the class converts its EPS logos by shell calls that ignore TEXINPUTS, so expose
# Definitions/ next to main.tex as well (untracked; see paper/.gitignore)
ln -sfn template/Definitions "$here/Definitions"
{
  echo "url: $URL"
  echo "fetched_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "sha256: $(shasum -a 256 "$tmp/template.zip" | cut -d' ' -f1)"
  echo "bytes: $(wc -c < "$tmp/template.zip" | tr -d ' ')"
} > "$dest/FETCHED.txt"
cat "$dest/FETCHED.txt"
grep -m1 'ProvidesClass' "$dest/Definitions/mdpi.cls" || true

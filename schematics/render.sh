#!/bin/sh
# Build one schematic with latexmk and write a 200 dpi PNG preview to $2.
# usage: sh render.sh fig_name [preview_dir]   (default preview dir: ../.cache/schematics, untracked)
set -e
cd "$(dirname "$0")"
out="${2:-../.cache/schematics}"; mkdir -p "$out"
OMP_NUM_THREADS=3 nice -n 15 latexmk -g -r latexmkrc "$1.tex" >/dev/null 2>&1 || { grep -E '^!|^\./' "$1.log" | head; exit 1; }
pdfinfo "$1.pdf" | awk '/Page size/ {printf "%s: %.1f x %.1f mm\n", "'"$1"'", $3/72*25.4, $5/72*25.4}'
pdffonts "$1.pdf" | awk 'NR>2 && $(NF-4)!="yes" {print "NOT EMBEDDED:", $0}'
pdftoppm -r 200 -png -singlefile "$1.pdf" "$out/$1"

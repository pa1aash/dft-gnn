"""Check the number macros used in paper/sections/*.tex (and the Supplementary Materials, paper/si).

1. Lists every \\num<Name> macro used in the section files and fails if any is not defined in
   paper/generated/numbers.tex (run make_numbers.py first).
2. Fails if section prose contains a typed number. Comments, chemical-formula subscripts, digits
   that are part of a name (B0, D3, MACE-MP-0), the
   arguments of referencing commands (\\cite, \\ref, \\label, \\input, ...) and blocks between
   "% verbatim-begin" and "% verbatim-end" (text quoted verbatim from a third party) are exempt.

The Supplementary Materials (W3) are scanned too: paper/si/*.tex and paper/si/sections/*.tex. Tables that
paper/si/tables/ holds are \\input and, like paper/tables/, are not scanned. Pass --dir (repeatable, relative to
paper/) to scan other directories instead of the default set.

Usage: python paper/tools/check_macros.py [--list] [--dir DIR ...]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
# directories scanned by default (relative to paper/); the SI entries are skipped while they do not exist
DEFAULT_DIRS = ("sections", "si", "si/sections")
USE = re.compile(r"\\(num[A-Z][A-Za-z]*)")
DEF = re.compile(r"\\newcommand\{\\(num[A-Z][A-Za-z]*)\}")
# commands whose (first) argument is a key or a path, not prose
ARG_CMDS = ("cite", "citep", "citet", "ref", "eqref", "label", "input", "include",
            "InputIfFileExists", "includegraphics", "figph", "url", "href", "textsubscript",
            "linksupplementary", "begin", "end", "hspace", "vspace", "setcounter")


def strip_comments(line: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", line)


def prose(text: str) -> list[tuple[int, str]]:
    """Lines of prose with exempt material removed, numbered from 1."""
    out, verbatim = [], False
    for i, raw in enumerate(text.splitlines(), 1):
        s = raw.strip()
        if s.startswith("% verbatim-begin"):
            verbatim = True
            continue
        if s.startswith("% verbatim-end"):
            verbatim = False
            continue
        if verbatim:
            continue
        line = strip_comments(raw)
        line = re.sub(r"\[[^\]]*\]", "", line)  # optional arguments (widths, placement)
        for cmd in ARG_CMDS:
            line = re.sub(rf"\\{cmd}\*?(\{{[^{{}}]*\}})+", " ", line)
        line = re.sub(r"_\{?[0-9.]+\}?", "", line)  # formula subscripts: SrTiO$_3$, O$_{2}$
        line = USE.sub(" ", line)
        line = re.sub(r"\\[A-Za-z]+", " ", line)  # remaining command names
        out.append((i, line))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true", help="print every macro used and its file")
    ap.add_argument("--numbers", type=Path, default=PAPER / "generated" / "numbers.tex")
    ap.add_argument("--dir", action="append", dest="dirs", metavar="DIR",
                    help="directory of .tex files to scan, relative to paper/ (repeatable)")
    a = ap.parse_args(argv)

    if not a.numbers.exists():
        print(f"missing {a.numbers}; run paper/tools/make_numbers.py", file=sys.stderr)
        return 2
    defined = set(DEF.findall(a.numbers.read_text()))

    used: dict[str, set[str]] = {}
    typed = []
    files = [f for d in (a.dirs or DEFAULT_DIRS) for f in sorted((PAPER / d).glob("*.tex"))]
    for f in files:
        text = f.read_text()
        for line in text.splitlines():
            for m in USE.findall(strip_comments(line)):
                used.setdefault(m, set()).add(f.name)
        for i, line in prose(text):
            # digits glued to a name (B0, D3, MACE-MP-0) are part of an identifier, not a number
            for m in re.finditer(r"(?<![A-Za-z])(?<![A-Za-z]-)[0-9]+", line):
                typed.append(f"{f.relative_to(PAPER)}:{i}: typed number '{m.group()}'")

    missing = sorted(m for m in used if m not in defined)
    if a.list:
        for m in sorted(used):
            print(f"\\{m}\t{'ok' if m in defined else 'UNDEFINED'}\t{','.join(sorted(used[m]))}")
    for m in missing:
        print(f"undefined: \\{m} (used in {', '.join(sorted(used[m]))})", file=sys.stderr)
    for t in typed:
        print(t, file=sys.stderr)
    print(f"{len(used)} number macros used, {len(missing)} undefined, {len(typed)} typed numbers")
    return 1 if missing or typed else 0


if __name__ == "__main__":
    raise SystemExit(main())

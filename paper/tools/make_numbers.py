"""Write paper/generated/numbers.tex: one \\newcommand per number in the named result records.

Reads every results/<name>.json whose stem equals its record's ``name`` field (the named analysis
records written by write_result; the per-run records named by a hex run id are skipped) and flattens the numeric
leaves of its ``payload``. The macro naming and formatting rules are documented in
paper/tools/README.md. A provenance table (macro, value, source pointer) is written next to the macros
as paper/generated/numbers.tsv.

Usage: python paper/tools/make_numbers.py [--results results] [--out paper/generated]
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# subtrees that are never flattened (per-replicate detail, run metadata)
SKIP_KEYS = {"config", "package_versions", "seeds", "input", "inputs"}
SKIP_KEY_PARTS = ("per_resample",)
# a list of dicts is flattened when its items carry one of these identifying keys
ID_KEYS = ("step", "name", "id", "model", "element", "site_label", "formula", "budget")
MAX_SCALAR_LIST = 12
# per-run records written by the training jobs are named by a 16-hex-digit run id
RUN_RECORD = re.compile(r"^[0-9a-f]{16}$")

ONES = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
        "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen",
        "Nineteen"]
TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def words(n: int) -> str:
    """Spell a non-negative integer in CamelCase English (654 -> SixHundredFiftyFour)."""
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + (ONES[n % 10] if n % 10 else "")
    for size, name in ((10**9, "Billion"), (10**6, "Million"), (1000, "Thousand"), (100, "Hundred")):
        if n >= size:
            head, rest = divmod(n, size)
            return words(head) + name + (words(rest) if rest else "")
    raise AssertionError(n)


def camel(token: str) -> str:
    """One name component: letters kept, digit runs spelled, everything else a word break."""
    out = []
    # decimals keep every fractional digit, so 0.05 and 0.5 stay distinct
    token = re.sub(r"(\d)\.(\d+)", lambda m: m.group(1) + "_Point_"
                   + "_".join(ONES[int(d)] for d in m.group(2)), token)
    for part in re.split(r"[^A-Za-z0-9]+", token):
        for piece in re.findall(r"[A-Za-z]+|[0-9]+", part):
            out.append(words(int(piece)) if piece.isdigit() else piece[0].upper() + piece[1:])
    return "".join(out)


def fmt(x: float | int) -> str:
    """LaTeX rendering of one number (rules in README.md)."""
    if isinstance(x, bool):
        raise TypeError("bool")
    if isinstance(x, float) and x.is_integer() and abs(x) < 1e15:
        x = int(x)
    if isinstance(x, int):
        s = f"{abs(x):,}" if abs(x) >= 10000 else str(abs(x))
        s = s.replace(",", "{,}")
    elif x == 0:
        s = "0.000"
    elif abs(x) >= 1000:
        s = f"{abs(x):,.0f}".replace(",", "{,}")
    elif abs(x) >= 0.001:
        s = f"{abs(x):.3f}"
    else:
        m, e = f"{abs(x):.1e}".split("e")
        s = f"{m}\\times10^{{{int(e)}}}"
    return f"\\ensuremath{{{'-' if x < 0 else ''}{s}}}"


def is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def skip(key: str) -> bool:
    return key in SKIP_KEYS or any(p in key for p in SKIP_KEY_PARTS)


def flatten(obj, path: list[str], out: list[tuple[list[str], float]]) -> None:
    if is_num(obj):
        out.append((path, obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if not skip(str(k)):
                flatten(v, path + [str(k)], out)
    elif isinstance(obj, list):
        if not obj:
            return
        key = path[-1] if path else ""
        if len(obj) == 2 and all(is_num(v) for v in obj) and re.search(r"(^|_)ci($|_)", key):
            out.append((path + ["lo"], obj[0]))
            out.append((path + ["hi"], obj[1]))
        elif all(is_num(v) for v in obj) and len(obj) <= MAX_SCALAR_LIST:
            for i, v in enumerate(obj, 1):
                out.append((path + [f"item{i}"], v))
        elif all(isinstance(v, dict) for v in obj):
            idk = next((k for k in ID_KEYS if all(k in v for v in obj)), None)
            if idk and len({str(v[idk]) for v in obj}) == len(obj):
                for v in obj:
                    flatten({k: w for k, w in v.items() if k != idk}, path + [str(v[idk])], out)


def named_records(results: Path) -> list[Path]:
    keep = []
    for p in sorted(results.glob("*.json")):
        try:
            rec = json.loads(p.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if RUN_RECORD.match(p.stem):
            continue
        if isinstance(rec, dict) and rec.get("name") == p.stem and "payload" in rec:
            keep.append(p)
    return keep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--results", type=Path, default=ROOT / "results")
    ap.add_argument("--out", type=Path, default=ROOT / "paper" / "generated")
    a = ap.parse_args(argv)

    macros: dict[str, tuple[str, str, str]] = {}
    clashes = []
    files = named_records(a.results)
    for p in files:
        rec = json.loads(p.read_text())
        leaves: list[tuple[list[str], float]] = []
        flatten(rec["payload"], [], leaves)
        stem = camel(p.stem)
        for path, val in leaves:
            name = "num" + stem + "".join(camel(c) for c in path)
            src = f"results/{p.name}#/payload/" + "/".join(path)
            if name in macros and macros[name][2] != src:
                clashes.append((name, macros[name][2], src))
                continue
            macros[name] = (fmt(val), repr(val), src)

    if clashes:
        for name, s1, s2 in clashes[:20]:
            print(f"clash: \\{name}: {s1} vs {s2}", file=sys.stderr)
        print(f"{len(clashes)} macro-name clashes; first kept", file=sys.stderr)

    a.out.mkdir(parents=True, exist_ok=True)
    head = ("% Generated by paper/tools/make_numbers.py from results/*.json. Do not edit.\n"
            f"% {len(macros)} macros from {len(files)} records; naming rules in paper/tools/README.md.\n")
    tex = [head]
    tsv = ["macro\tvalue\traw\tsource"]
    for name in sorted(macros):
        latex, raw, src = macros[name]
        tex.append(f"\\newcommand{{\\{name}}}{{{latex}}}\n")
        tsv.append(f"\\{name}\t{latex}\t{raw}\t{src}")
    (a.out / "numbers.tex").write_text("".join(tex))
    (a.out / "numbers.tsv").write_text("\n".join(tsv) + "\n")
    print(f"wrote {len(macros)} macros from {len(files)} records to {a.out}/numbers.tex")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

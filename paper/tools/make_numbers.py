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

import yaml

ROOT = Path(__file__).resolve().parents[2]

# subtrees that are never flattened (per-replicate detail, run metadata)
SKIP_KEYS = {"config", "package_versions", "seeds", "input", "inputs"}
SKIP_KEY_PARTS = ("per_resample",)
# a list of dicts is flattened when its items carry one of these identifying keys
ID_KEYS = ("step", "name", "id", "model", "element", "site_label", "formula", "budget")
MAX_SCALAR_LIST = 12
# per-run records written by the training jobs are named by a 16-hex-digit run id
RUN_RECORD = re.compile(r"^[0-9a-f]{16}$")
# named records in these subdirectories of results/ are read too; their lists of objects without one
# unique identifying key are flattened by the joined values of COMPOSITE_KEYS (N1 GPU repeatability)
EXTRA_RESULT_DIRS = ("nrp",)
# named analysis records written by write_result beside a figure (path relative to the repository root)
FIGURE_RECORD_DIRS = ("figures/main/data",)
COMPOSITE_KEYS = ("class", "model", "B", "node", "pass", "a", "b")
# named records with a list of objects identified by several fields together (M9 within-host breakdown):
# record stem -> {payload list key: identifying fields}; each item is flattened under the joined field values
MULTIKEY_LISTS = {"within_host_breakdown": {"groups": ("variable", "group")},
                  # A2 swap-in check: one item per (backbone, r, B, seed) cell
                  "staging_swapin_check": {"cells": ("backbone", "r", "B", "seed")}}
# A1 precision and CV records: lists of objects identified by several fields, nested one level below a payload
# path (path -> {design point: [items]}); each item is flattened under the design point and its joined fields
NESTED_MULTIKEY_LISTS = {
    stem: {("descriptive", "gpu_class"): ("backbone", "gpu_class"), ("descriptive", "capped"): ("backbone", "model")}
    for stem in ("precision_a_b400_b654", "cv_extended_budget")}
# A5 sensitivity records: lists of objects at a nested payload path, identified by several fields together;
# record stem -> {payload path: identifying fields}; each item is flattened under the joined field values
PATH_MULTIKEY_LISTS = {
    "sens_capped_post_hoc": {("descriptive_runs", "groups"): ("kind", "model", "B")},
    "sens_high_moment_v1": {("excluded_per_resample",): ("r",)},
    # A4 probe sanity checks: one item per (r, B) cell
    "probe_fit_v1": {("sanity",): ("r", "B")},
}
# protocol constants (not results): file, macro prefix, top-level keys to read (None = all)
PROTOCOL_SOURCES = (
    ("configs/config.yaml", "Cfg", None),
    ("configs/tuned_v1.yaml", "TunedVOne", None),
    ("configs/tuned_v2.yaml", "TunedVTwo", None),
    ("splits/meta.json", "SplitMeta", ("n_hosts", "n_test_hosts", "pool_size", "test_fraction",
                                       "coverage")),
    ("splits/loco_v1.json", "SplitLoco", ("n_families", "n_folds", "n_hosts")),
    ("splits/cv_v1.json", "SplitCv", ("ks", "seed", "n_hosts")),
    ("splits/resamples_10_29.json", "SplitExt", ("n_test_hosts", "pool_size", "budgets")),
)

# W3 (Supplementary Materials): render parameters of the structure figures (not results; written by
# blender/render_host.py beside each PNG): file, macro prefix. The first-shell list is keyed by atom index.
RENDER_SOURCES = (
    ("figures/main/fig1_zno_vacancy.render.json", "RenderZnO"),
    ("figures/si/structure_sno2_vacancy.render.json", "RenderSnOTwo"),
)
RENDER_KEYS = ("n_atoms", "vacancy_atom_index", "first_shell", "cation_O_bond_cutoff_A", "dpi", "width_mm",
               "px", "samples")
# W3: tuned values printed to three significant figures (suffix "Sig"), beside the three-decimal macros of
# PROTOCOL_SOURCES, so that learning rates and weight decays keep their leading digits in the SI tables
SIG_SOURCES = (("configs/tuned_v1.yaml", "TunedVOne"), ("configs/tuned_v2.yaml", "TunedVTwo"))

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


def fmt_sig(x: float) -> str:
    """Three significant figures: plain decimals from 0.01 up, m\\times10^{e} below (W3, tuned values)."""
    if abs(x) >= 0.01 or x == 0:
        s = f"{abs(x):.3g}"
    else:
        m, e = f"{abs(x):.2e}".split("e")
        s = f"{m}\\times10^{{{int(e)}}}"
    return f"\\ensuremath{{{'-' if x < 0 else ''}{s}}}"


def render_leaves(path: Path) -> list[tuple[list[str], float]]:
    """Numeric render parameters of one structure render (RENDER_KEYS; first shell keyed by atom index)."""
    obj = json.loads(path.read_text())
    keep = {k: obj[k] for k in RENDER_KEYS if k in obj}
    keep["first_shell"] = {str(a["index"]): {"distance_A": a["distance_A"]} for a in keep.get("first_shell", [])}
    leaves: list[tuple[list[str], float]] = []
    flatten(keep, [], leaves)
    return leaves


def is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def skip(key: str) -> bool:
    return key in SKIP_KEYS or any(p in key for p in SKIP_KEY_PARTS)


def flatten(obj, path: list[str], out: list[tuple[list[str], float]],
            composite: bool = False) -> None:
    if is_num(obj):
        out.append((path, obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if not skip(str(k)):
                flatten(v, path + [str(k)], out, composite)
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
                    flatten({k: w for k, w in v.items() if k != idk}, path + [str(v[idk])], out,
                            composite)
            elif composite:
                ck = [k for k in COMPOSITE_KEYS if all(k in v for v in obj)]
                ids = ["_".join(str(v[k]) for k in ck) for v in obj]
                if ck and len(set(ids)) == len(obj):
                    for i, v in zip(ids, obj):
                        flatten({k: w for k, w in v.items() if k not in ck}, path + [i], out,
                                composite)


def protocol_leaves(path: Path, keys: tuple[str, ...] | None) -> list[tuple[list[str], float]]:
    """Numeric leaves of a protocol file (config YAML or split metadata JSON), optionally only some keys."""
    text = path.read_text()
    obj = yaml.safe_load(text) if path.suffix in (".yaml", ".yml") else json.loads(text)
    if keys is not None:
        obj = {k: obj[k] for k in keys}
    leaves: list[tuple[list[str], float]] = []
    flatten(obj, [], leaves)
    return leaves


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

    def add(prefix: str, leaves: list[tuple[list[str], float]], src_head: str) -> None:
        for path, val in leaves:
            name = "num" + prefix + "".join(camel(c) for c in path)
            src = src_head + "/".join(path)
            if name in macros and macros[name][2] != src:
                clashes.append((name, macros[name][2], src))
                continue
            macros[name] = (fmt(val), repr(val), src)

    # the top-level records come first, so a later source never displaces one of their names
    files = named_records(a.results)
    for p in files:
        leaves: list[tuple[list[str], float]] = []
        flatten(json.loads(p.read_text())["payload"], [], leaves)
        add(camel(p.stem), leaves, f"results/{p.name}#/payload/")
    for sub in EXTRA_RESULT_DIRS:
        extra = named_records(a.results / sub)
        for p in extra:
            leaves = []
            flatten(json.loads(p.read_text())["payload"], [], leaves, composite=True)
            add(camel(p.stem), leaves, f"results/{sub}/{p.name}#/payload/")
        files += extra
    for sub in FIGURE_RECORD_DIRS:
        extra = named_records(ROOT / sub)
        for p in extra:
            leaves = []
            flatten(json.loads(p.read_text())["payload"], [], leaves)
            add(camel(p.stem), leaves, f"{sub}/{p.name}#/payload/")
        files += extra
    for p in files:
        payload = json.loads(p.read_text())["payload"]
        for key, ids in MULTIKEY_LISTS.get(p.stem, {}).items():
            keyed = {"_".join(str(v[k]) for k in ids): {k: w for k, w in v.items() if k not in ids}
                     for v in payload[key]}
            leaves = []
            flatten({key: keyed}, [], leaves)
            add(camel(p.stem), leaves, f"results/{p.name}#/payload/")
    for p in files:
        payload = json.loads(p.read_text())["payload"]
        for keypath, ids in NESTED_MULTIKEY_LISTS.get(p.stem, {}).items():
            node = payload
            for k in keypath:
                node = node.get(k, {}) if isinstance(node, dict) else {}
            keyed = {point: {"_".join(str(v[k]) for k in ids): {k: w for k, w in v.items() if k not in ids}
                             for v in items} for point, items in node.items()}
            leaves = []
            flatten(keyed, list(keypath), leaves)
            add(camel(p.stem), leaves, f"results/{p.name}#/payload/")
    for p in files:
        payload = json.loads(p.read_text())["payload"]
        for keypath, ids in PATH_MULTIKEY_LISTS.get(p.stem, {}).items():
            node = payload
            for k in keypath:
                node = node.get(k, []) if isinstance(node, dict) else []
            keyed = {"_".join(str(v[k]) for k in ids): {k: w for k, w in v.items() if k not in ids} for v in node}
            leaves = []
            flatten(keyed, list(keypath), leaves)
            add(camel(p.stem), leaves, f"results/{p.name}#/payload/")
    for rel, prefix, keys in PROTOCOL_SOURCES:
        add(prefix, protocol_leaves(ROOT / rel, keys), f"{rel}#/")
    for rel, prefix in RENDER_SOURCES:
        if (ROOT / rel).exists():
            add(prefix, render_leaves(ROOT / rel), f"{rel}#/")
    for rel, prefix in SIG_SOURCES:
        for path, val in protocol_leaves(ROOT / rel, None):
            if isinstance(val, float) and not val.is_integer():
                name = "num" + prefix + "".join(camel(c) for c in path) + "Sig"
                if name in macros:
                    clashes.append((name, macros[name][2], f"{rel}#/" + "/".join(path)))
                    continue
                macros[name] = (fmt_sig(val), repr(val), f"{rel}#/" + "/".join(path) + " (3 s.f.)")

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

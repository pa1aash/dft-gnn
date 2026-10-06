"""Validate docs/claims.yaml. Exit non-zero on any schema violation."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("id", "statement", "tested_by", "figure", "falsifiable_how", "status")
OPTIONAL = ("result_ref",)
REQUIRED_NONEMPTY = ("tested_by", "figure", "falsifiable_how")
STATUSES = {"planned", "in_progress", "measured", "supported", "refuted", "moved_to_si", "dropped"}


def check(path: Path) -> list[str]:
    errs: list[str] = []
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or set(doc) != {"claims"} or not isinstance(doc["claims"], list):
        return ["top level must be a mapping with the single key 'claims' holding a list"]
    seen: set[str] = set()
    for i, c in enumerate(doc["claims"]):
        where = f"claims[{i}]"
        if not isinstance(c, dict):
            errs.append(f"{where}: not a mapping")
            continue
        where = f"claim {c.get('id', i)}"
        if missing := [f for f in FIELDS if f not in c]:
            errs.append(f"{where}: missing {missing}")
        if extra := sorted(set(c) - set(FIELDS) - set(OPTIONAL)):
            errs.append(f"{where}: unknown fields {extra}")
        for f in FIELDS:
            if f in c and (not isinstance(c[f], str) or not c[f].strip()):
                errs.append(f"{where}: {f} must be a non-empty string")
        for f in REQUIRED_NONEMPTY:
            if f not in c:
                errs.append(f"{where}: lacks {f}")
        if c.get("id") in seen:
            errs.append(f"{where}: duplicate id")
        seen.add(c.get("id"))
        if "result_ref" in c:
            if not isinstance(c["result_ref"], str) or not (ROOT / c["result_ref"]).is_file():
                errs.append(f"{where}: result_ref must name an existing file")
        if c.get("status") == "measured" and "result_ref" not in c:
            errs.append(f"{where}: status measured requires result_ref")
        if "status" in c and c["status"] not in STATUSES:
            errs.append(f"{where}: status {c['status']!r} not in {sorted(STATUSES)}")
    return errs


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "claims.yaml"
    errs = check(path)
    for e in errs:
        print(e, file=sys.stderr)
    if not errs:
        n = len(yaml.safe_load(path.read_text(encoding="utf-8"))["claims"])
        print(f"{path}: {n} claims valid")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())

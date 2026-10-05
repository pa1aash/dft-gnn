"""File and column inventory of the pinned data release (Step 2 of the S02 audit)."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
DB = RAW / "unpacked/oxygen_vacancies_db"
ML = DB / "vacancy_formation_energy_ml"
README = (DB / "README.md").read_text(encoding="utf-8")
README_K25 = (RAW / "unpacked/ML_charged_defects/README.md").read_text(encoding="utf-8")
FORMAT = {".gz": "tar.gz", ".csv": "csv", ".pcl": "pickle", ".json": "json", ".txt": "text",
          ".cif": "cif", ".vesta": "vesta", ".md": "markdown", ".py": "python",
          ".ipynb": "notebook", ".css": "css", ".png": "png", ".ico": "ico", ".js": "js"}


def rows_of(p: Path) -> int | None:
    s = p.suffix
    if s == ".csv":
        return sum(1 for _ in p.open("rb")) - 1
    if s in (".txt", ".md", ".py", ".vesta"):
        return sum(1 for _ in p.open("rb"))
    if s == ".cif":
        return len(re.findall(r"^\s+[A-Z][a-z]?\s+\S+\s+1\s+[-\d.]+\s+[-\d.]+\s+[-\d.]+\s+1\s*$",
                              p.read_text(), re.M))
    if s == ".json":
        v = json.loads(p.read_text())
        return len(v) if isinstance(v, (dict, list)) else 1
    return None


def file_row(p: Path) -> dict:
    fmt = FORMAT.get(p.suffix, p.suffix.lstrip(".") or "none")
    if p.name.endswith(".tar.gz"):
        fmt = "tar.gz"
    return {"path": p.relative_to(ROOT).as_posix(), "format": fmt, "size_bytes": p.stat().st_size,
            "rows": rows_of(p)}


def column_inventory(df: pd.DataFrame, readme: str) -> list[dict]:
    out = []
    for c in df.columns:
        s = df[c]
        num = pd.api.types.is_numeric_dtype(s)
        ex = [x.item() if hasattr(x, "item") else x for x in s.dropna().head(3)]
        out.append({
            "column": c, "dtype": str(s.dtype), "nulls": int(s.isna().sum()),
            "unique": int(s.nunique(dropna=True)),
            "min": float(s.min()) if num else None, "max": float(s.max()) if num else None,
            "examples": ex,
            # element symbols and short words match README prose by accident, so require a name of 3+ characters
            "in_readme": len(c) > 2 and bool(re.search(rf"(?<![A-Za-z_]){re.escape(c)}(?![A-Za-z_])", readme)),
        })
    return out


def _paths(o, prefix="", depth=0, out=None):
    out = out if out is not None else {}
    if depth > 4:
        return out
    if isinstance(o, dict):
        for k, v in o.items():
            if k.startswith("@"):
                continue
            key = f"{prefix}.{k}" if prefix else k
            # collapse per-site / per-defect dict keys (Va_O1_0, Zn1, ...) so the schema stays small
            key = re.sub(r"\bVa_O\d+(_\d)?\b", "Va_O<n>", key)
            out.setdefault(key, (type(v).__name__, repr(v)[:60]))
            _paths(v, key, depth + 1, out)
    elif isinstance(o, list) and o:
        key = prefix + "[]"
        out.setdefault(key, (type(o[0]).__name__, repr(o[0])[:60]))
        _paths(o[0], key, depth + 1, out)
    return out


def _schema(p: str) -> dict:
    return _paths(json.loads(Path(p).read_text()))


def json_schema(pattern: str, base: Path, readme: str) -> list[dict]:
    files = sorted(base.glob(pattern))
    with Pool() as pool:
        res = pool.map(_schema, [str(f) for f in files], chunksize=16)
    count: dict = defaultdict(int)
    ex: dict = {}
    for r in res:
        for k, v in r.items():
            count[k] += 1
            ex.setdefault(k, v)
    out = []
    for k in sorted(count):
        leaf = re.split(r"[.\[\]]", k.rstrip("[]"))[-1] if k else k
        out.append({"field": k, "type": ex[k][0], "n_files": count[k], "n_files_total": len(files),
                    "example": ex[k][1],
                    "in_readme": bool(leaf and re.search(rf"(?<![A-Za-z_]){re.escape(leaf)}(?![A-Za-z_])", readme))})
    return out


def file_class(path: str) -> str:
    """Collapse per-host / per-defect file names into one class label."""
    rel = path.replace("data/raw/", "")
    m = re.match(r"(unpacked/oxygen_vacancies_db/oxygen_vacancies_db_data)/([^/]+?)(\.tar\.gz|/(.*))?$", rel)
    if m:
        base, formula, tgz, inner = m.groups()
        if tgz == ".tar.gz":
            return f"{base}/<formula>.tar.gz"
        return f"{base}/<formula>/" + re.sub(r"^[^/]+_Va_O\d+_(\d)", r"<formula>_Va_O<n>_<q>", inner)
    m = re.match(r"(unpacked/oxygen_vacancies_db/site_info)/[^/]+/(.*)$", rel)
    if m:
        return f"{m.group(1)}/<formula>/{m.group(2)}"
    m = re.match(r"(unpacked/ML_charged_defects/oxy_vac_data/materials_[A-Za-z_]+)/[^/]+\.json$", rel)
    if m:
        return f"{m.group(1)}/<formula>.json"
    return rel


def main() -> dict:
    files = [file_row(p) for p in sorted(RAW.rglob("*")) if p.is_file()]
    by_class: dict = defaultdict(lambda: {"files": 0, "bytes": 0})
    for f in files:
        by_class[file_class(f["path"])]["files"] += 1
        by_class[file_class(f["path"])]["bytes"] += f["size_bytes"]
    tables = {}
    for q in (0, 1, 2):
        csv = pd.read_csv(ML / f"charge{q}.csv", index_col=0)
        pcl = pd.read_pickle(ML / f"df_charge{q}.pcl")
        num = [c for c in csv.columns if pd.api.types.is_numeric_dtype(csv[c])]
        tables[f"charge{q}.csv"] = {
            "rows": len(csv), "columns": csv.shape[1], "inventory": column_inventory(csv, README),
            "pickle_nan_cells": int(pcl.isna().sum().sum()),
            "pickle_nan_columns": int((pcl.isna().sum() > 0).sum()),
            "pickle_matches_csv_after_nan_to_zero": bool(
                list(pcl.columns) == list(csv.columns)
                and np.allclose(pcl[num].fillna(0.0).to_numpy(float), csv[num].to_numpy(float), rtol=0, atol=1e-12)
                and (pcl["full_name"].to_numpy() == csv["full_name"].to_numpy()).all()),
            "pickle_max_abs_diff_non_nan_cells": float(np.nanmax(np.abs(pcl[num].to_numpy(float) - csv[num].to_numpy(float)))),
        }
    for sp in ("train", "val", "test"):
        for ph in ("wo", "w"):
            p = RAW / f"unpacked/ML_charged_defects/oxy_vac_data/{sp}_{ph}_PHS.txt"
            lines = [x for x in p.read_text().splitlines() if x.strip()]
            tables[p.name] = {"rows": len(lines), "columns": 1,
                              "inventory": [{"column": "formula", "dtype": "object", "nulls": 0,
                                             "unique": len(set(lines)), "examples": lines[:3],
                                             "in_readme": False}]}
    schemas = {
        "defect_visual_data.json": json_schema("oxygen_vacancies_db_data/*/defect_visual_data.json", DB, README),
        "bulk_visual_data.json": json_schema("oxygen_vacancies_db_data/*/bulk_visual_data.json", DB, README),
        "chem_pot_diag.json": json_schema("oxygen_vacancies_db_data/*/chem_pot_diag.json", DB, README),
        "K25 host json (materials_coreAlign_with_PHS)": json_schema(
            "materials_coreAlign_with_PHS/*.json", RAW / "unpacked/ML_charged_defects/oxy_vac_data", README_K25),
    }
    return {"files": files, "file_classes": {k: v for k, v in sorted(by_class.items())},
            "n_files": len(files), "total_bytes": sum(f["size_bytes"] for f in files),
            "tables": tables, "json_schemas": schemas}


if __name__ == "__main__":
    r = main()
    print(r["n_files"], r["total_bytes"], len(r["file_classes"]))

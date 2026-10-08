"""S09 step 4: completeness and health check of the sweep session. NOT an analysis.

Counts the expected runs (S, D-state and P1 over 10 resamples x 6 budgets x 3 seeds; the same three models on the
Kiyohara split with S taken from the official C0 runs; the epoch-cap runs), checks that every run has a result
JSON, a predictions parquet and a checkpoint whose hashes match the result record, that the predictions cover
every test site of the run's split exactly once and are finite, and reports failures, wall times, the fraction
of runs stopped by the epoch cap and one sanity table of the mean test MAE per (model, budget). No gaps,
no intervals, no comparison of S with D.

    python scripts/sweep_completeness.py [--write]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

MODELS = ("S", "D-state", "P1")
BUDGETS = (25, 50, 100, 200, 400, 654)


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def load_all() -> list[dict]:
    runs = []
    for sub, kind in (("", "sweep"), ("capsens", "capsens"), ("c0_official", "c0")):
        for f in sorted((ROOT / "results" / sub).glob("*.json")) if sub else sorted((ROOT / "results").glob("*.json")):
            try:
                rec = json.loads(f.read_text())
            except ValueError:
                continue
            pay = rec.get("payload")
            if not isinstance(pay, dict) or "spec" not in pay or "run_id" not in pay or pay.get("smoke"):
                continue
            sp = pay["spec"]
            if sp.get("tags", {}).get("pilot") or sp.get("results_subdir") not in (None, "capsens", "c0_official"):
                continue
            pay["_kind"] = kind if sub else ("kiyohara" if sp["split"] == "kiyohara" else "sweep")
            pay["_git_sha"] = rec.get("git_sha")
            pay["_dirty"] = rec.get("git_dirty")
            pay["_file"] = str(f.relative_to(ROOT))
            runs.append(pay)
    return runs


def expected_cells() -> dict[tuple, str]:
    """(kind, model, r, budget, seed) -> label for every run the session must have."""
    cells = {}
    for m in MODELS:
        for r in range(10):
            for b in BUDGETS:
                for s in range(3):
                    cells[("sweep", m, r, b, s)] = "sweep"
        for s in range(3):
            cells[("kiyohara", m, -1, 571, s)] = "kiyohara"
    for m in ("S", "D-state"):
        for r in range(3):
            for s in range(3):
                cells[("capsens", m, r, 654, s)] = "capsens"
    return cells


def cell_of(p: dict) -> tuple:
    sp = p["spec"]
    kind = p["_kind"]
    if kind == "c0":
        kind = "kiyohara"
    return (kind, sp["model"], sp["r"], sp["budget"], sp["seed"])


def check_run(p: dict, test_hosts: dict[str, set]) -> list[str]:
    errs = []
    pr, ck = p["predictions"], p.get("checkpoint")
    pp = ROOT / pr["path"]
    if not pp.is_file():
        return ["predictions file missing"]
    if sha(pp) != pr["sha256"]:
        errs.append("predictions hash mismatch")
    if ck is None or not (ROOT / ck["path"]).is_file():
        errs.append("checkpoint missing")
    elif sha(ROOT / ck["path"]) != ck["sha256"]:
        errs.append("checkpoint hash mismatch")
    df = pd.read_parquet(pp)
    if len(df) != p["n_sites"]["test"] or len(df) != pr["rows"]:
        errs.append(f"rows {len(df)} != n_sites.test {p['n_sites']['test']}")
    if df.site_id.duplicated().any():
        errs.append("a test site appears more than once")
    cols = [c for c in df.columns if c.startswith("pred_")] if p["spec"]["model"] == "P1" else ["y_pred"]
    if not cols or not np.isfinite(df[cols].to_numpy(dtype=float)).all():
        errs.append("non-finite predictions")
    hosts = test_hosts[p["spec"]["split"]]
    if set(df.host_id) != hosts:
        errs.append(f"test hosts differ from the split ({len(set(df.host_id) ^ hosts)} differ)")
    return errs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write results/sweep_completeness.json")
    a = ap.parse_args()
    from dftgnn.split import load_split

    runs = load_all()
    exp = expected_cells()
    by_cell = defaultdict(list)
    for p in runs:
        by_cell[cell_of(p)].append(p)
    missing = sorted(c for c in exp if c not in by_cell)
    unexpected = sorted(c for c in by_cell if c not in exp)
    duplicates = {str(c): [x["run_id"] for x in v] for c, v in by_cell.items() if len(v) > 1}
    test_hosts = {sp: set(load_split(sp)["test"]) for sp in {p["spec"]["split"] for p in runs}}
    problems = {}
    for p in runs:
        e = check_run(p, test_hosts)
        if e:
            problems[p["run_id"]] = e
    counts = defaultdict(int)
    for c in by_cell:
        counts[c[0]] += 1
    # epochs run versus the cap
    cap = defaultdict(lambda: [0, 0])
    walls = defaultdict(list)
    for p in runs:
        sp = p["spec"]
        key = f"{p['_kind'] if p['_kind'] != 'c0' else 'kiyohara'}|{sp['model']}|{sp['budget']}"
        cap[key][1] += 1
        cap[key][0] += int(p["epochs_run"] >= p["max_epochs"])
        walls[key].append(p["wall_time_s"])
    def metric(p):
        return p["metrics"]["mean_standardised_mae"] if p["spec"]["model"] == "P1" else p["metrics"]["mae"]

    nonfinite = [p["run_id"] for p in runs if not np.isfinite(metric(p))]
    # sanity table: mean test MAE per (model, budget) over resamples and seeds (sweep runs only)
    tab = defaultdict(list)
    for p in runs:
        if p["_kind"] == "sweep":
            tab[(p["spec"]["model"], p["spec"]["budget"])].append(metric(p))
    sanity = {f"{m}|{b}": {"mean_test_mae": float(np.mean(v)), "n_runs": len(v),
                           "unit": "mean standardised descriptor MAE (health only)" if m == "P1" else "eV"}
              for (m, b), v in sorted(tab.items())}
    flags = []
    for m in ("S", "D-state"):
        prev = None
        for b in BUDGETS:
            v = sanity.get(f"{m}|{b}")
            if not v:
                continue
            if v["mean_test_mae"] > 0.8:
                flags.append(f"{m} B={b}: mean MAE {v['mean_test_mae']:.3f} > 0.8 eV")
            if prev is not None and v["mean_test_mae"] - prev[1] > 0.1:
                flags.append(f"{m}: MAE rises {prev[1]:.3f} -> {v['mean_test_mae']:.3f} from B={prev[0]} to {b}")
            prev = (b, v["mean_test_mae"])
    payload = {
        "expected": {"sweep": 540, "kiyohara": 9, "capsens": 18, "total": len(exp)},
        "found": dict(counts), "found_total": len(by_cell),
        "missing_cells": [list(c) for c in missing], "unexpected_cells": [list(c) for c in unexpected],
        "duplicate_cells": duplicates, "runs_with_problems": problems, "non_finite_mae_runs": nonfinite,
        "git_shas": sorted({p["_git_sha"] for p in runs}), "dirty_runs": [p["run_id"] for p in runs if p["_dirty"]],
        "stopped_by_cap": {k: {"capped": v[0], "runs": v[1], "fraction": v[0] / v[1]} for k, v in sorted(cap.items())},
        "wall_time_s": {k: {"mean": float(np.mean(v)), "max": float(np.max(v)), "sum": float(np.sum(v)),
                            "n": len(v)} for k, v in sorted(walls.items())},
        "sanity_mean_test_mae": sanity, "sanity_flags": flags,
        "checkpoints": json.loads((ROOT / "results" / "checkpoint_manifest.json").read_text())["n_files"]
        if (ROOT / "results" / "checkpoint_manifest.json").exists() else None,
    }
    print(json.dumps({k: v for k, v in payload.items() if k not in ("stopped_by_cap", "wall_time_s")}, indent=1))
    if a.write:
        from dftgnn.io.results import write_result

        print(write_result("sweep_completeness", payload))


if __name__ == "__main__":
    main()

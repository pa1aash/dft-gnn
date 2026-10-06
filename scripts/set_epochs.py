"""Apply the pre-logged rule that sets max_epochs and patience from the S07 epoch pilots.

Reads the three pilot runs in ``results/pilot_epochs/`` (model S, resample 0, budgets 25, 200, 654,
seed 0, 1500 epochs, early stopping disabled) and applies the rule of docs/deviations.md (2026-10-06):

    e_conv(B)  = first epoch (counted from 1) with validation MAE <= 1.01 x the run's minimum
    max_epochs = smallest multiple of 50 that is >= 1.5 x max_B e_conv(B)
    patience   = max(30, round_half_up(0.15 x max_epochs))

Writes ``results/pilot_epochs.json`` (write_result) and ``results/pilot_epochs/curves.csv``; with
``--apply`` it replaces the two TBD-S07 values in configs/config.yaml.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

PILOT_DIR = ROOT / "results" / "pilot_epochs"
TOL = 1.01


def e_conv(val: list[float], tol: float = TOL) -> int:
    """First epoch, counted from 1, whose validation MAE is within ``tol`` x the minimum."""
    lo = min(val)
    return next(i + 1 for i, v in enumerate(val) if v <= tol * lo)


def round_half_up(x: float) -> int:
    return math.floor(x + 0.5)


def rule(conv: dict[int, int]) -> tuple[int, int]:
    worst = max(conv.values())
    max_epochs = 50 * math.ceil(1.5 * worst / 50)
    return max_epochs, max(30, round_half_up(0.15 * max_epochs))


def load_runs(pilot_dir: Path = PILOT_DIR) -> dict[int, dict]:
    runs = {}
    for f in sorted(pilot_dir.glob("*.json")):
        pay = json.loads(f.read_text())["payload"]
        if pay["spec"]["tags"].get("pilot") != "epochs":
            continue
        runs[pay["spec"]["budget"]] = pay
    return runs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write the values into configs/config.yaml")
    a = ap.parse_args()
    runs = load_runs()
    if sorted(runs) != [25, 200, 654]:
        raise SystemExit(f"need pilots for budgets 25, 200, 654; found {sorted(runs)}")
    for b, pay in runs.items():
        assert pay["epochs_run"] == 1500 and pay["spec"]["eval_test"] is False and pay["metrics"] == {}, b
    curves = {b: [h["val_metric"] for h in pay["history"]] for b, pay in runs.items()}
    conv = {b: e_conv(v) for b, v in curves.items()}
    max_epochs, patience = rule(conv)
    detail = {b: {"e_conv": conv[b], "min_val_mae_eV": min(v), "epoch_of_min": 1 + v.index(min(v)),
                  "val_mae_at_e_conv_eV": v[conv[b] - 1], "epochs_run": len(v),
                  "n_train_hosts": runs[b]["n_hosts"]["train"], "n_val_hosts": runs[b]["n_hosts"]["val"],
                  "run_id": runs[b]["run_id"]} for b in sorted(runs)}
    csv = PILOT_DIR / "curves.csv"
    csv.write_text("epoch," + ",".join(f"val_mae_B{b}" for b in sorted(curves)) + "\n" +
                   "".join(f"{i + 1}," + ",".join(f"{curves[b][i]:.6f}" for b in sorted(curves)) + "\n"
                           for i in range(1500)))
    from dftgnn.io.results import write_result

    payload = {"rule": "docs/deviations.md 2026-10-06 row on the S07 epoch rule", "tolerance": TOL,
               "budgets": detail, "max_over_budgets_e_conv": max(conv.values()),
               "max_epochs": max_epochs, "patience": patience, "pilot": True,
               "curves_csv": str(csv.relative_to(ROOT)),
               "test_hosts_evaluated": 0}
    print(json.dumps({k: payload[k] for k in ("max_over_budgets_e_conv", "max_epochs", "patience")}),
          {b: d["e_conv"] for b, d in detail.items()})
    if a.apply:
        cfgp = ROOT / "configs" / "config.yaml"
        t = cfgp.read_text()
        t = re.sub(r"(max_epochs: )TBD-S07", rf"\g<1>{max_epochs}", t, count=1)
        t = re.sub(r"(patience: )TBD-S07", rf"\g<1>{patience}", t, count=1)
        cfgp.write_text(t)
    print(write_result("pilot_epochs", payload, allow_dirty=True))


if __name__ == "__main__":
    main()

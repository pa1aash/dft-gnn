"""Check that configs/config.yaml matches the numeric decisions of docs/ANALYSIS_PLAN.md.

The plan ends with a fenced ``yaml prereg`` block whose keys are dotted config paths. Every key must
resolve in the config and hold the same value; a set of required keys (delta, anchors, trials, budgets,
seeds, cutoff, bootstrap draws) must be present in the block. Exit non-zero on any mismatch.
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "ANALYSIS_PLAN.md"
CONFIG = ROOT / "configs" / "config.yaml"
REQUIRED = (
    "stats.delta_eV",
    "tuning.anchors",
    "tuning.optuna_trials_per_model_per_anchor",
    "budgets.hosts",
    "training.seeds",
    "graph.cutoff_A",
    "analysis.bootstrap.draws",
)
BLOCK = re.compile(r"^```yaml prereg\n(.*?)^```", re.DOTALL | re.MULTILINE)


def plan_block(text: str) -> dict:
    blocks = BLOCK.findall(text)
    if len(blocks) != 1:
        raise SystemExit(f"expected exactly one 'yaml prereg' block in {PLAN}, found {len(blocks)}")
    return yaml.safe_load(blocks[0])


def lookup(cfg: dict, dotted: str):
    node = cfg
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(dotted)
        node = node[part]
    return node


def same(a, b) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, rel_tol=0, abs_tol=1e-12)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    return a == b


def check(plan_text: str, cfg: dict) -> list[str]:
    block = plan_block(plan_text)
    errs = [f"required key missing from plan block: {k}" for k in REQUIRED if k not in block]
    for key, want in block.items():
        try:
            got = lookup(cfg, key)
        except KeyError:
            errs.append(f"{key}: not in config")
            continue
        if not same(want, got):
            errs.append(f"{key}: plan {want!r} != config {got!r}")
    return errs


def main() -> int:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    errs = check(PLAN.read_text(encoding="utf-8"), cfg)
    for e in errs:
        print(f"MISMATCH {e}", file=sys.stderr)
    if errs:
        return 1
    print(f"{PLAN.relative_to(ROOT)}: {len(plan_block(PLAN.read_text(encoding='utf-8')))} pre-registered "
          f"values match {CONFIG.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

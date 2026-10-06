"""Check that configs/config.yaml matches the numeric decisions of docs/ANALYSIS_PLAN.md.

The plan ends with a fenced ``yaml prereg`` block whose keys are dotted config paths. Every key must
resolve in the config and hold the same value; a set of required keys (delta, anchors, trials, budgets,
seeds, cutoff, bootstrap draws) must be present in the block. Exit non-zero on any mismatch.

The plan is read from the tag ``prereg-v1`` when git and the tag are available, and the working copy
must equal it. Rows of ``docs/deviations.md`` carry machine-readable ``config: <key> = <value>`` tokens.
A logged key must hold its logged value in the config, and a plan key whose config value differs from
the plan is accepted only if a logged row sets that key to the config value (the whitelist). The keys
in ``CLARIFIED`` must be covered by the plan block or by a logged row.
"""
from __future__ import annotations

import math
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "ANALYSIS_PLAN.md"
CONFIG = ROOT / "configs" / "config.yaml"
DEVIATIONS = ROOT / "docs" / "deviations.md"
TAG = "prereg-v1"
REQUIRED = (
    "stats.delta_eV",
    "tuning.anchors",
    "tuning.optuna_trials_per_model_per_anchor",
    "budgets.hosts",
    "training.seeds",
    "graph.cutoff_A",
    "analysis.bootstrap.draws",
)
CLARIFIED = (
    "training.early_stopping.min_delta",
    "training.validation.seed_rule",
    "robustness.loco.grouping",
)
EPOCH_KEYS = ("training.max_epochs", "training.early_stopping.patience")   # set by S07, rule in deviations.md
TOKEN = re.compile(r"`config: ([\w.]+) = ([^`]+)`")
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


def logged_values(log_text: str) -> list[dict]:
    """``{"kind", "section", "key", "value"}`` for every ``config:`` token in a deviations-log row."""
    out = []
    for line in log_text.splitlines():
        if not line.startswith("| 20"):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line)[1:-1]]
        kind = "CLARIFICATION" if cells[2].startswith("CLARIFICATION") else "DEVIATION"
        for key, val in TOKEN.findall(line):
            out.append({"kind": kind, "section": cells[1], "key": key, "value": yaml.safe_load(val)})
    return out


def tagged_plan(tag: str = TAG) -> str | None:
    """The plan as frozen at ``tag``, or None when git or the tag is unavailable."""
    try:
        return subprocess.run(["git", "show", f"{tag}:docs/ANALYSIS_PLAN.md"], cwd=ROOT, check=True,
                              capture_output=True, text=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def round_half_up(x: float) -> int:
    return math.floor(x + 0.5)


def epoch_rule_errors(cfg: dict, logged: list[dict]) -> list[str]:
    """max_epochs and patience must be set, logged and consistent with the S07 rule (docs/deviations.md):
    max_epochs a multiple of 50 and patience = max(30, round_half_up(0.15 x max_epochs))."""
    me, pa = (lookup(cfg, k) for k in EPOCH_KEYS)
    errs = []
    for k in EPOCH_KEYS:
        rows = [r for r in logged if r["key"] == k and r["kind"] == "CLARIFICATION"]
        if not rows:
            errs.append(f"{k}: not set by a logged CLARIFICATION row")
    if not (isinstance(me, int) and not isinstance(me, bool) and isinstance(pa, int)
            and not isinstance(pa, bool)):
        return [*errs, f"max_epochs / patience not set: {me!r}, {pa!r}"]
    if me <= 0 or me % 50:
        errs.append(f"training.max_epochs {me} is not a positive multiple of 50")
    if pa != max(30, round_half_up(0.15 * me)):
        errs.append(f"training.early_stopping.patience {pa} != max(30, round(0.15 x {me}))")
    return errs


def check(plan_text: str, cfg: dict, log_text: str | None = None) -> list[str]:
    log_text = DEVIATIONS.read_text(encoding="utf-8") if log_text is None else log_text
    logged = logged_values(log_text)
    block = plan_block(plan_text)
    errs = [f"required key missing from plan block: {k}" for k in REQUIRED if k not in block]
    for key, want in block.items():
        try:
            got = lookup(cfg, key)
        except KeyError:
            errs.append(f"{key}: not in config")
            continue
        if not same(want, got) and not any(r["key"] == key and same(r["value"], got) for r in logged):
            errs.append(f"{key}: plan {want!r} != config {got!r}")
    for r in logged:
        try:
            got = lookup(cfg, r["key"])
        except KeyError:
            errs.append(f"{r['key']}: logged in deviations but not in config")
            continue
        if not same(r["value"], got):
            errs.append(f"{r['key']}: deviations log {r['value']!r} != config {got!r}")
    covered = set(block) | {r["key"] for r in logged}
    errs += [f"{k}: neither pre-registered nor logged" for k in CLARIFIED if k not in covered]
    errs += epoch_rule_errors(cfg, logged)
    return errs


def main() -> int:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    working = PLAN.read_text(encoding="utf-8")
    plan = tagged_plan()
    if plan is not None and plan != working:
        print(f"MISMATCH {PLAN.relative_to(ROOT)} differs from tag {TAG}", file=sys.stderr)
        return 1
    errs = check(plan if plan is not None else working, cfg)
    for e in errs:
        print(f"MISMATCH {e}", file=sys.stderr)
    if errs:
        return 1
    n_log = len(logged_values(DEVIATIONS.read_text(encoding="utf-8")))
    src = f"tag {TAG}" if plan is not None else "working copy (tag unavailable)"
    print(f"{PLAN.relative_to(ROOT)} ({src}): {len(plan_block(plan or working))} pre-registered values "
          f"and {n_log} logged values match {CONFIG.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

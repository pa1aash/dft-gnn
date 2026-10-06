"""Check that configs/config.yaml matches the numeric decisions of docs/ANALYSIS_PLAN.md.

The plan ends with a fenced ``yaml prereg`` block whose keys are dotted config paths. Every key must
resolve in the config and hold the same value; a set of required keys (delta, anchors, trials, budgets,
seeds, cutoff, bootstrap draws) must be present in the block. Exit non-zero on any mismatch.

The plan is read from the tag ``prereg-v1`` when git and the tag are available, and the working copy
must equal it. Rows of ``docs/deviations.md`` carry machine-readable ``config: <key> = <value>`` tokens.
A logged key must hold its logged value in the config, and a plan key whose config value differs from
the plan is accepted only if a logged row sets that key to the config value (the whitelist). The keys
in ``CLARIFIED`` must be covered by the plan block or by a logged row.

Tuned hyperparameters (S08). Once ``models.injection_mode`` is set, ``configs/tuned_v1.yaml`` must exist and
agree with the twelve study results in ``results/tuning/``: every (model, anchor) holds its study's best
parameters, each study has the configured number of COMPLETE trials, every value lies in the search space,
``d_variant`` is the variant with the lower mean best-trial validation MAE over the anchors, it equals
``models.injection_mode``, and ``D`` is a copy of that variant.
"""
from __future__ import annotations

import json
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
TUNED = ROOT / "configs" / "tuned_v1.yaml"
TUNING_RESULTS = ROOT / "results" / "tuning"
TUNED_MODELS = ("S", "D-state", "D-late", "P1")
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


def _in_space(v, p: dict) -> bool:
    if p["dist"] == "categorical":
        return v in p["choices"]
    return isinstance(v, (int, float)) and p["low"] <= v <= p["high"]


def tuned_errors(cfg: dict, tuned_path: Path = TUNED, results: Path = TUNING_RESULTS) -> list[str]:
    """``tuned_v1.yaml`` against the study results and the D-selection rule (see the module docstring)."""
    mode = lookup(cfg, "models.injection_mode")
    if not tuned_path.is_file():
        return [] if mode == "TBD" else [f"models.injection_mode is {mode!r} but {tuned_path.name} is missing"]
    t = yaml.safe_load(tuned_path.read_text(encoding="utf-8"))
    tc = lookup(cfg, "tuning")
    anchors, n_trials, space = tc["anchors"], tc["optuna_trials_per_model_per_anchor"], tc["search_space"]
    errs, best = [], {}
    models = {m: {int(a): p for a, p in by.items()} for m, by in t.get("models", {}).items()}
    for m in TUNED_MODELS:
        for a in anchors:
            f = results / f"tuning_{m}_a{a}.json"
            if not f.is_file():
                errs.append(f"{f.name} missing")
                continue
            pay = json.loads(f.read_text())["payload"]
            best[(m, a)] = pay["best_value"]
            if pay["n_complete"] != n_trials:
                errs.append(f"{f.name}: {pay['n_complete']} complete trials, want {n_trials}")
            got = models.get(m, {}).get(a)
            if got != pay["best_params"]:
                errs.append(f"tuned {m} a{a} != best params of {f.name}")
                continue
            if set(got) != set(space):
                errs.append(f"tuned {m} a{a}: parameters {sorted(got)} != search space")
            errs += [f"tuned {m} a{a}: {k} = {v!r} outside the search space" for k, v in got.items()
                     if k in space and not _in_space(v, space[k])]
    if errs:
        return errs
    means = {v: sum(best[(v, a)] for a in anchors) / len(anchors) for v in ("D-state", "D-late")}
    rule = min(means, key=lambda v: (means[v], v))
    if t.get("d_variant") != rule:
        errs.append(f"d_variant {t.get('d_variant')!r} != rule output {rule!r} (means {means})")
    if mode != t.get("d_variant"):
        errs.append(f"models.injection_mode {mode!r} != d_variant {t.get('d_variant')!r}")
    if models.get("D") != models.get(rule):
        errs.append("tuned D is not a copy of the selected variant")
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
    errs += tuned_errors(cfg)
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
    if TUNED.is_file():
        print(f"{TUNED.relative_to(ROOT)}: matches the tuning results; D = {cfg['models']['injection_mode']} by the "
              "logged rule")
    return 0


if __name__ == "__main__":
    sys.exit(main())

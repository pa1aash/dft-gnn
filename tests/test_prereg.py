import importlib.util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_prereg", ROOT / "scripts" / "check_prereg.py")
check_prereg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_prereg)


def _cfg():
    return yaml.safe_load((ROOT / "configs" / "config.yaml").read_text())


def _plan():
    return (ROOT / "docs" / "ANALYSIS_PLAN.md").read_text()


def test_plan_matches_config():
    assert check_prereg.check(_plan(), _cfg()) == []


def test_mismatch_detected():
    cfg = _cfg()
    cfg["stats"]["delta_eV"] = 0.06
    cfg["graph"]["cutoff_A"] = 6.0
    errs = check_prereg.check(_plan(), cfg)
    assert any(e.startswith("stats.delta_eV") for e in errs)
    assert any(e.startswith("graph.cutoff_A") for e in errs)


def _log():
    return (ROOT / "docs" / "deviations.md").read_text()


def test_clarifications_logged_and_covered():
    logged = {r["key"]: r for r in check_prereg.logged_values(_log())}
    assert logged["training.early_stopping.min_delta"]["value"] == 0.0
    assert logged["robustness.loco.grouping"]["kind"] == "CLARIFICATION"
    assert set(check_prereg.CLARIFIED) <= set(logged)


def test_clarification_mismatch_detected():
    cfg = _cfg()
    cfg["training"]["early_stopping"]["min_delta"] = 0.01
    errs = check_prereg.check(_plan(), cfg, _log())
    assert any(e.startswith("training.early_stopping.min_delta") for e in errs)


def test_uncovered_clarification_detected():
    errs = check_prereg.check(_plan(), _cfg(), log_text="")
    assert any("neither pre-registered nor logged" in e for e in errs)


def test_logged_value_whitelists_plan_key():
    cfg = _cfg()
    cfg["graph"]["cutoff_A"] = 6.0
    row = "| 2026-01-01 | §3 | DEVIATION x `config: graph.cutoff_A = 6.0` | r | i |\n"
    assert not any(e.startswith("graph.cutoff_A") for e in check_prereg.check(_plan(), cfg, _log() + row))


def test_tagged_plan_equals_working_copy():
    tagged = check_prereg.tagged_plan()
    if tagged is not None:
        assert tagged == _plan()


def test_epoch_values_are_set_logged_and_follow_the_rule():
    cfg = _cfg()
    assert isinstance(cfg["training"]["max_epochs"], int)
    logged = check_prereg.logged_values(_log())
    assert check_prereg.epoch_rule_errors(cfg, logged) == []
    assert {r["key"] for r in logged} >= set(check_prereg.EPOCH_KEYS)


def test_epoch_rule_violations_detected():
    logged = check_prereg.logged_values(_log())
    for me, pa in ((210, 30), (200, 25), (300, 30), ("TBD-S07", "TBD-S07")):
        cfg = _cfg()
        cfg["training"]["max_epochs"] = me
        cfg["training"]["early_stopping"]["patience"] = pa
        assert check_prereg.epoch_rule_errors(cfg, logged), (me, pa)


def test_unlogged_epoch_values_detected():
    errs = check_prereg.epoch_rule_errors(_cfg(), [])
    assert sum("not set by a logged CLARIFICATION row" in e for e in errs) == 2

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

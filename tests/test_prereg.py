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


_fspec = importlib.util.spec_from_file_location("freeze", ROOT / "scripts" / "tune" / "freeze.py")
freeze = importlib.util.module_from_spec(_fspec)
_fspec.loader.exec_module(freeze)


def _studies(d_state=(0.30, 0.40, 0.60), d_late=(0.31, 0.41, 0.58)):
    """Synthetic study payloads for the twelve (model, anchor) pairs; mean D-late (0.4333) < D-state (0.4333+)."""
    vals = {"S": (0.5, 0.6, 0.9), "D-state": d_state, "D-late": d_late, "P1": (0.2, 0.3, 0.4)}
    out = {}
    for i, m in enumerate(freeze.MODELS):
        for j, a in enumerate((654, 200, 50)):
            p = {"learning_rate": 1e-3 + 1e-5 * (3 * i + j), "weight_decay": 1e-5, "hidden_width": 64,
                 "megnet_blocks": 3, "dropout": 0.1, "batch_size": 32, "readout_mlp_width": 64, "pooling": "mean"}
            out[(m, a)] = {"best_value": vals[m][j], "best_params": p, "n_complete": 30}
    return out


def _write(tmp_path, studies, tuned_text):
    res = tmp_path / "res"
    res.mkdir()
    for (m, a), pay in studies.items():
        (res / f"tuning_{m}_a{a}.json").write_text(__import__("json").dumps({"payload": pay}))
    t = tmp_path / "tuned_v1.yaml"
    t.write_text(tuned_text)
    return t, res


def test_tuned_file_checks(tmp_path):
    studies = _studies()
    anchors = [50, 200, 654]
    dec = freeze.select_d(studies, anchors)
    assert dec["selected"] == "D-late"
    assert abs(dec["means_eV"]["D-state"] - (0.3 + 0.4 + 0.6) / 3) < 1e-12
    t, res = _write(tmp_path, studies, freeze.tuned_yaml(studies, dec, anchors, "abc"))
    cfg = _cfg()
    cfg["models"]["injection_mode"] = "D-late"
    assert check_prereg.tuned_errors(cfg, t, res) == []
    cfg["models"]["injection_mode"] = "D-state"
    assert any("injection_mode" in e for e in check_prereg.tuned_errors(cfg, t, res))
    cfg["models"]["injection_mode"] = "D-late"
    t.write_text(t.read_text().replace("d_variant: D-late", "d_variant: D-state"))
    assert any("rule output" in e for e in check_prereg.tuned_errors(cfg, t, res))


def test_tuned_file_must_match_best_params_and_exist(tmp_path):
    studies = _studies()
    dec = freeze.select_d(studies, [50, 200, 654])
    t, res = _write(tmp_path, studies, freeze.tuned_yaml(studies, dec, [50, 200, 654], "abc"))
    cfg = _cfg()
    cfg["models"]["injection_mode"] = "D-late"
    t.write_text(t.read_text().replace("dropout: 0.1", "dropout: 0.2", 1))
    assert any("!= best params" in e for e in check_prereg.tuned_errors(cfg, t, res))
    assert check_prereg.tuned_errors(cfg, tmp_path / "missing.yaml", res)
    cfg["models"]["injection_mode"] = "TBD"
    assert check_prereg.tuned_errors(cfg, tmp_path / "missing.yaml", res) == []


def test_set_injection_mode():
    text = (ROOT / "configs" / "config.yaml").read_text()
    new = freeze.set_injection_mode(text, "D-state")
    assert yaml.safe_load(new)["models"]["injection_mode"] == "D-state"
    assert len(new.splitlines()) == len(text.splitlines())

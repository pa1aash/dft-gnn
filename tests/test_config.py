import pytest
import yaml
from pydantic import ValidationError

from dftgnn.config import DEFAULT_CONFIG, load_config


def test_default_config_loads():
    cfg = load_config()
    assert cfg.data.charge_state == 0
    assert cfg.split.group_key == "formula"
    assert cfg.split.n_outer_resamples == 10
    assert cfg.stats.delta_eV == 0.05
    assert cfg.stats.ci == 0.95
    assert cfg.mlip.model == "mace-mp-0"
    assert cfg.budgets.max == 654
    assert cfg.data.universe == "universe_v1"
    assert cfg.secondary_metric.within_host is True
    assert cfg.data.filters[0].startswith("D1")


def _raw():
    return yaml.safe_load(DEFAULT_CONFIG.read_text())


def test_unknown_key_rejected(tmp_path):
    raw = _raw()
    raw["split"]["surprise"] = 1
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(raw))
    with pytest.raises(ValidationError):
        load_config(p)


def test_bad_group_key_rejected(tmp_path):
    raw = _raw()
    raw["split"]["group_key"] = "structure"
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(raw))
    with pytest.raises(ValidationError):
        load_config(p)


def test_tbd_only_where_allowed(tmp_path):
    raw = _raw()
    raw["stats"]["bootstrap_n"] = "TBD"
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(raw))
    with pytest.raises(ValidationError):
        load_config(p)


def test_model_d_descriptor_classes():
    import pandas as pd

    cfg = load_config()
    taxonomy = set(pd.read_csv(DEFAULT_CONFIG.parents[1] / "docs" / "descriptor_taxonomy.csv")["class"])
    assert cfg.models.D.descriptor_classes == ["host-electronic DFT", "site-electronic DFT"]
    assert set(cfg.models.D.descriptor_classes) <= taxonomy

"""Load and validate the project configuration."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

TBD = Literal["TBD"]
DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "configs" / "config.yaml"


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DataCfg(_Strict):
    raw_dir: str
    processed_dir: str
    charge_state: int = 0
    filters: list[str] = Field(default_factory=list)
    universe: str | TBD = "TBD"


class SplitCfg(_Strict):
    group_key: Literal["formula"] = "formula"
    n_outer_resamples: int = Field(10, gt=0)
    test_fraction: float = Field(gt=0, lt=1)
    seeds: list[int]


class BudgetsCfg(_Strict):
    hosts: list[int] = Field(default_factory=list)
    max: int | TBD


class ToggleCfg(_Strict):
    enabled: bool = True


class PhysicsFloorCfg(ToggleCfg):
    n_parameters: int = 2


class NetCfg(ToggleCfg):
    backbone: Literal["megnet"] = "megnet"


DescriptorClass = Literal["structural/compositional", "host-electronic DFT", "site-electronic DFT"]


class DNetCfg(NetCfg):
    descriptor_classes: list[DescriptorClass] = Field(min_length=1)


class ModelsCfg(_Strict):
    rf: ToggleCfg
    physics_floor: PhysicsFloorCfg
    S: NetCfg
    D: DNetCfg
    P: NetCfg
    injection_mode: str | TBD


class TuningCfg(_Strict):
    optuna_trials_per_model_per_anchor: int | TBD
    anchors: list[int] | TBD


class EarlyStoppingCfg(_Strict):
    patience: int | TBD
    min_delta: float | TBD


class TrainingCfg(_Strict):
    max_epochs: int | TBD
    early_stopping: EarlyStoppingCfg


class SecondaryMetricCfg(_Strict):
    within_host: bool | TBD = "TBD"


class StatsCfg(_Strict):
    bootstrap_n: int = Field(gt=0)
    delta_eV: float = Field(gt=0)
    ci: float = Field(gt=0, lt=1)


class MlipCfg(_Strict):
    model: str
    version: str | TBD


class ProbeCfg(_Strict):
    enabled: bool = False
    settings: dict | TBD = "TBD"


class PathsCfg(_Strict):
    results_dir: str
    figures_dir: str
    handoff_dir: str


class Config(_Strict):
    data: DataCfg
    split: SplitCfg
    budgets: BudgetsCfg
    models: ModelsCfg
    tuning: TuningCfg
    training: TrainingCfg
    stats: StatsCfg
    secondary_metric: SecondaryMetricCfg = Field(default_factory=SecondaryMetricCfg)
    mlip: MlipCfg
    probe: ProbeCfg
    paths: PathsCfg


def load_config(path: str | Path | None = None) -> Config:
    """Read a YAML file and return the validated Config."""
    with open(path or DEFAULT_CONFIG, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    return Config.model_validate(raw)

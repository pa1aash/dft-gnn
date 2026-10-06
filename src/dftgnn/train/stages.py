"""Job-spec builders for the queue stages. S06 implements ``smoke`` and ``kiyohara``.

Every job is ``{"run_id", "stage", "spec", "after"}``. The run id is computed at enqueue time from the
code SHA and the graphs manifest sha256, so the pod computes the same id from the same commit.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from dftgnn.config import Config, load_config
from dftgnn.models import HParams
from dftgnn.split import budget_train, load_split
from dftgnn.train import RunSpec, run_id, val_seed

STAGES = ("tune", "sweep", "kiyohara", "loco", "sensitivity", "smoke")
# smoke only: fixed, untuned optimiser settings for a pipeline check (not a hyperparameter choice)
SMOKE_OPT = {"lr": 1e-3, "weight_decay": 1e-5, "batch_size": 16}
SMOKE_EPOCHS = 3
SMOKE_SIZES = {"train": 20, "val": 5, "test": 10}


def _job(spec: RunSpec, stage: str, code: str, gsha: str, after=()) -> dict:
    return {"run_id": run_id(spec, code, gsha), "stage": stage, "spec": spec.to_dict(),
            "after": list(after)}


def smoke_hosts(r: int = 0, budget: int = 25) -> dict[str, list[str]]:
    """20 train + 5 val hosts from resample r's budget-25 set, 10 test hosts from its test set."""
    sp = load_split(f"outer_r{r}")
    pool = sorted(budget_train(sp, budget))
    rng = np.random.default_rng(val_seed(r, budget, 0))
    perm = rng.permutation(len(pool))
    val = sorted(pool[i] for i in perm[: SMOKE_SIZES["val"]])
    train = sorted(set(pool) - set(val))
    test = sorted(rng.choice(sorted(sp["test"]), size=SMOKE_SIZES["test"], replace=False).tolist())
    return {"train": train, "val": val, "test": test}


def build_smoke(code: str, gsha: str) -> list[dict]:
    hosts = smoke_hosts()
    base = {"hp": HParams().to_dict(), **SMOKE_OPT, "split": "outer_r0", "r": 0, "budget": 25,
            "seed": 0, "hosts": hosts, "max_epochs": SMOKE_EPOCHS, "patience": SMOKE_EPOCHS,
            "smoke": True}
    jobs = {m: _job(RunSpec(model=m, **base), "smoke", code, gsha) for m in ("S", "D-state", "D-late", "P1")}
    p = RunSpec(model="P", **base, p1_run=jobs["P1"]["run_id"], d_run=jobs["D-state"]["run_id"])
    return [*jobs.values(), _job(p, "smoke", code, gsha, after=[jobs["P1"]["run_id"],
                                                               jobs["D-state"]["run_id"]])]


def build_kiyohara(code: str, gsha: str, hparams: dict, cfg: Config | None = None,
                   d_variant: str | None = None) -> list[dict]:
    """S, D and P on the Kiyohara split (sensitivity b, gate C0), seeds ``training.seeds``.

    ``hparams[model]`` = {"hp": {...}, "lr", "weight_decay", "batch_size"} from tuning, for S, the D
    variant and P1; the budget's anchor is 654. D is ``models.injection_mode`` unless ``d_variant`` is
    given. ``max_epochs`` and the early-stopping patience must be set in the config (S07).
    """
    cfg = cfg if cfg is not None else load_config()
    if "TBD-S07" in (cfg.training.max_epochs, cfg.training.early_stopping.patience):
        raise ValueError("training.max_epochs / early_stopping.patience are still TBD-S07")
    d = d_variant or cfg.models.injection_mode
    if d not in ("D-state", "D-late"):
        raise ValueError("D variant undecided: set models.injection_mode or pass d_variant")
    models = []
    for m in cfg.sensitivity.kiyohara_split.models:
        models += {"S": ["S"], "D": [d], "P": ["P1"]}[m]
    missing = [m for m in models if m not in hparams]
    if missing:
        raise ValueError(f"no tuned hyperparameters for {missing}")
    n_train = len(load_split("kiyohara")["train"])
    jobs = []
    for seed in cfg.training.seeds:
        made = {}
        for m in models:
            h = hparams[m]
            spec = RunSpec(model=m, hp=h["hp"], lr=h["lr"], weight_decay=h["weight_decay"],
                           batch_size=h["batch_size"], split="kiyohara", r=-1, budget=n_train, seed=seed)
            made[m] = _job(spec, "kiyohara", code, gsha)
        jobs += made.values()
        if "P" in cfg.sensitivity.kiyohara_split.models:
            h = hparams[d]
            p = RunSpec(model="P", hp=h["hp"], lr=h["lr"], weight_decay=h["weight_decay"],
                        batch_size=h["batch_size"], split="kiyohara", r=-1, budget=n_train, seed=seed,
                        p1_run=made["P1"]["run_id"], d_run=made[d]["run_id"])
            jobs.append(_job(p, "kiyohara", code, gsha, after=[made["P1"]["run_id"], made[d]["run_id"]]))
    return jobs


def load_hparams(path: Path) -> dict:
    return json.loads(Path(path).read_text())

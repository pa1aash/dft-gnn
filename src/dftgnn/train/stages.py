"""Job-spec builders for the queue stages: ``smoke`` and ``kiyohara`` (S06), ``pilot_epochs``,
``c0_pilot`` and ``c0_ablate`` (S07), ``sweep`` (S08).

Every job is ``{"run_id", "stage", "spec", "after", "est_peak_gb"}``. The run id is computed at enqueue
time from the code SHA and the graphs manifest sha256, so the pod computes the same id from the same
commit. ``est_peak_gb`` is the admission estimate (``dftgnn.train.admission``) when a benchmark table
is passed.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from dftgnn.config import Config, load_config
from dftgnn.models import HParams
from dftgnn.split import budget_train, load_split
from dftgnn.train import RunSpec, admission, run_id, val_seed

STAGES = ("tune", "sweep", "kiyohara", "loco", "sensitivity", "smoke", "pilot_epochs", "c0_pilot", "c0_ablate",
          "c0_capcheck", "c0_official")
# smoke only: fixed, untuned optimiser settings for a pipeline check (not a hyperparameter choice)
SMOKE_OPT = {"lr": 1e-3, "weight_decay": 1e-5, "batch_size": 16}
SMOKE_EPOCHS = 3
SMOKE_SIZES = {"train": 20, "val": 5, "test": 10}


def _job(spec: RunSpec, stage: str, code: str, gsha: str, after=(), table: dict | None = None) -> dict:
    job = {"run_id": run_id(spec, code, gsha), "stage": stage, "spec": spec.to_dict(), "after": list(after)}
    if table is not None:
        job["est_peak_gb"] = round(admission.est_peak_for_spec(table, spec.hp, spec.batch_size), 3)
    return job


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


def build_smoke(code: str, gsha: str, table: dict | None = None) -> list[dict]:
    hosts = smoke_hosts()
    base = {"hp": HParams().to_dict(), **SMOKE_OPT, "split": "outer_r0", "r": 0, "budget": 25,
            "seed": 0, "hosts": hosts, "max_epochs": SMOKE_EPOCHS, "patience": SMOKE_EPOCHS,
            "smoke": True}
    jobs = {m: _job(RunSpec(model=m, **base), "smoke", code, gsha, table=table)
            for m in ("S", "D-state", "D-late", "P1")}
    p = RunSpec(model="P", **base, p1_run=jobs["P1"]["run_id"], d_run=jobs["D-state"]["run_id"])
    return [*jobs.values(), _job(p, "smoke", code, gsha, after=[jobs["P1"]["run_id"],
                                                               jobs["D-state"]["run_id"]], table=table)]


def build_kiyohara(code: str, gsha: str, hparams: dict, cfg: Config | None = None,
                   d_variant: str | None = None, table: dict | None = None) -> list[dict]:
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
            made[m] = _job(spec, "kiyohara", code, gsha, table=table)
        jobs += made.values()
        if "P" in cfg.sensitivity.kiyohara_split.models:
            h = hparams[d]
            p = RunSpec(model="P", hp=h["hp"], lr=h["lr"], weight_decay=h["weight_decay"],
                        batch_size=h["batch_size"], split="kiyohara", r=-1, budget=n_train, seed=seed,
                        p1_run=made["P1"]["run_id"], d_run=made[d]["run_id"])
            jobs.append(_job(p, "kiyohara", code, gsha, after=[made["P1"]["run_id"], made[d]["run_id"]],
                             table=table))
    return jobs


def load_hparams(path: Path) -> dict:
    return json.loads(Path(path).read_text())


TUNED = Path(__file__).resolve().parents[3] / "configs" / "tuned_v1.yaml"
OPT_KEYS = ("learning_rate", "weight_decay", "batch_size")


def load_tuned(path: Path = TUNED) -> dict:
    """``configs/tuned_v1.yaml``: ``{"d_variant", "models": {model: {anchor: search-space params}}}``."""
    import yaml

    t = yaml.safe_load(Path(path).read_text())
    t["models"] = {m: {int(a): p for a, p in by.items()} for m, by in t["models"].items()}
    return t


def tuned_hparams(tuned: dict, model: str, anchor: int) -> dict:
    """Tuned search-space parameters -> {"hp", "lr", "weight_decay", "batch_size"} for a RunSpec."""
    p = tuned["models"][model][anchor]
    return {"hp": {k: v for k, v in p.items() if k not in OPT_KEYS}, "lr": float(p["learning_rate"]),
            "weight_decay": float(p["weight_decay"]), "batch_size": int(p["batch_size"])}


def build_sweep(code: str, gsha: str, tuned: dict, cfg: Config | None = None,
                table: dict | None = None) -> list[dict]:
    """The primary sweep (ANALYSIS_PLAN sections 7-8): S, D (the selected injection variant) and P1 for
    every outer resample, budget and seed, plus one P evaluation per (r, B, seed) that depends on its
    P1 and D runs. Each run takes the tuned hyperparameters of its budget's anchor
    (``tuning.budget_to_anchor``). Validation hosts and run ids follow the same rules as every other
    stage (``val_seed``, ``run_id``)."""
    cfg = cfg if cfg is not None else load_config()
    if "TBD-S07" in (cfg.training.max_epochs, cfg.training.early_stopping.patience):
        raise ValueError("training.max_epochs / early_stopping.patience are still TBD-S07")
    d = tuned["d_variant"]
    if d not in ("D-state", "D-late") or cfg.models.injection_mode != d:
        raise ValueError(f"D variant {d!r} does not match models.injection_mode {cfg.models.injection_mode!r}")
    b2a = cfg.tuning.budget_to_anchor
    jobs = []
    for r in range(cfg.split.n_outer_resamples):
        for b in cfg.budgets.hosts:
            for seed in cfg.training.seeds:
                made = {}
                for m in ("S", d, "P1"):
                    spec = RunSpec(model=m, **tuned_hparams(tuned, m, b2a[b]), split=f"outer_r{r}", r=r,
                                   budget=b, seed=seed)
                    made[m] = _job(spec, "sweep", code, gsha, table=table)
                jobs += made.values()
                p = RunSpec(model="P", **tuned_hparams(tuned, d, b2a[b]), split=f"outer_r{r}", r=r, budget=b,
                            seed=seed, p1_run=made["P1"]["run_id"], d_run=made[d]["run_id"])
                jobs.append(_job(p, "sweep", code, gsha, after=[made["P1"]["run_id"], made[d]["run_id"]],
                                 table=table))
    return jobs


def kiyohara_hparams_from_tuned(tuned: dict, anchor: int = 654) -> dict:
    """``build_kiyohara``'s hparams: the 654-host anchor's values (clarification, docs/deviations.md)."""
    d = tuned["d_variant"]
    return {m: tuned_hparams(tuned, m, anchor) for m in ("S", d, "P1")}


# Untuned mid-space hyperparameters of the S07 pilots (bug detection and epoch calibration only; the
# official C0 uses the tuned values). Logged in docs/deviations.md before the runs.
PILOT_HP = {"hidden_width": 64, "megnet_blocks": 3, "dropout": 0.1, "readout_mlp_width": 64,
            "pooling": "set2set"}
PILOT_OPT = {"lr": 1e-3, "weight_decay": 1e-5, "batch_size": 32}
PILOT_BUDGETS = (25, 200, 654)
PILOT_MAX_EPOCHS = 1500


def build_pilot_epochs(code: str, gsha: str, table: dict | None = None) -> list[dict]:
    """Model S on resample 0's budget-25/200/654 sets, seed 0, 1500 epochs, early stopping disabled
    (patience = max_epochs), validation MAE every epoch. The test hosts are never loaded."""
    jobs = []
    for b in PILOT_BUDGETS:
        spec = RunSpec(model="S", hp=PILOT_HP, **PILOT_OPT, split="outer_r0", r=0, budget=b, seed=0,
                       max_epochs=PILOT_MAX_EPOCHS, patience=PILOT_MAX_EPOCHS, eval_test=False,
                       results_subdir="pilot_epochs", tags={"pilot": "epochs"})
        jobs.append(_job(spec, "pilot_epochs", code, gsha, table=table))
    return jobs


def build_c0_pilot(code: str, gsha: str, cfg: Config | None = None, table: dict | None = None,
                   ablate: str | None = None) -> list[dict]:
    """Model S on the Kiyohara split with the untuned mid-space hyperparameters, seeds
    ``training.seeds``, the max_epochs and patience set in the config. ``ablate='vacancy_flag'`` is the
    diagnostic that zeroes the vacancy flag (run only if the pilot misses the C0 threshold)."""
    cfg = cfg if cfg is not None else load_config()
    if "TBD-S07" in (cfg.training.max_epochs, cfg.training.early_stopping.patience):
        raise ValueError("training.max_epochs / early_stopping.patience are still TBD-S07")
    n_train = len(load_split("kiyohara")["train"])
    sub = "c0_pilot" if ablate is None else f"c0_pilot_ablate_{ablate}"
    jobs = []
    for seed in cfg.training.seeds:
        spec = RunSpec(model="S", hp=PILOT_HP, **PILOT_OPT, split="kiyohara", r=-1, budget=n_train,
                       seed=seed, ablate=ablate, results_subdir=sub, tags={"pilot": "c0"})
        jobs.append(_job(spec, "c0_pilot" if ablate is None else "c0_ablate", code, gsha, table=table))
    return jobs


def build_c0_capcheck(code: str, gsha: str, table: dict | None = None, seeds=(0, 2),
                      max_epochs: int = 600) -> list[dict]:
    """Diagnostic only (S07): the C0-pilot seeds whose best epoch fell at the 200-epoch cap, rerun with a
    larger cap and the same patience, to see whether the cap truncates training. Excluded from every
    analysis."""
    cfg = load_config()
    n_train = len(load_split("kiyohara")["train"])
    return [_job(RunSpec(model="S", hp=PILOT_HP, **PILOT_OPT, split="kiyohara", r=-1, budget=n_train,
                         seed=seed, max_epochs=max_epochs, patience=cfg.training.early_stopping.patience,
                         results_subdir="c0_cap_check", tags={"pilot": "c0_cap_check"}),
                 "c0_capcheck", code, gsha, table=table) for seed in seeds]


def build_c0_official(code: str, gsha: str, tuned: dict, cfg: Config | None = None,
                      table: dict | None = None) -> list[dict]:
    """The official C0 of ANALYSIS_PLAN section 14: model S on the Kiyohara split (train on its train
    hosts, early-stop on its validation hosts, test on its test hosts) with the 654-host anchor's tuned
    hyperparameters, seeds ``training.seeds``, the frozen max_epochs and patience."""
    cfg = cfg if cfg is not None else load_config()
    n_train = len(load_split("kiyohara")["train"])
    h = tuned_hparams(tuned, "S", 654)
    return [_job(RunSpec(model="S", **h, split="kiyohara", r=-1, budget=n_train, seed=seed,
                         results_subdir="c0_official", tags={"c0": "official"}), "c0_official", code, gsha,
                 table=table) for seed in cfg.training.seeds]

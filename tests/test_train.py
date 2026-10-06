"""Training-loop tests (S06 step 4): tiny CPU runs on the graph store, written to tmp dirs."""
from __future__ import annotations

import hashlib
import json

import pytest
import torch

from dftgnn.config import load_config
from dftgnn.graphs import store as G
from dftgnn.split import load_split
from dftgnn.train import RunSpec, Store, epoch_limits, pick_device, resolve_hosts, run_id, val_seed

HAVE_STORE = (G.STORE_DIR / "meta.json").is_file()
needs_store = pytest.mark.skipif(not HAVE_STORE, reason="graph store not built")
HP = {"hidden_width": 64, "megnet_blocks": 2, "dropout": 0.0, "readout_mlp_width": 64, "pooling": "mean"}


def _spec(model="S", **kw):
    sp = load_split("outer_r0")
    hosts = {"train": sp["budget_order"][:6], "val": sp["budget_order"][6:8], "test": sp["test"][:3]}
    base = {"model": model, "hp": HP, "lr": 1e-3, "weight_decay": 1e-5, "batch_size": 8,
            "split": "outer_r0", "r": 0, "budget": 25, "seed": 0, "hosts": hosts, "max_epochs": 2,
            "patience": 5, "smoke": True}
    return RunSpec(**{**base, **kw})


def test_val_seed_matches_clarified_rule():
    r, b, s = 3, 200, 1
    want = int.from_bytes(hashlib.sha256(f"val|{r}|{b}|{s}".encode()).digest()[:4], "big")
    assert val_seed(r, b, s) == want
    assert load_config().training.validation.seed_rule == "sha256_val_r_B_seed_first4_bigendian"


def test_outer_val_split_is_carved_from_training_hosts():
    cfg = load_config()
    spec = _spec(hosts=None, budget=50)
    h = resolve_hosts(spec, cfg)
    assert len(h["val"]) == 5 and len(h["train"]) == 45
    assert set(h["val"]) | set(h["train"]) == set(load_split("outer_r0")["budget_order"][:50])
    assert not set(h["test"]) & (set(h["train"]) | set(h["val"]))


def test_tbd_epochs_require_override():
    with pytest.raises(ValueError):
        epoch_limits(_spec(max_epochs=None, patience=None), load_config())


def test_run_id_sensitivity():
    a = run_id(_spec(), "c", "g")
    assert a == run_id(_spec(), "c", "g") and len(a) == 16
    assert a != run_id(_spec(seed=1), "c", "g")
    assert a != run_id(_spec(), "c2", "g")
    assert a != run_id(_spec(), "c", "g2")
    assert a != run_id(_spec(hp={**HP, "pooling": "set2set"}), "c", "g")


def test_device_never_mps():
    assert pick_device().type in ("cuda", "cpu")


@pytest.fixture(scope="module")
def data():
    return Store()


@needs_store
@pytest.mark.parametrize("model", ["S", "D-state", "D-late", "P1"])
def test_train_and_idempotent(data, model, tmp_path):
    from dftgnn.train.runner import execute

    spec = _spec(model)
    kw = {"results_dir": tmp_path / "res", "ckpt_dir": tmp_path / "ck", "allow_dirty": True,
          "log": lambda *_: None}
    out = execute(spec, data, **kw)
    assert out["status"] == "done"
    pay = json.loads(out["result"].read_text())["payload"]
    assert pay["epochs_run"] == 2 and pay["smoke"] is True
    assert pay["n_hosts"] == {"train": 6, "val": 2, "test": 3}
    if model == "P1":
        assert len(pay["metrics"]["per_descriptor"]) == 22
    else:
        assert set(pay["metrics"]) == {"mae", "rmse", "r2", "within_host_mae", "host_mean_mae"}
    ck = torch.load(tmp_path / "ck" / f"{out['run_id']}.pt", weights_only=False)
    assert {"target_mean", "target_sd", "desc_mean", "desc_sd"} <= set(ck)
    assert execute(spec, data, **kw)["status"] == "skipped"


@needs_store
def test_early_stopping_restores_best(data, tmp_path):
    from dftgnn.train import train_run

    res = train_run(_spec(max_epochs=6, patience=1), data, device=torch.device("cpu"),
                    log=lambda *_: None)
    vals = [h["val_metric"] for h in res["history"]]
    assert res["best_val_metric"] == min(vals)
    assert res["epochs_run"] <= 6
    if res["epochs_run"] < 6:
        assert res["epochs_run"] - 1 - res["best_epoch"] >= 1


@needs_store
def test_cpu_runs_are_reproducible(data):
    from dftgnn.train import train_run

    a = train_run(_spec(max_epochs=1), data, device=torch.device("cpu"), log=lambda *_: None)
    b = train_run(_spec(max_epochs=1), data, device=torch.device("cpu"), log=lambda *_: None)
    assert a["predictions"].y_pred.equals(b["predictions"].y_pred)


@needs_store
def test_staged_p_evaluates(data, tmp_path):
    from dftgnn.train.runner import execute

    kw = {"results_dir": tmp_path / "res", "ckpt_dir": tmp_path / "ck", "allow_dirty": True,
          "log": lambda *_: None}
    p1 = execute(_spec("P1"), data, **kw)["run_id"]
    d = execute(_spec("D-late"), data, **kw)["run_id"]
    out = execute(_spec("P", p1_run=p1, d_run=d), data, **kw)
    pay = json.loads(out["result"].read_text())["payload"]
    assert pay["components"] == {"P1": p1, "D": d} and pay["checkpoint"] is None

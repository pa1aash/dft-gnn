"""Job-queue tests (S06 step 5): atomic claims, stale requeue, dependencies, status, stage builders."""
from __future__ import annotations

import json
import multiprocessing as mp
import os
import time

import pytest

from dftgnn import jobqueue as Q
from dftgnn.config import load_config
from dftgnn.split import load_split
from dftgnn.train import stages as ST


def _job(rid, after=()):
    return {"run_id": rid, "stage": "t", "spec": {"model": "S"}, "after": list(after)}


def _claimer(root, name, out):
    got = []
    while (job := Q.claim(root, name)) is not None:
        got.append(job["run_id"])
    out.put(got)


def test_concurrent_claims_are_exclusive(tmp_path):
    root = Q.init(tmp_path / "jobs")
    for i in range(60):
        Q.enqueue(root, _job(f"j{i:03d}"))
    ctx = mp.get_context("spawn")
    out = ctx.Queue()
    ps = [ctx.Process(target=_claimer, args=(root, f"w{k}", out)) for k in range(4)]
    for p in ps:
        p.start()
    got = [out.get(timeout=60) for _ in ps]
    for p in ps:
        p.join()
    flat = [x for g in got for x in g]
    assert len(flat) == 60 and len(set(flat)) == 60


def test_enqueue_is_idempotent(tmp_path):
    root = Q.init(tmp_path)
    assert Q.enqueue(root, _job("a"))
    assert not Q.enqueue(root, _job("a"))
    Q.claim(root, "w")
    assert not Q.enqueue(root, _job("a"))


def test_stale_job_returns_to_pending(tmp_path):
    root = Q.init(tmp_path)
    Q.enqueue(root, _job("a"))
    Q.claim(root, "w")
    hb = root / "running" / "a.hb"
    old = time.time() - 11 * 60
    os.utime(hb, (old, old))
    assert Q.requeue_stale(root) == ["a"]
    assert (root / "pending" / "a.json").exists() and not hb.exists()
    Q.claim(root, "w2")
    assert Q.requeue_stale(root) == []           # fresh heartbeat


def test_dependencies_gate_claims(tmp_path):
    root = Q.init(tmp_path)
    Q.enqueue(root, _job("p", after=["a"]))
    Q.enqueue(root, _job("a"))
    j = Q.claim(root, "w")
    assert j["run_id"] == "a"
    assert Q.claim(root, "w") is None
    Q.finish(root, j, ok=True, info={"wall_time_s": 2.0})
    assert Q.claim(root, "w")["run_id"] == "p"


def test_worker_records_done_and_failed(tmp_path):
    root = Q.init(tmp_path)
    for r in ("ok1", "bad", "ok2"):
        Q.enqueue(root, _job(r))

    def run(job):
        if job["run_id"] == "bad":
            raise RuntimeError("boom")
        return {"status": "done"}

    assert Q.run_worker(root, "w", run, log=lambda *_: None) == 3
    s = Q.status(root)
    assert s["counts"] == {"pending": 0, "running": 0, "done": 2, "failed": 1}
    assert "boom" in s["failures"][0]["traceback"]
    assert s["mean_wall_time_s"] is not None and s["eta_s"] == 0


def test_heartbeat_touches_file(tmp_path):
    root = Q.init(tmp_path)
    Q.enqueue(root, _job("a"))
    Q.claim(root, "w")
    hb = root / "running" / "a.hb"
    os.utime(hb, (0, 0))
    with Q.Heartbeat(root, "a", every=0.05):
        time.sleep(0.3)
    assert hb.stat().st_mtime > 1e9


def test_smoke_hosts():
    h = ST.smoke_hosts()
    assert [len(h[k]) for k in ("train", "val", "test")] == [20, 5, 10]
    sp = load_split("outer_r0")
    assert set(h["train"]) | set(h["val"]) == set(sp["budget_order"][:25])
    assert set(h["test"]) <= set(sp["test"])


def test_smoke_jobs():
    jobs = ST.build_smoke("c", "g")
    assert [j["spec"]["model"] for j in jobs] == ["S", "D-state", "D-late", "P1", "P"]
    assert all(j["spec"]["smoke"] and j["spec"]["max_epochs"] == 3 for j in jobs)
    assert set(jobs[-1]["after"]) == {jobs[3]["run_id"], jobs[1]["run_id"]}
    assert len({j["run_id"] for j in jobs}) == 5


def test_kiyohara_refuses_while_epochs_are_tbd():
    cfg = load_config()
    cfg.training.max_epochs = "TBD-S07"
    with pytest.raises(ValueError, match="TBD-S07"):
        ST.build_kiyohara("c", "g", {}, cfg, d_variant="D-state")


def test_kiyohara_jobs_when_configured():
    cfg = load_config()
    cfg.training.max_epochs = 10
    cfg.training.early_stopping.patience = 3
    hp = {"hp": {"hidden_width": 64, "megnet_blocks": 3, "dropout": 0.0, "readout_mlp_width": 64,
                 "pooling": "mean"}, "lr": 1e-3, "weight_decay": 1e-5, "batch_size": 32}
    jobs = ST.build_kiyohara("c", "g", {"S": hp, "D-late": hp, "P1": hp}, cfg, d_variant="D-late")
    assert len(jobs) == 3 * 4
    assert all(j["spec"]["split"] == "kiyohara" and j["spec"]["budget"] == 571 for j in jobs)
    assert json.dumps(jobs)                       # serialisable


def test_outbox_round_trip(tmp_path, monkeypatch):
    import importlib.util
    import sys

    qdir = Q.Path(__file__).resolve().parents[1] / "scripts" / "queue"
    monkeypatch.syspath_prepend(str(qdir))
    spec = importlib.util.spec_from_file_location("outbox", qdir / "outbox.py")
    ob = importlib.util.module_from_spec(spec)
    sys.modules["outbox"] = ob
    spec.loader.exec_module(ob)
    root = tmp_path / "repo"
    monkeypatch.setattr(ob, "ROOT", root)
    (root / "results/smoke/predictions").mkdir(parents=True)
    (root / "checkpoints").mkdir()
    (root / "results/smoke/predictions/x.parquet").write_bytes(b"pred")
    (root / "checkpoints/x.pt").write_bytes(b"ckpt")
    res = root / "results/smoke/x.json"
    res.write_text(json.dumps({"payload": {"predictions": {"path": "results/smoke/predictions/x.parquet"},
                                           "checkpoint": {"path": "checkpoints/x.pt"}}}))
    q = Q.init(root / "jobs")
    (q / "done" / "x.json").write_text(json.dumps({**_job("x"), "stage": "smoke", "result": str(res)}))
    tar = ob.pack(q, root / "outbox", "smoke")
    dest = tmp_path / "mac"
    assert ob.unpack(tar, dest) == 4
    assert (dest / "checkpoints/x.pt").read_bytes() == b"ckpt"
    with pytest.raises(SystemExit):
        tar.write_bytes(tar.read_bytes()[:-5] + b"xxxxx")
        ob.unpack(tar, dest)


def test_epoch_pilot_jobs_never_touch_test_hosts():
    from dftgnn.train import RunSpec, resolve_hosts

    jobs = ST.build_pilot_epochs("c", "g")
    assert [j["spec"]["budget"] for j in jobs] == [25, 200, 654]
    for j in jobs:
        s = j["spec"]
        assert (s["model"], s["seed"], s["r"], s["max_epochs"], s["patience"]) == ("S", 0, 0, 1500, 1500)
        assert s["eval_test"] is False and s["results_subdir"] == "pilot_epochs"
        assert resolve_hosts(RunSpec.from_dict(s), load_config())["test"] == []


def test_c0_pilot_jobs():
    jobs = ST.build_c0_pilot("c", "g", load_config())
    assert [j["spec"]["seed"] for j in jobs] == [0, 1, 2]
    assert all(j["spec"]["split"] == "kiyohara" and j["spec"]["model"] == "S" and j["spec"]["ablate"] is None
               and j["spec"]["tags"] == {"pilot": "c0"} for j in jobs)
    ab = ST.build_c0_pilot("c", "g", load_config(), ablate="vacancy_flag")
    assert {j["run_id"] for j in jobs}.isdisjoint(j["run_id"] for j in ab)
    assert all(j["stage"] == "c0_ablate" for j in ab)

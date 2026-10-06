"""S07 step 5: report the C0 bug-detection pilot (NOT the C0 result).

Model S with untuned mid-space hyperparameters, trained on Kiyohara's train hosts, early-stopped on their
validation hosts, tested on their 126 test hosts; seeds 0, 1, 2 (``results/c0_pilot/``). Reports the
seed-ensemble test MAE with its host-cluster-bootstrap 95% CI (``stats.cluster_bootstrap_n`` draws), the
within-host residual MAE, the per-seed values, and the comparison with RF-Kumagai on the same split and
with Kiyohara's published 0.29 eV. Always adds the diagnostics of the brief (curves, per-element error,
paired comparison with RF on the same hosts); with ``--ablation`` it also reads the vacancy-flag ablation
runs in ``results/c0_pilot_ablate_vacancy_flag/``. Writes ``results/c0_pilot.json`` with ``pilot = true``.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

KIYOHARA_MAE = 0.29
THRESHOLD = 0.35


def load_runs(sub: str) -> list[dict]:
    out = []
    for f in sorted((ROOT / "results" / sub).glob("*.json")):
        pay = json.loads(f.read_text())["payload"]
        if pay["spec"]["tags"].get("pilot") == "c0":
            pay["_pred"] = pd.read_parquet(ROOT / pay["predictions"]["path"])
            out.append(pay)
    return sorted(out, key=lambda p: p["spec"]["seed"])


def ensemble(runs: list[dict]) -> pd.DataFrame:
    """Per-site mean prediction over the seeds."""
    frames = [r["_pred"].set_index("site_id") for r in runs]
    base = frames[0][["host_id", "y_true"]].copy()
    base["y_pred"] = np.mean([f.loc[base.index, "y_pred"].to_numpy() for f in frames], axis=0)
    base["y_sd"] = np.std([f.loc[base.index, "y_pred"].to_numpy() for f in frames], axis=0)
    return base.reset_index()


def per_element(df: pd.DataFrame) -> list[dict]:
    from pymatgen.core import Composition

    u = pd.read_parquet(ROOT / "data" / "processed" / "universe_v1.parquet").drop_duplicates("host_id")
    comp = {h: [e.symbol for e in Composition(f).elements if e.symbol != "O"]
            for h, f in zip(u.host_id, u.formula, strict=True)}
    d = df.assign(err=(df.y_pred - df.y_true).abs())
    rows = [(el, e) for h, e in zip(d.host_id, d.err, strict=True) for el in comp[h]]
    t = pd.DataFrame(rows, columns=["element", "err"]).groupby("element").err.agg(["mean", "size"])
    t = t[t["size"] >= 8].sort_values("mean", ascending=False)
    return [{"element": k, "mae_eV": float(v["mean"]), "n_site_hosts": int(v["size"])}
            for k, v in t.head(12).iterrows()]


def summarise(runs: list[dict], n_boot: int) -> dict:
    from dftgnn.stats.metrics import cluster_bootstrap_ci, point_metrics

    ens = ensemble(runs)
    ci = cluster_bootstrap_ci(ens.y_true, ens.y_pred, ens.host_id, n_boot=n_boot)
    per_seed = [{"seed": r["spec"]["seed"], "epochs_run": r["epochs_run"], "best_epoch": r["best_epoch"],
                 "best_val_mae_eV": r["best_val_metric"], "test_mae_eV": r["metrics"]["mae"],
                 "within_host_mae_eV": r["metrics"]["within_host_mae"],
                 "final_train_l1_standardised": r["history"][-1]["train_loss"],
                 "min_train_l1_standardised": min(h["train_loss"] for h in r["history"]),
                 "wall_time_s": r["wall_time_s"]} for r in runs]
    return {"ensemble": ci, "ensemble_point": point_metrics(ens.y_true, ens.y_pred, ens.host_id),
            "per_seed": per_seed, "n_test_sites": len(ens), "n_test_hosts": int(ens.host_id.nunique()),
            "seed_sd_mean_eV": float(ens.y_sd.mean()), "per_element_top": per_element(ens),
            "_ens": ens}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ablation", action="store_true")
    a = ap.parse_args()

    from dftgnn.config import load_config
    from dftgnn.io.results import write_result
    from dftgnn.stats.metrics import cluster_bootstrap_ci

    cfg = load_config()
    n_boot = cfg.stats.cluster_bootstrap_n
    runs = load_runs("c0_pilot")
    if len(runs) != len(cfg.training.seeds):
        raise SystemExit(f"expected {len(cfg.training.seeds)} pilot runs, found {len(runs)}")
    s = summarise(runs, n_boot)
    ens = s.pop("_ens")

    rf = pd.read_parquet(ROOT / "results" / "predictions" / "rf_kumagai.parquet")
    rf = rf[rf.resample == -1].set_index("site_id").loc[ens.site_id]
    same = bool((rf.y_true.to_numpy() == ens.y_true.to_numpy()).all())
    rf_ci = cluster_bootstrap_ci(rf.y_true, rf.y_pred, rf.host_id, n_boot=n_boot)
    # paired host-bootstrap of MAE(S) - MAE(RF) on the same hosts
    eS, eR = (ens.y_pred - ens.y_true).abs().to_numpy(), np.abs(rf.y_pred.to_numpy() - rf.y_true.to_numpy())
    g = ens.host_id.to_numpy()
    hosts = np.unique(g)
    idx = {h: np.nonzero(g == h)[0] for h in hosts}
    st = np.array([[eS[idx[h]].sum(), eR[idx[h]].sum(), len(idx[h])] for h in hosts])
    w = np.random.default_rng(0).multinomial(len(hosts), np.ones(len(hosts)) / len(hosts), size=n_boot)
    tot = w @ st
    diff = tot[:, 0] / tot[:, 2] - tot[:, 1] / tot[:, 2]
    mae = s["ensemble"]["mae"]
    payload = {
        "pilot": True,
        "definition": __doc__,
        "split": "kiyohara (train 571 hosts, val 121, test 126)",
        "hyperparameters": "untuned mid-space: lr 1e-3, wd 1e-5, hidden 64, 3 blocks, dropout 0.1, batch 32, "
                           "readout 64, set2set",
        "max_epochs": runs[0]["max_epochs"], "patience": runs[0]["patience"],
        "S": s,
        "rf_kumagai_same_split": {"mae_eV": rf_ci["mae"], "within_host_mae_eV": rf_ci["within_host_mae"],
                                  "same_test_sites_and_targets": same},
        "paired_mae_S_minus_RF_eV": {"point": float(mae["point"] - rf_ci["mae"]["point"]),
                                     "ci95": [float(np.quantile(diff, 0.025)), float(np.quantile(diff, 0.975))],
                                     "n_boot": n_boot},
        "kiyohara_published_mae_eV": KIYOHARA_MAE, "c0_threshold_eV": THRESHOLD,
        "exceeds_threshold": bool(mae["point"] > THRESHOLD),
        "note": "bug-detection pilot with untuned hyperparameters; the official C0 uses tuned values after tuning",
    }
    if a.ablation:
        ab = load_runs("c0_pilot_ablate_vacancy_flag")
        sa = summarise(ab, n_boot)
        sa.pop("_ens")
        payload["ablation_vacancy_flag"] = {"S": sa, "worse_than_with_flag": bool(
            sa["ensemble"]["mae"]["point"] > mae["point"])}
    print(json.dumps({"S_mae": mae, "within_host": s["ensemble"]["within_host_mae"],
                      "rf": rf_ci["mae"]["point"], "paired": payload["paired_mae_S_minus_RF_eV"],
                      "per_seed": [(p["seed"], round(p["test_mae_eV"], 3), p["best_epoch"], p["epochs_run"])
                                   for p in s["per_seed"]]}, indent=1, default=float))
    print(write_result("c0_pilot", payload, allow_dirty=True))


if __name__ == "__main__":
    main()

"""S08 step 5: the official C0 check (ANALYSIS_PLAN section 14).

Model S with the 654-host anchor's tuned hyperparameters (``configs/tuned_v1.yaml``), trained on Kiyohara's
train hosts, early-stopped on their validation hosts and tested on their 126 test hosts; seeds 0, 1, 2
(``results/c0_official/``). Reports the seed-ensemble test MAE with its host-cluster-bootstrap 95% CI
(``stats.cluster_bootstrap_n`` draws), the within-host residual MAE, the per-seed values and the comparison
with Kiyohara's published 0.29 eV, the S07 untuned pilot and RF-Kumagai on the same split (with a paired
host bootstrap of S minus RF). The gate fails if the ensemble MAE exceeds ``gates.C0_kiyohara_max_mae_eV``.

Disclosure: the tuning objective used validation MAE on hosts of resample 0's anchor training sets. Hosts
of those sets that are Kiyohara test hosts were seen (as training or validation hosts) while the
hyperparameters were chosen; their counts per anchor are reported here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import c0_pilot_report as PILOT

KIYOHARA_MAE = PILOT.KIYOHARA_MAE


def load_runs() -> list[dict]:
    out = []
    for f in sorted((ROOT / "results" / "c0_official").glob("*.json")):
        pay = json.loads(f.read_text())["payload"]
        if pay["spec"]["tags"].get("c0") == "official":
            pay["_pred"] = pd.read_parquet(ROOT / pay["predictions"]["path"])
            out.append(pay)
    return sorted(out, key=lambda p: p["spec"]["seed"])


def tuning_overlap(cfg) -> dict:
    """Hosts of resample 0's anchor training sets (train + validation carve-out) that are Kiyohara test hosts."""
    from dftgnn.split import load_split
    from dftgnn.tune import anchor_hosts

    kt = set(load_split("kiyohara")["test"])
    out = {}
    for a in cfg.tuning.anchors:
        h = anchor_hosts(a, cfg)
        tr, va = set(h["train"]), set(h["val"])
        out[str(a)] = {"anchor_hosts": len(tr | va), "in_kiyohara_test": len((tr | va) & kt),
                       "of_which_validation_hosts": len(va & kt), "validation_hosts": len(va)}
    return out


def paired_vs_rf(ens: pd.DataFrame, rf: pd.DataFrame, n_boot: int) -> dict:
    eS = (ens.y_pred - ens.y_true).abs().to_numpy()
    eR = np.abs(rf.y_pred.to_numpy() - rf.y_true.to_numpy())
    g = ens.host_id.to_numpy()
    hosts = np.unique(g)
    idx = {h: np.nonzero(g == h)[0] for h in hosts}
    st = np.array([[eS[idx[h]].sum(), eR[idx[h]].sum(), len(idx[h])] for h in hosts])
    w = np.random.default_rng(0).multinomial(len(hosts), np.ones(len(hosts)) / len(hosts), size=n_boot)
    tot = w @ st
    diff = tot[:, 0] / tot[:, 2] - tot[:, 1] / tot[:, 2]
    return {"point": float(eS.mean() - eR.mean()),
            "ci95": [float(np.quantile(diff, 0.025)), float(np.quantile(diff, 0.975))], "n_boot": n_boot}


def main() -> None:
    from dftgnn.config import load_config
    from dftgnn.io.results import write_result
    from dftgnn.stats.metrics import cluster_bootstrap_ci

    cfg = load_config()
    n_boot = cfg.stats.cluster_bootstrap_n
    thr = cfg.gates.C0_kiyohara_max_mae_eV
    runs = load_runs()
    if len(runs) != len(cfg.training.seeds):
        raise SystemExit(f"expected {len(cfg.training.seeds)} official C0 runs, found {len(runs)}")
    s = PILOT.summarise(runs, n_boot)
    ens = s.pop("_ens")
    for p, r in zip(s["per_seed"], runs, strict=True):
        p["curve_val_mae_eV"] = [h["val_metric"] for h in r["history"]]
        p["run_id"] = r["run_id"]
    rf = pd.read_parquet(ROOT / "results" / "predictions" / "rf_kumagai.parquet")
    rf = rf[rf["resample"] == -1].set_index("site_id").loc[ens.site_id]
    same = bool((rf.y_true.to_numpy() == ens.y_true.to_numpy()).all())
    rf_ci = cluster_bootstrap_ci(rf.y_true, rf.y_pred, rf.host_id, n_boot=n_boot)
    pilot = json.loads((ROOT / "results" / "c0_pilot.json").read_text())["payload"]["S"]["ensemble"]["mae"]
    mae = s["ensemble"]["mae"]
    spec = runs[0]["spec"]
    payload = {
        "pilot": False,
        "definition": __doc__,
        "split": "kiyohara (train 571 hosts, val 121, test 126)",
        "hyperparameters": {"source": "configs/tuned_v1.yaml, model S, anchor 654", "hp": spec["hp"],
                            "lr": spec["lr"], "weight_decay": spec["weight_decay"], "batch_size": spec["batch_size"]},
        "code_sha": runs[0]["code_sha"], "max_epochs": runs[0]["max_epochs"], "patience": runs[0]["patience"],
        "S": s,
        "comparison_eV": {"kiyohara_published": KIYOHARA_MAE, "s07_untuned_pilot": pilot["point"],
                          "rf_kumagai_same_split": rf_ci["mae"]["point"]},
        "rf_kumagai_same_split": {"mae_eV": rf_ci["mae"], "within_host_mae_eV": rf_ci["within_host_mae"],
                                  "same_test_sites_and_targets": same},
        "paired_mae_S_minus_RF_eV": paired_vs_rf(ens, rf, n_boot),
        "tuning_overlap_with_kiyohara_test": tuning_overlap(cfg),
        "c0_threshold_eV": thr, "gate_passed": bool(mae["point"] <= thr),
    }
    print(json.dumps({"S_mae": mae, "within_host": s["ensemble"]["within_host_mae"],
                      "comparison": payload["comparison_eV"], "paired": payload["paired_mae_S_minus_RF_eV"],
                      "overlap": payload["tuning_overlap_with_kiyohara_test"], "gate_passed": payload["gate_passed"],
                      "per_seed": [(p["seed"], round(p["test_mae_eV"], 3), round(p["within_host_mae_eV"], 3),
                                    p["best_epoch"], p["epochs_run"]) for p in s["per_seed"]]},
                     indent=1, default=float))
    print(write_result("c0_official", payload, config=cfg))


if __name__ == "__main__":
    main()

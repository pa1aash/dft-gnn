"""N1 comparison: predictions of the 12 repeatability specs on each GPU class and node against the original sweep.

    python scripts/nrp/n1_compare.py [--faulty-node HOST] [--no-write]

Descriptive only; no tests and no thresholds. Reads every run under results/nrp/n1/<class>/<node>[/<pass>]/ and, for
the same key (model, r, B, seed), the original sweep record under results/ (read-only). Reports per run the test
MAE, the maximum and mean absolute prediction difference from the reference and whether the prediction arrays are
bitwise equal (and their sha256); per (class, model, B) the seed-ensemble MAE (mean of the three seeds' predictions
per site, as in the primary analysis) and its difference from the reference ensemble MAE; for the same-node repeat
the number of bitwise-identical runs and the maximum difference between passes; the seed SD of MAE at the same
(model, B) from results/g1_variance.json for scale; and a node flag where a node's ensemble MAE differs from the
other nodes of its class by more than that seed SD. Writes write_result("nrp_n1_gpu_repeat").
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

MODEL_KEY = {"S": "S", "D-state": "D"}


def arr_sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a, dtype=np.float64).tobytes()).hexdigest()


def references() -> dict:
    ref = {}
    for f in glob.glob(str(ROOT / "results" / "*.json")):
        try:
            p = json.loads(Path(f).read_text()).get("payload")
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(p, dict) or "spec" not in p:
            continue
        s = p["spec"]
        if s["split"] == "outer_r0" and s.get("results_subdir") is None and not s.get("smoke") \
                and s["model"] in MODEL_KEY and s["budget"] in (654, 200):
            fr = pd.read_parquet(ROOT / p["predictions"]["path"]).sort_values("site_id").reset_index(drop=True)
            ref[(s["model"], s["budget"], s["seed"])] = {"run_id": p["run_id"], "frame": fr}
    return ref


def runs() -> list[dict]:
    out = []
    for f in sorted(glob.glob(str(ROOT / "results" / "nrp" / "n1" / "**" / "*.json"), recursive=True)):
        p = json.loads(Path(f).read_text())["payload"]
        if "key" not in p:
            continue
        rel = Path(f).relative_to(ROOT / "results" / "nrp" / "n1").parts
        cls, node = rel[0], rel[1]
        pas = rel[2] if len(rel) > 3 else "pass1"
        fr = pd.read_parquet(ROOT / p["predictions"]["path"]).sort_values("site_id").reset_index(drop=True)
        out.append({"class": cls, "node": node, "pass": pas, "key": (p["key"]["model"], p["key"]["B"], p["key"]["seed"]),
                    "frame": fr, "hardware": p["hardware"], "peak_gb": p["peak_memory_bytes"] / 2**30,
                    "wall_s": p["wall_time_s"], "best_epoch": p["best_epoch"], "run_id": p["run_id"]})
    return out


def seed_sd() -> dict:
    v = json.loads((ROOT / "results" / "g1_variance.json").read_text())["payload"]["models"]
    return {(m, int(b)): {"seed_sd_resample0": x["seed_sd_per_resample"][0],
                          "seed_sd_mean_over_resamples": x["seed_sd_mean_over_resamples"]}
            for m, by in v.items() for b, x in by.items() if int(b) in (654, 200)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--faulty-node", default="hcc-nrp-shor-c6017.unl.edu")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args()
    ref, rs, sd = references(), runs(), seed_sd()
    per_run = []
    for r in rs:
        f, g = r["frame"], ref[r["key"]]["frame"]
        if not f.site_id.equals(g.site_id):
            raise SystemExit(f"site mismatch for {r['key']} on {r['node']}")
        d = (f.y_pred - g.y_pred).abs()
        per_run.append({"class": r["class"], "node": r["node"], "pass": r["pass"], "model": r["key"][0], "B": r["key"][1],
                        "seed": r["key"][2], "run_id": r["run_id"], "ref_run_id": ref[r["key"]]["run_id"],
                        "mae": float((f.y_pred - f.y_true).abs().mean()), "ref_mae": float((g.y_pred - g.y_true).abs().mean()),
                        "max_abs_diff_eV": float(d.max()), "mean_abs_diff_eV": float(d.mean()),
                        "bitwise_equal_ref": bool(np.array_equal(f.y_pred.to_numpy(), g.y_pred.to_numpy())),
                        "pred_sha256": arr_sha(f.y_pred.to_numpy()), "peak_gpu_gb": r["peak_gb"], "wall_s": r["wall_s"],
                        "best_epoch": r["best_epoch"], "gpu_model": r["hardware"]["gpu_model"],
                        "driver": r["hardware"]["driver"], "gpu_uuid": r["hardware"]["gpu_uuid"]})
    pr = pd.DataFrame(per_run)
    # seed-ensemble MAE per (class, node, pass, model, B) and per reference
    ens = []
    for (cls, node, pas, m, b), g in pr.groupby(["class", "node", "pass", "model", "B"]):
        if g.seed.nunique() < 3:
            continue
        frames = [next(x["frame"] for x in rs if x["class"] == cls and x["node"] == node and x["pass"] == pas
                       and x["key"] == (m, b, s)) for s in (0, 1, 2)]
        refs = [ref[(m, b, s)]["frame"] for s in (0, 1, 2)]
        e = np.mean([f.y_pred.to_numpy() for f in frames], axis=0)
        er = np.mean([f.y_pred.to_numpy() for f in refs], axis=0)
        yt = frames[0].y_true.to_numpy()
        ens.append({"class": cls, "node": node, "pass": pas, "model": m, "B": int(b),
                    "ensemble_mae": float(np.abs(e - yt).mean()), "ref_ensemble_mae": float(np.abs(er - yt).mean()),
                    "ensemble_mae_minus_ref": float(np.abs(e - yt).mean() - np.abs(er - yt).mean()),
                    "max_abs_ensemble_pred_diff_eV": float(np.abs(e - er).max()),
                    **sd[(MODEL_KEY[m], int(b))]})
    en = pd.DataFrame(ens)
    # same-node repeat: pass1 against pass2 on the same node
    rep = []
    for (cls, node), g in pr.groupby(["class", "node"]):
        if set(g["pass"]) >= {"pass1", "pass2"}:
            p1 = g[g["pass"] == "pass1"].set_index(["model", "B", "seed"])
            p2 = g[g["pass"] == "pass2"].set_index(["model", "B", "seed"])
            for k in p1.index.intersection(p2.index):
                f1 = next(x["frame"] for x in rs if x["node"] == node and x["pass"] == "pass1" and x["key"] == k)
                f2 = next(x["frame"] for x in rs if x["node"] == node and x["pass"] == "pass2" and x["key"] == k)
                rep.append({"class": cls, "node": node, "model": k[0], "B": k[1], "seed": k[2],
                            "bitwise_identical": p1.loc[k, "pred_sha256"] == p2.loc[k, "pred_sha256"],
                            "max_abs_diff_eV": float((f1.y_pred - f2.y_pred).abs().max())})
    rp = pd.DataFrame(rep)
    # node effects within a class (pass1 only): ensemble MAE spread across nodes against the seed SD
    flags = []
    e1 = en[en["pass"] == "pass1"] if not en.empty else en
    for (cls, m, b), g in e1.groupby(["class", "model", "B"]):
        if g.node.nunique() < 2:
            continue
        for _, row in g.iterrows():
            others = g[g.node != row.node].ensemble_mae.mean()
            dev = abs(row.ensemble_mae - others)
            flags.append({"class": cls, "model": m, "B": int(b), "node": row.node, "abs_diff_from_other_nodes_eV": float(dev),
                          "seed_sd_resample0": row.seed_sd_resample0, "exceeds_seed_sd": bool(dev > row.seed_sd_resample0)})
    hosts = sorted(pr.node.unique())
    res = {"per_run": per_run, "ensemble": ens, "same_node_repeat": rep, "node_effects": flags,
           "classes": sorted(pr["class"].unique()), "nodes": hosts,
           "peak_gpu_gb_by_class": pr.groupby("class").peak_gpu_gb.max().to_dict(),
           "wall_s_by_class_model_B": {f"{c}|{m}|{b}": float(v) for (c, m, b), v in pr.groupby(["class", "model", "B"]).wall_s.median().items()},
           "faulty_node": a.faulty_node, "runs_on_faulty_node": int((pr.node == a.faulty_node).sum()),
           "n_runs": len(pr)}
    if not rp.empty:
        res["same_node_repeat_summary"] = {"n": len(rp), "bitwise_identical": int(rp.bitwise_identical.sum()),
                                           "max_abs_diff_eV": float(rp.max_abs_diff_eV.max())}
    pd.set_option("display.width", 220)
    print(pr.groupby(["class", "model", "B"]).agg(runs=("seed", "size"), max_abs_diff=("max_abs_diff_eV", "max"),
                                                  bitwise=("bitwise_equal_ref", "sum"), peak_gb=("peak_gpu_gb", "max")).round(4))
    if not en.empty:
        print(en[["class", "node", "pass", "model", "B", "ensemble_mae", "ref_ensemble_mae", "ensemble_mae_minus_ref",
                  "seed_sd_resample0"]].round(4).to_string(index=False))
    print(res.get("same_node_repeat_summary"), "nodes:", hosts, "runs on faulty node:", res["runs_on_faulty_node"])
    if not a.no_write:
        from dftgnn.io.results import write_result

        print(write_result("nrp_n1_gpu_repeat", res, results_dir=ROOT / "results" / "nrp"))


if __name__ == "__main__":
    main()

"""Checkpoint diagnostics for the 2026-10-07 review (docs/diagnostics_sweep.md), run after the ``review`` stage.

    python scripts/diag_checkpoints.py [--device cuda] [--no-write]

Item 3, permutation importance of D's descriptors. For every unablated D run of ``results/d_ablation/``,
each descriptor column is permuted among the test examples and the rise in test MAE (eV) is recorded,
averaged over ``diagnostics.descriptor_ablation.permutation_repeats`` permutations. Host-electronic
descriptors are permuted among test hosts (a host keeps one value for all its sites); site-electronic
descriptors are permuted among test sites. Whole classes are permuted the same way. Values are reported
per run and averaged over runs.

Item 1, what training does to S's view of the site. For every S checkpoint of ``results/diag_cross/``:
the within-host spread of the test predictions, and on a fixed sample of test sites the gradient of the
output with respect to the interatomic distances (summed |d out / d r_ij| over the edges of the graph,
the geometry pathway) and with respect to the vacancy flag (the site marker). The same quantities for an
untrained network with the run's hyperparameters are the reference.
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dftgnn.config import load_config
from dftgnn.graphs import collate_sites
from dftgnn.models import HParams, build_model
from dftgnn.split import load_split
from dftgnn.train import REPO_ROOT, Store, _predict, load_checkpoint

N_GRAD_SITES = 64


def records(subdir: str) -> list[dict]:
    out = []
    for f in sorted(glob.glob(str(ROOT / "results" / subdir / "*.json"))):
        p = json.loads(Path(f).read_text())["payload"]
        out.append(p)
    return out


def test_positions(data: Store, spec: dict) -> np.ndarray:
    return data.positions(load_split(spec["split"])["test"])


def mae(pred, true) -> float:
    return float(np.abs(np.asarray(pred) - np.asarray(true)).mean())


def permutation_importance(data: Store, pay: dict, device, repeats: int, seed: int) -> dict:
    net, ck = load_checkpoint(REPO_ROOT / pay["checkpoint"]["path"], device)
    net = net.to(device)
    spec = pay["spec"]
    te = test_positions(data, spec)
    raw = data.sites["desc"].double()
    mean, sd = ck["desc_mean"].cpu().double(), ck["desc_sd"].cpu().double()
    desc = ((raw - mean) / sd).float()
    t_mean, t_sd = float(ck["target_mean"].cpu().reshape(-1)[0]), float(ck["target_sd"].cpu().reshape(-1)[0])
    true = data.sites["target"][te].numpy()

    def run(dz: torch.Tensor) -> float:
        out = _predict(net, data, te, None, dz, spec["batch_size"], device)
        return mae(out.double().numpy() * t_sd + t_mean, true)

    base = run(desc)
    names = ck["desc_names"]
    nh = len(data.sites["desc_host_names"])
    hosts = data.site_host[te]
    uh, inv = np.unique(hosts, return_inverse=True)
    rng = np.random.default_rng(seed)
    cols = {n: [j] for j, n in enumerate(names)}
    cols["class:host"] = list(range(nh))
    cols["class:site"] = list(range(nh, len(names)))
    res = {}
    for key, js in cols.items():
        host_level = all(j < nh for j in js)
        deltas = []
        for _ in range(repeats):
            dz = desc.clone()
            if host_level:                       # one permutation of the hosts, applied to all their sites
                perm_h = rng.permutation(len(uh))
                src_site = np.array([te[np.nonzero(inv == perm_h[k])[0][0]] for k in inv])
            else:
                src_site = te[rng.permutation(len(te))]
            dz[np.ix_(te, js)] = desc[np.ix_(src_site, js)]
            deltas.append(run(dz) - base)
        res[key] = {"delta_mae_eV": float(np.mean(deltas)), "sd": float(np.std(deltas, ddof=1))}
    return {"run_id": pay["run_id"], "r": spec["r"], "seed": spec["seed"], "base_mae_eV": base, "importance": res}


def grad_probe(net, data: Store, pos: np.ndarray, device) -> dict:
    """Mean over sites of summed |d out / d edge distance| and |d out / d flag at the vacancy node|."""
    net = net.to(device).eval()
    g_geo, g_flag = [], []
    for p in pos:
        b = collate_sites(data.graphs, data.sites, [int(p)]).to(device)
        b.edge_dist = b.edge_dist.clone().requires_grad_(True)
        b.vac_flag = b.vac_flag.clone().requires_grad_(True)
        net.zero_grad()
        with torch.backends.cudnn.flags(enabled=False):   # cuDNN's LSTM (set2set) has no backward in eval mode
            net(b).sum().backward()
        g_geo.append(float(b.edge_dist.grad.abs().sum()))
        g_flag.append(float(b.vac_flag.grad[b.vacancy_index].abs().sum()))
    return {"geometry_grad": float(np.mean(g_geo)), "flag_grad": float(np.mean(g_flag))}


def within_spread(pred_path: Path) -> dict:
    d = pd.read_parquet(pred_path)
    n = d.groupby("host_id").y_pred.transform("size")
    m = d[n >= 2]
    g = m.groupby("host_id")
    rng = g.y_pred.max() - g.y_pred.min()
    return {"pred_within_spread_eV": float((m.y_pred - g.y_pred.transform("mean")).abs().mean()),
            "n_multi_hosts": int(rng.size), "n_const_hosts_1meV": int((rng < 1e-3).sum())}


def cross_probe(data: Store, pay: dict, device) -> dict:
    spec = pay["spec"]
    te = test_positions(data, spec)
    sample = np.random.default_rng(0).choice(te, size=min(N_GRAD_SITES, len(te)), replace=False)
    trained, _ = load_checkpoint(REPO_ROOT / pay["checkpoint"]["path"], device)
    torch.manual_seed(spec["seed"])
    fresh = build_model(spec["model"], HParams(**spec["hp"]), n_host=data.n_host,
                        n_site=data.sites["desc"].shape[1] - data.n_host, cutoff=data.meta["cutoff_A"])
    return {"run_id": pay["run_id"], "budget": spec["budget"], "anchor": spec["tags"].get("anchor"),
            "r": spec["r"], "seed": spec["seed"], "best_epoch": pay["best_epoch"] + 1,
            "test_mae_eV": pay["metrics"]["mae"], "within_host_mae_eV": pay["metrics"]["within_host_mae"],
            **within_spread(REPO_ROOT / pay["predictions"]["path"]),
            "trained": grad_probe(trained, data, sample, device), "untrained": grad_probe(fresh, data, sample, device)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args()
    cfg = load_config()
    dev = torch.device(a.device)
    data = Store()
    da = cfg.diagnostics.descriptor_ablation
    perm = [permutation_importance(data, p, dev, da.permutation_repeats, da.permutation_seed)
            for p in records("d_ablation") if p["spec"]["ablate"] is None]
    keys = perm[0]["importance"].keys() if perm else []
    perm_mean = {k: float(np.mean([p["importance"][k]["delta_mae_eV"] for p in perm])) for k in keys}
    cross = [cross_probe(data, p, dev) for p in records("diag_cross")]
    payload = {"permutation_importance": {"per_run": perm, "mean_over_runs": perm_mean,
                                         "repeats": da.permutation_repeats, "seed": da.permutation_seed},
               "hparam_cross_probe": cross, "n_grad_sites": N_GRAD_SITES, "device": str(dev)}
    for k, v in sorted(perm_mean.items(), key=lambda kv: -kv[1]):
        print(f"{k:40s} {v:+.4f}")
    for c in cross:
        print({k: c[k] for k in ("budget", "anchor", "r", "seed", "within_host_mae_eV", "pred_within_spread_eV")},
              c["trained"], c["untrained"])
    if not a.no_write:
        from dftgnn.io.results import write_result

        print(write_result("diag_checkpoints", payload, config=cfg))


if __name__ == "__main__":
    main()

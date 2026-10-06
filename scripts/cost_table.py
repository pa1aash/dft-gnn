"""S07 step 6: GPU-hour and cost table for the remaining pre-registered workload (runs on the Mac).

Inputs (all committed results): ``gpu_benchmark.json`` (seconds per epoch for every (hidden, batch,
blocks) cell at budget 654, and the concurrency scaling), ``gpu_epoch_scaling.json`` (measured seconds
per epoch, training plus validation pass, at every budget and on the Kiyohara split; the ratio to the
654-host training epoch scales a cell's time to any budget), ``pilot_epochs.json`` (e_conv per budget, max_epochs, patience)
and ``configs/config.yaml`` (the workload). Prices are fetched headlessly from RunPod's public GraphQL
endpoint; a failed fetch is logged and the price left blank, never estimated.

Model of one run's GPU time (central)
    s_epoch(cell, B) = s_epoch_654(cell) x epoch_total(B) / train_epoch(654)
    epochs           = e_conv(B) + patience               (expected early-stopping point)
    GPU-hours        = runs x epochs x s_epoch / speedup / 3600
with ``cell`` the mean over the 18 benchmarked (hidden, batch, blocks) cells for tuning trials (the
search space is categorical in all three) and the model's fixed cell otherwise, and ``speedup`` the
measured aggregate-throughput ratio of N concurrent workers to one (CUDA MPS, 4 workers).
Upper bound: the slowest cell, ``max_epochs`` epochs (early stopping never fires) and no concurrency gain.
e_conv(B) for budgets other than the three piloted ones is interpolated linearly in log B and clamped
to the piloted range.
"""
# ruff: noqa: ISC004
from __future__ import annotations

import json
import math
import sys
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

DISK_USD_PER_H = 0.04          # observed in this deployment (S07 brief), not fetched
GQL = "https://api.runpod.io/graphql"
CARDS = {                      # RunPod gpuTypes id -> label used in the table
    "NVIDIA L40S": "L40S (current)",
    "NVIDIA RTX 6000 Ada Generation": "RTX 6000 Ada",
    "NVIDIA A40": "A40",
    "NVIDIA GeForce RTX 4090": "RTX 4090",
    "NVIDIA A100 80GB PCIe": "A100 80GB PCIe",
    "NVIDIA A100-SXM4-80GB": "A100 80GB SXM",
    "NVIDIA H100 PCIe": "H100 PCIe",
    "NVIDIA H100 80GB HBM3": "H100 SXM",
    "NVIDIA H100 NVL": "H100 NVL",
}


def fetch_prices() -> tuple[dict, list[str]]:
    """{gpu id: {"secure": usd/h or None, "community": usd/h or None}} and a list of failure notes."""
    notes: list[str] = []
    out = {k: {"secure": None, "community": None} for k in CARDS}
    q = {"query": "query { gpuTypes { id displayName memoryInGb securePrice communityPrice } }"}
    try:
        req = urllib.request.Request(GQL, data=json.dumps(q).encode(),
                                     headers={"Content-Type": "application/json", "User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=30) as r:
            types = {g["id"]: g for g in json.load(r)["data"]["gpuTypes"]}
    except Exception as e:  # noqa: BLE001 - any fetch failure leaves every price blank
        return out, [f"RunPod GraphQL gpuTypes fetch failed: {e!r}; all prices left blank"]
    for k in CARDS:
        g = types.get(k)
        if g is None:
            notes.append(f"{k}: not listed by the endpoint; prices left blank")
            continue
        for tier, key in (("secure", "securePrice"), ("community", "communityPrice")):
            v = g.get(key)
            if v:                                    # 0 / null: the tier does not offer this card
                out[k][tier] = float(v)
            else:
                notes.append(f"{k}: no {tier} price listed; left blank")
        out[k]["memory_gb"] = g.get("memoryInGb")
    return out, notes


def load(name: str) -> dict:
    return json.loads((ROOT / "results" / f"{name}.json").read_text())["payload"]


def interp_e_conv(budget: int, conv: dict[int, int]) -> float:
    bs = sorted(conv)
    return float(np.interp(math.log(budget), [math.log(b) for b in bs], [conv[b] for b in bs]))


def train_sites(budgets: list[int]) -> dict[int, int]:
    """Training sites of resample 0 at each budget (after the 10% validation hosts are removed)."""
    from dftgnn.config import load_config
    from dftgnn.train import RunSpec, Store, resolve_hosts

    data, cfg = Store(verify=False), load_config()
    out = {}
    for b in budgets:
        spec = RunSpec(model="S", hp={}, lr=0, weight_decay=0, batch_size=32, split="outer_r0", r=0,
                       budget=b, seed=0, eval_test=False)
        out[b] = len(data.positions(resolve_hosts(spec, cfg)["train"]))
    spec = RunSpec(model="S", hp={}, lr=0, weight_decay=0, batch_size=32, split="kiyohara", r=-1,
                   budget=0, seed=0, eval_test=False)
    out["kiyohara"] = len(data.positions(resolve_hosts(spec, cfg)["train"]))
    return out


def workload(cfg) -> list[dict]:
    """The remaining pre-registered runs, by stage and (model group, budget, n_runs)."""
    t = cfg.tuning
    n_models_tune = len(t.models)
    stages = []
    stages.append({"stage": "tune", "note": "S, D-state, D-late, P1 x anchors x trials; one run per trial",
                   "groups": [{"budget": a, "runs": n_models_tune * t.optuna_trials_per_model_per_anchor,
                               "cell": "mean"} for a in t.anchors]})
    n_res, seeds = cfg.split.n_outer_resamples, len(cfg.training.seeds)
    stages.append({"stage": "sweep", "note": "S, D, P1 x resamples x budgets x seeds (P is evaluation only)",
                   "groups": [{"budget": b, "runs": 3 * n_res * seeds, "cell": "tuned"}
                              for b in cfg.budgets.hosts]})
    stages.append({"stage": "kiyohara", "note": "S, D, P1 x seeds", "groups": [
        {"budget": "kiyohara", "runs": 3 * seeds, "cell": "tuned"}]})
    lo = cfg.robustness.loco
    stages.append({"stage": "loco", "note": "S, D x folds x seeds; training size taken as the 654-host maximum",
                   "groups": [{"budget": cfg.budgets.max, "runs": len(lo.models) * lo.k * len(lo.seeds),
                               "cell": "tuned"}]})
    s = cfg.sensitivity
    stages.append({"stage": "sensitivity", "note": "high-moment exclusion, S and D at the maximum budget",
                   "groups": [{"budget": s.exclude_high_moment.budget,
                               "runs": len(s.exclude_high_moment.models) * n_res * seeds, "cell": "tuned"}]})
    c = s.cgcnn_check
    stages.append({"stage": "cgcnn", "note": "S, D x budgets x seeds, resample 0; timed with the MEGNet-S cell "
                   "(a CGCNN backbone was not benchmarked)",
                   "groups": [{"budget": b, "runs": len(c.models) * len(c.seeds), "cell": "tuned"}
                              for b in c.budgets]})
    return stages


def main() -> None:
    from dftgnn.config import load_config
    from dftgnn.io.results import write_result

    cfg = load_config()
    bench, scaling, pilot = load("gpu_benchmark"), load("gpu_epoch_scaling"), load("pilot_epochs")
    mps = load("gpu_benchmark_mps")
    grid = {(r["hidden"], r["batch"], r["blocks"]): r["s_per_epoch"] for r in bench["grid"]}
    cells = {"mean": float(np.mean(list(grid.values()))), "slowest": max(grid.values()),
             "tuned": grid[(64, 32, 3)]}
    # "tuned" cells are unknown until tuning: use the mean of the grid as the central value and the
    # slowest cell as the bound, exactly as for tuning trials; (64, 32, 3) is reported for reference.
    cells["tuned"] = cells["mean"]
    rows_by = {("kiyohara" if r["split"] == "kiyohara" else r["budget_hosts"]): r for r in scaling["rows"]}
    ref = rows_by[cfg.budgets.max]["train_epoch_s_median"]
    epoch_scale = {b: r["epoch_total_s"] / ref for b, r in rows_by.items()}
    conv = {int(b): d["e_conv"] for b, d in pilot["budgets"].items()}
    max_epochs, patience = pilot["max_epochs"], pilot["patience"]

    def one_worker(rows):
        return float(np.mean([r["aggregate_epochs_per_hour"] for r in rows if r["workers"] == 1]))

    mps_rows = mps["concurrency"]
    speed = {n: float(np.mean([r["aggregate_epochs_per_hour"] for r in mps_rows if r["workers"] == n]))
             / one_worker(mps_rows) for n in sorted({r["workers"] for r in mps_rows})}
    plain = {n: float(np.mean([r["aggregate_epochs_per_hour"] for r in bench["concurrency"] if r["workers"] == n]))
             / one_worker(bench["concurrency"]) for n in sorted({r["workers"] for r in bench["concurrency"]})}
    central_speedup = speed[4]

    stages = workload(cfg)
    budgets = sorted({g["budget"] for s in stages for g in s["groups"] if isinstance(g["budget"], int)})
    sites = train_sites(budgets)
    prices, notes = fetch_prices()
    rows, tot_c, tot_u = [], 0.0, 0.0
    for s in stages:
        runs = c_h = u_h = 0.0
        det = []
        for g in s["groups"]:
            b = g["budget"]
            n_sites = sites[b]
            scale = epoch_scale[b]
            epochs_c = interp_e_conv(sites_budget(b), conv) + patience
            c_h_g = g["runs"] * epochs_c * cells[g["cell"]] * scale / central_speedup / 3600
            u_h_g = g["runs"] * max_epochs * cells["slowest"] * scale / 1.0 / 3600
            runs += g["runs"]
            c_h += c_h_g
            u_h += u_h_g
            det.append({"budget": b, "runs": g["runs"], "train_sites": n_sites,
                        "expected_epochs": epochs_c, "central_gpu_h": c_h_g, "upper_gpu_h": u_h_g})
        rows.append({"stage": s["stage"], "note": s["note"], "runs": int(runs), "central_gpu_h": c_h,
                     "upper_gpu_h": u_h, "detail": det})
        tot_c += c_h
        tot_u += u_h
    l40s = prices["NVIDIA L40S"]
    rate = (l40s["secure"] or 0) + DISK_USD_PER_H
    for r in rows:
        r["central_usd"] = r["central_gpu_h"] * rate if l40s["secure"] else None
        r["upper_usd"] = r["upper_gpu_h"] * rate if l40s["secure"] else None
    payload = {
        "definition": __doc__, "pilot": False, "card": "NVIDIA L40S (measured)", "rate_usd_per_h": rate if l40s["secure"] else None,
        "rate_basis": "RunPod Secure Cloud GPU price from the public GraphQL endpoint + 0.04 USD/h disks (observed)",
        "max_epochs": max_epochs, "patience": patience, "e_conv": conv,
        "s_per_epoch_cells": {"mean": cells["mean"], "slowest": cells["slowest"],
                              "h64_b32_k3": grid[(64, 32, 3)]},
        "epoch_scale_vs_654_train_epoch": {str(k): v for k, v in epoch_scale.items()},
        "train_sites": {str(k): v for k, v in sites.items()},
        "speedup_mps": speed, "speedup_no_mps": plain, "central_speedup_used": central_speedup,
        "epochs_per_h_mps": {str(n): speed[n] * one_worker(mps_rows) for n in speed},
        "epochs_per_h_no_mps": {str(n): plain[n] * one_worker(bench["concurrency"]) for n in plain},
        "saturation_note": saturation_note(bench, mps, speed, plain),
        "stages": rows, "total_central_gpu_h": tot_c, "total_upper_gpu_h": tot_u,
        "total_central_usd": tot_c * rate if l40s["secure"] else None,
        "total_upper_usd": tot_u * rate if l40s["secure"] else None,
        "tune_plus_sweep_central_gpu_h": sum(r["central_gpu_h"] for r in rows if r["stage"] in ("tune", "sweep")),
        "tune_plus_sweep_upper_gpu_h": sum(r["upper_gpu_h"] for r in rows if r["stage"] in ("tune", "sweep")),
        "prices": {CARDS[k]: v for k, v in prices.items()}, "price_fetch_notes": notes,
        "price_source": GQL, "excluded": ["MLIP relaxations (MACE-MP-0, S09+)", "latent probe (CPU)",
                                          "figures and statistics (CPU)"],
    }
    path = write_result("cost_table", payload, allow_dirty=True)
    (ROOT / "docs" / "cost_table.md").write_text(render_md(payload))
    print(path, f"central {tot_c:.1f} GPU-h, upper {tot_u:.1f} GPU-h")


def saturation_note(bench: dict, mps: dict, speed: dict, plain: dict) -> str:
    util = {n: float(np.mean([r["gpu_util_mean_pct"] for r in bench["concurrency_sustained"]
                              if r["workers"] == n])) for n in sorted(plain)}
    return (f"**Saturation.** nvidia-smi utilisation was {util[1]:.0f}% with one worker and "
            f"{min(util[n] for n in util if n > 1):.0f}-{max(util[n] for n in util if n > 1):.0f}% with 2-8 workers; "
            f"without MPS the aggregate rate fell to {plain[2]:.2f}x (2 workers) and {plain[8]:.2f}x (8 workers) "
            f"of one worker's, because the processes time-slice the device. With CUDA MPS it rose to "
            f"{speed[4]:.2f}x at 4 workers and {speed[8]:.2f}x at 8, so the card is saturated at about 4 "
            f"workers. Utilisation did not stay low, so the data do not support moving to several cheaper cards "
            f"to gain throughput; running one pod with MPS and about 4 workers is the efficient setting "
            f"on this card.")


def _p(x) -> str:
    return "blank" if x is None else f"{x:.2f}"


def _usd(x) -> str:
    return "n/a" if x is None else f"{x:,.0f}"


def render_md(p: dict) -> str:
    """docs/cost_table.md from the payload."""
    sp = p["speedup_mps"]
    lines = [
        "# GPU cost table (S07)",
        "",
        "Remaining pre-registered training workload on the measured card (L40S, 1 GPU, 44.4 GiB usable). "
        "Numbers are generated by `scripts/cost_table.py` from committed results "
        "(`results/cost_table.json`); nothing here is a new scientific result.",
        "",
        "## Basis",
        "",
        f"- Epoch limits set by the logged rule: max_epochs {p['max_epochs']}, patience {p['patience']}; "
        f"e_conv per piloted budget {p['e_conv']}.",
        f"- Seconds per epoch at 654 hosts (set2set, single worker): mean over the 18 benchmarked "
        f"(hidden, batch, blocks) cells {p['s_per_epoch_cells']['mean']:.2f} s (central), slowest cell "
        f"{p['s_per_epoch_cells']['slowest']:.2f} s (upper); the mid-space cell (64, 32, 3) takes "
        f"{p['s_per_epoch_cells']['h64_b32_k3']:.2f} s. Scaled to each budget by the measured epoch time "
        f"(training plus the validation pass, `results/gpu_epoch_scaling.json`): "
        f"{', '.join(f'{k}: x{v:.3f}' for k, v in p['epoch_scale_vs_654_train_epoch'].items())}. "
        f"The cell of the tuned model is unknown until tuning, so the central value uses the grid mean for "
        f"every stage and the upper bound the slowest cell.",
        f"- Central: expected epochs = e_conv(B) + patience (log-linear interpolation of e_conv between the "
        f"piloted budgets); concurrency speedup {p['central_speedup_used']:.2f}x (CUDA MPS, 4 workers). "
        f"Upper: slowest cell, max_epochs epochs, no concurrency gain.",
        f"- Price: L40S Secure Cloud ${p['rate_usd_per_h'] - DISK_USD_PER_H:.2f}/h GPU (RunPod public API) plus "
        f"${DISK_USD_PER_H:.2f}/h disks (observed) = ${p['rate_usd_per_h']:.2f}/h." if p["rate_usd_per_h"] else
        "- Price: not fetched; cost columns are blank.",
        "",
        "## Cost by stage (L40S)",
        "",
        "| Stage | Runs | Central GPU-h | Upper GPU-h | Central USD | Upper USD |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in p["stages"]:
        lines.append(f"| {r['stage']} | {r['runs']} | {r['central_gpu_h']:.1f} | {r['upper_gpu_h']:.1f} | "
                     f"{_usd(r['central_usd'])} | {_usd(r['upper_usd'])} |")
    lines.append(f"| **total** | {sum(r['runs'] for r in p['stages'])} | **{p['total_central_gpu_h']:.1f}** | "
                 f"**{p['total_upper_gpu_h']:.1f}** | **{_usd(p['total_central_usd'])}** | "
                 f"**{_usd(p['total_upper_usd'])}** |")
    tu = p["tune_plus_sweep_central_gpu_h"], p["tune_plus_sweep_upper_gpu_h"]
    rate = p["rate_usd_per_h"]
    lines += ["", f"Tuning plus sweep alone: {tu[0]:.1f} GPU-h central, {tu[1]:.1f} GPU-h upper"
              + (f" (${tu[0] * rate:,.0f} and ${tu[1] * rate:,.0f})." if rate else "."),
              "", "Stage notes: " + "; ".join(f"{r['stage']}: {r['note']}" for r in p["stages"]) + ".",
              f"Excluded (not measured or not GPU work): {', '.join(p['excluded'])}.",
              "", "## Concurrency and saturation (current card only)", "",
              "| Workers | Aggregate epochs/h, no MPS | Speedup vs 1 | Aggregate epochs/h, CUDA MPS | Speedup vs 1 |",
              "|---:|---:|---:|---:|---:|"]
    for n in sorted(sp):
        lines.append(f"| {n} | {p['epochs_per_h_no_mps'][str(n)]:.0f} | {p['speedup_no_mps'][n]:.2f} | "
                     f"{p['epochs_per_h_mps'][str(n)]:.0f} | {sp[n]:.2f} |")
    lines += ["", p["saturation_note"], "", "## Prices fetched (USD per GPU-hour, on demand)", "",
              "| Card | Secure | Community | Memory (GB) |", "|---|---:|---:|---:|"]
    for k, v in p["prices"].items():
        lines.append(f"| {k} | {_p(v['secure'])} | {_p(v['community'])} | {v.get('memory_gb', 'blank')} |")
    lines += ["", f"Source: {p['price_source']} (`gpuTypes`), fetched when the table was generated.",
              "Throughput was measured only on the L40S. For another card the cost per run falls only if its "
              "speedup over the L40S exceeds the ratio of its hourly price to the L40S price; that break-even "
              "ratio is the last column below (price ratios use Secure Cloud).", "",
              "| Card | Break-even speedup vs L40S (Secure) |", "|---|---:|"]
    base = p["prices"]["L40S (current)"]["secure"]
    for k, v in p["prices"].items():
        r = "blank" if (v["secure"] is None or base is None) else f"{(v['secure'] + DISK_USD_PER_H) / (base + DISK_USD_PER_H):.2f}"
        lines.append(f"| {k} | {r} |")
    if p["price_fetch_notes"]:
        lines += ["", "Price gaps logged: " + "; ".join(p["price_fetch_notes"]) + "."]
    return "\n".join(lines) + "\n"


def sites_budget(b) -> int:
    """Budget in hosts used for the e_conv interpolation (Kiyohara: its training-host count)."""
    if b == "kiyohara":
        from dftgnn.split import load_split

        return len(load_split("kiyohara")["train"])
    return b


if __name__ == "__main__":
    main()

"""S10b step 3: epoch-cap audit of the sweep and Kiyohara-split runs, and the post-hoc rerun specification.

Reads the result JSONs of the 540 sweep runs (S, D-state, P1) and the 9 Kiyohara-split runs (S from
results/c0_official/). A run is listed if it stopped at the cap (epochs run = max_epochs) or if its best
epoch, counted from 1, is >= 195. For each listed run the 600-epoch twin is specified (same hyperparameters,
split, budget and seed; max_epochs 600, patience 30; results under results/capped_rerun_v1/). Nothing is
enqueued or executed. The twin run ids are provisional: the run id hashes the code SHA, so it is recomputed
when the job is built at execution time.

Cost (docs/cost_table.md scaling, L40S): seconds per epoch = 2.44 s (central, grid mean at 654 hosts) or
4.56 s (slowest cell) times the budget factor; central divides by the 1.23x MPS concurrency gain. Epochs:
lower = max(200, best epoch + 30) (the twin repeats the stored trajectory up to the old best and stops 30
epochs later if nothing improves), upper = 600. A second estimate uses each run's own measured wall time
per epoch (4 workers sharing the card under MPS, so GPU-hours = wall hours / 4).

    python scripts/analysis/capped_run_audit.py            # print
    python scripts/analysis/capped_run_audit.py --write    # also spec file + write_result
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from dftgnn.config import load_config

ROOT = Path(__file__).resolve().parents[2]
SPEC_OUT = ROOT / "scripts" / "queue" / "capped_rerun_v1.json"
BEST_EPOCH_MIN = 195          # counted from 1
NEW_CAP, NEW_PATIENCE = 600, 30
SUBDIR = "capped_rerun_v1"
S_PER_EPOCH = {"central": 2.44, "upper": 4.56}          # docs/cost_table.md, 654 hosts
SCALE = {25: 0.049, 50: 0.079, 100: 0.213, 200: 0.361, 400: 0.665, 654: 1.073, 571: 1.130}   # 571 = Kiyohara
MPS_GAIN = 1.23


def records() -> list[dict]:
    out = []
    for sub in ("", "c0_official"):
        for f in sorted((ROOT / "results" / sub).glob("*.json")):
            try:
                p = json.loads(f.read_text()).get("payload")
            except ValueError:
                continue
            if not isinstance(p, dict) or "spec" not in p or p.get("smoke"):
                continue
            s = p["spec"]
            if s.get("results_subdir") != (sub or None) or s.get("tags", {}).get("pilot"):
                continue
            if s["model"] not in ("S", "D-state", "P1"):
                continue
            kind = "kiyohara" if s["split"] == "kiyohara" else "sweep"
            if kind == "sweep" and not s["split"].startswith("outer_r"):
                continue
            out.append({**p, "_kind": kind})
    n = Counter(p["_kind"] for p in out)
    assert n == {"sweep": 540, "kiyohara": 9}, n
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    cfg = load_config()
    from dftgnn.graphs import store as G
    from dftgnn.train import RunSpec, code_sha, run_id

    code, gsha = code_sha(), G.manifest_sha(G.MANIFEST)
    runs = records()
    capsens = {}
    for f in (ROOT / "results" / "capsens").glob("*.json"):
        c = json.loads(f.read_text())["payload"]
        capsens[(c["spec"]["model"], c["spec"]["r"], c["spec"]["budget"], c["spec"]["seed"])] = c["run_id"]
    listed, counts = [], Counter()
    for p in runs:
        s = p["spec"]
        capped = p["epochs_run"] >= p["max_epochs"]
        best1 = p["best_epoch"] + 1
        late = best1 >= BEST_EPOCH_MIN
        key = f"{p['_kind']}|{s['model']}|{s['budget']}"
        counts[(key, "total")] += 1
        if not (capped or late):
            continue
        counts[(key, "listed")] += 1
        counts[(key, "capped")] += int(capped)
        counts[(key, "best_ge_195")] += int(late)
        twin = {**s, "max_epochs": NEW_CAP, "patience": NEW_PATIENCE, "results_subdir": SUBDIR,
                "tags": {**s.get("tags", {}), "posthoc": SUBDIR}}
        twin.pop("_kind", None)
        rid = run_id(RunSpec.from_dict(twin), code, gsha)
        b = s["budget"]
        lo_ep = max(p["max_epochs"], best1 + NEW_PATIENCE)
        wall_per_epoch = p["wall_time_s"] / p["epochs_run"]
        listed.append({
            "original_run_id": p["run_id"], "kind": p["_kind"], "model": s["model"], "r": s["r"], "budget": b,
            "seed": s["seed"], "epochs_run": p["epochs_run"], "best_epoch_from_1": best1, "stopped_by_cap": capped,
            "best_epoch_ge_195": late, "twin_run_id_provisional": rid, "twin_spec": twin,
            "existing_600_epoch_twin": capsens.get((s["model"], s["r"], b, s["seed"])) if p["_kind"] == "sweep" else None,
            "est_gpu_h": {
                "central_lower_epochs": lo_ep * S_PER_EPOCH["central"] * SCALE[b] / MPS_GAIN / 3600,
                "central_600_epochs": NEW_CAP * S_PER_EPOCH["central"] * SCALE[b] / MPS_GAIN / 3600,
                "upper_600_epochs_slowest_cell": NEW_CAP * S_PER_EPOCH["upper"] * SCALE[b] / 3600,
                "measured_lower_epochs": lo_ep * wall_per_epoch / 4 / 3600,
                "measured_600_epochs": NEW_CAP * wall_per_epoch / 4 / 3600},
        })
    table = {}
    for (key, what), v in sorted(counts.items()):
        table.setdefault(key, {"total": 0, "listed": 0, "capped": 0, "best_ge_195": 0})[what] = v
    cost = {k: sum(j["est_gpu_h"][k] for j in listed) for k in listed[0]["est_gpu_h"]} if listed else {}
    have = [j for j in listed if j["existing_600_epoch_twin"]]
    print(f"{len(listed)} jobs; {len(have)} already have a pre-registered 600-epoch twin in results/capsens/")
    for k, v in table.items():
        if v["listed"]:
            print(f"  {k:24s} listed {v['listed']:2d}/{v['total']:2d}  capped {v['capped']:2d}  best>=195 {v['best_ge_195']:2d}")
    print("estimated GPU-h:", {k: round(v, 2) for k, v in cost.items()})
    if not a.write:
        return
    spec = {"name": SUBDIR, "status": "specification only; not enqueued, not executed",
            "posthoc": True, "label": "post-hoc sensitivity, not pre-registered (docs/deviations.md 2026-10-08)",
            "selection": f"epochs_run == max_epochs or best epoch (from 1) >= {BEST_EPOCH_MIN}",
            "max_epochs": NEW_CAP, "patience": NEW_PATIENCE, "results_subdir": SUBDIR,
            "run_id_note": f"twin run ids computed with code {code} and graphs {gsha}; recompute at execution",
            "n_jobs": len(listed),
            "n_with_existing_600_epoch_twin": len(have),
            "existing_twin_note": "jobs with existing_600_epoch_twin set duplicate a pre-registered capsens run "
                                  "(same spec except results_subdir and tags); the author decides whether to skip them",
            "jobs": listed}
    SPEC_OUT.write_text(json.dumps(spec, indent=1) + "\n")
    print(SPEC_OUT)
    from dftgnn.io.results import write_result

    print(write_result("capped_run_audit", {
        "selection": spec["selection"], "counts": table, "n_jobs": len(listed),
        "n_with_existing_600_epoch_twin": len(have), "est_gpu_h_total": cost,
        "cost_basis": {"s_per_epoch_654": S_PER_EPOCH, "budget_scale": SCALE, "mps_gain": MPS_GAIN,
                       "source": "docs/cost_table.md; measured = each run's wall time per epoch / 4 workers"},
        "spec_file": str(SPEC_OUT.relative_to(ROOT)),
        "jobs": [{k: v for k, v in j.items() if k != "twin_spec"} for j in listed]}, config=cfg))


if __name__ == "__main__":
    main()

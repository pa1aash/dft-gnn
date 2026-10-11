"""Split a shared job queue into one queue per GPU pod (runs on the loader pod with plain python3).

    python3 partition_queue.py <jobs dir> <out dir> <n queues>

Why: VRAM admission (dftgnn.jobqueue) sums the estimates of every job in ``running/`` as if they shared one GPU, so
pods sharing one queue throttle each other. With one queue per pod, each pod's admission sees only its own jobs.
Nothing about a job changes (same JSON, same run id), so results are identical.

Jobs are grouped so that a P evaluation and the P1 and D runs it depends on share a queue: v2_sweep, p1_v2 and
p_v2 by (split, budget, seed); loco_v2 and v2_kiyohara by (split, seed). Groups are assigned largest first to the
least-loaded queue by a cost proxy (training hosts; P evaluations cost 1). Every queue gets a copy of ``done/`` so
dependencies on finished runs resolve. Jobs found in ``running/`` must have been moved back to ``pending/`` first.
"""
import json
import shutil
import sys
from pathlib import Path

src, out, n = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])
if any((src / "running").glob("*.json")):
    sys.exit("running/ is not empty: stop the workers and return running jobs to pending/ first")
groups = {}
for f in sorted((src / "pending").glob("*.json")):
    j = json.loads(f.read_text())
    s = j["spec"]
    key = (s["split"], s["seed"]) if j["stage"] in ("loco_v2", "v2_kiyohara") else (s["split"], s["budget"], s["seed"])
    groups.setdefault(key, []).append((f, j))


def cost(j):
    return 1 if j["spec"]["model"] == "P" else j["spec"]["budget"]


order = sorted(groups.values(), key=lambda g: -sum(cost(j) for _, j in g))
load = [0] * n
assign = {}
for g in order:
    k = min(range(n), key=lambda i: load[i])
    load[k] += sum(cost(j) for _, j in g)
    for f, _ in g:
        assign[f] = k
for k in range(n):
    for s_ in ("pending", "running", "done", "failed"):
        (out / f"q{k}" / s_).mkdir(parents=True, exist_ok=True)
    for d in (src / "done").glob("*.json"):
        shutil.copy2(d, out / f"q{k}" / "done" / d.name)
moved = 0
for f, k in assign.items():
    try:
        f.rename(out / f"q{k}" / "pending" / f.name)
        moved += 1
    except FileNotFoundError:
        pass                                    # claimed by a worker meanwhile (should not happen when stopped)
print(f"moved {moved} jobs into {n} queues; load per queue: {load}")

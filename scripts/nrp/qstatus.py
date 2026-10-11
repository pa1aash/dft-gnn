"""One-call status of per-pod queues (plain python3, file counts only; parses failed jobs only).

    python3 qstatus.py <queue root>
First line: ``pending P running R done D failed F`` (done = distinct run ids across queues). Then one line per failed
job: ``queue|run_id|claimed_by|kind|last error line`` (kind as in failed_info.py).
"""
import glob
import json
import os
import sys

TRANSIENT = ("cudaError", "CUDA error", "illegal memory access", "misaligned address", "out of memory", "CUBLAS",
             "cuDNN error", "NCCL", "Input/output error", "Stale file handle", "Connection reset", "unspecified launch")
qs = sorted(glob.glob(os.path.join(sys.argv[1], "q*")))
n = {"pending": 0, "running": 0, "failed": 0}
done = set()
fails = []
for q in qs:
    for s in ("pending", "running", "failed"):
        n[s] += sum(1 for x in os.listdir(os.path.join(q, s)) if x.endswith(".json") and not x.startswith("."))
    done.update(x for x in os.listdir(os.path.join(q, "done")) if x.endswith(".json"))
    for f in glob.glob(os.path.join(q, "failed", "*.json")):
        j = json.load(open(f))
        tb = j.get("traceback", "")
        lines = [ln for ln in tb.splitlines() if ln.strip()]
        kind = "transient" if any(t in tb for t in TRANSIENT) else "bug"
        fails.append(f"{q}|{j['run_id']}|{j.get('_claimed_by', '')}|{kind}|{lines[-1][:200] if lines else ''}")
print(f"pending {n['pending']} running {n['running']} done {len(done)} failed {n['failed']}")
print("\n".join(fails))

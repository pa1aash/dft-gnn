"""On the loader pod: one line per failed queue job, ``run_id|claimed_by|kind|last error line``.

kind is ``transient`` for CUDA faults, out-of-memory and I/O drops (requeue is safe), else ``bug``.
    python3 failed_info.py /workspace/dft-gnn-v2/jobs
"""
import glob
import json
import sys

TRANSIENT = ("cudaError", "CUDA error", "illegal memory access", "misaligned address", "out of memory", "CUBLAS",
             "cuDNN error", "NCCL", "Input/output error", "Stale file handle", "Connection reset", "unspecified launch")
for f in sorted(glob.glob(sys.argv[1] + "/failed/*.json")):
    j = json.load(open(f))
    tb = j.get("traceback", "")
    lines = [ln for ln in tb.splitlines() if ln.strip()]
    kind = "transient" if any(t in tb for t in TRANSIENT) else "bug"
    print(f"{j['run_id']}|{j.get('_claimed_by', '')}|{kind}|{lines[-1][:200] if lines else ''}")

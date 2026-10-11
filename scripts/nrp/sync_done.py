"""Copy every finished-job record into every per-pod queue's done/ (plain python3 on the loader pod).

    python3 sync_done.py

A job is claimable only when all its ``after`` ids are in its own queue's done/. Records are completion markers only,
so copying them lets a job depend on a run that finished in another queue (the Kiyohara P evaluations were
partitioned apart from their D runs).
"""
import glob, os, shutil
root = "/workspace/dft-gnn-v2/jobq"
qs = sorted(glob.glob(root + "/q*"))
alld = {}
for q in qs:
    for f in glob.glob(q + "/done/*.json"): alld.setdefault(os.path.basename(f), f)
n = 0
for q in qs:
    have = set(os.listdir(q + "/done"))
    for name, src in alld.items():
        if name not in have:
            shutil.copy2(src, os.path.join(q, "done", name)); n += 1
print("copied", n, "done records;", len(alld), "distinct")

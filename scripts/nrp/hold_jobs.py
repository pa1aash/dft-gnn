"""Hold or release staged jobs in per-pod queues (plain python3 on the loader pod).

    python3 hold_jobs.py hold       move pending p1_v2 / p_v2 jobs to q*/hold/ in queues that still have v2 runs
    python3 hold_jobs.py release    move every held job back to its queue's pending/
    python3 hold_jobs.py v2left     print the number of v2_sweep / v2_kiyohara / loco_v2 jobs still pending
    python3 hold_jobs.py ready      release the held jobs of every queue that has no v2 job left pending

Why: VRAM admission skips a job that does not fit and admits the next one, so a stream of small P1 jobs (3-5 GB)
keeps a card from ever having the 17 GB an S-v2 a654 run needs. Holding the small jobs lets the large ones be
admitted; they are released once no large job is left pending (a pod exits when its pending/ and running/ are both
empty, so they must be released before that). Jobs are moved, never edited.
"""
import glob
import json
import os
import sys

ROOT = "/workspace/dft-gnn-v2/jobq"
V2 = ("v2_sweep", "v2_kiyohara", "loco_v2")


def stage(f):
    return json.load(open(f))["stage"]


mode = sys.argv[1]
n = 0
for q in sorted(glob.glob(ROOT + "/q*")):
    hold = os.path.join(q, "hold")
    os.makedirs(hold, exist_ok=True)
    pend = glob.glob(q + "/pending/*.json")
    if mode == "hold":
        if not any(stage(f) in V2 for f in pend):
            continue
        for f in pend:
            if stage(f) in ("p1_v2", "p_v2"):
                try:
                    os.rename(f, os.path.join(hold, os.path.basename(f)))
                    n += 1
                except FileNotFoundError:
                    pass
    elif mode == "release":
        for f in glob.glob(hold + "/*.json"):
            os.rename(f, os.path.join(q, "pending", os.path.basename(f)))
            n += 1
    elif mode == "ready":
        if not any(stage(f) in V2 for f in pend):
            for f in glob.glob(hold + "/*.json"):
                os.rename(f, os.path.join(q, "pending", os.path.basename(f)))
                n += 1
    elif mode == "v2left":
        n += sum(stage(f) in V2 for f in pend)
print(n if mode == "v2left" else f"{mode} {n}")

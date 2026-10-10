# N1 submission template (NRP, namespace cms-ml)

One Kubernetes Job per GPU class (and per node, where two nodes of a class are wanted), each holding one GPU and
running one training process at a time (no MPS). `scripts/nrp/n1_launch.sh <N1_BASE> <N1_SHA> <committer email>`
creates all of them at once; each runs `scripts/nrp/n1_pod.sh` (copied to `/workspace/n1/n1_pod.sh` on the project
volume `dftgnn-vol`, mounted at `/workspace`).

## What each pod does

1. Clones main at `N1_BASE` onto the pod's local disk (cloning onto the CephFS volume broke off mid-transfer in N0)
   and applies the N1 commit from `/workspace/n1/n1.patch` (`git format-patch` of the commit, made with author date
   equal to committer date) with `git am --committer-date-is-author-date` and the same committer, which reproduces the
   commit exactly. It stops unless `HEAD` equals `N1_SHA`, so every record's `code_sha` is the N1 commit.
2. Installs the N0 environment lock (`/workspace/n0/lock-nrp.txt`, committed as `env/lock-nrp-<gpu>.txt` on
   `nrp/n0-checkout`) into a venv on local disk; importing torch from the CephFS volume took over 20 minutes in
   earlier sessions.
3. Links `data/processed/graphs_v1` to the verified store on the volume and `results/nrp/n1` to
   `/workspace/n1/results/nrp/n1`, so records survive the pod and a rerun skips finished runs (idempotent by run id).
4. Runs `scripts/nrp/run_n1.sh [pass-label]`; records land under
   `results/nrp/n1/<gpu-class-slug>/<node hostname>[/<pass-label>]/`. Logs go to `/workspace/n1/logs/<job>.log`.

## Pinning a GPU class and a node

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - {key: nvidia.com/gpu.product, operator: In, values: [NVIDIA-A10]}     # one class per Job
            - {key: kubernetes.io/hostname, operator: NotIn, values: [hcc-nrp-shor-c6017.unl.edu]}
```

Product label values: `NVIDIA-A10`, `NVIDIA-GeForce-RTX-4090`, `NVIDIA-GeForce-RTX-3090`, `NVIDIA-L4`,
`NVIDIA-RTX-A4000`. The second A10 Job uses `kubernetes.io/hostname NotIn [<faulty node>, <node a>]`; the same-node
repeat uses `In [<node a>]` with pass label `pass2` and runs on another GPU of that node at the same time.

## Resources

`cpu: 2, memory: 16Gi, nvidia.com/gpu: 1, ephemeral-storage: 20Gi` (requests = limits; one training process uses about one core, and 2 CPUs fit nodes whose GPUs are free but whose CPUs are mostly taken), a 4 GiB in-memory
`/dev/shm`, `backoffLimit: 0`, `ttlSecondsAfterFinished: 172800`, image `python:3.11-bookworm`, `NODE_NAME` from the
downward API (`spec.nodeName`), recorded in every result next to the pod hostname.

## Policy notes (NRP)

Jobs have no runtime cap. GPU utilisation should stay above 40% of the requested GPUs; one training process per GPU
keeps it busy except during the environment install. The namespace pod quota (200, shared with other groups) bounds
how many Jobs can run at once.

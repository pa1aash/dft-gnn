# GPU pod runbook

The exact command sequence for a training stage on a RunPod GPU pod. The pod never holds git
credentials: it clones the public repository over HTTPS at a fixed commit, and results come back as
verified tarballs that are committed from the Mac. Steps marked **[YOU]** need Palaash.

## 0. On the Mac, before the pod exists

```bash
cd ~/Desktop/dft-gnn
git status --porcelain --untracked-files=no      # must be empty
git push origin main
COMMIT=$(git rev-parse HEAD)
mamba run -n dftgnn python scripts/check_prereg.py
```

The graph shards in `data/processed/graphs_v1/` must match `data/graphs_v1_manifest.sha256`;
`push_data.sh` checks this before it copies anything.

## 1. Create the pod

1. **[YOU]** Create the pod on RunPod (GPU class from the latest handoff's recommendation; PyTorch
   template; SSH public key `~/.ssh/id_ed25519.pub` added; expose TCP port 22). Treat all pod storage as
   ephemeral unless `mount | grep workspace` shows a separate volume you created: stopping or
   terminating the pod wipes the container disk. Always connect over the exposed-TCP route
   (`ssh root@<ip> -p <port>`); the `ssh.runpod.io` proxy has no rsync/scp support.
2. **[YOU]** Approve the cost shown by RunPod (hourly rate times the stage's ETA; the cost gate of
   ANALYSIS_PLAN §14 applies before S09).
3. **[YOU]** Paste the pod's SSH host and port, then set them on the Mac:

```bash
export POD_HOST=<ip> POD_PORT=<port> POD_KEY=~/.ssh/id_ed25519   # read by push_data.sh and pull_results.sh
HOST=$POD_HOST; PORT=$POD_PORT; KEY=$POD_KEY
```

The IP and port change if the pod is ever restarted. On a fresh container `setup.sh` creates
`/workspace`, installs rsync/git if missing, reuses a `conda`/`mamba` already on the PATH or an earlier
`/workspace/miniforge3`, and otherwise installs miniforge non-interactively into `/workspace/miniforge3`.
Existing `/workspace/dft-gnn` and the `dftgnn-gpu` env are reused (the env is updated, not rebuilt).

## 2. Bootstrap the pod

```bash
ssh -p $PORT -i $KEY -o StrictHostKeyChecking=accept-new root@$HOST 'mkdir -p /workspace'
scp -P $PORT -i $KEY scripts/pod/setup.sh root@$HOST:/workspace/setup.sh
ssh -p $PORT -i $KEY root@$HOST "bash /workspace/setup.sh install $COMMIT"
```

This clones the repository at `$COMMIT` into `/workspace/dft-gnn`, builds the `dftgnn-gpu` env from
`env/environment-gpu.yml`, writes the resolved lock to `outbox/lock-gpu.txt` and prints `nvidia-smi`.

## 3. Send the data and verify it

```bash
bash scripts/pod/push_data.sh                       # uses POD_HOST / POD_PORT / POD_KEY
ssh -p $PORT -i $KEY root@$HOST "bash /workspace/dft-gnn/scripts/pod/setup.sh verify"
```

The two checks must both print `OK`.

## 4. Enqueue and run

```bash
ssh -p $PORT -i $KEY root@$HOST
export PATH=/workspace/miniforge3/bin:$PATH     # only if setup.sh had to install miniforge
cd /workspace/dft-gnn
mamba run -n dftgnn-gpu python scripts/queue/enqueue.py <stage>        # e.g. smoke, kiyohara --hparams ...
nohup mamba run -n dftgnn-gpu python scripts/queue/worker.py --max-concurrent 8 --device cuda \
    > worker.log 2>&1 &
mamba run -n dftgnn-gpu python scripts/queue/status.py                  # counts, ETA, failures
```

For several GPUs, start one worker per GPU with `CUDA_VISIBLE_DEVICES=<i>`. A worker that dies leaves
its jobs in `jobs/running/`; after 10 minutes without a heartbeat they return to pending, so restarting
the worker resumes the stage. Finished runs are skipped on re-enqueue.

## 5. Bring the results back

On the pod:

```bash
mamba run -n dftgnn-gpu python scripts/queue/outbox.py pack --stage <stage>
```

On the Mac:

```bash
bash scripts/pod/pull_results.sh                    # uses POD_HOST / POD_PORT / POD_KEY
```

This copies `outbox/`, checks each tarball against its `.sha256`, unpacks it into `results/` and the
gitignored `checkpoints/`, and re-verifies every file. On the first run, copy `outbox/lock-gpu.txt` to
`env/lock-gpu.txt`. Then commit the results from a clean tree and push.

## 6. Shut down

1. Confirm on the Mac that `pull_results.sh` reported every tarball as verified and that the results
   are committed.
2. **[YOU]** Terminate the pod on RunPod (stop the volume too if it is not needed for the next stage).

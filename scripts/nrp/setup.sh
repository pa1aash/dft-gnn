#!/usr/bin/env bash
# Runs inside dftgnn-loader (scripts/nrp/loader-pod.yaml) with the project volume at /workspace.
#
#   bash setup.sh install <commit>      checkout <commit> from /workspace/dft-gnn.bundle, build /workspace/venv
#   bash setup.sh store                 move /workspace/graphs_v1 into the checkout and verify its manifest
#   bash setup.sh enqueue <stage>       add a stage's jobs to /workspace/dft-gnn/jobs
#
# The pod holds no git credentials: code arrives as a git bundle made on the Mac, so the run ids (which
# hash the commit SHA) match the ones computed there.
set -euo pipefail
WS=/workspace
REPO=${DFTGNN_REPO:-$WS/dft-gnn}     # a second checkout lets a new commit run beside workers of an older one
PY=$WS/venv/bin/python
git config --global --add safe.directory '*'

case "${1:-}" in
  install)
    COMMIT=${2:?commit}
    if [[ ! -d $REPO/.git ]]; then
      git clone -q "$WS/dft-gnn.bundle" "$REPO"
    else
      git -C "$REPO" fetch -q "$WS/dft-gnn.bundle" '+refs/heads/*:refs/remotes/bundle/*'
    fi
    git -C "$REPO" checkout -q --detach "$COMMIT"
    test "$(git -C "$REPO" rev-parse HEAD)" = "$COMMIT"
    if [[ ! -x $PY ]]; then
      python3.11 -m venv "$WS/venv"
      "$PY" -m pip install -q --upgrade pip
      grep -v '^dftgnn' "$REPO/env/lock-gpu.txt" > "$WS/lock-gpu.txt"
      "$PY" -m pip install -q -r "$WS/lock-gpu.txt"
    fi
    "$PY" -m pip install -q -e "$REPO" --no-deps
    "$PY" -c "import torch, matgl, torch_geometric; print('torch', torch.__version__, 'matgl', matgl.__version__)"
    ;;
  store)
    mkdir -p "$REPO/data/processed"
    if [[ -d $WS/graphs_v1 ]]; then rm -rf "$REPO/data/processed/graphs_v1"; mv "$WS/graphs_v1" "$REPO/data/processed/"
    elif [[ ! -d $REPO/data/processed/graphs_v1 ]]; then cp -r "$WS/dft-gnn/data/processed/graphs_v1" "$REPO/data/processed/"; fi
    cd "$REPO" && "$PY" -c "from dftgnn.graphs import store as S; bad = S.verify_store(); print('store', 'OK' if not bad else bad); raise SystemExit(bool(bad))"
    test -z "$(git -C "$REPO" status --porcelain --untracked-files=no)" && echo "tree clean: OK"
    ;;
  enqueue)
    cd "$REPO" && "$PY" scripts/queue/enqueue.py "${2:?stage}"
    "$PY" scripts/queue/status.py
    ;;
  *)
    echo "usage: setup.sh install <commit> | store | enqueue <stage>" >&2; exit 2 ;;
esac

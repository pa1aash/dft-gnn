#!/usr/bin/env bash
# Pod bootstrap (runs ON the pod; no git credentials needed).
#   bash setup.sh install <commit> [workdir]   clone the public repo at <commit>, build the env, nvidia-smi
#   bash setup.sh verify [workdir]             verify the graph shards against the tracked manifest
set -euo pipefail
REPO_URL="https://github.com/pa1aash/dft-gnn.git"
CMD="${1:?usage: setup.sh install <commit> [workdir] | verify [workdir]}"
ENV_NAME="dftgnn-gpu"
CONDA_DIR="${CONDA_DIR:-/workspace/miniforge}"

conda_bin() {
  if command -v mamba >/dev/null 2>&1; then echo mamba; return; fi
  if command -v conda >/dev/null 2>&1; then echo conda; return; fi
  if [ ! -x "$CONDA_DIR/bin/mamba" ]; then
    curl -fsSL -o /tmp/miniforge.sh \
      "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh"
    bash /tmp/miniforge.sh -b -p "$CONDA_DIR"
  fi
  echo "$CONDA_DIR/bin/mamba"
}

case "$CMD" in
  install)
    COMMIT="${2:?commit SHA required}"
    WORK="${3:-/workspace/dft-gnn}"
    if [ ! -d "$WORK/.git" ]; then git clone "$REPO_URL" "$WORK"; fi
    cd "$WORK"
    git fetch --quiet origin
    git checkout --quiet --detach "$COMMIT"
    echo "repo at $(git rev-parse HEAD)"
    CB="$(conda_bin)"
    if "$CB" env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
      "$CB" env update -y -n "$ENV_NAME" -f env/environment-gpu.yml
    else
      "$CB" env create -y -f env/environment-gpu.yml
    fi
    "$CB" run -n "$ENV_NAME" pip install --no-deps -e .
    mkdir -p outbox
    "$CB" run -n "$ENV_NAME" pip list --format=freeze > outbox/lock-gpu.txt
    echo "resolved lock: outbox/lock-gpu.txt (pulled back with the results; commit it as env/lock-gpu.txt)"
    "$CB" run -n "$ENV_NAME" python -c "import torch, torch_geometric, matgl; print('torch', torch.__version__, 'cuda', torch.version.cuda, 'available', torch.cuda.is_available()); print('pyg', torch_geometric.__version__, 'matgl', matgl.__version__)"
    nvidia-smi
    ;;
  verify)
    WORK="${2:-/workspace/dft-gnn}"
    cd "$WORK"
    CB="$(conda_bin)"
    "$CB" run -n "$ENV_NAME" python -c "
from dftgnn.graphs import store
bad = store.verify_store()
print('graph manifest:', 'OK' if not bad else f'MISMATCH {bad}')
raise SystemExit(1 if bad else 0)"
    (cd splits && sha256sum -c --quiet MANIFEST.sha256) && echo "splits manifest: OK"
    nvidia-smi
    ;;
  *) echo "unknown command $CMD" >&2; exit 2 ;;
esac

#!/usr/bin/env bash
# N1: run the 12 repeatability specs sequentially on this node's GPU (one worker, no MPS), idempotently.
#   bash scripts/nrp/run_n1.sh [pass-label]      (pass-label, e.g. pass2, for the same-node repeat)
# Uses $N1_PYTHON (default: python). Exits non-zero if any run fails after its one retry.
set -uo pipefail
cd "$(dirname "$0")/../.."
"${N1_PYTHON:-python}" scripts/nrp/n1_run.py --out-root results/nrp/n1 ${1:+--pass-label "$1"}

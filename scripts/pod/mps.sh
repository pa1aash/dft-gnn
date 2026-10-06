#!/usr/bin/env bash
# CUDA MPS daemon on the pod (runs ON the pod). Without MPS, processes sharing one GPU are time-sliced and
# 2-8 concurrent workers were 35% slower in aggregate than one (results/gpu_benchmark.json); with MPS the
# aggregate rose to 1.3x one worker (results/gpu_benchmark_mps.json). Start it before the queue workers.
#   bash scripts/pod/mps.sh start | stop | status
set -euo pipefail
case "${1:?usage: mps.sh start|stop|status}" in
  start) pgrep -f nvidia-cuda-mps-control >/dev/null || nvidia-cuda-mps-control -d; sleep 1; pgrep -fa nvidia-cuda-mps-control ;;
  stop) echo quit | nvidia-cuda-mps-control || true ;;
  status) pgrep -fa nvidia-cuda-mps || echo "MPS not running" ;;
  *) echo "unknown command" >&2; exit 2 ;;
esac

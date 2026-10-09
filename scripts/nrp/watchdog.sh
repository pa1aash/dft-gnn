#!/usr/bin/env bash
# Mac-side watchdog for a queue stage on NRP. Exits (so the caller is woken) on DRAINED, BUG, REPEAT or NODE;
# fixes transient faults itself. Watches every queue under QROOT (default <remote>/jobs; with per-pod queues, the
# directory holding q0..qN). Usage: bash scripts/nrp/watchdog.sh <remote checkout> <worker job name> <launch cmd> [QROOT]
set -uo pipefail
cd "$(dirname "$0")/../.."
NS=cms-ml; POD=dftgnn-loader; REMOTE=$1; JOB=$2; LAUNCH=$3; QROOT=${4:-}
STATE=${WATCHDOG_STATE:-/tmp/dftgnn_watchdog}; mkdir -p "$STATE"; touch "$STATE/requeues" "$STATE/nodes"
# exec streams ignore --request-timeout, so every call also has a hard wall-clock limit
k() { perl -e 'alarm shift; exec @ARGV' 120 kubectl --request-timeout=60s -n "$NS" "$@"; }
log() { echo "$(date +%m-%d\ %H:%M) $*"; }
ensure_loader() {
  phase=$(k get pod "$POD" -o jsonpath='{.status.phase}' 2>/dev/null)
  if [ "$phase" != "Running" ]; then
    log "loader is '$phase'; recreating"
    k delete pod "$POD" --wait=true >/dev/null 2>&1
    k apply -f scripts/nrp/loader-pod.yaml >/dev/null && k wait --for=condition=Ready "pod/$POD" --timeout=900s >/dev/null
    k exec "$POD" -- git config --global --add safe.directory '*'
    k cp scripts/nrp/failed_info.py "$POD:/workspace/failed_info.py"; k cp scripts/nrp/qstatus.py "$POD:/workspace/qstatus.py"
  fi
}
ensure_loader; k cp scripts/nrp/failed_info.py "$POD:/workspace/failed_info.py" >/dev/null
k cp scripts/nrp/qstatus.py "$POD:/workspace/qstatus.py" >/dev/null
while true; do
  ensure_loader
  if [ -n "$QROOT" ]; then
    out=$(k exec "$POD" -- python3 /workspace/qstatus.py "$QROOT" 2>/dev/null)
  else
    out=$(k exec "$POD" -- bash -c "cd $REMOTE && /workspace/venv/bin/python scripts/queue/status.py 2>/dev/null | head -1; python3 /workspace/failed_info.py $REMOTE/jobs | sed 's|^|$REMOTE/jobs\||'")
  fi
  s=$(echo "$out" | head -1)
  p=$(echo "$s" | sed -n 's/.*pending \([0-9]*\).*/\1/p'); r=$(echo "$s" | sed -n 's/.*running \([0-9]*\).*/\1/p')
  d=$(echo "$s" | sed -n 's/.*done \([0-9]*\).*/\1/p'); f=$(echo "$s" | sed -n 's/.*failed \([0-9]*\).*/\1/p')
  if [ -z "$p" ] || [ -z "$r" ] || [ -z "$d" ] || [ -z "$f" ]; then log "status incomplete; retrying"; sleep 60; continue; fi
  workers=$(k get pods -l job-name="$JOB" --no-headers 2>/dev/null | grep -cE "Running|Pending|ContainerCreating")
  log "pending $p running $r done $d failed $f | worker pods $workers"
  if [ "$f" != "0" ]; then
    while IFS='|' read -r q rid by kind msg; do
      [ -z "$rid" ] && continue
      if [ "$kind" != "transient" ]; then log "BUG $rid ($by): $msg"; echo BUG; exit 0; fi
      n=$(grep -c "^$rid$" "$STATE/requeues"); if [ "$n" -ge 3 ]; then log "REPEAT $rid failed $((n+1)) times: $msg"; echo REPEAT; exit 0; fi
      pod=${by%-*-w*}; node=$(k get pod "$pod" -o jsonpath='{.spec.nodeName}' 2>/dev/null)
      log "transient failure $rid on $pod ($node): $msg -> requeue, delete pod"
      echo "$rid" >> "$STATE/requeues"; [ -n "$node" ] && echo "$node" >> "$STATE/nodes"
      k exec "$POD" -- mv "$q/failed/$rid.json" "$q/pending/$rid.json"
      [ -n "$node" ] && k delete pod "$pod" --wait=false >/dev/null 2>&1
      if [ -n "$node" ] && [ "$(grep -c "^$node$" "$STATE/nodes")" -ge 3 ]; then log "NODE $node faulted 3 times"; echo NODE; exit 0; fi
    done < <(echo "$out" | tail -n +2)
  fi
  if [ "${p:-0}" = "0" ] && [ "${r:-0}" = "0" ]; then log "DRAINED"; echo DRAINED; exit 0; fi
  if [ "${p:-0}" != "0" ] && [ "$workers" = "0" ]; then log "pending work but no workers; relaunching"; eval "$LAUNCH"; fi
  sleep 300
done

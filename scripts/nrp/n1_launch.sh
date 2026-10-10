#!/usr/bin/env bash
# Launch the N1 Jobs on NRP (namespace cms-ml), one GPU each, all at once; each runs scripts/nrp/n1_pod.sh:
#   A10 on node a (pass1), A10 on a different node b, A10 pass2 pinned to node a (same-node repeat),
#   and one Job each for RTX 4090, RTX 3090, L4 and RTX A4000.
# The node-relative Jobs are created once the first A10 pod has been scheduled. Excluded nodes: CUDA illegal-address
# errors (hcc-nrp-shor-c6017, 2026-10-08) and CUDA "unknown error" on moving the model to the GPU
# (nautilus-ext-gpu01.fullerton.edu, RTX 3090, 2026-10-10). ONLY="<job> ..." limits the call to those Jobs.
# REPEAT="<job>:<product>:<node> ..." adds same-node repeats (pass label pass2) pinned to the named nodes.
# CHAIN="<job>:<product> ..." adds Jobs that run pass1 then pass2 in one pod on any node of that class, so the repeat is
# on the same node and GPU without waiting for a GPU on a named node to come free. CHAIN_EXCLUDE="<node>, ..." keeps
# them off nodes whose pass1 directory another Job is still writing.
#   [ONLY="..."] [REPEAT="..."] [CHAIN="..."] bash scripts/nrp/n1_launch.sh <N1_BASE> <N1_SHA> <committer email>
set -euo pipefail
NS=cms-ml
FAULTY="hcc-nrp-shor-c6017.unl.edu, nautilus-ext-gpu01.fullerton.edu"
BASE=$1 SHA=$2 EMAIL=$3
k() { kubectl --request-timeout=60s -n "$NS" "$@"; }

job() {   # job <name> <product> <hostname-op> <hostnames> <pass-label>
  local name=$1 product=$2 op=$3 hosts=$4 pass=$5
  local run="bash /workspace/n1/n1_pod.sh $pass"
  [ "$pass" = chain ] && run="bash /workspace/n1/n1_pod.sh && bash /workspace/n1/n1_pod.sh pass2"
  if [ -n "${ONLY:-}" ] && [[ " $ONLY " != *" $name "* ]]; then return; fi
  cat <<YAML | k apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: $name
  labels: {app: dftgnn, role: n1}
spec:
  backoffLimit: 0
  ttlSecondsAfterFinished: 172800
  template:
    metadata:
      labels: {app: dftgnn, role: n1, n1job: $name}
    spec:
      restartPolicy: Never
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
              - matchExpressions:
                  - {key: nvidia.com/gpu.product, operator: In, values: [$product]}
                  - {key: kubernetes.io/hostname, operator: $op, values: [$hosts]}
      containers:
        - name: n1
          image: python:3.11-bookworm
          command: ["bash", "-c", "set -o pipefail; mkdir -p /workspace/n1/logs && { $run; } 2>&1 | tee -a /workspace/n1/logs/$name.log"]
          env:
            - {name: N1_BASE, value: $BASE}
            - {name: N1_SHA, value: $SHA}
            - {name: N1_EMAIL, value: "$EMAIL"}
            - name: NODE_NAME
              valueFrom: {fieldRef: {fieldPath: spec.nodeName}}
          resources:
            requests: {cpu: "2", memory: 8Gi, nvidia.com/gpu: 1, ephemeral-storage: 20Gi}
            limits: {cpu: "2", memory: 8Gi, nvidia.com/gpu: 1, ephemeral-storage: 20Gi}
          volumeMounts:
            - {name: vol, mountPath: /workspace}
            - {name: shm, mountPath: /dev/shm}
      volumes:
        - {name: vol, persistentVolumeClaim: {claimName: dftgnn-vol}}
        - {name: shm, emptyDir: {medium: Memory, sizeLimit: 4Gi}}
YAML
}

job dftgnn-n1-a10-a NVIDIA-A10 NotIn "$FAULTY" ""
job dftgnn-n1-rtx4090 NVIDIA-GeForce-RTX-4090 NotIn "$FAULTY" ""
job dftgnn-n1-rtx3090 NVIDIA-GeForce-RTX-3090 NotIn "$FAULTY" ""
job dftgnn-n1-l4 NVIDIA-L4 NotIn "$FAULTY" ""
job dftgnn-n1-a4000 NVIDIA-RTX-A4000 NotIn "$FAULTY" ""
for c in ${CHAIN:-}; do
  IFS=: read -r cn cp <<< "$c"
  job "$cn" "$cp" NotIn "$FAULTY${CHAIN_EXCLUDE:+, $CHAIN_EXCLUDE}" "chain"
done
for r in ${REPEAT:-}; do
  IFS=: read -r rn rp rh <<< "$r"
  job "$rn" "$rp" In "$rh" "pass2"
done
echo "waiting for the first A10 pod to be scheduled"
until NODE_A=$(k get pods -l n1job=dftgnn-n1-a10-a -o jsonpath='{.items[0].spec.nodeName}' 2>/dev/null) && [ -n "$NODE_A" ]; do
  sleep 15
done
echo "A10 node a: $NODE_A"
job dftgnn-n1-a10-b NVIDIA-A10 NotIn "$FAULTY, $NODE_A" ""
job dftgnn-n1-a10-a-pass2 NVIDIA-A10 In "$NODE_A" "pass2"

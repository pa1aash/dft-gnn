#!/usr/bin/env bash
# N0 checkout on one NRP GPU pod (Job spec: docs/nrp/n0_job.yaml). Clones main at a fixed SHA onto the pod's local
# disk (a clone onto the CephFS volume broke off mid-transfer), builds the locked environment on local disk, points at the verified graph store already on the volume,
# checks the GPU (MEGNet forward/backward), the manifests, the test suite and a 5-epoch S smoke run, then writes
# results/nrp/n0_checkout.json with write_result from a clean tree. Inputs prepared on the workstation:
# /workspace/n0/universe_v1.parquet (built by scripts/build_universe.py) and /workspace/n0/workstation_checks.json
# (tags, hooks, release --verify-only).
set -uo pipefail
W=/workspace/n0
R=/tmp/dft-gnn
SHA=${N0_SHA:?main SHA}
log() { echo "[n0 $(date -u +%H:%M:%S)] $*"; }
git config --global --add safe.directory '*'

log "hardware"
nvidia-smi --query-gpu=name,uuid,driver_version,memory.total --format=csv,noheader > $W/gpu.csv
nvidia-smi | grep -o "CUDA Version: [0-9.]*" > $W/cuda.txt
echo "${NODE_NAME:-unknown}" > $W/node.txt

log "checkout $SHA"
for i in 1 2 3; do
  rm -rf $R && git clone -q https://github.com/pa1aash/dft-gnn.git $R && break
  log "clone attempt $i failed"; sleep 20
done
cd $R && git fetch -q origin && git checkout -q -B nrp/n0-checkout "$SHA" || exit 2
test "$(git rev-parse HEAD)" = "$SHA" || exit 2

log "environment from env/environment-gpu.yml (unpinned packages constrained to env/lock-gpu.txt)"
python3.11 -m venv /tmp/venv && /tmp/venv/bin/python -m pip install -q --upgrade pip || exit 3
grep -v '^dftgnn' env/lock-gpu.txt > /tmp/constraints.txt
PKGS=$(awk '/- pip:/{f=1; next} f && /^ +- /{sub(/#.*/, ""); sub(/^ +- /, ""); gsub(/ /, ""); print}' env/environment-gpu.yml)
echo "$PKGS" > $W/env_packages.txt
/tmp/venv/bin/python -m pip install -q -c /tmp/constraints.txt $PKGS || exit 3
/tmp/venv/bin/python -m pip install -q -e . --no-deps || exit 3
/tmp/venv/bin/python -m pip freeze --exclude-editable > $W/lock-nrp.txt
PY=/tmp/venv/bin/python

log "data: graph store on the volume (symlink), universe parquet"
mkdir -p data/processed
ln -sfn /workspace/dft-gnn/data/processed/graphs_v1 data/processed/graphs_v1
cp $W/universe_v1.parquet data/processed/universe_v1.parquet

log "GPU forward/backward"
$PY - > $W/gpu_check.json <<'PYEOF'
import json, torch, matgl
from pymatgen.core import Lattice, Structure
from torch_geometric.data import Batch
from dftgnn.graphs import host_graph, site_data
from dftgnn.models import HParams, build_model
ok = torch.cuda.is_available()
s = Structure.from_spacegroup("Fm-3m", Lattice.cubic(4.21), ["Mg", "O"], [[0, 0, 0], [0.5, 0.5, 0.5]])
s.make_supercell([2, 2, 2])
g = host_graph(s, 5.0)
vac = [i for i, z in enumerate(g["z"].tolist()) if z == 8][:4]
b = Batch.from_data_list([site_data(g, v, y=1.0) for v in vac]).to("cuda")
torch.manual_seed(0)
net = build_model("S", HParams()).cuda()
out = net(b)
loss = (out - b.y).abs().mean()
loss.backward()
grad = sum(float(p.grad.abs().sum()) for p in net.parameters() if p.grad is not None)
print(json.dumps({"cuda_available": ok, "device": torch.cuda.get_device_name(0), "torch": torch.__version__,
                  "torch_cuda": torch.version.cuda, "matgl": matgl.__version__, "loss": float(loss),
                  "grad_abs_sum": grad, "finite": bool(torch.isfinite(out).all()) and grad > 0}))
PYEOF
cat $W/gpu_check.json

log "manifests"
$PY -c "from dftgnn.graphs import store as S; bad = S.verify_store(); print('PASS' if not bad else 'FAIL ' + str(bad))" > $W/m_graphs.txt
(cd data && sha256sum -c universe_v1_ids.csv.sha256 >/dev/null 2>&1 && echo PASS || echo FAIL) > $W/m_universe.txt
(cd splits && sha256sum -c MANIFEST.sha256 > $W/m_splits_detail.txt 2>&1 && echo PASS || echo FAIL) > $W/m_splits.txt
grep -q "loco_v1.json: OK" $W/m_splits_detail.txt && echo yes > $W/m_loco.txt || echo no > $W/m_loco.txt

log "tests"
$PY -m pytest -q -rs -p no:cacheprovider > $W/pytest.txt 2>&1
echo $? > $W/pytest_rc.txt
tail -3 $W/pytest.txt

log "smoke: S, budget-25 setting (a50 tuned values), 5 epochs, GPU"
$PY - > $W/smoke.json <<'PYEOF'
import json, torch
from dftgnn.train import RunSpec, Store
from dftgnn.train.runner import execute
from dftgnn.train.stages import load_tuned, tuned_hparams
t = load_tuned()
spec = RunSpec(model="S", **tuned_hparams(t, "S", 50), split="outer_r0", r=0, budget=25, seed=0,
               max_epochs=5, patience=5, smoke=True, tags={"nrp": "n0"})
out = execute(spec, Store(), device=torch.device("cuda"), log=lambda *_: None)
pay = json.load(open(out["result"]))["payload"]
print(json.dumps({"status": out["status"], "run_id": out["run_id"], "result": str(out["result"]),
                  "epochs_run": pay["epochs_run"], "smoke": pay["smoke"], "mae": pay["metrics"]["mae"],
                  "device": pay["device"]}))
PYEOF
cat $W/smoke.json

log "write results/nrp/n0_checkout.json"
$PY - <<'PYEOF'
import json, re
from pathlib import Path
from dftgnn.io.results import write_result
W = Path("/workspace/n0")
rd = lambda n: (W / n).read_text().strip()
ws = json.loads(rd("workstation_checks.json"))
gpu = rd("gpu.csv").split(", ")
gc = json.loads(rd("gpu_check.json"))
smoke = json.loads(rd("smoke.json"))
tail = rd("pytest.txt").splitlines()[-1]
counts = {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|skipped|xfailed|xpassed|errors?)", tail)}
skips = [ln for ln in rd("pytest.txt").splitlines() if ln.startswith("SKIPPED")]
manifests = {"graphs_v1_shards": rd("m_graphs.txt"), "universe_v1_ids": rd("m_universe.txt"),
             "splits": rd("m_splits.txt"), "splits_includes_loco_v1": rd("m_loco.txt") == "yes",
             "release_verify_only": ws["release_verify_only"]["status"]}
env_ok = gc["cuda_available"] and gc["finite"]
tests_ok = rd("pytest_rc.txt") == "0" and counts.get("failed", 0) == 0 and counts.get("error", counts.get("errors", 0)) == 0
man_ok = all(v in ("PASS", True) for v in manifests.values())
passed = bool(ws["tags_match_origin"] and all(ws["hooks"][k] for k in ws["hooks"] if k != "note")
              and env_ok and man_ok and tests_ok and smoke["status"] in ("done", "skipped"))
import subprocess
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
payload = {"pass": passed, "main_head_sha": head,
           "gpu_model": gpu[0], "gpu_uuid": gpu[1], "driver": gpu[2], "gpu_memory": gpu[3],
           "cuda": rd("cuda.txt").replace("CUDA Version: ", ""), "node_hostname": rd("node.txt"),
           "torch": gc["torch"], "torch_cuda": gc["torch_cuda"], "matgl": gc["matgl"],
           "gpu_forward_backward": gc, "manifests": manifests, "tests": counts, "test_skips": skips,
           "smoke": smoke, "tags": ws["tags"], "hooks": ws["hooks"],
           "env_packages": rd("env_packages.txt").split(), "lock_file": "env/lock-nrp-<gpu>.txt"}
print(write_result("n0_checkout", payload, results_dir=Path("results/nrp")))
print(json.dumps({k: payload[k] for k in ("pass", "gpu_model", "node_hostname", "manifests", "tests")}))
PYEOF
log "copy results to the volume"
mkdir -p $W/out && cp -r results/nrp $W/out/ && cp -r results/smoke $W/out/ 2>/dev/null
log "done"

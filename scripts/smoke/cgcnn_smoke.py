"""3-epoch CPU smoke of cgcnn-S and cgcnn-D on 20 training hosts (smoke=true; results/smoke/, excluded from
every analysis). Fixed cross-check optimiser settings (lr 1e-3, weight decay 1e-5, batch 32)."""
from __future__ import annotations

import torch

from dftgnn.models.cgcnn import CGCNNParams
from dftgnn.train import RunSpec, Store
from dftgnn.train.runner import execute
from dftgnn.train.stages import SMOKE_EPOCHS, smoke_hosts

torch.set_num_threads(3)
data = Store()
for m in ("cgcnn-S", "cgcnn-D"):
    spec = RunSpec(model=m, hp=CGCNNParams().to_dict(), lr=1e-3, weight_decay=1e-5, batch_size=32, split="outer_r0",
                   r=0, budget=25, seed=0, hosts=smoke_hosts(), max_epochs=SMOKE_EPOCHS, patience=SMOKE_EPOCHS,
                   smoke=True, tags={"smoke": "cgcnn"})
    out = execute(spec, data, device=torch.device("cpu"))
    import json

    pay = json.loads(out["result"].read_text())["payload"]
    print(m, out["status"], out["run_id"], "epochs", pay["epochs_run"], "val",
          [round(h["val_metric"], 3) for h in pay["history"]], "test MAE", round(pay["metrics"]["mae"], 3),
          "wall", round(pay["wall_time_s"], 1), "s")

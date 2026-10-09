"""P evaluation smoke on two real (P1, D) checkpoint pairs (resample 0, seed 0, B = 654 and B = 200).

    nice -n 15 python scripts/smoke/peval_smoke.py

Checks (results/smoke/peval_smoke.json, smoke=true, excluded from every analysis):
* true-descriptor swap-in: the staged model P with the TRUE descriptors in place of P1's predictions (written in
  P1's standardisation and passed through StagedP's affine map) equals D on every test site to 1e-5 eV;
* P runs end to end (P1 predictions -> D) and per-descriptor test R^2 and MAE of P1 are produced.
No staging contrast (D - P, P - S) is computed.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import torch

from dftgnn import infer
from dftgnn.io.results import write_result
from dftgnn.models import Standardiser
from dftgnn.split import load_split
from dftgnn.train import Store, runindex

ROOT = Path(__file__).resolve().parents[2]


class SwapIn(torch.nn.Module):
    """StagedP with P1's output replaced by the true descriptors (given in P1's standardisation)."""

    def __init__(self, staged, true_p1: torch.Tensor):
        super().__init__()
        self.p, self.true_p1 = staged, true_p1

    def forward(self, batch):
        p = self.p
        z = self.true_p1[batch.site_pos.view(-1)]
        z = z if p.identity else z * p.scale + p.shift
        return p.d(batch, desc_host=z[:, : p.n_host], desc_site=z[:, p.n_host:])


def main() -> None:
    torch.set_num_threads(3)
    sites = infer.Sites(Store())
    prim = runindex.primary(runindex.load())
    out = []
    for b in (654, 200):
        p1r, dr = prim[("P1", "outer_r0", b, 0)], prim[("D-state", "outer_r0", b, 0)]
        p, ckd = infer.staged(p1r, dr)
        d, _ = infer.load(dr)
        p1, ck1 = infer.load(p1r)
        test = sorted(load_split("outer_r0")["test"])
        pos = sites.positions(test)
        graphs = sites.dft_graphs(test)
        y_d = infer.predict(d, ckd, sites, graphs, pos)
        y_p = infer.predict(p, ckd, sites, graphs, pos)
        # swap-in: true descriptors in P1's standardisation, through StagedP's map, into D
        true_p1 = Standardiser(ck1["desc_mean"], ck1["desc_sd"])(sites.desc).float()

        y_swap = infer.predict(SwapIn(p, true_p1).eval(), ckd, sites, graphs, pos)
        swap_dev = float(np.abs(y_swap - y_d).max())
        pr = infer.predict(p1, ck1, sites, graphs, pos)
        tr = sites.desc[pos].numpy()
        sst = ((tr - tr.mean(0)) ** 2).sum(0)
        per = {nm: {"mae": float(np.abs(pr[:, j] - tr[:, j]).mean()),
                    "r2": float(1 - ((pr[:, j] - tr[:, j]) ** 2).sum() / sst[j]) if sst[j] > 0 else None}
               for j, nm in enumerate(ck1["desc_names"])}
        row = {"budget": b, "P1_run": p1r["run_id"], "D_run": dr["run_id"], "n_test_sites": len(pos),
               "swap_in_max_abs_dev_eV": swap_dev, "swap_in_equals_D_1e-5": swap_dev < 1e-5,
               "affine_identity": p.identity, "P_predictions_finite": bool(np.isfinite(y_p).all()),
               "P1_per_descriptor_test": per}
        print(b, {k: v for k, v in row.items() if k != "P1_per_descriptor_test"}, flush=True)
        assert swap_dev < 1e-5, swap_dev
        out.append(row)
    write_result("peval_smoke", {"smoke": True, "note": "P evaluation pipeline check on two checkpoint pairs; no "
                                 "staging contrast computed; excluded from every analysis", "pairs": out},
                 results_dir=ROOT / "results" / "smoke")


if __name__ == "__main__":
    main()

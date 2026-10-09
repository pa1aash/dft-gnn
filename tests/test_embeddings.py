"""Embedding extraction on stored S checkpoints (skipped without checkpoints / graph store)."""
import numpy as np
import pandas as pd
import pytest
import torch

from dftgnn import embeddings as E
from dftgnn import infer
from dftgnn.graphs.store import STORE_DIR
from dftgnn.train import REPO_ROOT, runindex

pytestmark = pytest.mark.skipif(not ((REPO_ROOT / "checkpoints").is_dir() and (STORE_DIR / "meta.json").is_file()),
                                reason="checkpoints or graph store not present")
torch.set_num_threads(3)


@pytest.fixture(scope="module")
def sites():
    from dftgnn.train import Store

    return infer.Sites(Store())


@pytest.fixture(scope="module")
def prim():
    return runindex.primary(runindex.load())


@pytest.mark.parametrize("budget", [654, 200, 25])
def test_readout_mlp_reproduces_stored_predictions(sites, prim, budget):
    rec = prim[("S", "outer_r0", budget, 0)]
    net, ck = infer.load(rec)
    stored = pd.read_parquet(REPO_ROOT / rec["predictions"]["path"]).sort_values("site_id").head(25)
    pos = np.array([sites.site_id.index(s) for s in stored.site_id])
    vec = infer.predict(net, ck, sites, sites.dft_graphs(sorted(set(stored.host_id))), pos, what="readout")
    with torch.no_grad():
        z = net.head(torch.from_numpy(vec.astype(np.float32))).squeeze(-1).double()
    pred = (z * ck["target_sd"].cpu() + ck["target_mean"].cpu()).numpy()
    assert np.abs(pred - stored.y_pred.to_numpy()).max() < 1e-3
    assert vec.shape[1] == E.block_bounds(net)[-1]


def test_init_extraction_deterministic_and_differs_from_trained(sites, prim, monkeypatch):
    rec = prim[("S", "outer_r0", 25, 0)]
    a = E.extract("init0", rec, sites, 0, 25)
    b = E.extract("init0", rec, sites, 0, 25)
    c = E.extract("init1", rec, sites, 0, 25)
    t = E.extract("trained", rec, sites, 0, 25)
    assert np.array_equal(a["embeddings"], b["embeddings"]) and list(a["site_ids"]) == list(t["site_ids"])
    assert not np.allclose(a["embeddings"], c["embeddings"]) and not np.allclose(a["embeddings"], t["embeddings"])
    assert set(a["split"]) == {"train", "val", "test"} and a["embeddings"].dtype == np.float32
    groups = E.site_split(0, 25)
    assert len(groups["train"]) + len(groups["val"]) == 25

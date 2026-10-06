"""Model tests (S06 step 3) on synthetic rock-salt MgO graphs; no data files needed."""
from __future__ import annotations

import pytest
import torch
from torch_geometric.data import Batch

from dftgnn.graphs import host_graph, site_data
from dftgnn.models import KINDS, HParams, StagedP, Standardiser, build_model, n_parameters

N_HOST, N_SITE = 12, 10


def _mgo(n=2):
    from pymatgen.core import Lattice, Structure

    s = Structure.from_spacegroup("Fm-3m", Lattice.cubic(4.21), ["Mg", "O"], [[0, 0, 0], [0.5, 0.5, 0.5]])
    s.make_supercell([n, n, n])
    return s


@pytest.fixture(scope="module")
def graph():
    return host_graph(_mgo(), 5.0)


def _oxygens(g):
    return torch.nonzero(g["z"] == 8).flatten().tolist()


def _batch(g, vacs, desc=None):
    torch.manual_seed(0)
    desc = torch.randn(len(vacs), N_HOST + N_SITE) if desc is None else desc
    return Batch.from_data_list([site_data(g, v, y=1.0, desc_host=desc[i, :N_HOST],
                                           desc_site=desc[i, N_HOST:]) for i, v in enumerate(vacs)])


@pytest.mark.parametrize("pooling", ["set2set", "mean"])
@pytest.mark.parametrize("kind", KINDS)
def test_forward_shapes(graph, kind, pooling):
    torch.manual_seed(0)
    net = build_model(kind, HParams(pooling=pooling)).eval()
    b = _batch(graph, _oxygens(graph)[:3])
    out = net(b)
    assert out.shape == ((3, N_HOST + N_SITE) if kind == "P1" else (3,))
    assert net.readout_vector(b).shape == (3, net.readout_dim)
    assert torch.isfinite(out).all()


def _permuted(g, perm):
    inv = torch.empty_like(perm)
    inv[perm] = torch.arange(len(perm))
    return {**g, "z": g["z"][perm], "pos": g["pos"][perm], "edge_index": inv[g["edge_index"]]}, inv


@pytest.mark.parametrize("pooling", ["set2set", "mean"])
def test_s_permutation_invariant(graph, pooling):
    torch.manual_seed(1)
    net = build_model("S", HParams(pooling=pooling)).eval()
    vacs = _oxygens(graph)[:2]
    perm = torch.randperm(graph["z"].shape[0], generator=torch.Generator().manual_seed(3))
    g2, inv = _permuted(graph, perm)
    with torch.no_grad():
        a = net(_batch(graph, vacs))
        b = net(_batch(g2, [int(inv[v]) for v in vacs]))
    assert torch.allclose(a, b, atol=1e-5, rtol=1e-5)


def test_vacancy_flag_matters(graph):
    torch.manual_seed(2)
    net = build_model("S").eval()
    o = _oxygens(graph)
    with torch.no_grad():
        a = net(_batch(graph, [o[0]]))
        mg = int(torch.nonzero(graph["z"] == 12)[0])
        b = net(_batch(graph, [mg]))
    assert not torch.allclose(a, b)


@pytest.mark.parametrize("kind", ["D-state", "D-late"])
def test_descriptor_injection_wired(graph, kind):
    torch.manual_seed(4)
    net = build_model(kind).eval()
    vacs = _oxygens(graph)[:2]
    desc = torch.randn(2, N_HOST + N_SITE)
    with torch.no_grad():
        real = net(_batch(graph, vacs, desc))
        zero = net(_batch(graph, vacs, torch.zeros_like(desc)))
        host_only = net(_batch(graph, vacs, torch.cat([desc[:, :N_HOST], torch.zeros(2, N_SITE)], 1)))
    assert not torch.allclose(real, zero)
    assert not torch.allclose(real, host_only)       # site descriptors reach the output too


def test_s_ignores_descriptors(graph):
    torch.manual_seed(5)
    net = build_model("S").eval()
    vacs = _oxygens(graph)[:2]
    with torch.no_grad():
        a = net(_batch(graph, vacs, torch.randn(2, 22)))
        b = net(_batch(graph, vacs, torch.zeros(2, 22)))
    assert torch.equal(a, b)


class _Oracle(torch.nn.Module):
    """A stand-in P1 that returns the batch's own (true) standardised descriptors."""

    kind = "P1"

    def forward(self, batch):
        return torch.cat([batch.desc_host, batch.desc_site], dim=-1)


@pytest.mark.parametrize("kind", ["D-state", "D-late"])
def test_p_true_descriptor_swap_in_equals_d(graph, kind):
    torch.manual_seed(6)
    d = build_model(kind).eval()
    raw = torch.randn(40, 22, dtype=torch.float64) * 3 + 1
    st = Standardiser.fit(raw)
    p = StagedP(build_model("P1"), d, st, st).eval()
    p.p1 = _Oracle()
    vacs = _oxygens(graph)[:4]
    b = _batch(graph, vacs, st(raw[:4]).float())
    with torch.no_grad():
        assert torch.equal(p(b), d(b))


def test_p_maps_between_scalings(graph):
    torch.manual_seed(7)
    d = build_model("D-late").eval()
    raw = torch.randn(40, 22, dtype=torch.float64) * 2 + 5
    st_p1, st_d = Standardiser.fit(raw[:30]), Standardiser.fit(raw[10:])
    p = StagedP(build_model("P1"), d, st_p1, st_d).eval()
    p.p1 = _Oracle()
    vacs = _oxygens(graph)[:4]
    with torch.no_grad():
        out_p = p(_batch(graph, vacs, st_p1(raw[:4]).float()))
        out_d = d(_batch(graph, vacs, st_d(raw[:4]).float()))
    assert torch.allclose(out_p, out_d, atol=1e-5)


def test_standardiser_round_trip():
    x = torch.randn(50, 5, dtype=torch.float64)
    x[:, 2] = 3.0                                 # constant column: sd replaced by 1
    st = Standardiser.fit(x)
    assert torch.allclose(st.inverse(st(x)), x)
    assert torch.allclose(st(x)[:, 2], torch.zeros(50, dtype=torch.float64))


def test_parameter_counts_default():
    counts = {k: n_parameters(build_model(k)) for k in KINDS}
    print("parameter counts (default HParams):", counts)
    assert counts["D-state"] > counts["S"] and counts["P1"] > counts["S"]
    assert all(1e5 < c < 1e6 for c in counts.values())

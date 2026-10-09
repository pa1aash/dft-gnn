"""Relaxation pipeline with ASE's EMT potential (no MACE download needed)."""
import json

import numpy as np
import pytest

pytest.importorskip("ase")
from ase.calculators.emt import EMT
from pymatgen.core import Lattice, Structure

from dftgnn.mlip import relax, tiling


def _cu(a=3.75):
    return Structure.from_spacegroup("Fm-3m", Lattice.cubic(a), ["Cu"], [[0, 0, 0]]).get_primitive_structure()


def test_relax_structure_converges_and_changes_volume():
    _, info = relax.relax_structure(_cu(), EMT(), fmax=0.01, steps=300)
    assert info["converged"] and info["final_fmax_eV_per_A"] <= 0.01
    assert info["final_volume_A3"] < info["initial_volume_A3"]   # 3.75 A is expanded for EMT Cu (~3.59 A)


def test_relax_host_tiles_and_is_idempotent(tmp_path):
    uc = _cu()
    M = np.diag([2, 2, 2])
    sc = uc.copy()
    sc.make_supercell(M)
    row = tiling.map_host(uc, sc)
    row = {**row, "M": json.dumps(row["M"]), "perm": json.dumps(row["perm"])}
    rec = relax.relax_host("mp-test", uc, row, EMT(), model_sha256="x", out_dir=tmp_path)
    assert rec["tiled"] and not rec["skipped"] and relax.record_ok("mp-test", tmp_path)
    big = Structure.from_dict(json.loads((tmp_path / "mp-test_sc.json").read_text()))
    small = Structure.from_dict(json.loads((tmp_path / "mp-test_uc.json").read_text()))
    assert len(big) == 8 and abs(big.volume - 8 * small.volume) < 1e-8
    again = relax.relax_host("mp-test", uc, row, EMT(), model_sha256="x", out_dir=tmp_path)
    assert again["skipped"]
    (tmp_path / "mp-test_uc.json").write_text("{}")
    assert not relax.record_ok("mp-test", tmp_path)


def test_excluded_host_gets_no_supercell(tmp_path):
    rec = relax.relax_host("mp-x", _cu(), {"status": "failed"}, EMT(), model_sha256="x", out_dir=tmp_path)
    assert not rec["tiled"] and rec["excluded_from_C3b"] and "supercell" not in rec["files"]

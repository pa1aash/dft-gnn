"""Synthetic checks with known answers for the A6 freeze table (key resolution, repeats, notes, claims, figures)."""
import json

import pytest

from analysis import freeze_table as ft


def _record(root, rel, payload, name=None):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    stem = path.stem
    path.write_text(json.dumps({"name": name or stem, "git_sha": "0" * 40, "payload": payload}))
    return rel


@pytest.fixture
def root(tmp_path):
    _record(tmp_path, "results/a.json", {"x": {"654": {"A": -0.0116, "ci": [-0.035, 0.014]}},
                                         "groups": [{"variable": "pooled", "group": "all", "v": 0.184},
                                                    {"variable": "cation", "group": "Ti", "v": 0.2}],
                                         "per_class": [{"class": "a10", "model": "S", "B": 654, "d": -0.013},
                                                       {"class": "l4", "model": "S", "B": 654, "d": 0.0004},
                                                       {"class": "l4", "model": "S", "B": 200, "d": 0.04}],
                                         "outcome": "C4 moves to the SI"})
    _record(tmp_path, "results/b.json", {"same": -0.0116, "near": -0.0116 + 1e-13, "far": -0.0110})
    return tmp_path


def test_resolve_dict_index_and_selector(root):
    recs = ft.Records(root)
    assert recs.get("results/a.json", "payload.x.654.A") == -0.0116
    assert recs.get("results/a.json", "payload.x.654.ci[1]") == 0.014
    assert recs.get("results/a.json", "payload.groups[variable=pooled].v") == 0.184
    with pytest.raises(KeyError):
        recs.get("results/a.json", "payload.groups[variable=none].v")
    with pytest.raises(KeyError):
        recs.get("results/a.json", "payload.x.400")


def test_unnamed_record_is_refused(tmp_path):
    _record(tmp_path, "results/c.json", {"v": 1}, name="other")
    with pytest.raises(ValueError):
        ft.Records(tmp_path).load("results/c.json")


def test_repeats_identical_within_tolerance_and_differences_fail(root):
    recs = ft.Records(root)
    groups = [{"quantity": "same", "refs": [("results/a.json", "payload.x.654.A"), ("results/b.json", "payload.same")]},
              {"quantity": "rounding", "refs": [("results/a.json", "payload.x.654.A"),
                                                ("results/b.json", "payload.near")]},
              {"quantity": "different", "refs": [("results/a.json", "payload.x.654.A"),
                                                 ("results/b.json", "payload.far")]},
              {"quantity": "string", "refs": [("results/a.json", "payload.outcome"),
                                              ("results/a.json", "payload.outcome")]}]
    out = ft.check_repeats(groups, recs)
    assert [o["pass"] for o in out] == [True, True, False, True]
    assert out[2]["max_abs_diff"] == pytest.approx(0.0006)
    assert out[0]["n_records"] == 2


def test_estimator_differences_are_listed_with_their_size(root):
    recs = ft.Records(root)
    out = ft.check_estimators([{"quantity": "q", "ref": ("results/a.json", "payload.x.654.A"),
                                "other": ("results/b.json", "payload.far"), "reason": "r"}], recs)
    assert out[0]["difference"] == pytest.approx(-0.0006) and out[0]["pass"]


def test_notes_match_rounded_value_including_unicode_minus(root):
    (root / "docs").mkdir()
    (root / "docs" / "n1.md").write_text("A at 654 is −0.012 eV [-0.035, +0.014].")
    (root / "docs" / "n2.md").write_text("A at 654 is -0.0120 eV and 10.012.")
    checks = (("results/a.json", "payload.x.654.A", "{:+.3f}", ("docs/n1.md", "docs/n2.md")),)
    out = ft.check_notes(ft.Records(root), root, checks)
    assert [o["pass"] for o in out] == [True, False]


def test_evaluate_rows_value_interval_upper_and_range(root):
    recs = ft.Records(root)
    rows = [ft.row("r1", "C1", "A", ft.V1, "REGISTERED", ("results/a.json", "payload.x.654.A"),
                   ft.ci_pair("results/a.json", "payload.x.654"), ("results/b.json", "payload.same")),
            ft.row("r2", "PR1", "range", ft.NONE, "EXTENSION",
                   ("range", "results/a.json", "payload.per_class[model=S,B=654].d"))]
    out = ft.evaluate_rows(rows, recs)
    assert out[0]["value"] == -0.0116 and out[0]["interval"] == [-0.035, 0.014]
    assert out[0]["upper_one_sided_95"] == -0.0116
    assert out[1]["interval"] == [-0.013, 0.0004] and out[1]["n_items"] == 2 and out[1]["value"] is None


def test_labels_are_checked():
    with pytest.raises(AssertionError):
        ft.row("r", "C1", "q", ft.V1, "PRE-REG", ("results/a.json", "payload.x"))


def test_claims_status_rules(root):
    (root / "docs").mkdir()
    (root / "docs" / "claims.yaml").write_text("""claims:
  # registered result exists
  - id: OK1
    status: measured
    result_ref: results/a.json
  - id: SI
    status: moved_to_si
    result_ref: results/a.json
  - id: NOREF
    status: planned
  # status stays planned (old note)
  - id: STALE
    status: measured
    result_ref: results/b.json
  # status stays planned (old note)
  # [Superseded by A3: the result now exists.]
  - id: FIXED
    status: measured
    result_ref: results/b.json
  - id: PLANNEDREC
    status: planned
    result_ref: results/b.json
  - id: MISSING
    status: measured
    result_ref: results/none.json
""")
    out = {o["id"]: o for o in ft.check_claims(ft.Records(root), root)}
    assert out["OK1"]["pass"] and out["SI"]["pass"] and out["FIXED"]["pass"]
    assert not out["NOREF"]["pass"] and "no result_ref" in out["NOREF"]["problems"]
    assert not out["STALE"]["pass"]
    assert not out["PLANNEDREC"]["pass"]
    assert not out["MISSING"]["pass"] and not out["MISSING"]["result_ref_exists"]


def test_moved_to_si_needs_si_outcome(root):
    (root / "docs").mkdir()
    (root / "docs" / "claims.yaml").write_text("claims:\n  - id: X\n    status: moved_to_si\n"
                                               "    result_ref: results/b.json\n")
    assert not ft.check_claims(ft.Records(root), root)[0]["pass"]


class _QA:
    def __init__(self, failed):
        self.failed = failed

    def check(self, pdf):
        names = ("vector", "fonts", "one_family", "width", "no_text_in_axes")
        checks = {n: {"ok": n not in self.failed.get(pdf.name, ())} for n in names}
        checks["width"].update(width_mm=138.6, height_mm=80.0)
        return {"pdf": str(pdf), "ok": all(c["ok"] for c in checks.values()), "checks": checks}


def test_figures_caption_records_and_qa(root):
    for sub in ("main", "si"):
        (root / "figures" / sub).mkdir(parents=True)
    main = root / "figures" / "main"
    (main / "fig_ok.pdf").write_bytes(b"")
    (main / "fig_ok.caption.md").write_text("Values under `results/a.json` key `payload.x`.")
    (main / "fig_missing.pdf").write_bytes(b"")
    (main / "fig_missing.caption.md").write_text("Values under `results/nothere.json`.")
    (main / "fig_norecord.pdf").write_bytes(b"")
    (main / "fig_norecord.caption.md").write_text("No record named.")
    (main / "fig_qa.pdf").write_bytes(b"")
    (main / "fig_qa.caption.md").write_text("`results/b.json`")
    (main / "fig1_overview.pdf").write_bytes(b"")
    (main / "fig1_overview.caption.md").write_text("Schematic.")
    qa = _QA({"fig_qa.pdf": ("fonts",), "fig1_overview.pdf": ("vector", "no_text_in_axes")})
    out = {o["figure"]: o for o in ft.check_figures(root, qa)}
    assert out["main/fig_ok.pdf"]["pass"] and out["main/fig_ok.pdf"]["qa"] == "PASS"
    assert not out["main/fig_missing.pdf"]["pass"]
    assert not out["main/fig_norecord.pdf"]["pass"]
    assert not out["main/fig_qa.pdf"]["pass"] and out["main/fig_qa.pdf"]["qa"] == "FAIL"
    assert out["main/fig1_overview.pdf"]["pass"] and out["main/fig1_overview.pdf"]["qa"] == "accepted exception"


def test_latex_table_escapes_and_has_no_caption(root):
    rows = ft.evaluate_rows([ft.row("C3a-out654-v2", "C3a-v2", "TOST outcome, delta_P = 0.05 eV", ft.V2, "POST HOC",
                                    ("results/a.json", "payload.outcome"))], ft.Records(root))
    tex = ft.latex_table(rows)
    assert r"\caption" not in tex and r"\toprule" in tex and r"\bottomrule" in tex
    assert r"delta\_P" in tex and "C4 moves to the SI" in tex
    assert ft.fmt_value(-0.0116) == "-0.012" and ft.fmt_value(True) == "yes" and ft.fmt_value(654) == "654"

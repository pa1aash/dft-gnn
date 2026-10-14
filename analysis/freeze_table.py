"""Results freeze (A6): one table of every headline number, read from the committed result records, and the
consistency checks of the freeze.

Rule: `docs/deviations.md`, AUTHOR DECISION / FREEZE row of 2026-10-14 (tag `results-v1`). Nothing is recomputed:
every value is read from a named result record by its key. The only arithmetic is the minimum and maximum over the
per-class N1 entries of one record (marked in the row's key) and differences between records in the checks.

Consistency checks (all in the record, each with pass or fail):

    repeats     a quantity stored in several records is identical in all of them (|difference| <= 1e-12 eV)
    estimator   known differences between estimators (another bootstrap or a re-inference), listed with their size
    notes       the rounded value appears in the notes and documents that quote it
    claims      every row of docs/claims.yaml has a result_ref that exists, and a status consistent with the record
    figures     every PDF in figures/main and figures/si has a caption naming existing records and passes
                figures/code/qa_figure.py, or is a documented exception (docs/figure_style.md)

Writes through ``write_result``: ``results/freeze_table.json``; and ``paper/tables/freeze_table.tex`` (booktabs,
no caption). ``--dry-run`` prints the table and the checks without writing anything.

    PYTHONPATH=$PWD/src python analysis/freeze_table.py [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TOL_IDENTICAL = 1e-12
LABELS = ("REGISTERED", "POST HOC", "EXTENSION")
V1, V2, NONE = "v1 (originally registered)", "v2 (primary)", "none"
BUDGETS = (25, 50, 100, 200, 400, 654)

# figures whose caption must name these records (from docs/figure_style.md and docs/claims.yaml)
FIGURE_RECORDS = {
    "main/fig2_learning_curves.pdf": ("results/c1c2_v1.json", "results/c1c2_v2.json"),
    "main/fig3_advantage.pdf": ("results/c1c2_v1.json", "results/c1c2_v2.json",
                                "results/precision_a_b400_b654.json", "results/cv_extended_budget.json"),
    "main/fig4_staging.pdf": ("results/staging_v1.json", "results/staging_v2.json"),
    "main/fig5_geometry.pdf": ("results/geometry_c3b.json",),
    "main/fig7_screening.pdf": ("figures/main/data/screening_demo.json",),
    "main/fig_g1_learning_curves.pdf": ("results/g1_primary.json",),
    "main/fig_within_host.pdf": ("results/g1_within_host.json",),
    "si/fig6_probe.pdf": ("results/probe_c4_v1.json",),
    "si/fig_si_gpu_class.pdf": ("results/precision_a_b400_b654.json", "results/cv_extended_budget.json"),
    "si/fig_si_sensitivities.pdf": ("results/sens_high_moment_v1.json", "results/sens_cgcnn.json",
                                    "results/sens_capped_post_hoc.json"),
    "si/fig_si_withinhost_groups.pdf": ("results/within_host_breakdown.json",),
}
# schematics and renders: no data, so no record; QA exceptions as documented in docs/figure_style.md
NO_DATA_FIGURES = {"main/fig1_overview.pdf", "si/fig_readout.pdf"}
QA_EXCEPTIONS = {"main/fig1_overview.pdf": {"vector", "no_text_in_axes"}, "si/fig_readout.pdf": {"no_text_in_axes"}}
CAPTION_REF = re.compile(r"(?:results|figures/main/data|schematics|data)/[A-Za-z0-9_./-]+\.(?:json|parquet|pdf|csv|png)")


# ---------------------------------------------------------------- record access

class Records:
    """Named result records, read once; ``get(path, key)`` resolves a dotted key below the record root."""

    def __init__(self, root: Path = ROOT):
        self.root = root
        self.cache: dict[str, dict] = {}

    def load(self, path: str) -> dict:
        if path not in self.cache:
            rec = json.loads((self.root / path).read_text())
            stem = Path(path).stem
            if rec.get("name") != stem or "payload" not in rec:
                raise ValueError(f"{path}: not a named result record (name {rec.get('name')!r})")
            self.cache[path] = rec
        return self.cache[path]

    def get(self, path: str, key: str):
        return resolve(self.load(path), key)

    def sha(self, path: str) -> str:
        return hashlib.sha256((self.root / path).read_bytes()).hexdigest()


def _split(key: str) -> list[str]:
    """Dotted key; dots inside [...] selectors do not split."""
    parts, depth, cur = [], 0, ""
    for ch in key:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        if ch == "." and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return parts


def resolve(obj, key: str):
    """Walk ``a.b[0].c[k=v,k2=v2]``: dict keys, list indices, or the one list item whose fields match."""
    for part in _split(key):
        m = re.fullmatch(r"([^\[]*)((?:\[[^\]]*\])*)", part)
        name, sels = m.group(1), re.findall(r"\[([^\]]*)\]", m.group(2))
        if name:
            if not isinstance(obj, dict) or name not in obj:
                raise KeyError(f"{key}: no key {name!r}")
            obj = obj[name]
        for sel in sels:
            if re.fullmatch(r"-?\d+", sel):
                obj = obj[int(sel)]
                continue
            conds = dict(c.split("=", 1) for c in sel.split(","))
            hits = [x for x in obj if all(str(x.get(k)) == v for k, v in conds.items())]
            if len(hits) != 1:
                raise KeyError(f"{key}: selector [{sel}] matches {len(hits)} items")
            obj = hits[0]
    return obj


# ---------------------------------------------------------------- the table

def R(rec: str, key: str) -> tuple[str, str]:
    return (f"results/{rec}.json" if "/" not in rec else rec, key)


def row(rid, claim, quantity, backbone, label, value, interval=None, upper=None, kind="two-sided 95%"):
    """One headline quantity. value, interval ends and upper are (record path, key) references."""
    assert label.split(";")[0] in LABELS, label
    return {"id": rid, "claim": claim, "quantity": quantity, "backbone": backbone, "label": label,
            "value_ref": value, "interval_ref": interval, "upper_ref": upper, "interval_kind": kind}


def ci_pair(rec, base, name="ci"):
    """Two-sided interval stored as a two-item list under ``name``."""
    return (R(rec, f"{base}.{name}[0]"), R(rec, f"{base}.{name}[1]"))


def headline_rows() -> list[dict]:
    rows = []
    P = "payload."
    # ---- baselines, variance (fixed in the frozen plan, docs/ANALYSIS_PLAN.md)
    rows += [
        row("B0-654", "B0", "MAE of B0 at B = 654 (10 resamples)", NONE, "REGISTERED",
            R("b0_physics_floor", P + "outer.654.aggregate.mae.mean"),
            ci_pair("b0_physics_floor", P + "outer.654.aggregate.mae")),
        row("B0-kiyo", "B0", "MAE of B0 on the Kiyohara split (126 test hosts)", NONE, "REGISTERED",
            R("baselines_summary", P + "kiyohara_split.b0.mae.point"),
            ci_pair("baselines_summary", P + "kiyohara_split.b0.mae")),
        row("RF-K-654", "B0", "MAE of RF-Kumagai at B = 654", NONE, "REGISTERED",
            R("rf_kumagai", P + "outer.654.aggregate.mae.mean"),
            ci_pair("rf_kumagai", P + "outer.654.aggregate.mae")),
        row("RF-E-654", "B0", "MAE of RF-electronic at B = 654", NONE, "REGISTERED",
            R("baselines_summary", P + "outer_full_budget.rf_electronic.mae.mean"),
            ci_pair("baselines_summary", P + "outer_full_budget.rf_electronic.mae")),
        row("RF-S-654", "B0", "MAE of RF-structural at B = 654", NONE, "REGISTERED",
            R("baselines_summary", P + "outer_full_budget.rf_structural.mae.mean"),
            ci_pair("baselines_summary", P + "outer_full_budget.rf_structural.mae")),
        row("RF-K-kiyo", "C0", "MAE of RF-Kumagai on the Kiyohara split", NONE, "REGISTERED",
            R("c0_official", P + "rf_kumagai_same_split.mae_eV.point"),
            ci_pair("c0_official", P + "rf_kumagai_same_split.mae_eV")),
        row("ORACLE-654", "B0", "MAE of the host-mean oracle at B = 654 (descriptive bound)", NONE, "REGISTERED",
            R("host_mean_oracle", P + "aggregate.mae.mean"), ci_pair("host_mean_oracle", P + "aggregate.mae")),
        row("ICC-host", "B0", "ICC of E_f grouped by host (1726 sites, 818 hosts)", NONE, "REGISTERED",
            R("variance_decomposition", P + "host.icc"), ci_pair("variance_decomposition", P + "host", "icc_ci")),
    ]
    # ---- C0
    rows += [
        row("C0-kiyo-v1", "C0", "MAE of S on the Kiyohara split (seed ensemble)", V1, "REGISTERED",
            R("c0_official", P + "S.ensemble.mae.point"), ci_pair("c0_official", P + "S.ensemble.mae")),
        row("C0-kiyo-gate", "C0", "C0 gate passed (MAE below the 0.35 eV threshold)", V1, "REGISTERED",
            R("c0_official", P + "gate_passed")),
        row("C0-fg-v1", "C0", "MAE of S at B = 654, formula-grouped protocol", V1, "REGISTERED",
            R("g1_primary", P + "per_budget.654.MAE_S.mean"), ci_pair("g1_primary", P + "per_budget.654.MAE_S")),
        row("C0-fg-v2", "C0", "MAE of S at B = 654, formula-grouped protocol", V2, "POST HOC",
            R("c1c2_v2", P + "mae.654.S.mae.mean"), ci_pair("c1c2_v2", P + "mae.654.S.mae")),
    ]
    # ---- C1, C2: A per budget, both backbones
    for b in BUDGETS:
        rows.append(row(f"C1-A{b}-v1", "C1", f"A = MAE_S - MAE_D at B = {b}", V1, "REGISTERED",
                        R("g1_primary", P + f"per_budget.{b}.A.mean"), ci_pair("g1_primary", P + f"per_budget.{b}.A"),
                        R("g1_primary", P + f"per_budget.{b}.A.upper_one_sided")))
    for b in BUDGETS:
        rows.append(row(f"C1-A{b}-v2", "C1", f"A = MAE_S - MAE_D at B = {b}", V2, "POST HOC",
                        R("c1c2_v2", P + f"A_mae.{b}.A"), ci_pair("c1c2_v2", P + f"A_mae.{b}", "ci95"),
                        R("c1c2_v2", P + f"A_mae.{b}.upper_one_sided_95")))
    rows += [
        row("C1-Nstar-v1", "C1", "N* (upper bound on A below delta = 0.05 eV at N* and beyond)", V1, "REGISTERED",
            R("g1_primary", P + "n_star.n_star")),
        row("C1-Nstar-v2", "C1", "N* (upper bound on A below delta = 0.05 eV at N* and beyond)", V2, "POST HOC",
            R("c1c2_v2", P + "N_star.N_star")),
        row("C1-Nstar-v2-qual", "C1", "budgets with upper bound below delta (not monotone: 200 and 654)", V2,
            "POST HOC", R("c1c2_v2", P + "N_star.qualifying_budgets")),
        row("C2-v1", "C2", "C2 ceiling: A at B = 654", V1, "REGISTERED",
            R("g1_primary", P + "c2_ceiling.A"), ci_pair("g1_primary", P + "c2_ceiling")),
        row("C2-v2", "C2", "C2 ceiling: A at B = 654", V2, "POST HOC",
            R("c1c2_v2", P + "C2.A"), ci_pair("c1c2_v2", P + "C2", "ci95")),
    ]
    # ---- LOCO (collaborator runs adopted by the 2026-10-11 row, "EXTENSION (as run)"); G1 estimator of the M1 recompute
    rows += [
        row("LOCO-A-v1", "C1", "A under leave-one-cluster-out (5 folds, 818 hosts)", V1, "EXTENSION",
            R("ingest_m1_recompute", P + "loco_v1.A.mean"), ci_pair("ingest_m1_recompute", P + "loco_v1.A"),
            R("ingest_m1_recompute", P + "loco_v1.A.upper_one_sided")),
        row("LOCO-A-v2", "C1", "A under leave-one-cluster-out (5 folds, 818 hosts)", V2, "POST HOC",
            R("ingest_m1_recompute", P + "loco_v2.A.mean"), ci_pair("ingest_m1_recompute", P + "loco_v2.A"),
            R("ingest_m1_recompute", P + "loco_v2.A.upper_one_sided")),
    ]
    # ---- precision (PR1) and CV (CV1) extensions
    for bb, v, lab in (("v1", V1, "EXTENSION"), ("v2", V2, "EXTENSION; POST HOC (v2)")):
        rows += [
            row(f"PR1-A654-{bb}", "PR1", "A at B = 654, pooled 30 x 5", v, lab,
                R("precision_a_b400_b654", P + f"{bb}.30x5.654.A.mean"),
                ci_pair("precision_a_b400_b654", P + f"{bb}.30x5.654.A"),
                R("precision_a_b400_b654", P + f"{bb}.30x5.654.A.upper_one_sided")),
            row(f"PR1-A400-{bb}", "PR1", "A at B = 400, pooled 30 x 5", v, lab,
                R("precision_a_b400_b654", P + f"{bb}.30x5.400.A.mean"),
                ci_pair("precision_a_b400_b654", P + f"{bb}.30x5.400.A"),
                R("precision_a_b400_b654", P + f"{bb}.30x5.400.A.upper_one_sided")),
            row(f"PR1-holds-{bb}", "PR1", "non-inferiority bound holds at 654 (30 x 5 rule)", v, lab,
                R("precision_a_b400_b654", P + f"statement_654.{bb}.holds_at_654")),
        ]
        for k, n in (("k10", "736.2"), ("k20", "777.1")):
            rows.append(row(f"CV1-A{k}-{bb}", "CV1", f"A, grouped CV {k.upper()} (mean {n} training hosts)", v, lab,
                            R("cv_extended_budget", P + f"{bb}.{k}.A.mean"),
                            ci_pair("cv_extended_budget", P + f"{bb}.{k}.A"),
                            R("cv_extended_budget", P + f"{bb}.{k}.A.upper_one_sided")))
        rows.append(row(f"CV1-holds-{bb}", "CV1", "extended-budget statement holds (654, K10, K20)", v, lab,
                        R("cv_extended_budget", P + f"extended_budget_statement.{bb}.holds")))
    # ---- within-host
    rows += [
        row("WH-Aw654-v1", "C1", "A_within (within-host residual MAE, S - D) at B = 654", V1, "REGISTERED",
            R("g1_within_host", P + "within_host_residual_mae.per_budget.654.A_within.mean"),
            ci_pair("g1_within_host", P + "within_host_residual_mae.per_budget.654.A_within"),
            R("g1_within_host", P + "within_host_residual_mae.per_budget.654.A_within.upper_one_sided")),
        row("WH-Aw654-v2", "C1", "A_within at B = 654", V2, "POST HOC",
            R("c1c2_v2", P + "A_within_host.654.A"), ci_pair("c1c2_v2", P + "A_within_host.654", "ci95"),
            R("c1c2_v2", P + "A_within_host.654.upper_one_sided_95")),
        row("WH-Nstar-v1", "C1", "N* of A_within", V1, "REGISTERED", R("c1c2_v1", P + "N_star_within_host.N_star")),
        row("WH-Nstar-v2", "C1", "N* of A_within", V2, "POST HOC", R("c1c2_v2", P + "N_star_within_host.N_star")),
        row("WH1-zero", "WH1", "zero-skill within-host MAE, 739 tested hosts", NONE, "EXTENSION",
            R("within_host_breakdown", P + "groups[variable=pooled].v1.S.zero_skill_mae.point"),
            ci_pair("within_host_breakdown", P + "groups[variable=pooled].v1.S.zero_skill_mae", "ci95")),
    ]
    for bb, v, lab in (("v1", V1, "EXTENSION"), ("v2", V2, "EXTENSION; POST HOC (v2)")):
        for m in ("S", "D"):
            base = f"groups[variable=pooled].{bb}.{m}.within_host_mae"
            rows.append(row(f"WH1-{m}-{bb}", "WH1", f"within-host residual MAE of {m}, pooled, B = 654", v, lab,
                            R("within_host_breakdown", P + base + ".point"),
                            ci_pair("within_host_breakdown", P + base, "ci95")))
    # ---- staging C3a
    for bb, v, lab, rlab in (("v1", V1, "REGISTERED", "POST HOC"), ("v2", V2, "POST HOC", "POST HOC")):
        rec = f"staging_{bb}"
        rows += [
            row(f"C3a-PS654-{bb}", "C3a" if bb == "v1" else "C3a-v2", "P - S at B = 654", v, lab,
                R(rec, P + "budgets.654.P_minus_S.mean"), ci_pair(rec, P + "budgets.654.P_minus_S", "ci95"),
                R(rec, P + "budgets.654.P_minus_S.upper_one_sided_95")),
            row(f"C3a-DP654-{bb}", "C3a" if bb == "v1" else "C3a-v2", "D - P at B = 654", v, lab,
                R(rec, P + "budgets.654.D_minus_P.mean"), ci_pair(rec, P + "budgets.654.D_minus_P", "ci95")),
            row(f"C3a-MAEP654-{bb}", "C3a" if bb == "v1" else "C3a-v2", "MAE of P at B = 654", v, lab,
                R(rec, P + "budgets.654.mae.P.mean"), ci_pair(rec, P + "budgets.654.mae.P", "ci95")),
        ]
        for b in BUDGETS:
            rows.append(row(f"C3a-out{b}-{bb}", "C3a" if bb == "v1" else "C3a-v2",
                            f"TOST outcome of P - S at B = {b} (delta_P = 0.05 eV)", v, f"{rlab}",
                            R(rec, P + f"summary.outcome_by_budget.{b}")))
        rows.append(row(f"C3a-noninf-{bb}", "C3a" if bb == "v1" else "C3a-v2",
                        "budgets where P is non-inferior to S", v, rlab, R(rec, P + "summary.noninferior_by_budget")))
        for c in ("host_electronic", "site_electronic"):
            rows.append(row(f"C3a-P1{c[:4]}-{bb}", "C3a" if bb == "v1" else "C3a-v2",
                            f"P1 class-mean test R2, {c.replace('_', '-')}, B = 654", v, lab,
                            R(rec, P + f"p1_descriptors.654.by_class.{c}.class_mean_r2")))
    # ---- geometry C3b (v1, our 818 relaxations)
    for m in ("S", "D", "P"):
        for cond, cname in (("mlip", "MLIP"), ("mlip_rescaled", "rescaled MLIP")):
            base = f"budgets.654.delta_mae.{m}.{cond}"
            rows.append(row(f"C3b-d{m}-{cond}", "C3b", f"Delta-MAE of {m}, {cname} geometry, B = 654", V1,
                            "REGISTERED", R("geometry_c3b", P + base + ".mean"),
                            ci_pair("geometry_c3b", P + base, "ci95")))
    rows += [
        row("C3b-rmsd", "C3b", "median internal RMSD of the relaxations (A; threshold 0.01 A)", NONE, "REGISTERED",
            R("geometry_c3b", P + "null_rule.median_internal_rmsd_A")),
        row("C3b-null", "C3b", "null-rule outcome (ANALYSIS_PLAN §9)", V1, "REGISTERED",
            R("geometry_c3b", P + "null_rule.outcome")),
        row("C3b-nc-null", "C3b-nc", "null-rule outcome without the 7 non-converged hosts", V1, "REGISTERED",
            R("geometry_c3b", P + "nonconverged_sensitivity.null_rule.outcome")),
        row("C3b-tost-mlip", "C3b-tost", "Delta-MAE_P - Delta-MAE_S, MLIP, B = 654", V1, "POST HOC",
            R("geometry_c3b", P + "post_hoc_tost.by.654_mlip.mean"),
            ci_pair("geometry_c3b", P + "post_hoc_tost.by.654_mlip", "ci95")),
        row("C3b-tost-mlip-out", "C3b-tost", "TOST outcome, MLIP, B = 654", V1, "POST HOC",
            R("geometry_c3b", P + "post_hoc_tost.by.654_mlip.outcome")),
        row("C3b-tost-resc", "C3b-tost", "Delta-MAE_P - Delta-MAE_S, rescaled MLIP, B = 654", V1, "POST HOC",
            R("geometry_c3b", P + "post_hoc_tost.by.654_mlip_rescaled.mean"),
            ci_pair("geometry_c3b", P + "post_hoc_tost.by.654_mlip_rescaled", "ci95")),
        row("C3b-tost-resc-out", "C3b-tost", "TOST outcome, rescaled MLIP, B = 654", V1, "POST HOC",
            R("geometry_c3b", P + "post_hoc_tost.by.654_mlip_rescaled.outcome")),
        row("C3b-809-his", "C3b-809", "collaborator's largest |dMAE| on his 809 relaxations (P-v2, B = 654)", V2,
            "POST HOC", R("geometry_descriptive", P + "cross_check_809.his_max_abs_dmae.value_eV")),
    ]
    # ---- probe C4
    rows += [
        row("C4-outcome-v1", "C4", "outcome of the §10 rule", V1, "REGISTERED", R("probe_c4_v1", P + "outcome")),
        row("C4-holds-v1", "C4", "C4 holds", V1, "REGISTERED", R("probe_c4_v1", P + "C4_holds")),
    ]
    for c in ("host", "site"):
        rows.append(row(f"C4-rho-{c}-v1", "C4", f"Spearman rho of class-mean test R2 with budget, {c}-electronic",
                        V1, "REGISTERED", R("probe_c4_v1", P + f"rule.{c}.trend.rho"),
                        ci_pair("probe_c4_v1", P + f"rule.{c}.trend", "ci95")))
    rows.append(row("C4-holds-v2", "C4-v2", "C4 holds under the A4 application of the §10 rule", V2, "POST HOC",
                    R("probe_descriptive", P + "s_v2.C4_holds_under_A4_rule")))
    for c in ("host", "site"):
        rows.append(row(f"C4-rho-{c}-v2", "C4-v2", f"Spearman rho of class-mean test R2 with budget, {c}-electronic",
                        V2, "POST HOC", R("probe_descriptive", P + f"s_v2.{c}.rule.trend.rho"),
                        ci_pair("probe_descriptive", P + f"s_v2.{c}.rule.trend", "ci95")))
    # ---- sensitivities (v1)
    rows += [
        row("SENS1-A", "SENS1", "A at B = 654 without the 10 high-moment entries", V1, "EXTENSION",
            R("sens_high_moment_v1", P + "high_moment.A.mean"), ci_pair("sens_high_moment_v1", P + "high_moment.A"),
            R("sens_high_moment_v1", P + "high_moment.A.upper_one_sided")),
        row("SENS1-dA", "SENS1", "paired change of A (high moment - primary, common sites)", V1, "EXTENSION",
            R("sens_high_moment_v1", P + "change_high_moment_minus_primary.A.mean"),
            ci_pair("sens_high_moment_v1", P + "change_high_moment_minus_primary.A")),
        row("SENS2-A654-cgcnn", "SENS2", "A of CGCNN at B = 654, resample 0 (untuned)", NONE, "EXTENSION",
            R("sens_cgcnn", P + "table.cgcnn.654.A.point"), ci_pair("sens_cgcnn", P + "table.cgcnn.654.A", "ci95")),
        row("SENS2-A654-megnet", "SENS2", "A of MEGNet at B = 654, resample 0", V1, "EXTENSION",
            R("sens_cgcnn", P + "table.megnet_v1.654.A.point"),
            ci_pair("sens_cgcnn", P + "table.megnet_v1.654.A", "ci95")),
        row("SENS3-A654", "SENS3", "A at B = 654 with the 600-epoch capped twins", V1, "POST HOC",
            R("sens_capped_post_hoc", P + "per_budget.654.capped_twins.A.mean"),
            ci_pair("sens_capped_post_hoc", P + "per_budget.654.capped_twins.A"),
            R("sens_capped_post_hoc", P + "per_budget.654.capped_twins.A.upper_one_sided")),
        row("SENS3-dA654", "SENS3", "paired change of A at B = 654 (twins - primary)", V1, "POST HOC",
            R("sens_capped_post_hoc", P + "per_budget.654.change_twin_minus_primary.A.mean"),
            ci_pair("sens_capped_post_hoc", P + "per_budget.654.change_twin_minus_primary.A")),
        row("SENS3-A400", "SENS3", "A at B = 400 with the capped twins", V1, "POST HOC",
            R("sens_capped_post_hoc", P + "per_budget.400.capped_twins.A.mean"),
            ci_pair("sens_capped_post_hoc", P + "per_budget.400.capped_twins.A"),
            R("sens_capped_post_hoc", P + "per_budget.400.capped_twins.A.upper_one_sided")),
    ]
    # ---- screening C5, SD1
    sd = "figures/main/data/screening_demo.json"
    rows += [
        row("C5-mae-v1", "C5", "MAE of S at B = 654 on the 10 screened sites", V1, "REGISTERED",
            R("screening_c5", P + "mae_S"), (R(sd, P + "summary.v1.mae_ci[0]"), R(sd, P + "summary.v1.mae_ci[1]"))),
        row("C5-mae-v2", "C5", "MAE of S at B = 654 on the 10 screened sites", V2, "POST HOC",
            R("screening_c5", P + "mae_S_v2"), (R(sd, P + "summary.v2.mae_ci[0]"), R(sd, P + "summary.v2.mae_ci[1]"))),
    ]
    # ---- N1 hardware repeatability (descriptive)
    n1 = "results/nrp/n1_recompute.json"
    rows += [
        row("N1-same-node", "PR1", "same node, two passes: runs bitwise identical (of 12)", NONE, "EXTENSION",
            R(n1, P + "same_node_repeat[0].bitwise_identical")),
        row("N1-cross-node", "PR1", "same class, two nodes: runs bitwise identical (of 12)", NONE, "EXTENSION",
            R(n1, P + "cross_node_same_class[0].bitwise_identical")),
    ]
    for m, mlab in (("S", "S"), ("D-state", "D")):
        for b in (200, 654):
            rows.append(row(f"N1-{mlab}{b}", "PR1",
                            f"seed-ensemble MAE of {mlab} minus the sweep, B = {b}: range over 4 GPU classes", V1,
                            "EXTENSION", ("range", n1, P + f"per_class[model={m},B={b}].ensemble_mae_minus_ref_eV"),
                            kind="min, max over classes"))
    return rows


# ---------------------------------------------------------------- consistency groups

def repeat_groups() -> list[dict]:
    """Quantities stored in more than one record; every member must equal the first to TOL_IDENTICAL."""
    P = "payload."
    g = [
        ("A at 654, v1 (point)", [R("g1_primary", P + "per_budget.654.A.mean"), R("g1_primary", P + "c2_ceiling.A"),
                                  R("c1c2_v1", P + "A_mae.654.A"), R("c1c2_v1", P + "C2.A"),
                                  R("precision_g1_v1", P + "beside_subsets.10x3.654.A"),
                                  R("precision_a_b400_b654", P + "v1.10x3.654.A.mean"),
                                  R("sens_high_moment_v1", P + "primary_full_sites.A.mean"),
                                  R("sens_capped_post_hoc", P + "per_budget.654.primary.A.mean")]),
        ("A at 654, v1 (two-sided 95% low)", [R("g1_primary", P + "per_budget.654.A.ci[0]"),
                                              R("g1_primary", P + "c2_ceiling.ci[0]"),
                                              R("precision_a_b400_b654", P + "v1.10x3.654.A.ci[0]"),
                                              R("precision_g1_v1", P + "beside_subsets.10x3.654.ci95[0]"),
                                              R("sens_high_moment_v1", P + "primary_full_sites.A.ci[0]"),
                                              R("sens_capped_post_hoc", P + "per_budget.654.primary.A.ci[0]")]),
        ("A at 654, v1 (two-sided 95% high)", [R("g1_primary", P + "per_budget.654.A.ci[1]"),
                                               R("g1_primary", P + "c2_ceiling.ci[1]"),
                                               R("precision_a_b400_b654", P + "v1.10x3.654.A.ci[1]"),
                                               R("precision_g1_v1", P + "beside_subsets.10x3.654.ci95[1]"),
                                               R("sens_high_moment_v1", P + "primary_full_sites.A.ci[1]"),
                                               R("sens_capped_post_hoc", P + "per_budget.654.primary.A.ci[1]")]),
        ("A at 654, v1 (one-sided upper)", [R("g1_primary", P + "per_budget.654.A.upper_one_sided"),
                                            R("precision_a_b400_b654", P + "v1.10x3.654.A.upper_one_sided"),
                                            R("precision_g1_v1", P + "beside_subsets.10x3.654.upper_one_sided_95"),
                                            R("sens_high_moment_v1", P + "primary_full_sites.A.upper_one_sided"),
                                            R("sens_capped_post_hoc", P + "per_budget.654.primary.A.upper_one_sided")]),
        ("A at 654, v1, resample 0", [R("g1_primary", P + "c2_ceiling.per_resample[0]"),
                                      R("sens_cgcnn", P + "table.megnet_v1.654.A.point")]),
        ("A at 400, v1 (point)", [R("g1_primary", P + "per_budget.400.A.mean"), R("c1c2_v1", P + "A_mae.400.A"),
                                  R("precision_g1_v1", P + "beside_subsets.10x3.400.A"),
                                  R("precision_a_b400_b654", P + "v1.10x3.400.A.mean"),
                                  R("sens_capped_post_hoc", P + "per_budget.400.primary.A.mean")]),
        ("MAE_S at 654, v1", [R("g1_primary", P + "per_budget.654.MAE_S.mean"),
                              R("c1c2_v1", P + "mae.654.S.mae.mean"),
                              R("precision_a_b400_b654", P + "v1.10x3.654.MAE_S.mean"),
                              R("staging_v1", P + "budgets.654.mae.S.mean"),
                              R("within_host_breakdown", P + "sanity.i_site_mae_v1.g1_primary.S")]),
        ("MAE_D at 654, v1", [R("g1_primary", P + "per_budget.654.MAE_D.mean"),
                              R("c1c2_v1", P + "mae.654.D-state.mae.mean"),
                              R("precision_a_b400_b654", P + "v1.10x3.654.MAE_D.mean"),
                              R("staging_v1", P + "budgets.654.mae.D.mean"),
                              R("within_host_breakdown", P + "sanity.i_site_mae_v1.g1_primary.D")]),
        ("A_within at 654, v1 (point)", [R("g1_within_host", P + "within_host_residual_mae.per_budget.654.A_within.mean"),
                                         R("c1c2_v1", P + "A_within_host.654.A"),
                                         R("precision_a_b400_b654", P + "v1.10x3.654.A_within.mean")]),
        ("A at 654, v2 (point)", [R("c1c2_v2", P + "A_mae.654.A"), R("c1c2_v2", P + "C2.A"),
                                  R("precision_g1_v2", P + "beside_subsets.10x3.654.A"),
                                  R("precision_a_b400_b654", P + "v2.10x3.654.A.mean")]),
        ("A at 400, v2 (point)", [R("c1c2_v2", P + "A_mae.400.A"),
                                  R("precision_a_b400_b654", P + "v2.10x3.400.A.mean")]),
        ("MAE_S at 654, v2", [R("c1c2_v2", P + "mae.654.S.mae.mean"),
                              R("precision_a_b400_b654", P + "v2.10x3.654.MAE_S.mean"),
                              R("staging_v2", P + "budgets.654.mae.S.mean"),
                              R("c3a_v2", P + "budgets.654.mae.S.mean")]),
        ("MAE_D at 654, v2", [R("c1c2_v2", P + "mae.654.D-state.mae.mean"),
                              R("precision_a_b400_b654", P + "v2.10x3.654.MAE_D.mean"),
                              R("staging_v2", P + "budgets.654.mae.D.mean"),
                              R("c3a_v2", P + "budgets.654.mae.D.mean")]),
        ("A_within at 654, v2 (point)", [R("c1c2_v2", P + "A_within_host.654.A"),
                                         R("precision_a_b400_b654", P + "v2.10x3.654.A_within.mean")]),
        ("P - S at 654, v2 (point)", [R("staging_v2", P + "budgets.654.P_minus_S.mean"),
                                      R("c3a_v2", P + "budgets.654.P_minus_S.mean")]),
        ("D - P at 654, v2 (point)", [R("staging_v2", P + "budgets.654.D_minus_P.mean"),
                                      R("c3a_v2", P + "budgets.654.D_minus_P.mean")]),
        ("A pooled 30 x 5 at 654, v1", [R("precision_a_b400_b654", P + "v1.30x5.654.A.mean"),
                                        R("precision_g1_v1", P + "A_mae.654.A")]),
        ("A pooled 30 x 5 at 654, v2", [R("precision_a_b400_b654", P + "v2.30x5.654.A.mean"),
                                        R("precision_g1_v2", P + "A_mae.654.A")]),
        ("A pooled 30 x 5 at 654, v1 (upper)", [R("precision_a_b400_b654", P + "v1.30x5.654.A.upper_one_sided"),
                                                R("precision_g1_v1", P + "A_mae.654.upper_one_sided_95")]),
        ("A pooled 30 x 5 at 654, v2 (upper)", [R("precision_a_b400_b654", P + "v2.30x5.654.A.upper_one_sided"),
                                                R("precision_g1_v2", P + "A_mae.654.upper_one_sided_95")]),
        ("LOCO A, v1 (point)", [R("ingest_m1_recompute", P + "loco_v1.A.mean"), R("c1c2_v1", P + "loco.A")]),
        ("LOCO A, v2 (point)", [R("ingest_m1_recompute", P + "loco_v2.A.mean"), R("c1c2_v2", P + "loco.A")]),
        ("N* v1", [R("g1_primary", P + "n_star.n_star"), R("c1c2_v1", P + "N_star.N_star")]),
        ("C0 Kiyohara MAE of S, v1", [R("c0_official", P + "S.ensemble.mae.point"),
                                      R("c0_official", P + "S.ensemble_point.mae")]),
        ("RF-Kumagai, Kiyohara split", [R("c0_official", P + "rf_kumagai_same_split.mae_eV.point"),
                                        R("c0_official", P + "comparison_eV.rf_kumagai_same_split"),
                                        R("baselines_summary", P + "kiyohara_split.rf_kumagai.mae.point")]),
        ("B0 at 654", [R("b0_physics_floor", P + "outer.654.aggregate.mae.mean"),
                       R("baselines_summary", P + "outer_full_budget.b0.mae.mean")]),
        ("RF-Kumagai at 654", [R("rf_kumagai", P + "outer.654.aggregate.mae.mean"),
                               R("baselines_summary", P + "outer_full_budget.rf_kumagai.mae.mean")]),
        ("host-mean oracle at 654", [R("host_mean_oracle", P + "aggregate.mae.mean"),
                                     R("baselines_summary", P + "outer_full_budget.host_mean_oracle.mae.mean")]),
        ("ICC host = ICC formula", [R("variance_decomposition", P + "host.icc"),
                                    R("variance_decomposition", P + "formula.icc")]),
        ("screening MAE, v1", [R("screening_c5", P + "mae_S"),
                               R("figures/main/data/screening_demo.json", P + "summary.v1.mae_eV")]),
        ("screening MAE, v2", [R("screening_c5", P + "mae_S_v2"),
                               R("figures/main/data/screening_demo.json", P + "summary.v2.mae_eV")]),
        ("largest |Delta-MAE| (S, rescaled, 654), v1", [
            R("geometry_c3b", P + "budgets.654.delta_mae.S.mlip_rescaled.mean"),
            R("geometry_descriptive", P + "cross_check_809.our_max_abs_delta_mae.654.value_eV")]),
    ]
    for k in ("k10", "k20"):
        for bb in ("v1", "v2"):
            g.append((f"CV A {k}, {bb} (point)", [R("cv_extended_budget", P + f"{bb}.{k}.A.mean"),
                                                  R(f"cv_g1_{bb}", P + f"A_mae.{k}.A")]))
            g.append((f"CV A {k}, {bb} (upper)", [R("cv_extended_budget", P + f"{bb}.{k}.A.upper_one_sided"),
                                                  R(f"cv_g1_{bb}", P + f"A_mae.{k}.upper_one_sided_95")]))
    return [{"quantity": q, "refs": refs} for q, refs in g]


def estimator_groups() -> list[dict]:
    """Known differences between estimators: (quantity, reference, other, reason). Reported with their size."""
    P = "payload."
    g = [
        ("A at 654, v2: two-sided 95% high", R("precision_a_b400_b654", P + "v2.10x3.654.A.ci[1]"),
         R("c1c2_v2", P + "A_mae.654.ci95[1]"),
         "G1 estimator (dftgnn.stats.g1) vs the collaborator's bootstrap (scripts/analysis_c1c2.py); points identical"),
        ("A at 654, v2: two-sided 95% low", R("precision_a_b400_b654", P + "v2.10x3.654.A.ci[0]"),
         R("c1c2_v2", P + "A_mae.654.ci95[0]"), "same"),
        ("A at 654, v2: one-sided upper", R("precision_a_b400_b654", P + "v2.10x3.654.A.upper_one_sided"),
         R("c1c2_v2", P + "A_mae.654.upper_one_sided_95"), "same"),
        ("A at 654, v1: two-sided 95% low", R("g1_primary", P + "per_budget.654.A.ci[0]"),
         R("c1c2_v1", P + "A_mae.654.ci95[0]"), "same, v1"),
        ("A at 654, v1: two-sided 95% high", R("g1_primary", P + "per_budget.654.A.ci[1]"),
         R("c1c2_v1", P + "A_mae.654.ci95[1]"), "same, v1"),
        ("A at 654, v1: one-sided upper", R("g1_primary", P + "per_budget.654.A.upper_one_sided"),
         R("c1c2_v1", P + "A_mae.654.upper_one_sided_95"), "same, v1"),
        ("A_within at 654, v1: one-sided upper", R("g1_within_host",
                                                   P + "within_host_residual_mae.per_budget.654.A_within.upper_one_sided"),
         R("c1c2_v1", P + "A_within_host.654.upper_one_sided_95"), "same, within-host"),
        ("LOCO A, v1: one-sided upper", R("ingest_m1_recompute", P + "loco_v1.A.upper_one_sided"),
         R("c1c2_v1", P + "loco.upper_one_sided_95"), "G1 estimator (M1 recompute) vs the collaborator's bootstrap"),
        ("LOCO A, v2: one-sided upper", R("ingest_m1_recompute", P + "loco_v2.A.upper_one_sided"),
         R("c1c2_v2", P + "loco.upper_one_sided_95"), "same"),
        ("P - S at 654, v2: two-sided 95% high", R("staging_v2", P + "budgets.654.P_minus_S.ci95[1]"),
         R("c3a_v2", P + "budgets.654.P_minus_S.ci95[1]"), "G1 estimator vs his bootstrap generator (A2)"),
        ("D - P at 654, v2: two-sided 95% low", R("staging_v2", P + "budgets.654.D_minus_P.ci95[0]"),
         R("c3a_v2", P + "budgets.654.D_minus_P.ci95[0]"), "same"),
        ("MAE_D at 654, v1: DFT-geometry re-inference", R("g1_primary", P + "per_budget.654.MAE_D.mean"),
         R("geometry_c3b", P + "budgets.654.mae.D.dft.mean"),
         "geomeval re-ran inference from the S09 checkpoints on the cluster (A3); the sweep predictions are the G1 inputs"),
        ("MAE_S at 654, v1: DFT-geometry re-inference", R("g1_primary", P + "per_budget.654.MAE_S.mean"),
         R("geometry_c3b", P + "budgets.654.mae.S.dft.mean"), "same"),
        ("MAE_P at 654, v1: DFT-geometry re-inference", R("staging_v1", P + "budgets.654.mae.P.mean"),
         R("geometry_c3b", P + "budgets.654.mae.P.dft.mean"), "same; the staging value uses the stored peval predictions"),
        ("C0, Kiyohara split: S on our 818-host universe vs the published 0.29 eV", R("c0_official",
                                                                                       P + "S.ensemble.mae.point"),
         R("c0_official", P + "comparison_eV.kiyohara_published"), "different study (published value), not an estimator"),
    ]
    return [{"quantity": q, "ref": a, "other": b, "reason": why} for q, a, b, why in g]


# value in record, document, format; the formatted value must appear in the document (U+2212 counted as '-')
NOTE_CHECKS = (
    ("g1_primary", "payload.per_budget.654.A.mean", "{:+.3f}", ("docs/a1_notes.md", "docs/a2_notes.md",
                                                                "docs/a5_notes.md", "docs/g1_notes.md")),
    ("c1c2_v2", "payload.A_mae.654.A", "{:+.3f}", ("docs/a1_notes.md", "docs/a2_notes.md", "docs/claims.yaml")),
    ("precision_a_b400_b654", "payload.v2.30x5.654.A.mean", "{:+.3f}", ("docs/a1_notes.md",)),
    ("precision_a_b400_b654", "payload.v1.30x5.654.A.mean", "{:+.3f}", ("docs/a1_notes.md",)),
    ("precision_a_b400_b654", "payload.v2.30x5.654.A.upper_one_sided", "{:+.3f}", ("docs/a1_notes.md",)),
    ("precision_a_b400_b654", "payload.v1.30x5.654.A.upper_one_sided", "{:+.3f}", ("docs/a1_notes.md",)),
    ("cv_extended_budget", "payload.v2.k10.A.mean", "{:+.3f}", ("docs/a1_notes.md",)),
    ("cv_extended_budget", "payload.v1.k10.A.mean", "{:+.3f}", ("docs/a1_notes.md",)),
    ("c0_official", "payload.S.ensemble.mae.point", "{:.3f}", ("docs/claims.yaml", "docs/g1_notes.md")),
    ("g1_primary", "payload.per_budget.654.MAE_S.mean", "{:.3f}", ("docs/claims.yaml", "docs/a1_notes.md")),
    ("b0_physics_floor", "payload.outer.654.aggregate.mae.mean", "{:.3f}", ("docs/ANALYSIS_PLAN.md",
                                                                           "docs/baselines.md")),
    ("rf_kumagai", "payload.outer.654.aggregate.mae.mean", "{:.3f}", ("docs/ANALYSIS_PLAN.md", "docs/baselines.md")),
    ("host_mean_oracle", "payload.aggregate.mae.mean", "{:.3f}", ("docs/ANALYSIS_PLAN.md",)),
    ("variance_decomposition", "payload.host.icc", "{:.3f}", ("docs/ANALYSIS_PLAN.md",)),
    ("staging_v1", "payload.budgets.654.P_minus_S.mean", "{:+.3f}", ("docs/a2_notes.md",)),
    ("staging_v2", "payload.budgets.654.P_minus_S.mean", "{:+.3f}", ("docs/a2_notes.md",)),
    ("staging_v1", "payload.budgets.654.D_minus_P.mean", "{:+.3f}", ("docs/a2_notes.md",)),
    ("staging_v2", "payload.budgets.654.D_minus_P.mean", "{:+.3f}", ("docs/a2_notes.md",)),
    ("geometry_c3b", "payload.null_rule.median_internal_rmsd_A", "{:.3f}", ("docs/claims.yaml",)),
    ("geometry_c3b", "payload.null_rule.median_internal_rmsd_A", "{:.4f}", ("docs/a3_notes.md",)),
    ("geometry_c3b", "payload.post_hoc_tost.by.654_mlip.mean", "{:+.4f}", ("docs/claims.yaml",)),
    ("geometry_c3b", "payload.post_hoc_tost.by.654_mlip_rescaled.mean", "{:+.4f}", ("docs/claims.yaml",)),
    ("probe_c4_v1", "payload.rule.host.trend.rho", "{:.3f}", ("docs/claims.yaml", "docs/a4_notes.md")),
    ("probe_c4_v1", "payload.rule.site.trend.rho", "{:.3f}", ("docs/claims.yaml", "docs/a4_notes.md")),
    ("probe_descriptive", "payload.s_v2.host.rule.trend.rho", "{:.3f}", ("docs/claims.yaml", "docs/a4_notes.md")),
    ("sens_high_moment_v1", "payload.high_moment.A.mean", "{:+.3f}", ("docs/a5_notes.md",)),
    ("sens_capped_post_hoc", "payload.per_budget.654.capped_twins.A.mean", "{:+.3f}", ("docs/a5_notes.md",)),
    ("sens_cgcnn", "payload.table.cgcnn.654.A.point", "{:+.3f}", ("docs/a5_notes.md", "docs/claims.yaml")),
    ("screening_c5", "payload.mae_S", "{:.3f}", ("docs/claims.yaml",)),
    ("screening_c5", "payload.mae_S_v2", "{:.3f}", ("docs/claims.yaml",)),
    ("within_host_breakdown", "payload.groups[variable=pooled].v1.S.zero_skill_mae.point", "{:.3f}",
     ("docs/claims.yaml", "docs/within_host_physics.md")),
)


# ---------------------------------------------------------------- evaluation

def is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def evaluate_rows(rows: list[dict], recs: Records) -> list[dict]:
    out = []
    for r in rows:
        vref = r["value_ref"]
        if vref[0] == "range":
            _, path, key = vref
            listkey, sel_field = key.rsplit("[", 1)[0], key.rsplit(".", 1)[1]
            conds = dict(c.split("=", 1) for c in key.split("[", 1)[1].split("]", 1)[0].split(","))
            items = [x for x in recs.get(path, listkey) if all(str(x.get(k)) == v for k, v in conds.items())]
            vals = [x[sel_field] for x in items]
            if not vals:
                raise KeyError(f"{key}: no items")
            value, interval, rec_path, key_str = None, [min(vals), max(vals)], path, key + " (min, max)"
            n_items = len(vals)
        else:
            rec_path, key_str = vref
            value = recs.get(*vref)
            interval = [recs.get(*e) for e in r["interval_ref"]] if r["interval_ref"] else None
            n_items = None
        upper = recs.get(*r["upper_ref"]) if r["upper_ref"] else None
        o = {k: r[k] for k in ("id", "claim", "quantity", "backbone", "label", "interval_kind")}
        o.update({"value": value, "interval": interval if r["interval_ref"] or vref[0] == "range" else None,
                  "upper_one_sided_95": upper, "record": rec_path, "key": key_str,
                  "interval_keys": [e[1] for e in r["interval_ref"]] if r["interval_ref"] else None,
                  "upper_key": r["upper_ref"][1] if r["upper_ref"] else None})
        if n_items is not None:
            o["n_items"] = n_items
        out.append(o)
    return out


def check_repeats(groups: list[dict], recs: Records, tol: float = TOL_IDENTICAL) -> list[dict]:
    out = []
    for grp in groups:
        vals = [recs.get(*ref) for ref in grp["refs"]]
        if all(is_num(v) for v in vals):
            diff = max(abs(v - vals[0]) for v in vals)
            ok = diff <= tol
        else:
            diff = None
            ok = all(v == vals[0] for v in vals)
        out.append({"id": f"R{len(out) + 1:02d}", "quantity": grp["quantity"], "value": vals[0],
                    "n_records": len({p for p, _ in grp["refs"]}), "n_keys": len(vals), "max_abs_diff": diff,
                    "tolerance": tol, "pass": ok, "refs": [f"{p}#{k}" for p, k in grp["refs"]]})
    return out


def check_estimators(groups: list[dict], recs: Records) -> list[dict]:
    out = []
    for grp in groups:
        a, b = recs.get(*grp["ref"]), recs.get(*grp["other"])
        out.append({"id": f"E{len(out) + 1:02d}", "quantity": grp["quantity"], "value": a, "other": b,
                    "difference": a - b, "reason": grp["reason"], "pass": True, "kind": "known difference, listed",
                    "refs": [f"{grp['ref'][0]}#{grp['ref'][1]}", f"{grp['other'][0]}#{grp['other'][1]}"]})
    return out


def _norm(text: str) -> str:
    return text.replace("−", "-")


def check_notes(recs: Records, root: Path = ROOT, checks=NOTE_CHECKS) -> list[dict]:
    out = []
    for rec, key, fmt, docs in checks:
        path = f"results/{rec}.json" if "/" not in rec else rec
        v = recs.get(path, key)
        s = fmt.format(v)
        alts = {s, s.lstrip("+")}
        for doc in docs:
            text = _norm((root / doc).read_text())
            hit = any(re.search(r"(?<![0-9.])" + re.escape(a) + r"(?![0-9])", text) for a in alts)
            out.append({"id": f"N{len(out) + 1:02d}", "record": path, "key": key, "value": v, "formatted": s,
                        "document": doc, "pass": hit})
    return out


def _yaml_comments(text: str) -> dict[str, str]:
    """Comment block written directly above each '- id:' line of docs/claims.yaml."""
    out, buf = {}, []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#"):
            buf.append(s.lstrip("# "))
        elif s.startswith("- id:"):
            out[s.split(":", 1)[1].strip()] = " ".join(buf)
            buf = []
        elif s and not s.startswith("-") and ":" not in s:
            buf = []
    return out


def check_claims(recs: Records, root: Path = ROOT) -> list[dict]:
    text = (root / "docs" / "claims.yaml").read_text()
    claims = yaml.safe_load(text)["claims"]
    comments = _yaml_comments(text)
    out = []
    for c in claims:
        cid, status, ref = c["id"], c.get("status"), c.get("result_ref")
        problems = []
        exists = bool(ref) and (root / ref).is_file()
        named = False
        if not ref:
            problems.append("no result_ref")
        elif not exists:
            problems.append(f"result_ref {ref} does not exist")
        else:
            try:
                recs.load(ref)
                named = True
            except (ValueError, json.JSONDecodeError) as e:
                problems.append(str(e))
        if status not in ("measured", "moved_to_si", "planned"):
            problems.append(f"unknown status {status!r}")
        if status == "moved_to_si" and named:
            outcome = str(recs.get(ref, "payload").get("outcome", ""))
            if "SI" not in outcome:
                problems.append(f"status moved_to_si but record outcome is {outcome!r}")
        if status == "planned" and named:
            problems.append("status planned but the result record exists")
        if status == "measured" and not named:
            problems.append("status measured without a named result record")
        note = comments.get(cid, "")
        if status == "measured" and re.search(r"status stays planned", note) \
                and not re.search(r"superseded|predates|now exists|A6", note):
            problems.append("comment says the status stays planned")
        out.append({"id": cid, "status": status, "result_ref": ref, "result_ref_exists": exists,
                    "named_record": named, "problems": problems, "pass": not problems})
    return out


def _qa_module(root: Path):
    spec = importlib.util.spec_from_file_location("qa_figure", root / "figures" / "code" / "qa_figure.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_figures(root: Path = ROOT, qa=None) -> list[dict]:
    qa = qa or _qa_module(root)
    out = []
    for sub in ("main", "si"):
        for pdf in sorted((root / "figures" / sub).glob("*.pdf")):
            rel = f"{sub}/{pdf.name}"
            cap = pdf.with_suffix(".caption.md")
            refs = sorted(set(CAPTION_REF.findall(cap.read_text()))) if cap.is_file() else []
            missing = [p for p in refs if not (root / p).exists()]
            recs = [p for p in refs if p.endswith(".json")]
            need = FIGURE_RECORDS.get(rel, ())
            not_named = [p for p in need if p not in refs]
            rep = qa.check(pdf)
            failed = {name for name, c in rep["checks"].items() if not c["ok"]}
            excepted = QA_EXCEPTIONS.get(rel, set())
            problems = []
            if not cap.is_file():
                problems.append("no caption file")
            if missing:
                problems.append(f"caption names missing files: {missing}")
            if rel not in NO_DATA_FIGURES and not recs:
                problems.append("caption names no result record")
            # the brief asks for a caption naming existing records; a missing expected record is a warning
            warnings = [f"caption names keys but not the file {p}" for p in not_named]
            if failed - excepted:
                problems.append(f"QA fails: {sorted(failed - excepted)}")
            qa_result = "PASS" if not failed else ("accepted exception" if failed <= excepted else "FAIL")
            w = rep["checks"]["width"]
            out.append({"figure": rel, "caption": cap.relative_to(root).as_posix() if cap.is_file() else None,
                        "records_named": recs, "qa": qa_result, "qa_failed_checks": sorted(failed),
                        "width_mm": w["width_mm"], "height_mm": w["height_mm"],
                        "problems": problems, "warnings": warnings, "pass": not problems})
    return out


# ---------------------------------------------------------------- LaTeX

def _tex_escape(s: str) -> str:
    return (s.replace("\\", r"\textbackslash{}").replace("_", r"\_").replace("%", r"\%").replace("&", r"\&")
            .replace("#", r"\#").replace("|", r"\textbar{}").replace("§", r"\S{}").replace("~", r"\textasciitilde{}"))


def fmt_value(v) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, int):
        return str(v)
    if is_num(v):
        return f"{v:+.3f}" if abs(v) >= 0.001 or v == 0 else f"{v:+.1e}"
    if isinstance(v, list):
        return ", ".join(fmt_value(x) for x in v)
    if isinstance(v, dict):
        return "; ".join(f"{k}: {fmt_value(x)}" for k, x in v.items())
    return str(v)


def fmt_interval(r: dict) -> str:
    s = ""
    if r["interval"]:
        s = f"[{fmt_value(r['interval'][0])}, {fmt_value(r['interval'][1])}]"
    if r["upper_one_sided_95"] is not None:
        s += f"; U {fmt_value(r['upper_one_sided_95'])}"
    return s


def latex_table(rows: list[dict]) -> str:
    """booktabs longtable body, no caption; numbers as stored, rounded to 3 decimals for display."""
    head = ("Row & Claim & Quantity & Backbone & Label & Value & Interval & Record and key")
    lines = [
        "% Generated by analysis/freeze_table.py from the committed result records (results-v1 freeze). Do not edit.",
        "% Value and interval rounded to 3 decimals; full precision in results/freeze_table.json.",
        "% Interval: two-sided 95% unless the row says otherwise; U = one-sided 95% upper bound.",
        "% Needs \\usepackage{longtable}; booktabs is loaded by mdpi.cls.",
        r"\begin{scriptsize}",
        (r"\begin{longtable}{@{}p{0.09\linewidth}p{0.05\linewidth}p{0.2\linewidth}p{0.05\linewidth}"
         r"p{0.08\linewidth}p{0.1\linewidth}p{0.13\linewidth}p{0.21\linewidth}@{}}"),
        r"\toprule", head + r" \\", r"\midrule", r"\endhead", r"\bottomrule", r"\endfoot",
    ]
    for r in rows:
        bb = {V1: "v1", V2: "v2", NONE: "--"}[r["backbone"]]
        rk = f"\\texttt{{{_tex_escape(r['record'])}}} \\texttt{{{_tex_escape(r['key'].removeprefix('payload.'))}}}"
        cells = [_tex_escape(r["id"]), _tex_escape(r["claim"]), _tex_escape(r["quantity"]), bb,
                 _tex_escape(r["label"]), _tex_escape(fmt_value(r["value"])), _tex_escape(fmt_interval(r)), rk]
        lines.append(" & ".join(cells) + r" \\")
    lines += [r"\end{longtable}", r"\end{scriptsize}", ""]
    return "\n".join(lines)


# ---------------------------------------------------------------- main

def build(root: Path = ROOT, run_figures: bool = True) -> dict:
    recs = Records(root)
    rows = evaluate_rows(headline_rows(), recs)
    repeats = check_repeats(repeat_groups(), recs)
    estimators = check_estimators(estimator_groups(), recs)
    notes = check_notes(recs, root)
    claims = check_claims(recs, root)
    figures = check_figures(root) if run_figures else []
    blocks = {"repeats": repeats, "estimators": estimators, "notes": notes, "claims": claims, "figures": figures}
    summary = {k: {"n": len(v), "pass": sum(x["pass"] for x in v), "fail": sum(not x["pass"] for x in v)}
               for k, v in blocks.items()}
    records = sorted({r["record"] for r in rows} | {p for p in recs.cache})
    return {
        "label": "results freeze (AUTHOR DECISION / FREEZE, docs/deviations.md row of 2026-10-14); no recomputation",
        "rule": "every value read from a committed named result record by key; identical repeats to 1e-12",
        "tolerance_identical": TOL_IDENTICAL,
        "label_note": "v2 is the primary backbone and POST HOC in every row (never pre-registered); v1 is the "
                      "originally registered backbone. REGISTERED: fixed in the frozen plan or a rule logged before "
                      "the result; POST HOC: v2 backbone or a rule logged after the result it decides; EXTENSION: "
                      "beyond the plan.",
        "rows": rows,
        "checks": blocks,
        "summary": summary,
        "all_pass": all(s["fail"] == 0 for s in summary.values()),
        "inputs": {p: {"sha256": recs.sha(p), "git_sha": recs.cache[p]["git_sha"]} for p in records},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    payload = build()
    for r in payload["rows"]:
        print(f"{r['id']:20s} {r['label']:26s} {fmt_value(r['value']):>28s} {fmt_interval(r)}")
    for k, v in payload["checks"].items():
        for x in v:
            if not x["pass"]:
                print("FAIL", k, json.dumps(x)[:400])
    print(json.dumps(payload["summary"]), "all_pass", payload["all_pass"])
    if a.dry_run:
        return 0 if payload["all_pass"] else 1
    if not payload["all_pass"]:
        print("checks fail: nothing written", file=sys.stderr)
        return 1
    from dftgnn.config import load_config
    from dftgnn.io.results import write_result

    print(write_result("freeze_table", payload, config=load_config(), repo_root=ROOT))
    (ROOT / "paper" / "tables" / "freeze_table.tex").write_text(latex_table(payload["rows"]))
    print("wrote paper/tables/freeze_table.tex")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

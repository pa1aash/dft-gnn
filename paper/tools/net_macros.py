"""One-network macros for the rewrite: \\numNet... (the final network) and \\numAbl... (default-initialisation ablation).

The generic macros of make_numbers.py are named after their record and keep the repository's v1/v2 labels. The
rewritten text names one network, so this module adds a second, curated set of names that point at the same kind
of record leaves (no value is computed here): the C1 tables (results/derived_c1/), the W2 diagnostics
(results/derived_w2/) and the top-level records of the final network. Every macro is one JSON pointer; the
source column of numbers.tsv gives it. A missing pointer is an error, so a renamed record key fails the build.

Formats: "num" is the house rule of make_numbers.fmt (three decimals); "dp4" prints four decimals (energy changes
below 0.01 eV, as in the geometry check); "int" an exact integer; "hosts" the nearest whole number of hosts (the
cross-validation sizes are fold means); "word" a boolean as the word yes or no; "text" a short string as is;
"trim" three decimals without trailing zeros, for a set value or a published value printed at the precision of its
source (the tolerance 0.05 eV, the published 0.29 eV). A record ending in .yaml is read whole (no payload).

One block is not a record leaf: ILLUSTRATION, the Boltzmann-factor example of the Introduction (R4), evaluated from
exp(-E_f / k_B T) with k_B from scipy.constants (CODATA); its source column names the formula and the inputs.

Naming: \\numNet + row + field. Rows of the C1 table are budgets in words (TwentyFive ... SixHundredFiftyFour),
FourHundredThirtyByFive and SixHundredFiftyFourThirtyByFive (30 resamples x 5 seeds), CvTen and CvTwenty
(grouped cross-validation, K = 10 and 20) and Loco (leave one family out). Fields: MaeS, MaeD, MaeP, MaeRf,
MaeBZero with suffixes Lo and Hi for the two-sided 95% interval; A, ALo, AHi, AUpper (one-sided 95% bound);
AInside (two-sided interval inside +-delta), AUpperBelow (bound below delta), AExcludesZero (words); Hosts.
"""
from __future__ import annotations

import json
import math
import re
from collections.abc import Callable
from pathlib import Path

import yaml

C1 = "results/derived_c1"
W2 = "results/derived_w2"
BUDGETS = (25, 50, 100, 200, 400, 654)
ROWS = {**{f"B{b}": None for b in BUDGETS}, "B400_30x5": "FourHundredThirtyByFive",
        "B654_30x5": "SixHundredFiftyFourThirtyByFive", "CV_k10": "CvTen", "CV_k20": "CvTwenty", "LOCO": "Loco"}
MAE_FIELDS = (("MAE_S", "MaeS"), ("MAE_D", "MaeD"), ("MAE_P", "MaeP"), ("MAE_RF", "MaeRf"), ("MAE_B0", "MaeBZero"))


class Spec:
    """Collects (macro name, record file, pointer, format) rows."""

    def __init__(self, words: Callable[[int], str]):
        self.rows: list[tuple[str, str, tuple, str]] = []
        self.words = words

    def add(self, name: str, rel: str, path: tuple, f: str = "num") -> None:
        self.rows.append(("num" + name, rel, path, f))

    def ci(self, name: str, rel: str, path: tuple, key: str = "ci95") -> None:
        """Point at path + ('mean',) or a given leaf, interval at path + (key, 0 / 1)."""
        self.add(name + "Lo", rel, path + (key, 0))
        self.add(name + "Hi", rel, path + (key, 1))

    def b(self, x: int | str) -> str:
        return self.words(int(x))


def c1_table(s: Spec, prefix: str, rel: str, rows_present: dict) -> None:
    for key, tag in ROWS.items():
        if key not in rows_present:
            continue
        tag = tag or s.b(key[1:])
        row = rows_present[key]
        p = ("table", "rows", key)
        for k, f in MAE_FIELDS:
            if row.get(k):
                s.add(f"{prefix}{tag}{f}", rel, p + (k, "mean"))
                s.ci(f"{prefix}{tag}{f}", rel, p + (k,))
        a = p + ("A",)
        s.add(f"{prefix}{tag}A", rel, a + ("A",))
        s.ci(f"{prefix}{tag}A", rel, a)
        s.add(f"{prefix}{tag}AUpper", rel, a + ("upper_one_sided_95",))
        s.add(f"{prefix}{tag}AInside", rel, a + ("two_sided_within_pm_delta",), "word")
        s.add(f"{prefix}{tag}AUpperBelow", rel, a + ("upper_below_delta",), "word")
        s.add(f"{prefix}{tag}AExcludesZero", rel, a + ("ci95_excludes_zero",), "word")
        s.add(f"{prefix}{tag}Hosts", rel, p + ("x_training_hosts",), "hosts")


def spec(root: Path, words: Callable[[int], str]) -> Spec:
    s = Spec(words)
    load = lambda rel: json.loads((root / rel).read_text())["payload"]
    fin, abl = f"{C1}/final_network_summary.json", f"{C1}/default_init_ablation.json"

    # ---- C1 final-network table and default-initialisation ablation (Appendix D)
    c1_table(s, "Net", fin, load(fin)["table"]["rows"])
    c1_table(s, "Abl", abl, load(abl)["table"]["rows"])
    s.add("NetDelta", fin, ("table", "delta_eV"))
    # headline estimate at 654 training hosts: the 30 resamples x 5 seeds design (author decision, W2a)
    h = ("table", "rows", "B654_30x5")
    s.add("NetHeadlineA", fin, h + ("A", "A"))
    s.ci("NetHeadlineA", fin, h + ("A",))
    s.add("NetHeadlineAUpper", fin, h + ("A", "upper_one_sided_95"))
    s.add("NetHeadlineHosts", fin, h + ("x_training_hosts",), "hosts")
    for k in ("CV_k10", "CV_k20"):
        tag = ROWS[k]
        s.add(f"Net{tag}AFoldSd", fin, ("table", "rows", k, "A_fold_sd"))
        s.add(f"Abl{tag}AFoldSd", abl, ("table", "rows", k, "A_fold_sd"))
    # within-host spread of the predictions relative to the targets (site resolution)
    for b in BUDGETS:
        for m in ("S", "D", "P"):
            s.add(f"NetSpreadRatio{m}{s.b(b)}", fin,
                  ("table", "within_host_prediction_spread", m, str(b), "ratio_ensemble_to_target"))
        for m in ("S", "D"):
            s.add(f"AblSpreadRatio{m}{s.b(b)}", abl,
                  ("site_resolution", m, "v1", str(b), "ratio_ensemble_to_target"))
    s.add("NetSpreadTargetSd", fin, ("table", "within_host_prediction_spread", "S", "654", "target_eV"))
    # Kiyohara split: default initialisation only (Appendix D)
    c0 = "results/c0_official.json"
    s.add("AblKiyoharaMaeS", c0, ("S", "ensemble", "mae", "point"))
    s.ci("AblKiyoharaMaeS", c0, ("S", "ensemble", "mae"), "ci")
    s.add("NetPublishedMae", c0, ("comparison_eV", "kiyohara_published"), "trim")

    # ---- set values and counts printed in the text (R4)
    s.add("NetTolerance", "configs/config.yaml", ("stats", "delta_eV"), "trim")
    s.add("NetReleaseOxides", "results/structure_audit.json", ("polymorph", "release_hosts"), "int")
    for cls, tag in (("host_electronic", "Host"), ("site_electronic", "Site")):
        s.add(f"NetDescriptors{tag}", "results/staging_v2.json",
              ("p1_descriptors", "654", "by_class", cls, "n_descriptors"), "int")

    # ---- reproduction of the published structure-only error (formula-grouped split, 654 hosts)
    c2 = "results/c1c2_v2.json"
    s.add("NetReproMaeS", c2, ("mae", "654", "S", "mae", "mean"))
    s.ci("NetReproMaeS", c2, ("mae", "654", "S", "mae"), "ci")

    # ---- leave one family out
    lf = f"{C1}/loco_family.json"
    fams = load(lf)["v2"]["families_by_contribution"]
    i = next(k for k, x in enumerate(fams) if x["family"] == "1-14")
    fam = ("v2", "families_by_contribution", i)
    s.add("NetLocoUpperMinusDelta", lf, ("v2", "pooled", "upper_minus_delta"))
    s.add("NetLocoAlkaliGroupFourteenHosts", lf, fam + ("n_hosts",), "int")
    s.add("NetLocoAlkaliGroupFourteenSites", lf, fam + ("n_sites",), "int")
    s.add("NetLocoAlkaliGroupFourteenAFamily", lf, fam + ("A_family",))
    s.add("NetLocoAlkaliGroupFourteenContribution", lf, fam + ("contribution_to_pooled_A",))
    s.add("NetLocoUpperWithoutAlkaliGroupFourteen", lf, fam + ("pooled_without_this_family", "upper_one_sided_95"))
    s.add("NetLocoAWithoutAlkaliGroupFourteen", lf, fam + ("pooled_without_this_family", "A"))
    s.add("NetLocoNFamilies", lf, ("n_families",), "int")
    s.add("AblLocoAlkaliGroupFourteenContribution", lf,
          ("v1", "families_by_contribution",
           next(k for k, x in enumerate(load(lf)["v1"]["families_by_contribution"]) if x["family"] == "1-14"),
           "contribution_to_pooled_A"))

    # ---- within host
    s.add("NetWithinA", c2, ("A_within_host", "654", "A"))
    s.ci("NetWithinA", c2, ("A_within_host", "654"))
    s.add("NetWithinAUpper", c2, ("A_within_host", "654", "upper_one_sided_95"))
    s.add("NetWithinNStar", c2, ("N_star_within_host", "N_star"), "int")
    s.add("NetNStar", c2, ("N_star", "N_star"), "int")
    wh = "results/within_host_breakdown.json"
    groups = load(wh)["groups"]
    g = ("groups", next(k for k, x in enumerate(groups) if x["variable"] == "pooled"))
    for m in ("S", "D"):
        for k, f in (("within_host_mae", "WithinMae"), ("mae", "PooledMae")):
            s.add(f"Net{f}{m}", wh, g + ("v2", m, k, "point"))
            s.ci(f"Net{f}{m}", wh, g + ("v2", m, k))
    s.add("NetWithinZeroSkill", wh, g + ("v2", "S", "zero_skill_mae", "point"))
    s.ci("NetWithinZeroSkill", wh, g + ("v2", "S", "zero_skill_mae"))
    s.add("NetWithinSMinusD", wh, g + ("differences", "S_minus_D_v2", "within_host_mae", "point"))
    s.ci("NetWithinSMinusD", wh, g + ("differences", "S_minus_D_v2", "within_host_mae"))
    s.add("NetWithinHosts", wh, g + ("n_hosts_by_metric", "within_host_mae"), "int")
    s.add("NetWithinSites", wh, g + ("n_sites_within",), "int")
    s.add("NetWithinSpearmanSMinusD", wh, ("spearman", "differences", "S_minus_D_v2", "mean"))
    s.ci("NetWithinSpearmanSMinusD", wh, ("spearman", "differences", "S_minus_D_v2"))
    s.add("NetWithinSpearmanHosts", wh, ("spearman", "differences", "S_minus_D_v2", "n_hosts"), "int")
    for m in ("S", "D"):
        s.add(f"NetWithinSpearman{m}", wh, ("spearman", "v2", m, "mean"))
        s.ci(f"NetWithinSpearman{m}", wh, ("spearman", "v2", m))

    # ---- staging
    st = "results/staging_v2.json"
    s.add("NetStagingDeltaP", st, ("delta_P_eV",))
    for b in BUDGETS:
        p = ("budgets", str(b))
        s.add(f"NetStagingPMinusS{s.b(b)}", st, p + ("P_minus_S", "mean"))
        s.ci(f"NetStagingPMinusS{s.b(b)}", st, p + ("P_minus_S",))
        s.add(f"NetStagingPMinusS{s.b(b)}Upper", st, p + ("P_minus_S", "upper_one_sided_95"))
        s.add(f"NetStagingPMinusS{s.b(b)}Outcome", st, p + ("P_minus_S", "outcome"), "text")
        s.add(f"NetStagingPMinusS{s.b(b)}NonInferior", st, p + ("P_minus_S", "noninferior"), "word")
        s.add(f"NetStagingDMinusP{s.b(b)}", st, p + ("D_minus_P", "mean"))
        s.ci(f"NetStagingDMinusP{s.b(b)}", st, p + ("D_minus_P",))

    # ---- geometry (the collaborator's relaxations: 809 relaxed, 802 converged and evaluated)
    gd, me = "results/geometry_descriptive.json", "results/mlip_eval_v2.json"
    s.add("NetGeomRelaxedHosts", gd, ("cross_check_809", "n_his_relaxed"), "int")
    s.add("NetGeomEvaluatedHosts", me, ("n_hosts_mlip",), "int")
    s.add("NetGeomMaxAbsDeltaMae", gd, ("cross_check_809", "his_max_abs_dmae", "value_eV"), "dp4")
    for m in ("S", "D", "P"):
        for b in (200, 654):
            for cond, tag in (("mlip", "Relaxed"), ("rescaled", "Rescaled")):
                p = ("dMAE", f"{m}|{b}", cond)
                name = f"NetGeomDeltaMae{m}{s.b(b)}{tag}"
                s.add(name, me, p + ("mean",), "dp4")
                s.add(name + "Lo", me, p + ("ci95", 0), "dp4")
                s.add(name + "Hi", me, p + ("ci95", 1), "dp4")
    for k, tag in (("internal_rmsd_A", "InternalRmsd"), ("isotropic_strain", "IsotropicStrain"),
                   ("deviatoric_strain", "DeviatoricStrain")):
        s.add(f"NetGeom{tag}Median", me, ("geometry", k, "median"))

    # ---- probe (final network record)
    pr = "results/probe_descriptive.json"
    s.add("NetProbeHolds", pr, ("s_v2", "C4_holds_under_A4_rule"), "word")
    for cls, tag in (("host", "Host"), ("site", "Site"), ("all", "All")):
        p = ("s_v2", cls, "rule")
        s.add(f"NetProbe{tag}TrendRho", pr, p + ("trend", "rho"))
        s.ci(f"NetProbe{tag}TrendRho", pr, p + ("trend",))
        s.add(f"NetProbe{tag}TrendHolds", pr, p + ("trend", "holds"), "word")
        s.add(f"NetProbe{tag}ExceedsControls", pr, p + ("exceeds_both_controls_all_budgets",), "word")
        for b in BUDGETS:
            s.add(f"NetProbe{tag}Rsq{s.b(b)}", pr, ("s_v2", cls, "curves", "trained", str(b), "mean"))
        for b in (200, 400, 654):
            for ctl, ct in (("init0", "Untrained"), ("shuffled", "Shuffled")):
                q = p + ("controls", f"{b}|{ctl}")
                s.add(f"NetProbe{tag}Minus{ct}{s.b(b)}", pr, q + ("mean",))
                s.ci(f"NetProbe{tag}Minus{ct}{s.b(b)}", pr, q)
                s.add(f"NetProbe{tag}Exceeds{ct}{s.b(b)}", pr, q + ("exceeds",), "word")

    # ---- W2 diagnostics
    sc = f"{W2}/w2_screening_sites.json"
    s.add("NetScreenMae", sc, ("summary", "mae_eV"))
    s.ci("NetScreenMae", sc, ("summary",), "mae_ci95")
    for k, f, fm in (("bias_eV", "Bias", "num"), ("max_abs_err_eV", "MaxAbsErr", "num"), ("n_sites", "Sites", "int"),
                     ("n_hosts", "Hosts", "int"), ("n_over_prediction", "Over", "int"),
                     ("n_under_prediction", "Under", "int"), ("budget", "Budget", "int")):
        s.add(f"NetScreen{f}", sc, ("summary", k), fm)
    for i, row in enumerate(load(sc)["sites"]):
        tag = "".join(camel_formula(row["oxide"], words)) + camel_formula(row["site"], words)
        for k, f, fm in (("dft_eV", "Dft", "num"), ("prediction_eV", "Pred", "num"), ("error_eV", "Err", "num"),
                         ("abs_error_eV", "AbsErr", "num"), ("first_shell_cations", "Cations", "int"),
                         ("n_resamples", "N", "int")):
            s.add(f"NetScreen{tag}{f}", sc, ("sites", i, k), fm)
    sm = "figures/main/data/screening_demo.json"
    s.add("NetScreenSpearman", sm, ("summary", "v2", "spearman_across_sites"))
    s.add("NetScreenPairs", sm, ("summary", "v2", "within_host_pairs"), "int")
    s.add("NetScreenPairsConcordant", sm, ("summary", "v2", "within_host_pairs_concordant"), "int")

    cr = f"{W2}/w2_forest_crossover.json"
    for m in ("S", "D"):
        s.add(f"NetCross{m}Budget", cr, (m, "smallest_budget_below_with_95_interval"), "int")
        s.add(f"NetCross{m}PointBudget", cr, (m, "smallest_budget_point_below"), "int")
        for b in BUDGETS:
            p = (m, str(b))
            s.add(f"NetCross{m}MinusRf{s.b(b)}", cr, p + ("difference",))
            s.ci(f"NetCross{m}MinusRf{s.b(b)}", cr, p)
            s.add(f"NetCross{m}MinusRf{s.b(b)}Below", cr, p + ("below_with_95_interval",), "word")

    bs = f"{W2}/w2_bound_spread.json"
    for key in ("200", "400", "654", "400_30x5", "654_30x5"):
        b, _, des = key.partition("_")
        tag = s.b(b) + ("ThirtyByFive" if des else "")
        p = ("budgets", key)
        s.add(f"NetSpread{tag}SdOverResamples", bs, p + ("sd_over_resamples",))
        s.add(f"NetSpread{tag}MinResampleA", bs, p + ("min_resample_A",))
        s.add(f"NetSpread{tag}MaxResampleA", bs, p + ("max_resample_A",))
        s.add(f"NetSpread{tag}NAboveDelta", bs, p + ("n_resamples_A_above_delta",), "int")
        s.add(f"NetSpread{tag}NBelowZero", bs, p + ("n_resamples_A_below_0",), "int")
        if not des:
            s.add(f"NetSpread{tag}BootSd", bs, p + ("boot_sd",))
            s.add(f"NetSpread{tag}SingleRunASd", bs, p + ("single_run_A", "sd_over_30_runs"))

    tl = f"{W2}/w2_training_limit.json"
    s.add("NetCapMaxEpochs", tl, ("max_epochs", 0), "int")
    for b in BUDGETS:
        for m in ("S", "D", "P1"):
            s.add(f"NetCap{m.replace('1', 'One')}{s.b(b)}", tl, ("counts_sweep_10x3", str(b), m, "n_capped"), "int")
        s.add(f"NetCapP{s.b(b)}", tl, ("counts_sweep_10x3", str(b), "P", "n_capped_component"), "int")
        s.add(f"NetCapRuns{s.b(b)}", tl, ("counts_sweep_10x3", str(b), "S", "n_runs"), "int")
    for des, tag in (("precision_30x5", "ThirtyByFive"), ("sweep_10x3", "Sweep")):
        p = ("at_654", des)
        s.add(f"NetCap{tag}ACellAll", tl, p + ("mean_A_cell_all",))
        s.add(f"NetCap{tag}ACellUncapped", tl, p + ("mean_A_cell_without_capped_cells",))
        s.add(f"NetCap{tag}EffectOnA", tl, p + ("effect_of_capped_cells_on_mean_A_cell",), "dp4")
        s.add(f"NetCap{tag}CappedMinusUncappedMaeS", tl, p + ("capped_minus_uncapped_mae_S",))
        for grp, gt in (("S_capped_D_uncapped", "SCapped"), ("S_uncapped_D_capped", "DCapped"),
                        ("both_capped", "BothCapped"), ("neither_capped", "Neither")):
            s.add(f"NetCap{tag}{gt}Cells", tl, p + ("groups", grp, "n_cells"), "int")
    s.add("NetCapEnsembleAAll", tl, ("at_654", "ensemble_A_point_30x5", "all_runs"))
    s.add("NetCapEnsembleACappedRemoved", tl, ("at_654", "ensemble_A_point_30x5", "capped_runs_removed"))

    ds = f"{W2}/w2_descriptor_small_budget.json"
    for b in (25, 50):
        p = ("budgets", str(b))
        t = s.b(b)
        s.add(f"NetDsmall{t}NOutlying", ds, p + ("n_outlying",), "int")
        s.add(f"NetDsmall{t}Fence", ds, p + ("tukey_fence_eV",))
        for k, f in (("median", "Median"), ("trimmed_mean_10pc", "TrimmedMean"), ("mean", "Mean"), ("max", "Max")):
            s.add(f"NetDsmall{t}RunMae{f}", ds, p + ("D_run_mae", k))
        s.add(f"NetDsmall{t}ExtremeSites", ds, p + ("n_extreme_sites_total",), "int")
        s.add(f"NetDsmall{t}RunsWithExtreme", ds, p + ("n_runs_with_extreme_sites",), "int")
        s.add(f"NetDsmall{t}ExtremeShare", ds, p + ("share_of_abs_error_from_extreme_sites",))
        s.add(f"NetDsmall{t}NonfiniteRuns", ds, p + ("n_runs_with_nonfinite",), "int")
        for k, f in (("A_all_runs", "AAll"), ("A_outlying_runs_removed", "AClean")):
            s.add(f"NetDsmall{t}{f}", ds, p + (k, "A"))
            s.ci(f"NetDsmall{t}{f}", ds, p + (k,))
            s.add(f"NetDsmall{t}{f}Upper", ds, p + (k, "upper_one_sided_95"))
            s.add(f"NetDsmall{t}{f}MaeD", ds, p + (k, "MAE_D", "mean"))
    return s


# Introduction, paragraph 2: how much an error of 0.3 eV in E_f changes exp(-E_f / k_B T) at 1000 K
ILLUSTRATION_T_K, ILLUSTRATION_DE_EV = 1000, 0.3


def illustration(fmt: Callable) -> list[tuple[str, str, str, str]]:
    from scipy.constants import physical_constants
    kb = physical_constants["Boltzmann constant in eV/K"][0]
    kt = kb * ILLUSTRATION_T_K
    factor = math.exp(ILLUSTRATION_DE_EV / kt)
    one_sf = round(factor, -math.floor(math.log10(factor)))
    src = f"exp(dE / k_B T), k_B = {kb!r} eV/K (scipy.constants, CODATA), T = {ILLUSTRATION_T_K} K, dE = "
    src += f"{ILLUSTRATION_DE_EV} eV"
    return [("numNetIllusTemperature", fmt(ILLUSTRATION_T_K), repr(ILLUSTRATION_T_K), src + " (input T)"),
            ("numNetIllusDeltaE", "\\ensuremath{" + f"{ILLUSTRATION_DE_EV:g}" + "}", repr(ILLUSTRATION_DE_EV),
             src + " (input dE)"),
            ("numNetIllusKT", fmt(kt), repr(kt), src + " (k_B T, eV)"),
            ("numNetIllusFactor", fmt(int(one_sf)), repr(factor), src + " (factor, one significant figure)")]


def camel_formula(token: str, words: Callable[[int], str]) -> str:
    """Al2O3 -> AlTwoOThree, O1 -> OOne (digits spelled; macro names hold letters only)."""
    return "".join(words(int(p)) if p.isdigit() else p for p in re.findall(r"[A-Za-z]+|\d+", token))


def net_macros(root: Path, fmt: Callable, words: Callable[[int], str]) -> list[tuple[str, str, str, str]]:
    """(name, LaTeX value, raw value, source pointer) for every curated macro; raises on a missing pointer."""
    out, seen = [], set()
    cache: dict[str, dict] = {}
    for name, rel, path, f in spec(root, words).rows:
        if name in seen:
            raise ValueError(f"duplicate curated macro \\{name}")
        seen.add(name)
        if rel not in cache:
            text = (root / rel).read_text()
            cache[rel] = yaml.safe_load(text) if rel.endswith(".yaml") else json.loads(text)["payload"]
        node = cache[rel]
        try:
            for k in path:
                node = node[k]
        except (KeyError, IndexError, TypeError) as e:
            raise KeyError(f"\\{name}: {rel}#/payload/{'/'.join(map(str, path))} not found") from e
        src = f"{rel}#/{'' if rel.endswith('.yaml') else 'payload/'}" + "/".join(map(str, path))
        if f == "word":
            if not isinstance(node, bool):
                raise TypeError(f"\\{name}: {src} is not a boolean")
            latex = "yes" if node else "no"
        elif f == "text":
            if not isinstance(node, str) or re.search(r"[\\{}$%#&_^~]", node):
                raise TypeError(f"\\{name}: {src} is not a plain string")
            latex = node
        elif f in ("int", "hosts"):
            if f == "int" and float(node) != int(node):
                raise TypeError(f"\\{name}: {src} is not an integer")
            latex = fmt(round(node))
            src += " (nearest integer)" if f == "hosts" else ""
        elif f == "trim":
            txt = f"{abs(node):.3f}".rstrip("0").rstrip(".")
            latex = f"\\ensuremath{{{'-' if node < 0 else ''}{txt}}}"
            src += " (trailing zeros dropped)"
        elif f == "dp4":
            txt = f"{abs(node):.4f}"
            latex = f"\\ensuremath{{{'-' if node < 0 and txt != '0.0000' else ''}{txt}}}"
            src += " (4 decimals)"
        else:
            latex = fmt(node)
        out.append((name, latex, repr(node), src))
    for row in illustration(fmt):
        if row[0] in seen:
            raise ValueError(f"duplicate curated macro \\{row[0]}")
        out.append(row)
    return out

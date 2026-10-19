# Pending edits after the main-text rewrite (R3)

Session R3, 2026-10-17. Edits that the rewrite of the main text (Abstract to Conclusions) leaves for later sessions,
each with the place it affects and what has to happen. "The network" is the He-initialised, validation-tuned network
(repository name v2).

## 1. Staging conclusion, pending an extended-cap check

The descriptor predictor P1 reaches the training-length limit of 200 epochs in 2, 10 and 20 of 30 sweep runs at 200,
400 and 654 training hosts (`results/derived_w2/w2_training_limit.json`). The staging conclusion is written as it
stands and must be revisited once P1 has been rerun with a longer limit:

- Abstract, sentence 8: "Predicting them from structure never beats structure alone" (author text, kept verbatim).
- Results 3.4 (`sec:staging`), first paragraph: "P is never better than S", the outcomes per training size and
  `MAE_P - MAE_S` at 654 hosts; second paragraph: the epoch-limit counts, with a pointer to Appendix F.
- Discussion 4.1, last paragraph (staging cost carried by the site-level charges).
- Conclusions, first paragraph: "predicting them from structure never beats learning the energy from structure
  directly".
- Table 1, row `MAE_P - MAE_S`, B = 654.

If longer training lowers the error of P enough to change an outcome, every item above changes together; if not,
only the epoch-limit sentence of Results 3.4 gains the result of the check.

R4 (2026-10-17) found that P1 was not re-tuned under He initialisation: S and D received 30 trials at each of three
anchors under He initialisation, P1 none; it carries its default-initialisation values (`docs/r4_verification.md`
(d)). Every staging statement now reads "at the tuning and training length used", and the Methods say what was and was
not re-tuned. Each of these edits is pending the extended check (P1 re-tuned under He initialisation and trained with
a longer limit); if the check changes an outcome, all of them change together, and if it does not, the qualifier can be
replaced by the result of the check:

- Abstract s8: "At the tuning and training length used, predicting them from structure never beats structure alone".
- Results 3.4 p1: "At the tuning and training length used, P is never better than S (Figure 4); P1 kept the settings
  tuned under the default initialisation (Section 2.3)."
- Discussion 4.1 last paragraph: "At the tuning and training length used, staging costs accuracy", the second possible
  source (P1's tuning and training length) and the two checks.
- Conclusions s2: "and, at the tuning and training length used, predicting them from structure never beats ...".
- Table 1 row: "MAE_P - MAE_S, B = 654, at the tuning and training length used".
- Methods 2.3: the tuning paragraph ("Under the default initialisation every model, S, D and P1, received ...") and
  the initialisation paragraph ("P1 was not re-tuned: ... so the staged model P received no tuning trials under the
  initialisation used for S and D").
- Introduction p6: "the same tuning budget for S and D" (was "for every model").

## 2. Appendix stubs

`paper/sections/appendix_stub.tex` holds only the titles and `\label` targets of Appendices A to K (`app:data`,
`app:network`, `app:splits`, `app:ablation`, `app:within`, `app:sens`, `app:geometry`, `app:probe`,
`app:screening`, `app:stats`, `app:code`), so that every pointer of the main text resolves. The merge of
`paper/si/` into the appendices (the later SI-to-appendix session) replaces the stubs with content, in the plan of
`docs/story_spec.md` (iv). Material the main text now points to and the appendices must carry:

- Appendix A: the filter cascade (D1 to D3) with its table (`paper/tables/filter_cascade.tex`, removed from Methods
  2.1 in R3) and Figure A1; the descriptor taxonomy.
- Appendix B: the readout (Figure B1), the search space, the tuned values and validation errors of the network, the
  rule that assigns each training size to a tuning set, the choice of the descriptor injection route by validation
  error, and the tuning-overlap note (tuning on one resample; Kiyohara overlap). The former Methods tuning table
  (`tab:tuning`) was removed from the main text in R3.
- Appendix C: split schematic (Figure C1), resample construction, CV folds, cation families, the Kiyohara split.
- Appendix D: Table D1 from `docs/c1_ablation_table.md` (`\numAbl...` macros), including the plain statement that the
  network's structure-only error at 654 training hosts, 0.296 [0.276, 0.317] eV (`\numNetSixHundredFiftyFourMaeS`,
  `...Lo`, `...Hi`), is above the default-initialisation value, 0.273 [0.252, 0.300] eV
  (`\numAblSixHundredFiftyFourMaeS`), with overlapping intervals; the Kiyohara-split value of default initialisation,
  0.283 [0.237, 0.329] eV (`\numAblKiyoharaMaeS...`), appears only here; and the spread ratios of both initialisations.
- Appendix E: the within-host breakdown (Figure E1), its estimator (site-averaged, zero skill 0.184 eV) and the
  multiplicity statement, to which Results 3.3 points.
- Appendix F: the training-length counts of S, D and P1 (`\numNetCap...`), the effect of capped runs on A
  (`docs/w2_diagnostics.md` (b)), the untuned CGCNN check, and the high-moment exclusion once the rerun on the network
  exists (Figure F1 is not built).
- Appendix G: the relaxation and mapping protocol (809 relaxed hosts, 802 converged and evaluated), the strain
  components, and the table of `Delta MAE` for S, D and P at 200 and 654 hosts on relaxed and rescaled cells
  (`\numNetGeom...`).
- Appendix H: the probe on the network (Figure H1), its rule, controls and outcome.
- Appendix I: the full screened-site table (structure type, space group, mean first-shell distance, band gap, host
  formation energy), the site-pair table and the SnO2 render (Figure I1).
- Appendix J: the hierarchical bootstrap, the paired host-cluster bootstrap, the four-outcome staging rule and the
  multiplicity rule.
- Appendix K: repository, run identifiers, records, deposit and software versions (`\vermatgl` and the other version
  constants of `paper/main.tex`); the Data Availability Statement points here.

Until the merge, `paper/si/` builds on its own (`make -C paper/si PYTHON=python`) and is untouched.

**A4 update (2026-10-17).** Done: the SI is merged into Appendices A to K (`paper/sections/appendix_*.tex`, input by
`paper/main.tex`; `appendix_stub.tex` removed), with the labels above unchanged; `paper/si/` is no longer built or
referenced. Map and deletions in `docs/a4_merge_report.md`. Left open from this list:

- Appendix F, high-moment exclusion on the network: **TO BE ADDED.** The rerun of S and D without the entries whose
  defect moment exceeds 0.5 muB has no record on the network (`results/sens_high_moment_v1.json` holds the default
  initialisation only). Appendix F.2 states the exclusion and the network-free forest check
  (`results/sens_high_moment_rf.json`); once the network rerun exists, add its change in A and its upper bound there
  (with a claims row) and build Figure F1.
- Appendix F, Figure F1: not built (`docs/figure_numbering.md`).
- `paper/tables/filter_cascade.tex` ("Final universe") and `paper/tables/freeze_table.tex` (registration labels) are
  no longer input by `paper/main.tex` (Table A1 is written with macros in `appendix_a_data.tex`); delete them, or
  their generators, in a session whose scope includes `paper/tables/` and `analysis/`.

## 3. Supplementary statement

The MDPI `\supplementary{...}` statement listed Sections S1-S9 and Tables S1-S12 with registration labels; R3 removed
it from `paper/main.tex`, because the SI becomes Appendices A-K of one PDF. If a separate SI file remains at
submission, the statement has to be rewritten without labels.

**A4 update.** No separate SI file remains, so no Supplementary Materials statement is needed; `paper/main.tex`
has none, and every other back-matter statement is unchanged.

## 4. Bibliography (`paper/refs.bib`, not edited)

No new reference was needed: every key cited in the rewritten text was already in `paper/refs.bib`
(`Wexler2021factors` is now cited in the Introduction, `Shrout1979intraclass` in Results 3.1). Nothing to add.

## 5. Figures

- The main text now includes the new figure files of `docs/figure_numbering.md` (`figure1_models` to
  `figure5_screening`). The former files (`fig1_overview`, `fig2_learning_curves`, `fig3_advantage`, `fig4_staging`,
  `fig5_geometry`, `fig6_within_host`, `fig7_screening`) are no longer used by `paper/main.tex`; the SI still uses its
  own former files. Deleting the former main-text files and scripts belongs to a figure-scope session.
- The moved schematics now read "final 818-host dataset" (Figure A1) and "leave one family out" (Figure C1 (d)),
  fixed by W2c (`docs/w2c_figure_checks.md`), which merged during R3.

## 5b. Appendices and SI, from R4 (for the appendix session; R4 did not touch them)

**A4 status (2026-10-17).** Applied in the appendices: no appendix prints the tolerance as a number (it appears as
$\delta$), and $\delta_\mathrm{P}$ in Appendix J uses `\numNetStagingDeltaP`; Appendix D quotes the published error
through `\numNetPublishedMae`; Appendix B states that P1 was not re-tuned under He initialisation (S and D 30 trials per
tuning size under He, P1 30 under the default initialisation only), and Table B2 gives P1's best validation errors;
no appendix names the leave-one-family-out family (Appendix C points to Section 3.2); Appendix H gives the probe means
at 654 hosts, trained 0.555 and untrained 0.557. The title item below is outside the A4 scope (main.tex back matter
and appendix inputs only) and stays open.

- Tolerance: the main text prints delta = 0.05 eV through the curated macro `\numNetTolerance` (and delta_P through
  `\numNetStagingDeltaP`, now also 0.05). Appendix text and tables that print the tolerance should use
  `\numNetTolerance`, not `\numCfgStatsDeltaEV` (0.050).
- Published structure-only error: `\numNetPublishedMae` now prints 0.29, the precision of the source; an appendix that
  quotes the Kiyohara value should use it.
- Appendix B must say that P1 was not re-tuned under He initialisation, with the trial counts and best validation
  errors of `docs/r4_verification.md` (d): S and D 30 trials per anchor under He, and P1 30 per anchor under the
  default initialisation only.
- The family `1-14` of the leave-one-family-out folds is "the alkali tetrelates (silicates, germanates, stannates and
  plumbates of the alkali metals)", 48 hosts including 16 stannates and Li and Na compounds; any appendix family table
  should use that name.
- Appendix H: Discussion 4.1 now cites the probe means at 654 hosts, untrained encoder 0.557 against trained S 0.555
  (`\numProbeDescriptiveSVTwoAllCurvesInitZeroSixHundredFiftyFourMean`, `\numNetProbeAllRsqSixHundredFiftyFour`).

## 6. Wording decisions to confirm

- Conclusions, practical rule: the brief asked for "below about 150 oxides use the forest". No record holds 150; the
  measured crossover lies between 100 training hosts (forest as accurate or better) and 200 (the descriptor network
  below the forest with a 95% interval). The text therefore states the rule at the measured sizes ("with 100 training
  oxides or fewer ... between 100 and 200 the descriptor network overtakes it ... from 654 on, the structure-only
  network"). If a rounded "about 150" is wanted, it needs a text constant in `paper/main.tex` with its justification.
- Title: typed as "0.05~eV" in `paper/main.tex`, as the brief gives it; since R4 the text prints the same value through
  `\numNetTolerance`, so the title may switch to the macro when main.tex is next edited.
- Abstract: resolved in R4. The tolerance prints "0.05 eV" (`\numNetTolerance`). The Abstract now has 199 words, after
  the descriptor set of D and the staging qualifier were added (`docs/r4_changes.md`).

## 7. Appendix F after N4 (session I1, 2026-10-19; no paper file edited)

The network rerun of the high-moment exclusion now exists: `results/derived_n4/high_moment_final_network.json`
(`docs/n4_highmoment.md`). The staging swap-in on the network exists too: `results/swapin/swapin_v2.json`
(`docs/n4_swapin.md`). Both replace the open items "Appendix F, high-moment exclusion on the network: TO BE ADDED"
and "Appendix F, Figure F1: not built" of section 2.

### 7a. Macros to add (`paper/tools/net_macros.py`, record `results/derived_n4/high_moment_final_network.json`)

Every macro below is one JSON pointer into `payload`. The names are proposals: the appendix session may rename them,
but the pointers are fixed.

| Proposed macro | Pointer | Value (eV) |
|---|---|---|
| `\numNetHighMomentCommonA` (+ `Lo`, `Hi`) | `final_network/primary_common_sites/A/mean` (`ci/0`, `ci/1`) | +0.016 [-0.007, +0.038] |
| `\numNetHighMomentExclA` (+ `Lo`, `Hi`) | `final_network/high_moment/A/mean` (`ci/0`, `ci/1`) | +0.027 [+0.001, +0.052] |
| `\numNetHighMomentExclAUpper` | `final_network/high_moment/A/upper_one_sided` | +0.049 (+0.0488) |
| `\numNetHighMomentChangeA` (+ `Lo`, `Hi`) | `final_network/change_high_moment_minus_primary/A/mean` (`ci/0`, `ci/1`) | +0.011 [-0.008, +0.029] |

### 7b. Appendix F, subsection "Entries with a High Defect Moment" (`paper/sections/appendix_f_sens.tex`)

Replace the paragraph, from "The hosts are classified as non-magnetic" to "a small part of every test set.", with:

```latex
The hosts are classified as non-magnetic in the release, but \numSensHighMomentRfNExcludedEntries{} neutral vacancy calculations of the dataset end with a defect magnetic moment above \numSensHighMomentVOneThresholdMuB{}~$\mu_\mathrm{B}$; all lie in La- or Ce-containing oxides, apart from one tungstate, where the electrons left by the vacancy can localise on a reducible cation. The check removes these entries from training and test and repeats the fit. For the network with \numCfgBudgetsMax{} training hosts (ten resamples, three seeds), compared on the same test sites, the removal moves $A$ from \numNetHighMomentCommonA{} [\numNetHighMomentCommonALo{}, \numNetHighMomentCommonAHi{}]~eV to \numNetHighMomentExclA{} [\numNetHighMomentExclALo{}, \numNetHighMomentExclAHi{}]~eV, a change of \numNetHighMomentChangeA{} [\numNetHighMomentChangeALo{}, \numNetHighMomentChangeAHi{}]~eV whose interval contains zero (Figure~\ref{fig:app_sens}a; \texttt{results/derived\_n4/high\_moment\_final\_network.json}). The one-sided upper bound on $A$ becomes \numNetHighMomentExclAUpper{}~eV, still below $\delta = \numNetTolerance{}$~eV, so the statement at \numCfgBudgetsMax{} training hosts holds without these entries; the margin narrows, and the two-sided interval no longer lies inside $\pm\delta$. The runs without the entries were trained on a different pool of GPUs from the learning-curve runs, so the change also contains hardware variation. For RF-Kumagai with \numSensHighMomentRfPoolSize{} training hosts the removal changes the site MAE by \numSensHighMomentRfDeltaTotalExcludedMinusBaselineMaeMean{} [\numSensHighMomentRfDeltaTotalExcludedMinusBaselineMaeCiLo{}, \numSensHighMomentRfDeltaTotalExcludedMinusBaselineMaeCiHi{}]~eV (\texttt{results/sens\_high\_moment\_rf.json}), because the entries make up a small part of every test set.
```

Also, in the file header comment, replace "No figure (Figure F1 is not built)." with "Figure F1
(fig:app_sens, a new label)." and add `results/derived_n4/high_moment_final_network.json` to the "Numbers:" list.

### 7c. Figure F1 (`fig:app_sens`), data source

Build F1 from the network records only. The former Figure S6 (`figures/si/fig_si_sensitivities.pdf`) used
`results/sens_high_moment_v1.json` (default initialisation) for its panel (a), and that source is replaced.

- Panel (a), A at 654 training hosts: `results/derived_n4/high_moment_final_network.json`. Use
  `payload.final_network.primary_full_sites.A`, `payload.final_network.primary_common_sites.A` and
  `payload.final_network.high_moment.A`, each with `mean`, `ci` and `upper_one_sided`. Use
  `payload.final_network.change_high_moment_minus_primary.A` for the paired change, `payload.delta_eV` for the
  dashed delta line and `payload.bootstrap` for the interval method. The full-site series equals row B654 of
  `results/derived_c1/final_network_summary.json` (checked in `payload.reproduction`). The capped-twin series of
  Figure S6 exists for the default initialisation only (`docs/c1_coverage.md`) and is not drawn.
- Panel (b), the second architecture: `results/sens_cgcnn.json`, `payload.table.megnet_v2` and `payload.table.cgcnn`
  (unchanged source).
- After building, update `docs/figure_numbering.md` (row "Figure F1, sensitivities: not built") and write the caption
  file under the 70-word limit of `scripts/check_captions.py`.

### 7d. Claims row to add (`docs/claims.yaml`, outside the I1 scope)

```yaml
  - id: SENS1-v2
    statement: "EXTENSION on the final network. Removing the 10 entries with |defect moment| > 0.5 muB from training and test sites (B = 654, 10 resamples x 3 seeds) changes A on the common test sites from +0.016 to +0.027 eV (paired change +0.011 eV, two-sided 95% interval [-0.008, +0.029]); the one-sided 95% upper bound on A stays below delta = 0.05 eV (+0.034 without, +0.049 with the exclusion), so the non-inferiority statement at 654 does not change; the two-sided interval with the exclusion, [+0.001, +0.052], is not inside +-delta."
    tested_by: "analysis/n4/high_moment_final.py (estimator steps of analysis/sensitivity_analysis.high_moment, unchanged); G1 hierarchical bootstrap with the G1 draws; reproduces results/sens_high_moment_v1.json and row B654 of results/derived_c1/final_network_summary.json to 1e-9"
    figure: "Figure F1, panel a (to be built)"
    falsifiable_how: "A one-sided upper bound on the high-moment A at or above delta would change the non-inferiority statement at 654 for the final network."
    status: measured
    result_ref: results/derived_n4/high_moment_final_network.json
```

### 7e. Staging swap-in (no paper text required)

The paper text does not mention the swap-in check. If the Methods or Results 3.4 (`sec:staging`) come to mention it, they should say
that, on the network, the staged model with the true descriptors reproduces D exactly in all 183 pairs
(`results/swapin/swapin_v2.json`). Because P1 and D standardise the descriptors identically, this is a plumbing check
of the staged pipeline and not evidence that staging could win.

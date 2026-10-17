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

## 6. Wording decisions to confirm

- Conclusions, practical rule: the brief asked for "below about 150 oxides use the forest". No record holds 150; the
  measured crossover lies between 100 training hosts (forest as accurate or better) and 200 (the descriptor network
  below the forest with a 95% interval). The text therefore states the rule at the measured sizes ("with 100 training
  oxides or fewer ... between 100 and 200 the descriptor network overtakes it ... from 654 on, the structure-only
  network"). If a rounded "about 150" is wanted, it needs a text constant in `paper/main.tex` with its justification.
- Title: typed as "0.05~eV" in `paper/main.tex`, as the brief gives it; the tolerance macro would print "0.050".
- Abstract: the tolerance macro prints "0.050 eV" where the author text reads "0.05 eV"; the word count (196) and
  every other word are identical.

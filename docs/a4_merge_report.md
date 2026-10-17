# A4: Supplementary Materials merged into Appendices A to K

Session A4, 2026-10-17. The Supplementary Materials (`paper/si/`, sections S1 to S9) are merged into lettered
Appendices A to K of `paper/main.tex`, in the plan of `docs/story_spec.md` (iv), so the paper is one PDF. `paper/si/`
stays in the repository unchanged; it is no longer built or referenced by the paper. Nothing was computed: every
number is a macro of `paper/generated/numbers.tex`, and every table uses the records of the final network (the
He-initialised, validation-tuned network; repository name v2), except Table D1, which sets the default
initialisation (v1) beside it.

## Where each SI section went

| Old SI item | New home | Kept | Deleted, and why |
|---|---|---|---|
| Front matter of `si.tex` (provenance paragraph) | none | none | the labels registered / post hoc / extension (rule 2 of `docs/prose_style.md`) |
| S1 Data, Table S1 cascade, Table S3 descriptor taxonomy | Appendix A, Tables A1-A2, Figure A1 | cascade text and counts, D1-D3, the three descriptor classes, the taxonomy (now one row per descriptor family, at the full page width) | the pointer to the article's Table 1 (the cascade table now lives only in Appendix A) |
| S2.1 Readout, Figure S1 | Appendix B.1, Figure B1 | the readout and the injection points | "the readout is the same for both networks (v1, v2)" (rule 1) |
| S2.2 Protocol, search space, tuned values (Tables S2, S4, S5) | Appendix B.2-B.4, Tables B1-B2 | protocol, epoch-limit rule, search space, tuned values and validation errors of the network (S, D; P1 settings) | Table S4 (tuned values of v1) and the v1 validation errors (rule 1); "frozen plan", "logged before tuning", "post hoc", "adopted after test-set diagnostics" (rule 2); the D-state versus D-late numbers move to Appendix D, because that choice was made under the default initialisation |
| S2.3 Cap on training length, Table S6 | Appendix F.1, Table F1 | counts of runs at the epoch limit for S, D, P1 and P per training size, the direction of the effect on A (`docs/w2_diagnostics.md` (b)) | the registered cap-sensitivity check and the 600-epoch twins (v1 only; rule 1); the v1 rows of Table S6; the capped-run counts of the cross-validation (v1 and v2 mixed in one table) |
| S2.4 Hardware | none | none | all of it (rule 3; Methods 2.3 keeps the one GPU sentence) |
| S3 Splits, Figure S2 cascade, Figure S3 splits | Appendix C, Figure C1 (cascade figure moved to Appendix A as Figure A1) | resample construction, coverage, the additional resamples, cross-validation, families, the published split | "registered budget", "extension", the provenance of the collaborator's family-fold runs, the freeze-notes pointer (rule 2) |
| S4 Within-host breakdown, Table S7, Figure S4 | Appendix E, Table E1, Figure E1 | estimator, zero skill, pooled values, d class, stability, band gap, Bader rank, multiplicity statement, now with S - D and its interval per group | the v1 columns of Table S7, the v1 penalty of the descriptors in d10 and shallow-donor-prone hosts, the comparison of the estimator with the registered one (v1 numbers; rule 1); "logged before any number was computed" (rule 2) |
| S5 Hardware variation, Figure S5, Tables S8-S9 | none | none | all of it (rule 3, `docs/story_spec.md` (iv)) |
| S6 Sensitivities, Figure S6 | Appendix F.2-F.3 | the high-moment exclusion as a definition with the network-free forest check; the untuned CGCNN against the network | the v1 high-moment result and the v1 capped twins (no network record; rule 1); Figure S6 (Figure F1 is not built); the final-network high-moment rerun is listed as TO BE ADDED in `docs/pending_edits.md` |
| S7 Latent probe, Figure S7 | Appendix H, Figure H1 | protocol, the two-condition rule, the controls and the outcome, now on the network's probe record | the v1 probe numbers and the v1 checkpoint sanity check (rule 1); "claim C4, registered", "under the registered rule ... reported here rather than in the article" (rule 2) |
| S8 Structures, Table S10, Figure S8 | Appendix I, Tables I1-I3, Figure I1 | first-shell geometry, renders, render settings; plus the full screened-site table and the site-pair table from the former Results (network column only) | the v1 prediction columns (rule 1); the SnO2 render now prints at 69 mm, its 600 ppi width (checklist item 24) |
| S9.1 Code release, Table S11 release tags | Appendix K.1, Table K1 (records) | repository, licence, run identifiers, records, number macros | the release-tag table and the tag names (rule 2; the tags stay in the repository and the deposit) |
| S9.2 Deposit | Appendix K.2 | unchanged in content | none |
| S9.3 Provenance labels, Table S12 | none | none | all of it (rule 2) |
| S9.4 Deviations | none | none | all of it (rule 2; the dated log stays in the repository) |
| `sisetup.sty` text constants | `paper/main.tex` (after `\appendix`) | `\dten`, `\shatwo`, `\recprecision` and table helpers | dates, commits, tag and GPU constants (rules 2 and 3) |
| former Methods `sec:statistics`, `sec:mlip`, `sec:methods-probe`, `sec:repro` (before R3) | Appendices J, G, H, K | bootstrap, N* rule, staging outcomes, multiplicity; relaxation and mapping protocol; probe protocol; software versions | v1/v2 analysis split, provenance labels (rules 1 and 2) |

## Vocabulary hits removed per old SI file

Counts of the greps of this session over the prose of each SI file (comments removed): registration vocabulary
(registered, pre-registered, post hoc, extension, gate, frozen/freeze, deviation(s), provenance, v1, v2, tag names,
claim identifiers) and GPU/hardware vocabulary. None of these words is carried into the appendices; the counts are
the hits removed.

| SI file | Registration | Hardware |
|---|---|---|
| `si.tex` | 8 | 1 |
| `sisetup.sty` | 9 | 23 |
| `sections/s1_data.tex` | 0 | 0 |
| `sections/s2_training.tex` | 39 | 15 |
| `sections/s3_splits.tex` | 15 | 0 |
| `sections/s4_withinhost.tex` | 23 | 0 |
| `sections/s5_hardware.tex` | 18 | 32 |
| `sections/s6_sensitivities.tex` | 19 | 0 |
| `sections/s7_probe.tex` | 16 | 0 |
| `sections/s8_structures.tex` | 0 | 0 |
| `sections/s9_reproducibility.tex` | 30 | 1 |
| `sections/tab_capped.tex` | 16 | 0 |
| `sections/tab_gpu_class.tex` | 30 | 29 |
| `sections/tab_n1.tex` | 0 | 4 |
| `sections/tab_withinhost.tex` | 3 | 0 |
| `sections/tab_first_shell.tex`, `tab_tuned_v1.tex`, `tab_tuned_v2.tex` | 0 | 0 |
| `tables/provenance_labels.tex` | 127 | 0 |
| `tables/release_tags.tex` | 22 | 0 |
| `tables/descriptor_taxonomy.tex` | 0 | 0 |
| **All** | **375** | **105** |

Forbidden words (the list of `docs/prose_style.md`) had no hit in the SI and have none in the appendices.

## Grep of the built paper (paper/ without paper/si)

Over `paper/main.tex` and `paper/sections/*.tex`, prose only: 0 forbidden words; 0 hardware words except the one
GPU sentence of Methods 2.3 that rule 3 keeps; registration greps match only "standard deviation" (Results 3.2,
Appendix D) and "mean absolute deviation" (Appendix E), statistical terms, and the record path
`results/c0_official.json` in Table K1. Record paths in Appendix K and in captions keep their file names (`..._v2.json`),
which the word-boundary grep does not count. Outside the manuscript sources, `paper/tables/freeze_table.tex` (494
registration and 8 hardware hits) and `paper/tables/filter_cascade.tex` ("Final universe") are no longer input by
`paper/main.tex`; they are outside the A4 scope and listed in `docs/pending_edits.md`. Code and READMEs under
`paper/tools/` name the repository keys v1/v2 and are not paper text.

## Cross-references

The appendix sections carry exactly the labels of the former stub (`app:data`, `app:network`, `app:splits`,
`app:ablation`, `app:within`, `app:sens`, `app:geometry`, `app:probe`, `app:screening`, `app:stats`, `app:code`).
Every `\ref` of the main-text sections resolves (0 undefined references in `paper/main.log`); no main-text reference
lacks a target. The main text cites no appendix figure or table by number. Figures are numbered per appendix (A1,
B1, C1, E1, H1, I1, as in `docs/figure_numbering.md`), and so are tables (A1-A2, B1-B2, D1, E1, F1, G1, I1-I3, K1).

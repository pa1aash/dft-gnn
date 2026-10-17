# Caveat ledger (S1)

Session S1, 2026-10-17. Every caveat, hedge, disclaimer and piece of registration vocabulary in the manuscript at
`origin/main` 21158d2, with file, line and verdict for the rewrite specified in `docs/story_spec.md`. Search terms:
bound, equivalence, post hoc, registered, caution, "does not", "do not", "did not", "should not be", "not
established", "weak evidence", "not directly comparable", "not fully held out", "hypothesis", "limitation",
"qualification", "caveat", "no ... exists", "was not run", "not measured", plus the registration labels. Line
numbers are source lines; Results, Discussion and Methods are one paragraph per line, so one line can carry
several caveats, listed separately.

Verdicts: **KEEP-ONCE** (the single home is named; every other occurrence points there or goes), **MERGE** (folded
into the named KEEP-ONCE item), **DELETE** (one-line reason). Homes use the new section numbers of
`docs/story_spec.md` (3.2 = learning curve, 3.3 = site resolution, 4.4 = scope; appendices A-K).

## 1. Registration vocabulary: counts per file

Comment lines (`%`) excluded. "registered" includes "originally registered" and excludes "pre-registered";
"extension" counts every use, including a few in the plain sense ("an extension of the registered protocol"); v1 and
v2 count the bare tokens only (macro names such as `\numCOneCTwoVTwo...` are not prose and are not counted). Every
hit in the paper text, captions, tables and appendices is removed under rule (b), except the Appendix D table and
the one Methods paragraph of rule (a), which name "default initialisation", never "v1".

| File | registered | pre-registered | post hoc | extension | v1 | v2 | frozen/freeze | gate | total |
|---|---|---|---|---|---|---|---|---|---|
| `paper/main.tex` | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 3 |
| `paper/sections/abstract.tex` | 2 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 3 |
| `paper/sections/introduction.tex` | 3 | 0 | 2 | 1 | 3 | 3 | 0 | 0 | 12 |
| `paper/sections/data.tex` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `paper/sections/methods.tex` | 23 | 0 | 6 | 8 | 31 | 26 | 2 | 0 | 96 |
| `paper/sections/results.tex` | 28 | 0 | 12 | 15 | 39 | 37 | 1 | 1 | 133 |
| `paper/sections/results_screening.tex` | 5 | 0 | 4 | 0 | 11 | 12 | 0 | 0 | 32 |
| `paper/sections/discussion.tex` | 1 | 0 | 1 | 1 | 16 | 14 | 0 | 0 | 33 |
| `paper/sections/conclusions.tex` | 3 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 4 |
| `paper/si/si.tex` | 3 | 0 | 0 | 1 | 2 | 1 | 0 | 0 | 7 |
| `paper/si/sections/s1_data.tex` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `paper/si/sections/s2_training.tex` | 9 | 0 | 3 | 3 | 10 | 11 | 1 | 0 | 37 |
| `paper/si/sections/s3_splits.tex` | 5 | 0 | 1 | 5 | 0 | 0 | 2 | 0 | 13 |
| `paper/si/sections/s4_withinhost.tex` | 6 | 0 | 3 | 3 | 4 | 5 | 0 | 0 | 21 |
| `paper/si/sections/s5_hardware.tex` | 7 | 0 | 1 | 5 | 1 | 3 | 0 | 0 | 17 |
| `paper/si/sections/s6_sensitivities.tex` | 5 | 0 | 3 | 4 | 3 | 4 | 0 | 0 | 19 |
| `paper/si/sections/s7_probe.tex` | 6 | 0 | 1 | 0 | 3 | 2 | 0 | 0 | 12 |
| `paper/si/sections/s8_structures.tex` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `paper/si/sections/s9_reproducibility.tex` | 6 | 0 | 3 | 1 | 2 | 5 | 5 | 0 | 22 |
| `paper/si/tables/provenance_labels.tex` | 4 | 11 | 18 | 15 | 22 | 38 | 1 | 0 | 109 |
| `paper/si/tables/release_tags.tex` | 1 | 0 | 0 | 0 | 11 | 5 | 4 | 0 | 21 |
| `paper/si/sections/tab_capped.tex` | 0 | 0 | 0 | 0 | 8 | 8 | 0 | 0 | 16 |
| `paper/si/sections/tab_gpu_class.tex` | 1 | 0 | 0 | 1 | 14 | 14 | 0 | 0 | 30 |
| `paper/si/sections/tab_withinhost.tex` | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 3 |
| **Total** | 120 | 11 | 60 | 63 | 182 | 190 | 16 | 1 | 643 |

`tab_tuned_v1.tex`, `tab_tuned_v2.tex`, `tab_n1.tex` and `s8_structures.tex` have 0 prose hits (their file names
carry v1/v2; file paths may keep them). Figure captions inside `paper/figures/` caption files and the figure legends
("v1"/"v2", "registered", "post hoc" keys) are outside this count and must be redrawn with the figures
(`docs/story_spec.md` (v)).

Figure 1 (`methods.tex:21`), Figures 2-7 captions (`results.tex:32, 40, 97, 115, 122`; `results_screening.tex:37`) and
Table 2 (`results.tex:50, 56`) carry the dashed/solid v1/v2 key and the R/PH/E label column: all DELETE (one network,
rule b).

## 2. Abstract, Introduction, Conclusions

| File:line | Caveat or label (abridged) | Verdict |
|---|---|---|
| abstract.tex:2 | "On the primary network, adopted post hoc after diagnostics of the originally registered one" | DELETE: rule (b); one network |
| abstract.tex:2 | "On both networks its one-sided upper bound lay below the tolerance at 654, 736 and 777 ... but not at 400" | KEEP-ONCE 400 limit, home Results 3.2; Abstract keeps a one-clause pointer; CV part PENDING C1 |
| abstract.tex:2 | "The result applies to deep, localised neutral oxygen vacancies in ordered hosts classified as non-magnetic in the release" | MERGE into domain statement (home Methods 2.1); Abstract keeps a short scope clause |
| abstract.tex:2 | "geometry ... changed the originally registered network's error" | DELETE: default-initialisation result; replace with the network's geometry check |
| introduction.tex:11 | "We claim no priority for the structure-only result"; "a precedent in a metal, not a benchmark for oxides" | MERGE into Discussion 4.3 (prior work), one sentence; defensive in the Introduction |
| introduction.tex:15 | "registered before any network was trained, for the originally registered network (v1) ... every v2 result is labelled post hoc ... registered for v1 and are post hoc on v2 ... extensions, and every result is labelled" | DELETE: rule (b); replaced by "the tolerance was fixed before the analysis" (home Methods 2.5) |
| introduction.tex:17 | Scope paragraph: neutral, ordered, non-magnetic, deep-vacancy domain; shallow donors outside every model | MERGE into Methods 2.1 domain statement; Introduction ends on the question, not the scope |
| conclusions.tex:5 | "This one-sided bound held on the primary network, whose results are post hoc, and on the originally registered network" | DELETE: rule (b) |
| conclusions.tex:5 | "It is a bound, not an equivalence" | DELETE: defensive refrain (rule e); the number with its interval says it |
| conclusions.tex:5 | "on the originally registered network the sign of their advantage reversed beyond 654" | DELETE: default-initialisation result |
| conclusions.tex:5 | "a linear probe gave no evidence that training encodes the descriptors" | DELETE from Conclusions: probe moves to Appendix H (rule g) |
| conclusions.tex:5 | "at a cost below δ in mean absolute error over held-out oxides, not a bound for any single oxide" | KEEP-ONCE, home Methods 2.5 (the metric is a mean over held-out sites); Conclusions drop the clause |
| conclusions.tex:5 | "with fewer oxides, for shallow donors, charged vacancies or cation chemistries absent from training, the measurements do not support omitting it" | MERGE: 400 limit (Results 3.2), domain (Methods 2.1), family transfer (Results 3.2); Conclusions give the positive rule only |

## 3. Data and Methods

| File:line | Caveat or label (abridged) | Verdict |
|---|---|---|
| data.tex:14 | "Three further filters were fixed before any model was trained" | DELETE "fixed before": rule (b); state the filters |
| data.tex:35 | "A formation energy computed in a finite supercell for such a configuration does not describe an isolated neutral defect" | KEEP-ONCE, home Methods 2.1 (the physics of the domain) |
| data.tex:39 | "a prediction for an oxide whose neutral vacancy would be a shallow donor lies outside the domain"; "These counts describe the release; they do not establish the electronic mechanism of any individual entry" | KEEP-ONCE (domain statement, Methods 2.1); DELETE the second sentence (defensive; the counts are reported as counts) |
| data.tex:30 | "D is an oracle with respect to pristine electronic structure only, not with respect to the defect" | KEEP-ONCE, Methods 2.1 (it defines what D knows) |
| methods.tex:2 | comment "v2 primary, v1 as originally registered" | DELETE (source comment; rewrite with the section) |
| methods.tex:21 | Figure 1 caption, solid v2 / dashed v1 | DELETE: one network |
| methods.tex:35 | "the two routes are indistinguishable on this objective, and D-late ... is reported as an extension" | DELETE the D-late sentence (default-initialisation only, `results/dlate/`); keep "D-state was selected by validation error" in Appendix B, without "indistinguishable" |
| methods.tex:37 | "The staged model of v1 is a registered analysis; P-v2 is post hoc" | DELETE: rule (b) |
| methods.tex:39-48 | Whole `sec:backbones` subsection: tags, commits, dates, "post hoc", "registered", "author decision" | DELETE; replace by the single default-initialisation paragraph of rule (a) in Methods 2.3, numbers in Appendix D |
| methods.tex:59 | Epoch cap: "registered sensitivity analysis"; "post hoc rerun ... reported only as a sensitivity analysis" | MERGE into Appendix F (training-length limit), stated once without labels |
| methods.tex:81 | "Two limitations of tuning on one resample are disclosed" (cross-resample information; Kiyohara overlap) | KEEP-ONCE, home Appendix B; Results 3.1 points to it in a clause |
| methods.tex:85 | GPU repeatability study, bitwise counts, per-class shifts, "This repeatability study is an extension" | DELETE; replace by the one GPU sentence of rule (c) in Methods 2.3 |
| methods.tex:92-100 | Split labels "(primary design; registered for v1)", "(registered for v1)", "(extension)", "registered in design, adopted as run under the extension protocol; the validation-host seed differs from the registered rule" | DELETE all labels: rule (b); describe each design plainly |
| methods.tex:98 | "The registered ten-resample, three-seed result is reported beside it and is never replaced" | DELETE: rule (b); the two designs are reported as two estimates (`docs/open_questions.md` Q1) |
| methods.tex:111 | δ justification "so a difference smaller than δ would not change a physical conclusion" | KEEP-ONCE, home Methods 2.5, with "fixed before the analysis" (rule b) |
| methods.tex:111 | "If the first qualifying budget is the largest, N* is reported as reached only there, without extrapolation; if none qualifies, N* is reported as a lower bound" | DELETE: rule text that no result needs (N* = 654 is not the largest tested size once CV is shown); keep the definition |
| methods.tex:111 | "is the stated protection against multiplicity; no further correction is applied" | KEEP-ONCE, home Appendix J |
| methods.tex:113 | "This equivalence rule replaced a null rule of the registered plan before any staged model was evaluated" | DELETE: rule (b) |
| methods.tex:115 | "Results of v2 are primary; results of v1 are reported alongside as the originally registered analysis" | DELETE: rule (b) |
| methods.tex:120 | "Hosts that do not converge are kept and flagged, and a sensitivity analysis excludes them" | KEEP-ONCE, Appendix G (one clause) |
| methods.tex:122 | "With this rule, an extension of the registered protocol, all 818 hosts are mapped" | DELETE the label; the 818-host mapping belongs to the default-initialisation evaluation; the network's check uses n = 809 (Appendix G) |
| methods.tex:126 | "If the median internal displacement is below ... reported as a null. For v1 this is the registered analysis ... For v2 ... post hoc and descriptive" | DELETE the null rule and both labels; the check reports ΔMAE with intervals (Results 3.5) |
| methods.tex:131 | Probe pass rule; "The probe of the primary network uses the trained S-v2 networks and is post hoc; the registered probe uses those of S-v1" | MERGE pass rule into Appendix H; DELETE labels |
| methods.tex:136 | Whole `sec:repro` provenance paragraph (three labels, provenance table, deviations log) | DELETE: rule (b); provenance stays in the deposit |
| methods.tex:138 | "a worker refuses a run unless the tag ... `nrp-code-v1`" | DELETE from the paper (repository detail); Appendix K keeps run identifiers and records without tag names |

## 4. Results

| File:line | Caveat or label (abridged) | Verdict |
|---|---|---|
| results.tex:5 | "the primary network (v2), whose results are post hoc ... v1, whose results follow the registered analysis ... Extensions are labelled where they appear" | DELETE: rule (b) |
| results.tex:14 | "What is established is the scale of the problem ..." | DELETE closing refrain; the opening sentence carries the point |
| results.tex:19 | "below the registered gate of 0.35 eV"; "S ... on v2 (post hoc)" | DELETE: rule (b) |
| results.tex:21 | "Two qualifications apply" (tuning overlap with the Kiyohara test hosts; "C0 on the Kiyohara split exists for v1 only") | MERGE tuning overlap into Appendix B; the v1-only Kiyohara value is an open question (`docs/open_questions.md` Q3) |
| results.tex:23 | "single networks could not resolve the tolerance"; "it does not rank S against the published network" | MERGE the seed-ensemble point into Methods 2.3 (why the ensemble is reported); DELETE the ranking disclaimer (defensive) |
| results.tex:35 | "N* = 654, the largest registered budget, without extrapolation"; "The miss at 400 hosts is not marginal" | KEEP-ONCE 400 limit, home Results 3.2; DELETE "without extrapolation" and "registered" |
| results.tex:35 | "On v2 (post hoc)"; v2 bound below δ at 200 but not 400 | DELETE label; keep the 200 observation as one clause explaining N* (Results 3.2) |
| results.tex:43 | "Both intervals include zero ... but the networks disagree in sign ... The ceiling bounds the size of the electronic contribution at this data size; it does not fix its sign" | DELETE: two-network comparison and defensive refrain; the 654 interval of the network is stated once in Results 3.2 |
| results.tex:45 | "The cross-validation tests every host once, including hosts that no outer resample tests, and its training sizes are fold means, so its values are not directly comparable with the budget points" | KEEP-ONCE, home Results 3.2 paragraph 3 (together with "nothing known beyond about 777") |
| results.tex:47 | "Beyond the largest registered budget the two networks part ways. On v1 the sign of A changes" | DELETE: default-initialisation result |
| results.tex:47 | "On v2, A stays positive ... the descriptors still lower the error of the primary network, by less than δ" | KEEP-ONCE as the positive "at most about 0.04 eV" statement, home Results 3.2 |
| results.tex:47 | Leave-one-chemistry-out: "(extension, as run)"; "for transfer to absent cation chemistries the bound holds for v1 only" | KEEP-ONCE the network's upper bound 0.060 eV as a limit, home Results 3.2; DELETE label and v1 clause |
| results.tex:47 | "A further caveat is convergence ... S may not be fully converged at the largest budgets" | KEEP-ONCE, home Appendix F (training-length limit) |
| results.tex:50, 56 | Table 2: "Label: R, registered ...; PH, post hoc ...; E, extension"; column "Originally registered network (v1)" | DELETE: rule (b); the v1 column moves to Appendix D |
| results.tex:75 | Practitioner paragraph: "a bounded statement"; "It is not supported at 400 hosts or fewer, beyond the largest cross-validation training size, for cation families absent from training on the primary network, for shallow-donor oxides, or for other architectures"; "Nor do the measurements show that the descriptors carry no information" | DELETE paragraph; each limit has its home (400, CV range, families: Results 3.2; shallow donors: Methods 2.1; architectures: Appendix F); the "carry information" point becomes the positive 0.04 eV statement |
| results.tex:80 | "On v1, S has no within-host skill up to 200 training hosts ... (Section `sec:backbones`)" | KEEP-ONCE, moved to the default-initialisation Methods paragraph and Appendix D (rule a) |
| results.tex:82 | "an interval below zero, so D has the larger within-host residual" (v1) | DELETE: default-initialisation result |
| results.tex:84 | "(extension; ...)"; estimator shift of the breakdown; v1 group results | MERGE estimator note into Appendix E; DELETE label and v1 groups |
| results.tex:86 | "The breakdown carries about a thousand intervals without a multiplicity correction ... weak evidence"; "What is established ... which features ... is not established here" | KEEP-ONCE multiplicity, home Appendix E; DELETE the closing refrain |
| results.tex:91 | "below 654 training hosts their advantage is not bounded below δ under the registered rule"; "a rule fixed after the registered plan and therefore post hoc" | DELETE: rule (b); motivation of staging stays without the label |
| results.tex:93 | Whole v1 staging paragraph | DELETE: default-initialisation result |
| results.tex:97 | Figure 4 caption, v1/v2 key and labels | DELETE: one network |
| results.tex:100 | "At 25 and 50 hosts D is itself unstable ... so the cost of staging is not interpretable there" | KEEP-ONCE, Results 3.4 (one clause) |
| results.tex:102 | "this check was not run on v2, whose trained networks are stored only on the computing cluster" | KEEP-ONCE pending: Results 3.4 states the swap-in check once Aiden's rerun exists (`docs/open_questions.md` Q5); until then the clause is removed, not hedged |
| results.tex:102 | "what a more accurate descriptor predictor would achieve was not measured" | DELETE: restates the scope of the experiment |
| results.tex:107 | "The registered evaluation used v1 ... the evaluation at 200 hosts is a descriptive extra" | DELETE: default-initialisation evaluation; replace with the network's check on 809 relaxed hosts |
| results.tex:109-111 | "The registered null rule is not met, and neither of its conditions holds"; v1 ΔMAE values | DELETE: rule (b) and default initialisation |
| results.tex:115 | Figure 5 caption ("originally registered network", "all v1") | DELETE with the figure (main text) |
| results.tex:118 | "Whether staged and end-to-end models degrade differently was not registered as a test. Under the post hoc equivalence rule ... No v2 geometry evaluation on our relaxations exists; the collaborator's v2 evaluation ... post hoc cross-check outside C3b ... any geometry result for the primary network, are not established" | DELETE: rule (b); the network's check (809 hosts) becomes the main geometry statement |
| results.tex:122 | Figure 6 caption "provenance labels" | DELETE: one network |
| results.tex:128 | "(claim C4, registered on v1)"; "The registered rule fails, and the probe moves to Supplementary Figure S7"; "The probe of v2 (post hoc, descriptive)"; "this does not show that the network ignores electronic structure" | KEEP-ONCE, probe moved to Appendix H on the network; DELETE labels and the defensive closing clause |
| results.tex:135 | Sensitivities: "(extension, v1, ...)", "(post hoc, v1)", "neither exists for v2" | KEEP-ONCE, moved to Appendix F on the network; v1-only values cannot appear (`docs/open_questions.md` Q4, Q6) |
| results.tex:137 | CGCNN: "(extension, descriptive)"; "With one resample the intervals reflect only the sampling of test hosts, and no test is made" | KEEP-ONCE, Appendix F (one clause); DELETE label |
| results.tex:139 | GPU paragraph, "not read as hardware effects" | DELETE: rule (c) |
| results.tex:141 | Collaborator bootstrap comparison; "the sensitivity of v2 to these choices, and hardware effects separated from sampling, were not measured" | DELETE: provenance (deposit) and rule (c) |
| results_screening.tex:5 | "This is a demonstration, not a test"; "the aggregation registered for v1. The v2 predictions are post hoc; both are shown" | KEEP-ONCE "demonstration" as the first clause of Results 3.6; DELETE labels and the v1 series |
| results_screening.tex:7 | "These removals are consistent with ... but do not prove a mechanism" | DELETE the hedge: the domain physics is stated once in Methods 2.1 |
| results_screening.tex:10, 45 | Table captions "(v2, post hoc)", "(v1)" | DELETE: one network |
| results_screening.tex:33 | "wide because the hosts are few"; "the screened oxides are not a random sample, and no test of a difference was made. v1 has the lower error on these sites, but v2 is the primary network ... no ranking of the networks is read" | KEEP-ONCE "10 sites in 7 hosts, not a random sample", Results 3.6; DELETE the network comparison |
| results_screening.tex:37 | Figure 7 caption labels | DELETE: one network |
| results_screening.tex:62 | "These sites neither establish nor exclude a ranking of sites finer than the error, and nothing was measured for the absent candidates" | DELETE: hedge stack; the numbers stand |

## 5. Discussion

| File:line | Caveat or label (abridged) | Verdict |
|---|---|---|
| discussion.tex:2 | comment "Every physical reading is labelled as a hypothesis" | DELETE as a rule; replaced in `docs/prose_style.md` (one hypothesis marker per reading, no refrain) |
| discussion.tex:9 | "The principal result is a bound, not an equivalence"; "on v1 the sign of A turns negative"; "What needs explaining is ... not why it carries none" | DELETE the refrain and the v1 clause; keep the positive framing (descriptors add at most about 0.04 eV) |
| discussion.tex:13 | "We propose that ..."; "The probe does not decide the mechanism"; proposed test | KEEP-ONCE: the hypothesis and its test, stated once; DELETE the probe clause (Appendix H) |
| discussion.tex:15 | "The sign difference between the networks may be a property of the networks"; S-v1 vs S-v2 | DELETE from Discussion; whether the weaker S of the network deserves one sentence is `docs/open_questions.md` Q7 |
| discussion.tex:20 | "We propose that within a host ..." and its test | KEEP-ONCE (home Discussion 4.2) |
| discussion.tex:22 | v1 site-resolution diagnostics; "cannot be attributed to the number of oxides alone"; "resolution at the other oxygen sites of a supercell is untested" | KEEP-ONCE, diagnostics moved to the default-initialisation paragraph (Methods 2.3); DELETE the other two hedges (default-initialisation diagnostics) |
| discussion.tex:24 | "On v1, D is worse than S within Ga-containing hosts"; "a hypothesis four pairs cannot test"; "Each reading rests on a breakdown with about a thousand uncorrected intervals, so an isolated group is weak evidence until replicated" | DELETE v1 clause; MERGE multiplicity into Appendix E (pointer only); keep the d-shell hypothesis once |
| discussion.tex:29 | Domain paragraph ("Every statement of this paper describes deep, localised neutral oxygen vacancies"; one functional and workflow; high-moment exclusion "left the bound on v1 below δ ... no host outside that classification was tested") | MERGE into the domain statement (Methods 2.1); Discussion 4.4 points to it; high-moment clause waits for the network's rerun (Q4) |
| discussion.tex:31 | "For charged vacancies and shallow donors we expect the conclusion to change, and this is a hypothesis" | KEEP-ONCE, Discussion 4.4 (as the next test, without "and this is a hypothesis") |
| discussion.tex:33 | "the models say nothing about many of the materials in which oxygen vacancies are exploited"; "a descriptive value without an interval"; v1/v2 MAE "rank neither the networks nor the oxides" | KEEP-ONCE the absent-oxide sentence once (Discussion 4.4); DELETE the v1/v2 clause and "without an interval" (state the n instead) |
| discussion.tex:38 | Staging hypothesis with "We propose" and test | KEEP-ONCE, shortened (home Discussion 4.1) |
| discussion.tex:40 | "We propose, as a hypothesis and not a result"; v1 geometry numbers; "No v2 network was evaluated on these relaxations" | DELETE: default-initialisation geometry; double hedge |
| discussion.tex:42 | Probe: "the data do not show ... This neither supports nor excludes an implicit, nonlinear encoding" | KEEP-ONCE, moved to Appendix H, one sentence; DELETE the "neither ... nor" stack |
| discussion.tex:47 | "a reproduction and not an improvement, and the structure-only result is theirs"; "not a replica of their serial design" | KEEP-ONCE, Discussion 4.3, one sentence of credit (no double disclaimer) |
| discussion.tex:49 | "The site-resolution, staging, geometry and probe analyses are secondary; the structure-only accuracy, descriptor learning curves, the serial design and the data are not new" | MERGE into one positive sentence of what is new (Discussion 4.3) |
| discussion.tex:54 | Limitations paragraph (one database; beyond 777 unknown; LOCO v1 only; v2 post hoc; sign disagreement; GPU; epoch limit v1 only; no v2 geometry or swap-in; one-resample CGCNN; multiplicity; tuning overlap; ten screened sites) | DELETE as a paragraph: each kept limit has one home (`docs/story_spec.md` (ii)); post hoc, sign, GPU and v1/v2 availability items vanish |
| discussion.tex:56 | Practice paragraph: "may skip ... it should be kept there; ... for oxides likely to host shallow donors and for charged vacancies, where nothing was measured" | MERGE into Conclusions (positive rule); "should be kept" clauses DELETE (limits live in 3.2 and 2.1) |

## 6. Supplementary Information (becomes appendices)

| File:line | Caveat or label (abridged) | Verdict |
|---|---|---|
| si.tex (front block) | "Every result carries the label of its provenance: registered ..., post hoc ..., extension" | DELETE: rule (b) |
| s1_data.tex:12-14 | "so the subset, and every result of this work, describes deep, localised neutral vacancies ..." | MERGE into the domain statement (Methods 2.1); Appendix A points |
| s1_data.tex:36 | D2: "the host is excluded rather than repaired" | KEEP-ONCE (Appendix A, a fact of the filter) |
| s2_training.tex:18 | "The readout is the same for both networks" | DELETE: one network |
| s2_training.tex:76-87 | "tuned under the frozen plan"; "indistinguishable ... not evidence that one route encodes the electronic structure better"; "adopted after test-set diagnostics of v1 and is post hoc"; "should be read as one reasonable setting rather than an optimum" | DELETE labels and frozen; KEEP the smallest-anchor note once (Appendix B); D-route note one clause |
| s2_training.tex:102 | Table S5 caption "(v2, post hoc ...)" | DELETE label |
| s2_training.tex:117-123 | "registered check of the cap ... (registered v1; ...)" | MERGE into Appendix F; default-initialisation only (Q6) |
| s2_training.tex:125-140 | capped runs "may still have been improving"; "descriptive and carries no test"; "post hoc rerun ... no such reruns exist for v2" | KEEP-ONCE the network's capped counts as the training-length limit, Appendix F; DELETE labels and v1 twins (Q6) |
| s2_training.tex:154-164 | Hardware subsection; "not bitwise reproducible across GPU models" | DELETE; the one GPU sentence lives in Methods 2.3 (rule c) |
| s3_splits.tex:33-40 | "This comparison is not fully held out at the level of the settings" | KEEP-ONCE, Appendix B (tuning) and Appendix C points |
| s3_splits.tex:45-47 | "a cross-validated error is not directly comparable with a registered budget" | MERGE into Results 3.2 (home) |
| s3_splits.tex:51-55 | LOCO provenance ("follow the registered design but are the collaborator's ... labelled extension at the results freeze ... leaves the choice to the author ... post hoc") | DELETE: rule (b) |
| s4_withinhost.tex:5-8 | "(extension, not registered ...)", "logged in docs/deviations.md before any number was computed" | DELETE: rule (b) |
| s4_withinhost.tex:18-22 | estimator note "comparable with each other but not with the registered learning curves" | KEEP-ONCE, Appendix E, without "registered" |
| s4_withinhost.tex:31-34, 39-44 | v1 within-host penalty of D | DELETE: default initialisation |
| s4_withinhost.tex:48 | "a reading that is not tested here" | DELETE: hedge; state as a hypothesis once or drop |
| s4_withinhost.tex:53-59 | multiplicity, overlapping cation groups, "Physical readings ... are hypotheses ... not tested here" | KEEP-ONCE multiplicity and group overlap (Appendix E, home); DELETE the trailing refrain |
| s4_withinhost.tex:63, 80 | captions "(extension; both networks; v2 post hoc)" | DELETE labels |
| s5_hardware.tex (all) | GPU repeatability and GPU-class analysis, "not read as an effect of the hardware" | DELETE section, Figure S5, Tables S8-S9: rule (c) |
| s6_sensitivities.tex:4-10 | "All three were run for v1 only; no v2 sensitivity runs exist, so the v2 statement rests on its primary result alone" | DELETE; Appendix F reports what exists for the network (Q4, Q6) |
| s6_sensitivities.tex:13-14 | "whether their two electrons localise on reducible cations is a reading that this analysis does not test" | DELETE: hedge |
| s6_sensitivities.tex:24, 36 | "(post hoc, rule logged before the reruns)"; "the capped runs of the extensions ... were not rerun" | DELETE: rule (b) and default-initialisation twins |
| s6_sensitivities.tex:46-48 | CGCNN "With one resample, the intervals reflect only the sampling ... it does not establish a bound for other architectures" | KEEP-ONCE, Appendix F, one clause |
| s7_probe.tex:7-21, 41-46 | "claim C4, registered on v1"; "registered rule ... committed before any v1 probe number"; "C4 therefore does not hold, and under the registered rule the probe is reported here"; "What is not established ..."; "One reading, not tested here" | KEEP-ONCE in Appendix H on the network (rule and outcome); DELETE labels, claim IDs and the refrains |
| s7_probe.tex:57-58 | "a lower bound on what the vector encodes; this was recorded as found and not adjusted" | KEEP-ONCE "linear recoverability is a lower bound" (Appendix H); DELETE "recorded as found" |
| s9_reproducibility.tex:7-9, 47-77 | tags, "frozen at", provenance labels, deviation kinds, "post hoc ratification", "author decisions" | DELETE: rule (b); Appendix K keeps code, records, deposit and software only |
| tables/provenance_labels.tex, tables/release_tags.tex | provenance and tag tables | DELETE from the paper; stay in the deposit |

## 7. Summary

123 ledger rows (one row can bundle several hits of one line): KEEP-ONCE 39, MERGE 15, DELETE 69.
Rows that bundle a keep and a delete are counted by their first verdict.

| Verdict | Where the kept material lives |
|---|---|
| KEEP-ONCE | Methods 2.1 (domain, D as a pristine-only oracle); Methods 2.3 (default-initialisation paragraph, GPU sentence); Methods 2.5 (δ fixed before the analysis, MAE as a mean over held-out sites); Results 3.2 (400 limit, CV comparability and range, family transfer, at most about 0.04 eV); Results 3.4 (small-budget D, swap-in check once rerun); Results 3.6 (demonstration, 10 sites in 7 hosts); Discussion 4.1-4.4 (one hypothesis and its test per reading; charged vacancies; no experimental validation; credit to prior work); Appendices B, E, F, G, H, J |
| MERGE | folded into the KEEP-ONCE homes above |
| DELETE | every registration label (643 counted hits, Section 1), every default-initialisation result outside Appendix D and the Methods paragraph, every GPU caveat, and the defensive refrains and hedge stacks marked above |

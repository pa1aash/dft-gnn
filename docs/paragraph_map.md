# Paragraph map of Results and Discussion (S1)

Session S1, 2026-10-17. One line per paragraph of `paper/sections/results.tex`, `results_screening.tex` and
`discussion.tex` at `origin/main` 21158d2 (source line in brackets; each paragraph is one line). Verdicts: keep,
shorten (to what), move to Appendix X, delete. New section numbers follow `docs/story_spec.md` (iii). "The network"
is the He-initialised network (v2); every v1 number leaves the main text (rule a).

## Results

### Preamble and 3.1 Host and site contributions (old 3.1, 3.2)
- [results:5] Preamble on labels and both networks: **shorten** to one sentence (MAE in eV on held-out oxides, intervals 95%, $U$ one-sided, Table 1); labels and the v1/v2 split deleted (rule b).
- [results:10] ICC and host-versus-site variance: **keep**, cut by a third; it motivates the within-host metric. It now opens 3.1.
- [results:12] Host-mean oracle, zero skill, B0: **shorten** to two sentences (oracle MAE, zero skill, B0 at 25 and 654).
- [results:14] Random forests and the closing refrain: **shorten** to the RF-Kumagai reproduction (within 0.006 eV) and the RF-structural vs RF-electronic contrast in one sentence; drop "What is established".
- [results:19] Reproduction on the Kiyohara split: **shorten** to the network's formula-grouped value against the published 0.29 eV; the Kiyohara-split value exists only for default initialisation (`docs/open_questions.md` Q3); delete the registered gate.
- [results:21] Two qualifications (tuning overlap; v1 only): **move to Appendix B** (tuning overlap, one sentence); delete the v1-only clause.
- [results:23] Seed ensemble vs single networks: **move** the reason to Methods 2.3 (one sentence: single-network $A$ scatters by more than δ, so the ensemble is reported); delete the ranking disclaimer.

### 3.2 Learning curve and the descriptor advantage (old 3.3) — claim 1
- [results:28] Question and Figure 2 MAE values: **keep**, rewritten for the network alone (S from 1.133 to 0.296 eV, D 0.280 eV at 654); the question sentence opens the subsection.
- [results:35] $N^{*}$ on both networks, the 400 miss, v2 bound at 200: **shorten** to the network: $A$ at 654 with interval and $U$ in both designs, interval inside ±δ, $N^{*}$ = 654 because 400 fails ($U$ 0.075); one clause on the 200-host bound (0.047) explaining why $N^{*}$ is not 200. This is the home of the 400 limit.
- [results:43] Ceiling on both networks and sign disagreement: **delete**; the 654 interval of the network is stated once in the paragraph above, and the sign comparison is a v1 result.
- [results:45] Precision and cross-validation: **shorten** to the network: 30 x 5 at 654 (0.033 [0.021, 0.045], $U$ 0.043) and at 400 ($U$ 0.079); CV at about 736 and 777 hosts with $U$ 0.039 and 0.040, two-sided wording **[PENDING C1]**; keep the CV comparability clause once (home) and add "nothing is known beyond about 777".
- [results:47] Networks part ways; v2 positive; LOCO; convergence caveat: **shorten** to two sentences: the advantage stays positive and at most about 0.04 eV at every size from 654 on (home of that statement); leave-one-family-out $A$ = 0.041 [0.018, 0.064], $U$ = 0.060, above δ (home of that limit). Convergence caveat **moves to Appendix F**.
- [results:75] Practitioner paragraph with the list of unsupported cases: **delete**; each limit has one home, and the practical rule goes to the Conclusions.

### 3.3 Site resolution within a host (old 3.4) — claim 2
- [results:80] Within-host skill; v1 site blindness up to 200: **shorten** to the network's values against zero skill (0.150 S at 654 vs 0.187); the v1 site blindness **moves** to the default-initialisation paragraph (Methods 2.3) and Appendix D.
- [results:82] $A_\mathrm{within}$ on both networks and CV: **keep** for the network only (−0.002 [−0.013, 0.009] at 654; CV values); "Within a host, D is no better than S" stays as the closing sentence.
- [results:84] Breakdown by chemistry, estimator shift, v1 Ga result: **move to Appendix E**; keep in the main text one sentence on the d-shell contrast of the spread (zero skill by d class) as the bridge to Discussion 4.2.
- [results:86] Spearman ranking, Bader reference, multiplicity, refrain: **shorten** to one sentence (S and D rank sites alike; the Bader charge of the removed oxygen alone ranks them with a mean correlation of only 0.043 [−0.036, 0.120]); multiplicity **moves to Appendix E**; refrain deleted.

### 3.4 Staging (old 3.5) — claim 3
- [results:91] Staging question, rule labelled post hoc: **shorten** to the question and the identity $\mathrm{MAE_P} - \mathrm{MAE_S} = -A - (\mathrm{MAE_D} - \mathrm{MAE_P})$; the four-outcome rule is cited from Methods 2.5 without a label.
- [results:93] v1 staging paragraph: **delete** (default initialisation).
- [results:100] v2 staging outcomes: **keep** as the main staging paragraph: P never better than S; P worse at 50-200, equivalent at 400, worse within the margin at 654 (0.028 [0.008, 0.053]); the D instability at 25 and 50 hosts stays as one clause.
- [results:102] P1 recovery by class; swap-in check; refrain: **shorten** to P1 class means (0.751 host, 0.613 site) and the formation-energy vs Bader contrast (0.966 vs 0.387); the swap-in sentence waits for Aiden's rerun (`docs/open_questions.md` Q5); delete "what a more accurate predictor would achieve was not measured".

### 3.5 Relaxed geometry (old 3.6) — claim 3, a check
- [results:107] v1 registered evaluation on 818 relaxations, components: **shorten** to two sentences on the network's check: 809 relaxed hosts, three components with medians; protocol to Appendix G.
- [results:109] v1 null rule and ΔMAE: **delete**; replace with the network's ΔMAE of S, D and P at 654 (S +0.0002 [−0.0025, +0.0026] eV) in one sentence, table in Appendix G.
- [results:111] Regression on components, non-converged hosts: **move to Appendix G** only if a regression exists for the network (`docs/open_questions.md` Q8); otherwise delete.
- [results:118] Post hoc TOST, 809 cross-check, refrains: **delete** as written; its one useful fact (the 809-host evaluation) becomes the main geometry statement above.

### Probe (old 3.7) — check, moved
- [results:128] Probe on v1 with the v2 pattern: **move to Appendix H**, rewritten on the network (trend holds; exceeds shuffled labels; does not exceed the untrained encoder except the site class at 654); Results keeps no probe paragraph, Discussion 4.1 one pointer.

### 3.6 Screening of named oxides (old 3.8)
- [screening:5] Demonstration framing, aggregation, labels: **shorten** to two sentences ("a demonstration on the named oxides"; prediction = seed-ensemble mean over held-out resamples); labels deleted.
- [screening:7] Absent candidates and the perturbed-host-state removals: **keep**, cut the closing hedge; this is where the absent oxides are named (Methods 2.1 holds the physics).
- [screening:33] MAE over screened sites on both networks; net sign: **shorten** to the network (0.420 eV over 10 sites in 7 hosts, not a random sample) and the over/under count; delete the network comparison.
- [screening:40] Two energy groups; rank correlation: **keep**, one network; the SnO$_2$ render pointer goes to Appendix I.
- [screening:42] Within-host pairs (Ga$_2$O$_3$, ZrO$_2$): **keep**, one network; pair table to Appendix I.
- [screening:60] Largest errors; Al$_2$O$_3$ under-prediction: **shorten** to one sentence.
- [screening:62] Closing hedge stack: **delete**; one positive closing sentence (both groups and 3 of 4 pairs reproduced).

### Sensitivities (old 3.9) — moved
- [results:135] High-moment exclusion and capped twins (v1): **move to Appendix F**; both are default-initialisation results now; the high-moment rerun on the network is pending (Aiden; Q4), the twins are Q6.
- [results:137] Untuned CGCNN: **move to Appendix F**, values of the network and CGCNN only, one-resample clause once.
- [results:139] GPU repeatability and GPU-class $A$: **delete** (rule c).
- [results:141] Collaborator bootstrap comparison and closing: **delete** (provenance stays in the deposit).

## Discussion

### 4.1 Why structure suffices (old 4.1)
- [discussion:9] "A bound, not an equivalence", v1 sign: **shorten** to two sentences stating the positive result (from 654 training hosts on the descriptors add at most about 0.04 eV; at 400 their advantage is not bounded below δ) and the question (why explicit electronic information stops paying at a few hundred oxides); refrain and v1 clause deleted.
- [discussion:11] Descriptors are functions of the pristine structure: **keep** (the physical core of the paper), lightly cut.
- [discussion:13] Host-thermodynamics hypothesis with three measurements and a test: **keep**, network values only; the probe clause becomes a pointer to Appendix H.
- [discussion:15] Sign difference between networks: **delete** from Discussion; whether one sentence on the weaker S of the network belongs here or in Appendix D is Q7.
- [discussion:38] (from old 4.4) Staging cost set by site-level charges, with test: **shorten** to two sentences and attach here, after the host-thermodynamics paragraph.

### 4.2 Local vacancy chemistry (old 4.2)
- [discussion:20] Within-host spread, Bader reference, bonding-and-relaxation hypothesis: **keep**, network values.
- [discussion:22] v1 site-resolution diagnostics: **delete** here (they live in the default-initialisation Methods paragraph); drop the two hedges.
- [discussion:24] d-shell classes, Ga/Cd/Pb chemistry, band-gap tercile, Ga$_2$O$_3$/ZrO$_2$ pairs, multiplicity: **shorten** to the d-shell hypothesis and the ZrO$_2$ pair; v1 Ga clause deleted; multiplicity is a pointer to Appendix E.

### 4.3 Relation to prior work (old 4.5)
- [discussion:47] Kumagai, Kiyohara, Witman, Deml, Linton: **keep**, one credit clause per work, no double disclaimer; Kiyohara-split reproduction value per Q3.
- [discussion:49] What is new: **shorten** to one positive sentence.

### 4.4 Scope (old 4.3 and 4.6)
- [discussion:29] Domain paragraph: **shorten** to one sentence pointing to Methods 2.1; high-moment clause per Q4.
- [discussion:31] Charged vacancies and shallow donors as the next test: **keep**, as the forward-looking statement, without "and this is a hypothesis".
- [discussion:33] Screened oxides, absent oxides, band-gap correlation, energy groups, v1/v2 MAE: **shorten**: keep the absent-oxide sentence (TCOs, ceria, WO$_3$) and the band-gap reading of the two groups; delete the v1/v2 MAE clause.
- [discussion:54] Limitations paragraph: **delete**; each surviving limit has one home (`docs/story_spec.md` (ii)); add the single sentence "no experimental formation energies were used to validate the predictions" here (home).
- [discussion:56] Practice paragraph: **move** the positive rule to the Conclusions; delete the "should be kept" clauses.

### Old 4.4 Pipeline (staging, geometry, probe)
- [discussion:38] see 4.1.
- [discussion:40] v1 geometry reading and hypothesis: **delete** (default initialisation); one clause of the network's geometry result may appear in Discussion 4.4 as deployment relevance.
- [discussion:42] Probe reading: **move to Appendix H** (one sentence: an untrained encoder already exposes much of the descriptor variance, consistent with 4.1).

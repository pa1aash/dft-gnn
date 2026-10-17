# Open questions for the rewrite (S1)

Session S1, 2026-10-17. Points the records cannot decide for the story of `docs/story_spec.md`. Each has the
facts read from the records (no number was computed), a recommendation, and who decides. "The network" is the
He-initialised network (v2); "default initialisation" is v1.

## A. Pending runs and checks

**Q1. Which estimate carries the headline at 654 training hosts?** Two estimates exist for the network: the
learning-curve design (10 resamples x 3 seeds), $A$ = 0.015 eV [−0.008, 0.036], $U$ = 0.033
(`results/c1c2_v2.json`); and the additional-resample set (30 x 5, which contains the 10 x 3 runs), $A$ = 0.033 eV
[0.021, 0.045], $U$ = 0.043 (`results/precision_a_b400_b654.json`). Both satisfy the author's evidence form (one-sided
bound below 0.05 eV and two-sided interval inside ±0.05 eV). Recommendation: the 30 x 5 value in the Abstract,
Results 3.2 and Conclusions, because it is the more precise estimate and matches "small and positive"; the 10 x 3
curve stays as Figure 2 and its 654 value appears once beside it. *Author.*

**Q2. Two-sided intervals at the cross-validation sizes (task C1).** The brief says these are not yet computed, so
the wording at about 736 and 777 hosts is marked **[PENDING C1]** everywhere. Note:
`results/cv_extended_budget.json` already stores two-sided 95% host-cluster bootstrap intervals for the network:
$A$ = 0.024 [0.005, 0.042] at $K$ = 10 (736.2 hosts) and 0.026 [0.010, 0.043] at $K$ = 20 (777.1 hosts), with $U$ = 0.039
and 0.040; both intervals lie inside ±0.05 eV. If C1 is meant to recompute these with another estimator (for
example a seed- or fold-level bootstrap), its result replaces them; if not, C1 may only need to confirm these
values. *Author / task C1.*

**Q3. Reproduction of the published 0.29 eV.** The value on Kiyohara's released split (0.283 eV
[0.237, 0.329], `results/c0_official.json`) exists for
default initialisation only. For the network only the formula-grouped value exists: S = 0.296 eV [0.275, 0.317] at
654 hosts. Options: (a) cite only the network's formula-grouped value against 0.29 eV (recommended; it needs no
second network); (b) put the Kiyohara-split value in Table D1; (c) run the network on Kiyohara's split (a new run,
outside S1). *Author.*

**Q4. High-moment exclusion on the network (Aiden rerun, pending).** Only the default-initialisation result exists
(`results/sens_high_moment_v1.json`). Until the rerun lands, Appendix F carries no high-moment result and Methods
2.1 no high-moment sentence; the domain statement does not depend on it. *Aiden.*

**Q5. Staging true-descriptor swap-in check on the network (Aiden rerun, pending).** The check (D fed true
descriptors through the staging code reproduces D) exists for default initialisation only (183 cells). Until it
lands, Results 3.4 omits the sentence; it is a code check, not a limit. *Aiden.*

## B. Results that exist only for default initialisation

Rule (a) admits default-initialisation numbers only in Table D1 and the Methods paragraph. These results therefore
leave the paper unless the author moves them into Table D1:

| Result | Record | Recommendation |
|---|---|---|
| Kiyohara-split reproduction | `results/c0_official.json` | Q3 |
| Registered epoch-cap check (200 vs 600 epochs, identical) | `results/g1_cap_sensitivity.json` | Drop; Appendix F reports the network's capped-run counts plainly |
| Capped-twin reruns (Q6) | `results/sens_capped_post_hoc.json` | Q6 |
| D-late route in the full protocol | `results/dlate/` | Drop; Appendix B keeps the route selection on validation error |
| Geometry evaluation on all 818 relaxations, regression on strain components, non-converged sensitivity | `results/geometry_c3b.json` | Drop (Q8) |
| Probe figure (Figure S7 is drawn on default initialisation) | `results/probe_c4_v1.json` | Redraw on the network (Q9) |
| Within-host results by chemistry for default initialisation (Ga, PHS-prone penalty) | `results/within_host_breakdown.json` | Drop; the network's columns of the same record stay |
| GPU repeatability | `results/nrp/` | Drop (rule c) |

**Q6. Training-length limit on the network.** Capped twins exist for default initialisation only. For the network,
the record holds the counts of capped S and D runs at 654 hosts in the additional-resample set
(14 of 150 S runs and 6 of 150 D runs reached the 200-epoch limit;
`results/precision_a_b400_b654.json`, `payload.descriptive.capped`) and of the sweep (5 of 360 runs). Recommendation: Appendix F states these counts once as a limit of the network's training (S may
not be fully converged at 654); no twin result in the paper. *Author.*

**Q7. Does the paper say that the network's S is weaker than the default-initialisation S at 654?** Table D1 will
show S = 0.296 eV (network) against 0.273 eV (default initialisation) and $A$ = 0.015 against −0.012 eV at 654, so a
reader can see that part of the network's positive advantage comes from a less accurate S, while D is similar
(0.280 vs 0.284 eV). The old Discussion said so. Rule (a) confines default-initialisation numbers to Table D1 and
the Methods paragraph. Recommendation: one sentence in the Table D1 caption or the Methods paragraph ("At 654 hosts
the default initialisation gives a lower structure-only error and an advantage of −0.012 eV; the choice of
initialisation was made on validation data at small training sizes"), and nothing in the Discussion. *Author.*

## C. The final network's checks

**Q8. Geometry check: which n, which numbers, which figure.** The brief fixes n = 809 relaxed hosts. The network was
evaluated on Aiden's relaxations: 809 hosts relaxed, 802 converged and evaluated (`results/mlip_eval_v2.json`,
`n_hosts_mlip` = 802), with his bootstrap; at 654 hosts $\Delta$MAE of S = +0.0002 eV [−0.0025, +0.0026] (relaxed) and
−0.0002 [−0.0023, +0.0021] (rescaled), P +0.0033 [+0.0004, +0.0061], D below 0.001 eV. Decide: (a) state "809
relaxed hosts, 802 converged" once in Appendix G (recommended; the narrative says 809); (b) Figure 5 is drawn on
default initialisation and leaves the main text; an Appendix G table of the network's $\Delta$MAE from the record
needs a small table generator (the macros may not all exist yet: check `paper/generated/numbers.tsv` for
`mlip_eval_v2` pointers). The record has per-host values, so a figure could be drawn without computing anything
new, but rule (g) keeps the check short, and a table suffices. *Author; figure or table work in a later session.*

**Q9. Probe on the network.** `results/probe_descriptive.json` (`payload.s_v2`) holds the network's probe: trend
correlations 0.964 (host) and 0.978 (site), above the shuffled-label control at 200, 400 and 654 hosts, not above
the untrained encoder at 200 hosts and above, except the site class at 654. Figure S7 (`fig6_probe`) is drawn on
default initialisation and must be redrawn from `payload.s_v2` for Appendix H (a figure-scope session). Check that
the s_v2 payload holds every series the figure needs (per-budget class means, controls, per-descriptor values at
654: `per_descriptor_654` is present). *Later figure session.*

**Q10. Screening on the network.** The network's screening MAE is 0.420 eV [0.307, 0.553] over the 10 sites, against
0.294 eV for default initialisation and 0.296 eV over all held-out sites. With one network the paper reports 0.420
eV and the two energy groups; the higher error on these sites stands without comparison. The author should know the
screening demonstration looks weaker than in the current draft. *Author (awareness).*

## D. Wording and structure

**Q11. Title.** The current title asks a question with "non-magnetic oxides" first. A title in the new voice, for
example: "Crystal structure alone matches DFT electronic descriptors within 0.05 eV for oxygen-vacancy formation
energies from 650 training oxides". *Author.*

**Q12. Tolerance sentence.** Rule (b) allows "fixed before the analysis" once. The record supports it: δ = 0.05 eV
is in the analysis plan committed before any training. Recommendation: Methods 2.5, one sentence, with the physical
justification (one-sixth of the published structure-only error; below the DFT-experiment spread). *Settled unless the
author objects.*

**Q13. The 200-host bound.** On the network the one-sided bound at 200 hosts is 0.047 eV, below δ, while at 400 it
is 0.075 eV. The $N^{*}$ rule (bound below δ at a size and every larger size) gives 654. Recommendation: one clause in
Results 3.2 so a reader of Figure 2 is not surprised; no discussion. *Author.*

**Q14. Default-initialisation paragraph: what counts as "inspecting held-out predictions".** The diagnostic
numbers (median spread of predictions across the sites of a test host 2.8e-5 eV at 200 hosts against a target
spread of 0.121 eV; at initialisation the spread is at the same level) come from test-host predictions; the
paragraph states this plainly, as rule (a) requires, and adds that the He choice and the re-tuning used validation
oxides only. Recommendation: give the two spreads as macros in the paragraph and the rest in Table D1. *Settled
unless the author objects.*

**Q15. Leave-one-family-out with default initialisation.** Default initialisation passes ($A$ = 0.008, $U$ = 0.027), the network does not ($A$ = 0.041 [0.018, 0.064], $U$ =
0.060). With one network the limit is
stated plainly; the default-initialisation value goes to Table D1 only if the author wants the ablation table to
carry it. *Author.*

**Q16. Data Availability and provenance.** Rule (b) removes the provenance-label table, the deviation summary and the
tag table from the paper. Appendix K and the Data Availability Statement should name the deposit and say that run
records, the analysis plan and the dated log of every analysis decision are deposited with the code, without the
labels. *Settled unless the author objects.*

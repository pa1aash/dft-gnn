# Abstract trace (W2)

Session W2, 2026-10-14; wording re-verified in session T2, 2026-10-15 (terms aligned with the body, Abstract 230 words). Each sentence of `paper/sections/abstract.tex` against the Results subsection (or, for
background and method, the section) that supports it, with the macros it uses and their source records. Every number
in the Abstract is a macro; none is typed.

| # | Abstract sentence (abridged) | Support | Macros and records |
|---|---|---|---|
| 1 | The formation energy of the neutral oxygen vacancy sets how readily an oxide gives up lattice oxygen, and so its conductivity, reactivity and ionic transport. | Background, not a result: Introduction paragraphs 1 and 2 (`sec:introduction`, with their citations). | none |
| 2 | Machine-learned surrogates predict it from DFT descriptors of the pristine host or from the crystal structure alone. | Background: Introduction paragraphs 3 and 4 (Kumagai et al., Kiyohara et al., Witman et al.). | none |
| 3 | We asked at how many training hosts explicit pristine-host electronic information stops improving a structure-only graph network. | The question of Section 3.3 (`sec:learning_curves`, first sentence) and Introduction paragraph 5. | none |
| 4 | Using 1726 neutral vacancy sites in 818 oxides from the database of Kumagai et al., we trained a graph network on the pristine supercell with the removed oxygen site marked, with and without DFT descriptors, on 25 to 654 training hosts grouped by formula, and tested whether the descriptors lowered the site error by more than 0.05 eV. | Method: Data (`sec:data`, Table 1), Graph Representation (`sec:graph`), Models (`sec:models`), Splits (`sec:splits`), Statistics (`sec:statistics`); restated in the Results preamble. | `\numFilterCascadeStepsFinalSites`, `\numFilterCascadeStepsFinalHosts` (`results/filter_cascade.json`); `\numCfgBudgetsHostsItemOne`, `\numCfgBudgetsMax`, `\numCfgStatsDeltaEV` (`configs/config.yaml`) |
| 5 | On the primary network, adopted post hoc after diagnostics of the originally registered one, the descriptor advantage at 654 training hosts was 0.015 eV (two-sided interval −0.008 to 0.036 eV). | Section 3.3, third paragraph after Figure 2 ("On v2 (post hoc), A = ... at the largest budget"); Table 2 row "A, B = 654 (ceiling)"; chronology in Methods `sec:backbones`. | `\numCOneCTwoVTwoAMaeSixHundredFiftyFourA`, `...CiNinetyFiveItemOne`, `...CiNinetyFiveItemTwo` (`results/c1c2_v2.json`, `A_mae/654`) |
| 6 | On both networks its one-sided upper bound lay below the tolerance at 654, 736.2 and 777.1 training hosts (the last two cross-validation means), but not at 400. | Section 3.3: registered $N^*$ paragraph (654 on both, 400 fails: v1 $U$ 0.067, v2 $U$ 0.075) and the extension paragraph (cross-validation, every upper bound below δ, largest 0.040). | `\numGOnePrimaryNStarNStar`, `\numGOnePrimaryNStarBudgetsTestedItemFive` (`results/g1_primary.json`); `\numCvExtendedBudgetXTrainingHostsKTen`, `...KTwenty` (`results/cv_extended_budget.json`) |
| 7 | The result applies to deep, localised neutral oxygen vacancies in ordered hosts classified as non-magnetic in the release. | Section 3.3, practitioner paragraph ("for deep, localised neutral oxygen vacancies in non-magnetic ordered oxides"); Data `sec:domain`; the qualifier is the Introduction's (last paragraph). | none |
| 8 | Within hosts the descriptors did not improve site ordering, predicting them from structure never beat structure alone, and geometry relaxed with a machine-learned interatomic potential changed the originally registered network's error far less than the tolerance. | Section 3.4 (`sec:within_host`: "Within a host, D is no better than S on either network"; within-host Spearman difference); Section 3.5 (`sec:staging`: "Staging did not beat end-to-end learning from structure at any budget on either network"); Section 3.6 (`sec:geometry`: "MACE-MP-0 geometry measurably degrades the structure-only network, by an amount far inside the tolerance", v1 only). | none in the Abstract; the values are in Results |

## Notes

- Sentence 5 gives the registered-design value of the primary network, whose interval includes zero. The precision
  extension on v2 (thirty resamples, five seeds) gives an interval that excludes zero; that statement is carried by the
  Conclusions and Discussion (Section 4.1), not by the Abstract.
- Sentence 6 uses "on both networks": at 654 on the registered design (v1 $U$ 0.009, v2 $U$ 0.033) and at both
  cross-validation points (v1 $U$ −0.011 and −0.009, v2 $U$ 0.039 and 0.040), all below δ; at 400 the bound is above δ
  on both (v1 0.067, v2 0.075).
- Sentence 8, geometry: measured on the originally registered network only, as the sentence says; no v2 geometry
  evaluation on our relaxations exists.
- Sentences 1 and 2 are background and carry no result; they rest on the Introduction and its citations.
- T2 (2026-10-15) changed terms only: "training hosts" for "training oxides" (sentence 3); "grouped by formula" for
  "split by compound" (sentence 4, the grouping of Methods `sec:splits`); the non-magnetic qualifier moved from
  sentence 4 to sentence 7 in the Introduction's wording; "deep, localised neutral oxygen vacancies" (sentence 7);
  "machine-learned interatomic potential" (sentence 8). No macro, number, claim or caveat changed, and each sentence
  still maps to the Results subsection given in its row.

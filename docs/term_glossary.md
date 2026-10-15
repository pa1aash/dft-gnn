# Term glossary of the manuscript (T1)

Session T1, 2026-10-15. One row per term, symbol or abbreviation of the article and the Supplementary Materials,
with the definition the article uses and the place where it is first defined. Section labels are those of
`paper/sections/*.tex`; "Methods" means `sec:methods` and its subsections. The register follows
`docs/prose_style.md`; this file records usage and does not change it. Every term below is used in the same sense in
the Introduction, Data, Methods and Results after T1. Inconsistencies found in the Abstract, Discussion, Conclusions
and SI, which T1 did not edit, are listed at the end for the next session.

## Physical quantities and data

| Term | Definition used in the article | First defined |
|---|---|---|
| $E_\mathrm{f}$, formation energy | formation energy (eV) of the neutral oxygen vacancy at the reference oxygen chemical potential of the release | Introduction, second paragraph; target fixed in Data (`sec:data`, Source and target) |
| $V_\mathrm{O}^{\times}$ | the neutral oxygen vacancy in Kröger-Vink notation | Data (`sec:data`, Source and target) |
| $V_\mathrm{O}^{\bullet\bullet}$ | the doubly charged oxygen vacancy (Discussion only) | Discussion 4.3 (`sec:disc_domain`) |
| release | the public database of Kumagai et al., pinned to one commit | Data (`sec:data`, Source and target) |
| host, host oxide | one crystal structure of the release; hosts are distinct formulas, so host and formula grouping coincide | Data (`sec:data`, Filter cascade) |
| site | one symmetry-inequivalent oxygen of a host | Data (`sec:data`, Filter cascade) |
| pristine host | the host supercell without the vacancy, as read by the networks | Data and Methods (`sec:graph`) |
| universe, universe v1 | the final set of sites and hosts after the filter cascade D1 to D3 | Data (`sec:data`, Filter cascade) |
| D1, D2, D3 | the three filters of this work, applied in order | Data (`sec:data`, Filter cascade) |
| perturbed-host-state entry | an entry in which the two electrons of the neutral vacancy perturb the host band edge instead of occupying a localised state (shallow donor) | Data (`sec:domain`); gloss also in the Table 1 caption |
| deep, localised vacancy | the domain of every result: vacancies that remain after the perturbed-host-state filter | Data (`sec:domain`) |
| shallow donor | a vacancy whose electrons delocalise into the conduction band; outside the domain | Data (`sec:domain`) |
| non-magnetic | hosts classified as non-magnetic in the release | Introduction, last paragraph (T1 wording); Discussion 4.3 (T1 wording) |
| d0 cation (`\dzero`) | cation with an empty $d$ shell | Data (`sec:domain`) |
| $\mathrm{ICC}_\mathrm{host}$ | one-way random-effects intraclass correlation of $E_\mathrm{f}$ grouped by host | Data (`sec:data`, Source and target) |
| descriptors | DFT quantities of the pristine cell given to D | Introduction, third paragraph; classes in Data (`sec:descriptors`) |
| host-electronic, site-electronic, structural and compositional | the three descriptor classes, by the calculation needed for a new oxide | Data (`sec:descriptors`) |
| isotropic strain $\varepsilon_v$ | cube root of the relaxed-to-DFT volume ratio minus one; positive in every host | Methods (`sec:mlip`); sign in Results (`sec:geometry`) |
| deviatoric strain | Frobenius norm of the traceless stretch tensor after removal of rotation | Methods (`sec:mlip`) |
| internal displacement | RMS displacement of the relaxed fractional coordinates on the DFT lattice, mean removed | Methods (`sec:mlip`) |

## Models and networks

| Term | Definition used in the article | First defined |
|---|---|---|
| graph network | a learned encoder of the local coordination environment of every atom | Introduction, third paragraph (gloss added in T1) |
| backbone | the shared network architecture of MEGNet blocks | Methods (`sec:models`, Graph networks) |
| MEGNet block | one step of aggregation over bonded neighbours; successive blocks span successive coordination shells | Methods (`sec:models`, Graph networks) |
| neighbour list, cutoff | atoms closer than the cutoff are connected in the periodic graph | Methods (`sec:graph`) |
| vacancy flag | marks the oxygen site that is removed | Methods (`sec:graph`) |
| embedding | the learned vector of an atom (element) | Methods (`sec:graph`) |
| global state | the learned vector of the host as a whole | Methods (`sec:graph`) |
| readout | the final step that maps the learned vectors to one energy | Methods (`sec:models`, Graph networks) |
| S | structure-only network | Introduction, sixth paragraph; Methods (`sec:models`) |
| D, D-state, D-late | network given the two electronic descriptor classes; D-state (selected) injects them at the global state and vacancy node, D-late at the readout | Introduction; routes in Methods (`sec:models`) |
| P1, P | P1 predicts the descriptors from structure; the staged model P passes them to D | Methods (`sec:models`) |
| B0 | physics floor, linear in the oxide formation energy and the band gap | Methods (`sec:models`, Baselines) |
| RF-Kumagai, RF-electronic, RF-structural | random forests on all, electronic and structural descriptors | Methods (`sec:models`, Baselines) |
| primary network (v2) | He-uniform initialisation, adopted after diagnostics of v1; every result post hoc | Introduction, sixth paragraph; Methods (`sec:backbones`) |
| originally registered network (v1) | default initialisation; the network of the registered plan | Introduction, sixth paragraph; Methods (`sec:backbones`) |
| S-v2, D-v2, P1-v2, P-v2 | the models on v2 | Methods (`sec:backbones`) |
| seed, seed ensemble | random starting point; mean prediction of the three networks of one resample and budget | Methods (`sec:training`) |
| epoch, early stopping, epoch cap | one pass over the training hosts; stop after no improvement; maximum number of epochs | Methods (`sec:training`) |
| hyperparameters, anchors | settings not learned from the data; the three nested training sets of resample 0 used for tuning | Methods (`sec:tuning`) |
| host-mean oracle | predicts every site with the true mean of its host | Methods (`sec:statistics`) |
| linear probe, ridge regression | linear least-squares fit, with a coefficient penalty, from the readout input of S to each descriptor | Methods (`sec:methods-probe`) |
| MACE-MP-0 | the machine-learned interatomic potential used for the relaxations | Methods (`sec:mlip`) |

## Splits, metrics and statistics

| Term | Definition used in the article | First defined |
|---|---|---|
| training hosts, budget $B$ | number of hosts with DFT labels a model consumes, validation hosts included; the x-axis of every learning curve | Methods (`sec:training`, `sec:splits`) |
| resample | one outer grouped hold-out with its nested training sets | Methods (`sec:splits`) |
| grouped split | every site of one host on the same side | Introduction (T1 gloss); Methods (`sec:splits`) |
| Kiyohara split | the published training, validation and test hosts of Kiyohara et al. | Methods (`sec:splits`) |
| grouped $K$-fold cross-validation | folds over all hosts, every host tested once (extension) | Methods (`sec:splits`) |
| precision extension | twenty further resamples with five seeds at the two largest budgets | Methods (`sec:splits`) |
| leave one chemistry out | folds that hold out whole families of cation chemistry; registered in design, adopted as run under the extension protocol | Methods (`sec:splits`, T1 wording) |
| MAE | site-level test mean absolute error, eV | Methods (`sec:statistics`) |
| within-host residual MAE | MAE of the residuals after removing each host's mean of predictions and of targets | Methods (`sec:statistics`) |
| zero-skill value | within-host residual MAE of a predictor constant within a host; 0.187 eV under the registered resample-mean estimator (`\numHostMeanOracleAggregateWithinHostMaeMean`), 0.184 eV in the site-averaged breakdown (`\numWithinHostBreakdownGroupsPooledAllVOneSZeroSkillMaePoint`) | Methods (`sec:statistics`); the two estimators in Results (`sec:within_host`, T1) |
| $A$ | $\mathrm{MAE}_\mathrm{S} - \mathrm{MAE}_\mathrm{D}$; positive when the descriptors lower the error | Methods (`sec:statistics`) |
| $A_\mathrm{within}$ | the same contrast on the within-host residual MAE | Results (`sec:within_host`) |
| $\delta$, tolerance | 0.05 eV (`\numCfgStatsDeltaEV`); called "tolerance" everywhere after T1 | Introduction (value); Methods (`sec:statistics`) |
| $U$ | one-sided upper bound of $A$, the upper bootstrap quantile | Methods (`sec:statistics`); Results opening paragraph |
| non-inferiority test | asks whether the electronic information still lowers the site error by more than $\delta$ | Methods (`sec:statistics`, T1 gloss) |
| $N^{*}$, $N^{*}_\mathrm{within}$ | smallest tested budget from which $U$ stays below $\delta$ | Methods (`sec:statistics`) |
| ceiling (claim C2) | $A$ at the largest registered budget with its two-sided interval | Methods (`sec:statistics`) |
| $\delta_\mathrm{P}$, equivalence margin | margin of the four-outcome staging rule | Methods (`sec:statistics`, symbol added in T1); Results (`sec:staging`) |
| hierarchical bootstrap, host-cluster bootstrap | resamples then hosts with replacement; hosts only for single partitions | Methods (`sec:statistics`) |
| registered v1, post hoc, extension | provenance labels by chronology; R, PH, E in Table 2 | Methods (`sec:repro`); Table 2 caption |

## Inconsistencies in files T1 did not edit (for the next session)

1. Abstract: "training hosts split by compound"; the body says grouped by formula or by host (Methods `sec:splits`).
   Suggest "split by formula".
2. Abstract, Conclusions (first sentence) and Discussion 4.6 (first sentence): "ordered, non-magnetic hosts/oxides";
   Discussion 4.3 (second sentence) "on ordered hosts that are non-magnetic". The Introduction and the Discussion 4.3
   magnetic-host sentence now say "classified as non-magnetic in the release". Suggest the same qualifier, or one
   pointer, in the Abstract, Conclusions and Discussion 4.6.
3. Abstract: "deep, neutral vacancies"; the body and Conclusions say "deep, localised neutral oxygen vacancies".
4. Keywords: "graph neural network"; the article says "graph network" throughout.
5. Discussion 4.2 (`sec:disc_site`): "within-host error" (twice); Methods and Results define "within-host residual
   MAE". The SI also writes "within-host MAE" in Section S4 and its table. Suggest "within-host residual MAE" at
   first use in each.
6. Abstract: "geometry relaxed with an interatomic potential"; Conclusions "relaxed interatomic-potential geometry";
   Discussion 4.4 "universal interatomic potential"; Methods and Introduction "machine-learned interatomic potential"
   (MACE-MP-0). Suggest "machine-learned interatomic potential" everywhere.
7. Abstract: "training oxides" and "training hosts" in one paragraph; the defined term is training hosts (x-axis
   rule). "Training oxides" also appears in the Introduction and Discussion as a synonym; acceptable in motivation,
   but the Abstract should use one.
8. SI Table S7 (`tab_withinhost.tex`): "PHS-prone cation"; the abbreviation PHS is never defined in the article,
   which spells out "perturbed-host-state". Suggest spelling it out or defining it in the SI.
9. "universe v1" (Data and SI Tables S1, Figure S2 caption) shares the suffix v1 with the originally registered
   network; the two are unrelated. Consider dropping the label in the article or renaming it in a later pass.
10. SI Section S2 (`s2_training.tex`): label written "(registered v1; ...)"; the article tables use R, PH, E and the
   Methods label "Registered v1". Consistent in meaning; no change needed unless the SI adopts the table letters.
11. Introduction (before T1) called the staged model, the geometry evaluation and the probe extensions or post hoc on
   v2 only; Methods, Results and `docs/provenance_labels.md` (#20, #22, #26) record all three as registered for v1.
   T1 corrected the Introduction. The Abstract and Conclusions do not label them and need no change.

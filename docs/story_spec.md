# Story specification for the rewrite (S1)

Session S1, 2026-10-17. This file fixes the story of the rewritten manuscript before any prose is touched. Binding
author decisions (a) to (g) of the S1 brief are applied; the voice rules are in `docs/prose_style.md`, the terms in
`docs/term_glossary.md`, the caveat verdicts in `docs/caveat_ledger.md`, the paragraph verdicts in
`docs/paragraph_map.md` and every undecided point in `docs/open_questions.md`. "The network" is the He-initialised,
validation-tuned network (repository name v2); "default initialisation" names the first configuration (v1), which
appears only in Appendix D and one Methods paragraph. Numbers below are read from `paper/generated/numbers.tex`; in
the paper every one stays a macro. Nothing was computed. Updated after merging task C1 (`a5c11f7`): the two-sided intervals at the cross-validation
sizes are now confirmed (`results/derived_c1/final_network_summary.json`, `docs/c1_final_network_table.md`), so no
wording is pending C1.

## (i) The claim

**Paper claim.** A graph network that reads only the pristine crystal structure of an oxide, with the vacancy site
marked, predicts the neutral oxygen-vacancy formation energy to within 0.05 eV of the same network given the
complete set of pristine-host DFT electronic descriptors, from about 650 training oxides (654 hosts) on.

| # | Supporting claim | Evidence (final network) | Record; claim row |
|---|---|---|---|
| 1 | The descriptor advantage $A = \mathrm{MAE_S} - \mathrm{MAE_D}$ is bounded below $\delta = 0.05$ eV from 654 training hosts on, and not at 400. | 654, 30 resamples x 5 seeds: $A$ = 0.033 eV [0.021, 0.045], $U$ = 0.043. 654, learning-curve design (10 x 3): 0.015 [−0.008, 0.036], $U$ = 0.033. 400: $A$ = 0.054, $U$ = 0.075 (10 x 3); $A$ = 0.066, $U$ = 0.079 (30 x 5). (At 200 the 10 x 3 bound is 0.047; $N^{*}$ is 654 because 400 fails.) Cross-validation, about 736 and 777 hosts: $A$ = 0.024 [0.005, 0.042] and 0.026 [0.010, 0.043], $U$ = 0.039 and 0.040; both intervals inside ±δ (confirmed by C1). | `results/precision_a_b400_b654.json`, `results/c1c2_v2.json`, `results/cv_extended_budget.json`, `results/derived_c1/final_network_summary.json`; PR1, C1/C2, CV1 |
| 2 | What the descriptors still add is small, positive and host-level: at most about 0.04 eV, and nothing within a host. | $A_\mathrm{within}$ at 654 = −0.002 [−0.013, 0.009]; within-host Spearman S − D −0.042 (interval includes 0); ICC_host 0.930; P1 recovers the oxide formation energy best and site-level charges worst. | `results/c1c2_v2.json`, `results/within_host_breakdown.json`, `results/staging_v2.json`; WH1, C3a-v2 |
| 3 | The structure-only route holds up in deployment: predicting the descriptors never beats it, and relaxed geometry barely moves it. | Staging: P never better than S at any budget; at 654, P − S = 0.028 [0.008, 0.053]. Geometry (809 relaxed hosts): $\Delta$MAE of S at 654 = +0.0002 [−0.0025, +0.0026] eV. | `results/staging_v2.json`, `results/mlip_eval_v2.json`; C3a-v2, C3b-809 |

Anchor, not a claim: the network reaches 0.296 eV [0.275, 0.317] on held-out oxides at 654 hosts, against the
published structure-only 0.29 eV (Kiyohara et al.); RF-Kumagai reproduces the published forest within 0.006 eV.

## (ii) Stated limits, each in one place

| Limit | Single home | Elsewhere |
|---|---|---|
| Not within 0.05 eV at 400 training hosts ($U$ = 0.075) | Results 3.2, paragraph 2 | Abstract clause; Conclusions pointer |
| Leave-one-family-out upper bound 0.060 eV, above $\delta$; the excess comes from one family, the alkali group-14 oxides (48 hosts; without it the bound is 0.037 eV; `results/derived_c1/loco_family.json`) | Results 3.2, paragraph 4 | Discussion 4.4 pointer |
| Domain: deep neutral vacancies in ordered non-magnetic oxides, one functional and workflow; the perturbed-host-state filter drops shallow-donor hosts (SrTiO$_3$, BaTiO$_3$); charged vacancies untested | Methods 2.1 (Domain) | Abstract scope clause; Results 3.6 names the absent oxides; Discussion 4.4 one sentence |
| No experimental validation | Discussion 4.4 | none |
| Nothing known beyond about 777 training hosts; CV tests a different population | Results 3.2, paragraph 3 | none |
| Tuning on one resample (mild cross-resample information; Kiyohara overlap) | Appendix B | none |
| Uncorrected multiplicity of the within-host breakdown | Appendix E | Results 3.3 pointer |
| Screening covers 10 sites in 7 hosts | Results 3.6 | none |
| Some S runs at 654 stop at the training-length limit | Appendix F | none |

Removed as limits (they vanish with one network or under rule (c)): sign disagreement between networks, post hoc
status, GPU-class effects, estimator differences between bootstraps, v2-only or v1-only availability.

## (iii) Section map (main text)

| Section | Purpose | Claim carried | Words |
|---|---|---|---|
| Abstract | Question, data, headline number with interval, the 400 limit, two checks, scope | claim + 1-3 | ≤ 200 |
| 1 Introduction | Why $E_\mathrm{f}$ matters (TCOs, catalysis, electrolytes, memristors); DFT cost; two surrogate families; the open budget question; what we measure | sets up claim | 750 |
| 2.1 Data and domain | Release, target, ICC, 818-host dataset (cascade to App. A), descriptor classes, **domain statement (home of L3)** | domain | 450 |
| 2.2 Representation and models | Pristine supercell + vacancy flag; the network as encoder of coordination shells; S, D (D-state), P1/P; B0 and forests | – | 500 |
| 2.3 Training and tuning | Protocol; equal tuning budget; **default-initialisation paragraph** (rule a); **GPU sentence** (rule c) | – | 400 |
| 2.4 Splits | Formula-grouped hold-out with nested budgets; additional resamples; CV; leave-one-family-out; Kiyohara split | – | 250 |
| 2.5 Statistics | MAE, within-host residual MAE, zero skill; $A$; bootstrap; non-inferiority and $N^{*}$; **$\delta$ stated once as fixed before the analysis**; staging rule | – | 350 |
| 2.6 Checks | Geometry protocol (n = 809 relaxed hosts) and probe, one paragraph each, details in App. G, H | – | 150 |
| 3.1 Host and site | ICC; oracle and zero skill; B0 and forests; reproduction of 0.29 eV | anchor | 400 |
| 3.2 Learning curve | Fig. 2; $A$ by budget; $N^{*}$ = 654; interval inside ±δ; 400 limit; CV at about 736 and 777 hosts inside ±δ; leave-one-family-out limit and its family | claim 1 | 800 |
| 3.3 Site resolution | Fig. 3; within-host skill; $A_\mathrm{within}$; Bader-charge reference | claim 2 | 400 |
| 3.4 Staging | Fig. 4; P never better than S; D − P; P1 recovery by class | claim 3 | 350 |
| 3.5 Relaxed geometry | Three components; $\Delta$MAE of S, D, P; table in App. G | claim 3 | 200 |
| 3.6 Screening | Fig. 5, Table 2; absent oxides as a domain result; two energy groups; site pairs | demonstration | 450 |
| 4.1 Why structure suffices | Descriptors are functions of the pristine structure; host thermodynamics dominate; testable prediction (classes given separately) | claim 1, 2 | 450 |
| 4.2 Local chemistry | Within-host spread by d class; Ga/Zr pairs; bonding and relaxation hypothesis | claim 2 | 300 |
| 4.3 Prior work | Kumagai, Kiyohara, Witman, Deml, Linton; what is new | – | 250 |
| 4.4 Scope | Charged vacancies and shallow donors as the next test; **no experimental validation (home)**; family transfer pointer | limits | 300 |
| 5 Conclusions | The claim in physical terms and the practical rule for screening | claim | 180 |

Total main text about 7,000 words, against about 15,500 now (Introduction 1,064; Data 1,199; Methods 4,511;
Results 5,660; Discussion 2,847; Conclusions 282).

## (iv) Length and appendices

**Target: 18 main-text pages** (title to Conclusions, MDPI layout, 5 figures and 2 tables), plus about 2 pages of
back matter and references and about 12 pages of appendices: one PDF of about 32 pages, against 30 + 21 now.
Crystals sets no length limit; 15-20 main pages is common for a computational Article and leaves every
claim-bearing item in the main text. Rough budget: front matter and Abstract 1; Introduction 1.5; Methods 4.5
(with Figure 1); Results 7.5 (Figures 2-5, Tables 1-2); Discussion 2.5; Conclusions 0.5.

| Appendix | Holds | From |
|---|---|---|
| A Data | Filter cascade (table and figure), D1-D3 details, descriptor taxonomy | Table 1, SI S1, Fig. S2 |
| B Network and training | Readout schematic, protocol details, search space, tuned values and validation errors of the network, epoch-limit rule, tuning-overlap note | Methods, Table tuning, SI S2, Fig. S1, Tables S2-S4 |
| C Splits | Split schematic, resample construction, CV folds, cation families, Kiyohara split | SI S3, Fig. S3 |
| D Default-initialisation ablation | One table: default initialisation against the network (S and D MAE, $A$, interval and $U$ at every size, and the within-host spread of the predictions), rendered from `results/derived_c1/default_init_ablation.json` (`docs/c1_ablation_table.md`) | Methods `sec:backbones`, Table 2 v1 column, C1 |
| E Within-host breakdown | Groups table and figure; multiplicity statement | SI S4, Fig. S4, Table S7 |
| F Sensitivities | High-moment exclusion (final-network rerun pending), training-limit counts, untuned CGCNN | SI S6, Fig. S6, Table S6 |
| G Geometry check | Relaxation and mapping protocol, strain components, $\Delta$MAE table | Methods `sec:mlip`, Results 3.6 |
| H Latent probe | Protocol, rule, controls, figure on the network | Methods `sec:methods-probe`, SI S7, Fig. S7 |
| I Screening detail and structures | Full site table, site-pair table, first-shell table, SnO$_2$ render | Tables 3-4, SI S8, Fig. S8 |
| J Statistical details | Hierarchical bootstrap, four-outcome staging rule, multiplicity rule | Methods `sec:statistics` |
| K Code and data | Repository, run identifiers, records, deposit, software versions | Methods `sec:repro`, SI S9 |

Deleted outright: SI S5 and Figure S5, Tables S8-S9 (GPU class, rule c); provenance-label table and deviation
summary (SI S9.3-S9.4, rule b); release-tag table (rule b; stays in the deposit).

## (v) Figures and tables

All figures keep the house style: one network, so one line style (solid, filled); no in-figure annotations,
callouts or text labels; panel letters, axis labels and an outside legend only; one palette and type size across
the set. Information goes in the captions.

| New | Source | Action | Why it is in the main text |
|---|---|---|---|
| Figure 1 | Fig. 1 | Keep; drop the dashed v1 outline from panel a | Defines what each model reads; the vacancy-flag picture is the representation |
| Figure 2 | Figs. 2 + 3 | Merge: (a) MAE of S and D against training hosts, (b) $A$ with ±δ, one-sided bounds, 30 x 5 and CV points | Carries the headline claim |
| Figure 3 | Fig. 6 | Keep, one network: (a) within-host skill, (b) $A_\mathrm{within}$ | Carries claim 2 (no within-host value) |
| Figure 4 | Fig. 4 | Keep, one network | Carries claim 3 (staging never wins) |
| Figure 5 | Fig. 7 | Keep, one network | The only view of named oxides and of the domain |
| – | Fig. 5 | Remove from main text: drawn on default initialisation; geometry becomes a paragraph plus Appendix G table | A check, not a claim (rule g) |
| Fig. A1-A2, C1 | Figs. S2, S3 | Move | Reference |
| Fig. B1 | Fig. S1 | Move | Reference |
| Fig. E1 | Fig. S4 | Move, one network | Reference |
| Fig. F1 | Fig. S6 | Rebuild once the final-network sensitivities exist | Reference |
| Fig. H1 | Fig. S7 | Redraw from the network's probe record | Check (rule g) |
| Fig. I1 | Fig. S8 | Move | Reference |
| – | Fig. S5 | Delete | Rule (c) |

| New table | Source | Action |
|---|---|---|
| Table 1 Main results | Table 2 (`tab:headline`) | Keep, one value column, no label column; rows: ICC, oracle, B0, RF-Kumagai, S at 654, $A$ at 400 and 654 (both designs), CV $A$ at $K$ = 10 and 20, leave-one-family-out $A$, P − S at 654, $\Delta$MAE of S |
| Table 2 Screened sites | Table 3 | Keep, slimmed to oxide, site, cations, DFT, prediction, $N$; full columns to Table I1 |
| Tables A1-A2, B1-B3, C1, D1, E1, F1, G1, I1-I3 | Table 1, tuning table, SI tables | Move; Table D1 is the only place default-initialisation numbers appear |

## (vi) Proposed Abstract (199 words)

The formation energy of the neutral oxygen vacancy sets how readily an oxide releases lattice oxygen, and with it
conductivity, catalytic activity and ionic transport. Surrogates predict it from density-functional theory (DFT)
descriptors of the pristine host or from the crystal structure alone. We asked how many
computed oxides a graph network needs before structure alone suffices. Using 1726
vacancy sites in 818 oxides from the database of Kumagai et al., we trained one graph network on the pristine
supercell with the vacancy site marked, with and without all pristine-host electronic descriptors,
on 25 to 654 training oxides grouped by formula. From 654 training oxides the structure-only network matches the
descriptor network to within 0.05 eV: the descriptors lower the site error by 0.033 eV (95% interval 0.021 to 0.045 eV;
one-sided bound 0.043 eV). At 400 oxides their advantage is not bounded below 0.05 eV. What they still add places
each oxide, not the sites within one. Predicting the descriptors from structure never beats structure
alone, and relaxed geometries from a machine-learned interatomic potential change the structure-only error by less
than 0.003 eV. For deep neutral vacancies in ordered non-magnetic oxides, the pristine-host DFT calculation can be
skipped.

# R4 changes to the main text

Session R4, 2026-10-17. The text fixes of the R4 brief (Part 2, items 1-9), each with its place and its reason. The
answers they rest on are in `docs/r4_verification.md`. Every new number is a macro; `paper/tools/check_macros.py`
reports 0 undefined and 0 typed numbers.

## New curated macros (`paper/tools/net_macros.py`)

| Macro | Prints | Source |
|---|---|---|
| `\numNetTolerance` | 0.05 | `configs/config.yaml#/stats/delta_eV`, format `trim` (trailing zeros dropped) |
| `\numNetPublishedMae` (format changed) | 0.29 (was 0.290) | `results/c0_official.json#/payload/comparison_eV/kiyohara_published`, `trim` |
| `\numNetStagingDeltaP` (format changed) | 0.05 (was 0.050) | `results/staging_v2.json#/payload/delta_P_eV`, `trim` |
| `\numNetReleaseOxides` | 937 | `results/structure_audit.json#/payload/polymorph/release_hosts` |
| `\numNetDescriptorsHost`, `\numNetDescriptorsSite` | 12, 10 | `results/staging_v2.json#/payload/p1_descriptors/654/by_class/{host,site}_electronic/n_descriptors` |
| `\numNetIllusTemperature`, `\numNetIllusDeltaE`, `\numNetIllusKT`, `\numNetIllusFactor` | 1000, 0.3, 0.086, 30 | the Boltzmann-factor example (item 1): exp(ΔE/k_BT) with k_B from `scipy.constants` (CODATA), T = 1000 K, ΔE = 0.3 eV; raw factor 32.50, printed to one significant figure |

The module docstring records two additions: the `trim` format, and the illustration block. That block is the only
curated macro that is not a record leaf.

## Items 1-7 and 9

| Item | Place | Before | After |
|---|---|---|---|
| 1 | Introduction p2 | "an error of a few tenths of an electronvolt ... shifts it by orders of magnitude" | the concentration changes by the factor exp(ΔE_f/k_BT); at 1000 K, k_BT = 0.086 eV, and an error of 0.3 eV changes it by a factor of about 30 |
| 2a | Introduction p3; Methods 2.1 p2 | "for 935 oxides"; "The release holds 2103 ... in 935 hosts" | "for 937 oxides"; "The release covers 937 oxides and holds 2103 completed neutral calculations in 935 of them" |
| 2b | Introduction p4, Methods 2.5, Results 3.1, Discussion 4.3 | 0.290 eV | 0.29 eV (macro format) |
| 2c | Introduction p4, Discussion 4.3 | Kumagai learning-curve sentences | unchanged: K21 Fig. 5 and Sec. III D, quoted in `docs/claim_check.md` (a), support them |
| 3 | Abstract s4; Introduction p6; Methods 2.1 p3, 2.2 p3; Conclusions p1 | "all pristine-host descriptors" / "every pristine-host and pristine-site electronic descriptor" / "every pristine-host descriptor" | "the 22 pristine-cell electronic descriptors, 12 host-level and 10 site-level". The Abstract uses the short form "22 pristine-cell electronic descriptors (12 host-level, 10 site-level)". Methods 2.1 also: "cation neighbours" → "Voronoi neighbours" (taxonomy definition) |
| 3 | Abstract | 196 words | 199 words. Changes: "descriptors of the pristine host" → "descriptors" (s2; s4 now states the set), "before structure alone suffices" → "before structure suffices", "grouped by formula" → "formula-grouped", "descriptor-based forest" → "descriptor forest", "machine-learned relaxation of the host" → "machine-learned host relaxation". Every number kept |
| 4 | Conclusions s1 | "carries the information that the DFT electronic structure of the host adds" | "carries nearly all of the information ... (the descriptors still lower the error by 0.033 [0.021, 0.045] eV)". s2 and the practical rule stay. s2 repeats the same interval, because the brief keeps s2 as it is |
| 5 | Abstract (2x), Introduction p6, Methods 2.5, Table 1 caption, Conclusions s2, Methods 2.5 (δ_P) | 0.050 | 0.05 (`\numNetTolerance`, `\numNetStagingDeltaP`). No main-text figure prints the value |
| 6 | Results 3.2 last paragraph | "the alkali oxides of the tetrels, the group of Si, Ge and Pb (Cs, K and Rb germanates, silicates and plumbates; 48 hosts)" | "the alkali tetrelates (silicates, germanates, stannates and plumbates of the alkali metals; 48 hosts)". The brief's wording leaves out the stannates, and R3's "Cs, K and Rb" leaves out Li and Na. Family `1-14` of `splits/loco_v1.json` (`host_family`), mapped to formulas by `data/universe_v1_ids.csv`, holds 48 hosts: 16 stannates (for example K2SnO3, Na4SnO4, Rb2SnO3), Li and Na compounds (Li2SiO3, Na2GeO3, Li4PbO4), and Cs, K and Rb compounds. The term appears nowhere else in the main text |
| 7 | Introduction p6 | staging question without motivation | "whether predicting them from structure first, as staged pipelines for vacancies in alloys predict Bader charges before the energy \citep{Linton2026framework}, beats learning the energy directly". The key was already in refs.bib, so nothing was added to pending_edits |
| 9 | Abstract s8 | "Predicting them from structure never beats structure alone" | "At the tuning and training length used, predicting them from structure never beats structure alone" |
| 9 | Results 3.4 p1 | "P is never better than S (Figure 4)." | "At the tuning and training length used, P is never better than S (Figure 4); P1 kept the settings tuned under the default initialisation (Section 2.3)." |
| 9 | Discussion 4.1 last paragraph | "Staging costs accuracy for a related reason: ..." | opens "At the tuning and training length used, staging costs accuracy"; names P1's tuning and its epoch-limit count (20 of 30 at 654) as a second possible source of the cost, and gives the two checks that separate the sources (item 8) |
| 9 | Conclusions s2 | "and predicting them from structure never beats ..." | "and, at the tuning and training length used, predicting them from structure never beats ..." |
| 9 | Table 1 row | "MAE_P - MAE_S, B = 654" | "MAE_P - MAE_S, B = 654, at the tuning and training length used" |
| 9 | Methods 2.3 p2-p3 | "Every model received the same search space and the same number of trials"; "re-tuned S and D ...; P1 kept its tuned settings under the new initialisation" | "Under the default initialisation every model, S, D and P1, received the same search space and the same number of trials ... (for P1 the error over the standardised descriptors)"; "re-tuned S and D ... with the same search space and 30 trials on each of the three sets ... P1 was not re-tuned: it was trained with the He initialisation and the settings tuned for it under the default initialisation, so the staged model P received no tuning trials under the initialisation used for S and D" |
| 9 | Introduction p6 | "the same tuning budget for every model" | "the same tuning budget for S and D" (the old sentence was wrong for P1 under He initialisation) |

## Item 8: calibration of Results 3.3 and Discussion 4.1 and 4.2

The rule applied: every mechanism has its evidence beside it, and a bonding or relaxation explanation is worded as one
"We propose" with the measurement that motivates it and the measurement that would test it. No hedge was stacked and
no refrain added. The count of hedge words (may, might, could, perhaps, possibly, suggest, appear, seem) over
the main-text sections is the same as after R3: one, the conditional "could" of the opening question of Results 3.4,
which is pre-existing.

| Place | Before | Change and reason |
|---|---|---|
| Results 3.3, last sentence | "The site-to-site spread itself follows the cation d shell: ..." | "is larger in hosts with a filled cation d shell: ...". The measurement is a difference between two groups, not a dependence, and Results report measurements |
| Discussion 4.1 p2, last sentence | "The coordination of the oxygen, the strength of its M-O bonds and the stability of the lattice set how much the broken bonds cost and where the two electrons can go, and all three are written in the structure." | asserted with no evidence. Replaced by the evidence the paper cites: "Descriptor studies tie the vacancy energy to the oxide formation enthalpy and the band gap \citep{Deml2014oxide,Deml2015intrinsic,Wexler2021factors}, and both are properties of the pristine lattice that the structure fixes." |
| Discussion 4.1 p3 (host-thermodynamics proposal) | "Three measurements point there" followed by four items, of which one (B0 at 0.722 eV) does not bear on what the descriptors add at 654 hosts, and "an untrained encoder ... already exposes much of the descriptor variance" with no number | "Three measurements motivate the proposal", now exactly three: (1) ICC_host with A_within = -0.002 eV, so what the descriptors add acts between hosts; (2) P1, which has the architecture of S, recovers the formation energy at R^2 0.966, and the host class better than the site class (0.751 against 0.613); (3) RF-structural 0.386 against RF-electronic 0.423 eV, with the probe stated by its numbers (untrained 0.557 against trained 0.555 mean R^2 at 654 hosts, `results/probe_descriptive.json#/payload/s_v2/all/curves/init0/654/mean` and `.../trained/654/mean`). The two predictions are unchanged |
| Discussion 4.1 p4 (staging cost) | "Staging costs accuracy for a related reason: the descriptors it passes on carry their largest prediction errors in the site-level charges ..." | the cause was asserted, and the untuned P1 and its training-length limit were not mentioned. Now: one "We propose" (the cost sits in the site-level descriptors), with its evidence (site class worse than host class, Bader charge R^2 0.387), the second possible source (P1 not re-tuned, at the limit in 20 of 30 runs at 654), and the two checks that separate them (noise injection at P1's per-descriptor error, class by class; P1 re-tuned under He and trained longer) |
| Discussion 4.2 p1 (local bonding and relaxation) | "That reading explains why the Bader charge ranks ... and why pristine-site descriptors give D no within-host advantage; a breakdown ... would test it." | "explains" claimed more than the evidence allows. Now: "Two measurements motivate the proposal" (Bader rank correlation 0.043; A_within = -0.002 [-0.013, 0.009] eV), with one test for each part: the residual breakdown by coordination number and M-O bond length for the bonding, and the cation displacements in the relaxed defect cells of the release for the relaxation, which had no test before |
| Discussion 4.2 p2 (d-shell mechanism) | "The cation d shell sets the size of the spread", followed by the d0 and d10 bonding mechanisms stated as fact, and "The screened pairs follow this picture" | "sets" was causal on a two-group difference. Now: the measurement ("The spread is larger with filled cation d shells: ..."), then "We propose that the bonding sets this difference" with the mechanism, its prediction (coordination number orders the sites of d0 hosts better than those of filled-d hosts) and the test (the breakdown above). The pairs are now said to "bear on it", not to "follow this picture", and ZrO2, a d0 host whose four-coordinate site lies below a three-coordinate one, is stated to run against the bond-count picture for d0 hosts. Before, the text claimed that both pairs supported it |

## Not changed

- Kumagai learning-curve sentences (item 2c): the repository shows the source (`docs/r4_verification.md` (c)).
- The staging numbers, outcomes and figure: only the qualifier was added.
- Appendices, `paper/si/`, `paper/main.tex` (the title already reads 0.05~eV) and refs.bib.

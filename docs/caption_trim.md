# Caption trim (F2)

Every figure caption of the article and the Supplementary Materials is at most 3 sentences (target 2) and at most
70 words. A caption says what is plotted (sentence 1), how to read it (sentence 2: marker and line encoding, what
the bars and bands are, and the registered, post hoc and extension labels where a figure mixes them) and,
optionally, where the data come from (sentence 3). Interpretation, results and methods detail belong in the body.
`scripts/check_captions.py` enforces the limits (`make check-captions`, also run by the pre-push hook).

## 1. Caption sources (inventory, compiled before any edit)

### 1.1 Printed figure captions (in scope, trimmed)

The article and the SI print only the inline `\caption{...}` of the figure environments below; no caption is
read from a file. These are the 15 enforced captions.

| Figure | Label | Source |
|---|---|---|
| 1 | `fig:schematic` | `paper/sections/methods.tex` |
| 2 | `fig:learning_curves` | `paper/sections/results.tex` |
| 3 | `fig:advantage` | `paper/sections/results.tex` |
| 4 | `fig:staging` | `paper/sections/results.tex` |
| 5 | `fig:geometry` | `paper/sections/results.tex` |
| 6 | `fig:within_host` | `paper/sections/results.tex` |
| 7 | `fig:screening` | `paper/sections/results_screening.tex` |
| S1 | `fig:readout` | `paper/si/sections/s2_training.tex` |
| S2 | `fig:cascade` | `paper/si/sections/s3_splits.tex` |
| S3 | `fig:splits` | `paper/si/sections/s3_splits.tex` |
| S4 | `fig:withinhost` | `paper/si/sections/s4_withinhost.tex` |
| S5 | `fig:gpu` | `paper/si/sections/s5_hardware.tex` |
| S6 | `fig:sens` | `paper/si/sections/s6_sensitivities.tex` |
| S7 | `fig:probe` | `paper/si/sections/s7_probe.tex` |
| S8 | `fig:sno2` | `paper/si/sections/s8_structures.tex` |

### 1.2 Table captions (not in scope)

The other 15 `\caption` commands of `paper/sections/` and `paper/si/sections/` belong to tables (main:
`tab:filter_cascade`, `tab:tuning`, `tab:headline`, `tab:screening_sites`, `tab:screening_pairs`; SI: the
cascade, descriptor classes, search space, tuned v1 and v2 values, capped runs, within-host groups, N1, GPU class,
first shell and the reproducibility tables). The task covers figure captions only, so they are unchanged and the
check does not parse them.

### 1.3 Caption files beside the figures (not printed, not edited)

These Markdown files record a caption next to each figure file. None is read by `paper/` (W3 reworded the SI
captions from them into the register, and the article captions were written in the section files). Most are
written by the figure code, which is outside the F2 scope, so an edit here would be overwritten at the next
regeneration. `python3 scripts/check_captions.py --figure-files` reports their counts without failing on them.

| File | Written by |
|---|---|
| `figures/main/fig1_overview.caption.md` | by hand (F1b/W3) |
| `figures/main/fig1_zno_vacancy.caption.md` | by hand (render of record) |
| `figures/main/fig2_learning_curves.caption.md` | `figures/code/fig2_learning_curves.py` |
| `figures/main/fig3_advantage.caption.md` | `figures/code/fig3_advantage.py` |
| `figures/main/fig4_staging.caption.md` | `figures/code/fig4_staging.py` |
| `figures/main/fig5_geometry.caption.md` | `figures/code/fig5_geometry.py` (the F1b "caption file" of Fig 5) |
| `figures/main/fig6_within_host.caption.md`, `fig_within_host.caption.md` | `figures/code/fig_within_host.py` (byte-identical copy kept, F1c) |
| `figures/main/fig7_screening.caption.md` | `figures/code/fig7_screening.py` |
| `figures/si/fig_readout.caption.md` | by hand (F1c) |
| `figures/si/fig_cascade.caption.md`, `fig_splits.caption.md` | `figures/code/fig_si_schematics.py`, from `schematics/*.caption.md` |
| `figures/si/fig_si_withinhost_groups.caption.md` | `figures/code/fig_si_withinhost_groups.py` |
| `figures/si/fig_si_gpu_class.caption.md` | `figures/code/fig_si_gpu_class.py` |
| `figures/si/fig_si_sensitivities.caption.md` | `figures/code/fig_si_sensitivities.py` |
| `figures/si/fig6_probe.caption.md` | `figures/code/fig6_probe.py` |
| `figures/si/structure_sno2_vacancy.caption.md` | by hand (F1c) |
| `figures/si/fig_g1_learning_curves.caption.md` | `figures/code/fig_g1_learning_curves.py` (unnumbered, not cited) |
| `schematics/fig_pipeline.caption.md`, `fig_cascade.caption.md`, `fig_readout.caption.md`, `fig_splits.caption.md` | by hand (captions of record of the schematics) |

The schematics pages of the SI (Figures S1 to S3) print the inline captions of section 1.1, not these files.

## 2. Counts

Counted by `scripts/check_captions.py` (a formula, a path and a macro each count as one word; labels are not
counted). Targets: at most 3 sentences, at most 70 words.

| Figure | Label | Sentences before | Sentences after | Words before | Words after |
|---|---|---|---|---|---|
| 1 | `fig:schematic` | 10 | 2 | 239 | 70 |
| 2 | `fig:learning_curves` | 8 | 3 | 222 | 69 |
| 3 | `fig:advantage` | 6 | 3 | 149 | 64 |
| 4 | `fig:staging` | 9 | 3 | 181 | 70 |
| 5 | `fig:geometry` | 6 | 3 | 199 | 70 |
| 6 | `fig:within_host` | 7 | 3 | 167 | 58 |
| 7 | `fig:screening` | 9 | 3 | 185 | 70 |
| S1 | `fig:readout` | 5 | 2 | 154 | 69 |
| S2 | `fig:cascade` | 5 | 2 | 136 | 54 |
| S3 | `fig:splits` | 8 | 2 | 166 | 50 |
| S4 | `fig:withinhost` | 8 | 3 | 230 | 70 |
| S5 | `fig:gpu` | 10 | 3 | 196 | 70 |
| S6 | `fig:sens` | 11 | 3 | 245 | 70 |
| S7 | `fig:probe` | 9 | 3 | 221 | 70 |
| S8 | `fig:sno2` | 5 | 3 | 152 | 61 |
| all | | 116 | 41 | 2842 | 985 |

## 3. Where the removed material went

Classes: (a) interpretation or fact already stated in the body, deleted; (b) interpretation or result not in the
body, moved to the paragraph that first cites the figure; (c) methods detail, moved to or already in Methods or
the SI text; (d) redundant, deleted. A destination marked "already" means the body already said it and nothing
was added. No removed sentence needed a value without a macro, and none went to the Discussion: every physical
reading in the old captions is already stated in Results, Section 4 or the SI text.

### Figure 1 (`fig:schematic`)

| Removed (before text, abridged) | Class | Destination |
|---|---|---|
| Every graph network starts from the pristine host supercell; the removed oxygen stays and carries a binary vacancy flag | (c) | already: Methods, Graph representation (`sec:graph`) |
| S predicts $E_\mathrm{f}$ from the structure alone; D receives the descriptors, host class at the global state and site class at the vacancy node | (c) | already: Methods, Graph networks |
| P is staged: P1 predicts the standardised descriptors, D trained on true descriptors maps them to $E_\mathrm{f}$ | (c) | already: Methods, Graph networks |
| The baselines are RF on the Kumagai descriptors and B0, linear in formation energy and band gap | (c) | already: Methods, Baselines |
| v1 differs only in its weight initialisation (Section `sec:backbones`) | (c) | already: Methods, `sec:backbones` |
| "as it enters the data set", "PBEsol(+U) ... of the database" | (d) | deleted |
| The structure is the pristine host, not the relaxed defect cell | (a) | already: Methods, `sec:graph` (second paragraph) |

### Figure 2 (`fig:learning_curves`)

| Removed | Class | Destination |
|---|---|---|
| "Learning curves of the neutral oxygen-vacancy formation energy" (title) | (d) | deleted |
| D "also receives the DFT electronic descriptors of the pristine host and of the oxygen site" | (c) | already: Methods, Graph networks |
| The prediction for a site is the mean over networks from three sets of random starting weights | (c) | already: Methods, Training protocol |
| Bands are intervals of the paired hierarchical bootstrap over outer resamples and test hosts, clipped at the axis limits | (c) | already: Methods, Statistics; caption keeps "two-sided bootstrap intervals" |
| "which do not depend on the network"; "(the primary network evaluated on it is post hoc)" | (d) | deleted (v2 is labelled post hoc in the caption) |
| Precision extension = more resamples and seeds at the two largest budgets; CV at the mean fold training size; drawn as unconnected points | (c) | already: Methods, Data splits; Results `sec:learning_curves` ("its training sizes are fold means") |
| CV tests every host once, so its points are not directly comparable with the budget points | (a) | already: Results `sec:learning_curves`, paragraph on the two extensions |

### Figure 3 (`fig:advantage`)

| Removed | Class | Destination |
|---|---|---|
| "(positive when the descriptors lower the site error)" | (c) | already: Methods, Statistics (Advantage of the descriptors) |
| "where the decision on the tolerance is made" | (a) | already: Results `sec:learning_curves` |
| $N^{*}$ is the smallest budget whose upper bound lies below $\delta$ there and at every larger budget | (c) | already: Methods, Statistics (Non-inferiority and $N^{*}$) |
| Registered and precision points use the hierarchical bootstrap, CV points a host-cluster bootstrap | (c) | already: Methods, Statistics (Hierarchical bootstrap) |
| "(registered design, $N^{*}$ and the ceiling)" after the record name | (d) | deleted (record kept) |

### Figure 4 (`fig:staging`)

| Removed | Class | Destination |
|---|---|---|
| P1 predicts the descriptors from the pristine structure and passes them to D of the same resample, budget and seed | (c) | already: Results `sec:staging` first paragraph; Methods, Graph networks |
| "the cost of predicting rather than computing" and "staging against end-to-end learning"; sign readings "(negative: P worse than D)", "(negative: P better than S)" | (a) | already: Results `sec:staging` first paragraph defines both contrasts |
| The outcome follows the four-outcome equivalence rule, which is post hoc | (a) | already: Results `sec:staging`; Methods, Statistics (Staging) |
| "the registered staging analysis" | (d) | kept as the label "(v1, registered)" |
| One draw set for all models, budgets and both networks | (c) | already: Methods, Statistics (Hierarchical bootstrap) |
| Bands of D in (a) and of the cost contrast in (b) at the smallest budgets are clipped | (d) | condensed to "clipped at the axes" |

### Figure 5 (`fig:geometry`)

| Removed | Class | Destination |
|---|---|---|
| Trained on DFT geometry, evaluated without retraining; MACE-MP-0 medium model, double precision, cell and positions, tiled onto the release supercells; rescaled isotropically to the DFT volume | (c) | already: Methods `sec:mlip`; Results `sec:geometry` first paragraph |
| D keeps its DFT descriptors so that its change isolates the structural input | (a) | already: Results `sec:geometry` second paragraph; Methods `sec:mlip` |
| Bars are intervals of the paired hierarchical bootstrap | (c) | already: Methods, Statistics; caption keeps "two-sided bootstrap intervals" |
| $\varepsilon_v$ is the component with the largest coefficient for S and P in the joint regression | (a) | already: Results `sec:geometry` third paragraph |
| Hosts whose change is exactly zero (D on the rescaled geometry only) are not drawn | (b) | moved: Results `sec:geometry` third paragraph ("Only D on the rescaled geometry leaves the prediction of some hosts exactly unchanged; these hosts are absent from the logarithmic panels b to d."); the caption keeps "hosts with no change are absent from the logarithmic axes" |
| No evaluation of v2 on these relaxations exists | (a) | already: Results `sec:geometry` last paragraph |

### Figure 6 (`fig:within_host`)

| Removed | Class | Destination |
|---|---|---|
| "(structure only)", "(structure plus the DFT descriptors of the pristine host and site)" | (c) | already: Methods, Graph networks |
| On test hosts with at least two oxygen sites | (c) | already: Methods, Statistics (Metrics) |
| Zero means that the model places hosts but does not distinguish the sites of a host | (a) | already: Results `sec:within_host` first paragraph; Methods, Metrics (zero-skill value) |
| Bands are intervals of the paired hierarchical bootstrap; CV test sets differ from the registered ones | (a) | already: Results `sec:learning_curves`; caption refers to the encoding of Figure 2 |

### Figure 7 (`fig:screening`)

| Removed | Class | Destination |
|---|---|---|
| "both networks"; list of the screened oxides; each held out in at least one outer resample | (a) | already: Results `sec:screening` first, second and fourth paragraphs |
| The markers of the two networks for one site are offset horizontally by a small fixed amount | (d) | deleted |
| Grouped by oxide in ascending order of its mean DFT energy; the dotted line is zero error | (d) | deleted (the oxides are named on the axis) |
| Colour identifies the oxide | (d) | deleted (legend) |
| A marker is the mean of the seed-ensemble prediction over the resamples in which the host was held out | (c) | already: Results `sec:screening` first paragraph; caption keeps "mean and range over resamples holding the host out" |
| A site held out once has no bar | (d) | deleted (a range of one value) |
| A structure render of an SnO$_2$ site is given as Supplementary Figure S8 | (b) | moved: Results `sec:screening`, paragraph that first cites Figure 7a |
| "for the absent candidates" before the third record | (d) | deleted (record kept) |

### Figure S1 (`fig:readout`)

| Removed | Class | Destination |
|---|---|---|
| Each MEGNet block widens the coordination shell that informs every atom | (c) | already: SI S2.1 text |
| Pooling is Set2Set or the mean, a tuned choice | (c) | already: SI S2.1 text and Table S3 |
| The host-level thermodynamic term is carried by $\bar{\mathbf{h}}$ and $u$, the local environment by $\mathbf{h}_\mathrm{v}$ | (a) | already: SI S2.1 text |
| Descriptors standardised with training-set statistics; the readout is unchanged and the same for both networks | (c) | already: SI S2.1 text |

### Figure S2 (`fig:cascade`)

| Removed | Class | Destination |
|---|---|---|
| The machine-learning subset already excludes perturbed-host-state entries, undetermined band edges and unstable hosts | (c) | already: SI S1 text; article Table 1 caption |
| Definitions of D1, D2 (Sr$_2$Zr$_7$O$_{16}$) and D3 (removes nothing) | (c) | already: SI S1 text (integrity exclusions) |

### Figure S3 (`fig:splits`)

| Removed | Class | Destination |
|---|---|---|
| Every split keeps all sites of a host on one side | (c) | already: SI S3 first paragraph |
| (a) test hosts per resample, stratification, nested ordering, validation carve-out | (c) | already: SI S3 text; Methods, Data splits; SI S2.2 |
| (b) the networks train, stop early and are tested on the published split | (c) | already: SI S3 text |
| (c) $K$ values, every host tested once, larger training sets | (c) | already: SI S3 text; Methods, Data splits |
| (d) families from the periodic-table groups of the cations, folds, transfer | (c) | already: SI S3 text |
| "not to scale" | (d) | deleted ("widths are schematic" kept) |

### Figure S4 (`fig:withinhost`)

| Removed | Class | Destination |
|---|---|---|
| "by chemistry and site"; "lower is better" | (d) | deleted |
| A model point at or right of the zero-skill tick has no within-host skill | (a) | already: SI S4 first paragraph |
| Circles are point values | (d) | deleted |
| Intervals paired across models and networks | (c) | moved: SI S4 first paragraph ("a host-cluster bootstrap paired across models and networks") |
| No bar where too few hosts contribute | (a) | already: SI S4 last paragraph (small-group threshold) |
| v2 "adopted after diagnostics of the originally registered network" | (a) | already: Methods `sec:backbones` |
| Each host under every cation it contains; all tested hosts as the top row; the full panel definitions | (c) | already: SI S4 last paragraph (overlapping cation groups); panel definitions shortened to one clause each |
| Each site's prediction is the seed ensemble averaged over the registered resamples | (c) | already: SI S4 second paragraph |

### Figure S5 (`fig:gpu`)

| Removed | Class | Destination |
|---|---|---|
| $A$ of single runs averaged over cells in which the S and D runs of the same resample or fold, budget and seed ran on one class | (c) | already: SI S5 text and Table S9 caption |
| The classes are the GPU models of the cluster pool, read from the run records; "sweep" is precision only | (c) | already: SI S2.4 and S5 text |
| GPU class was not randomised, so differences are not read as hardware effects | (a) | already: SI S5 text; Results `sec:sensitivities` |
| Classes without a paired cell are not drawn | (d) | deleted |
| Diamonds: precision; triangles: cross-validation | (d) | deleted (panels a, b and c, d already separate them) |

### Figure S6 (`fig:sens`)

| Removed | Class | Destination |
|---|---|---|
| Definition of $A$ and its sign; seed-ensemble MAE averaged over the registered resamples | (c) | already: Methods, Statistics |
| Definitions of the high-moment exclusion and of the capped twins | (c) | already: SI S6 text |
| Both sensitivities exist for v1 only | (a) | already: SI S6 first paragraph |
| Hierarchical bootstrap in (a), host-cluster bootstrap in (b) | (c) | already: Methods, Statistics (single partitions use the host-cluster bootstrap) |
| One outer resample at three budgets; CGCNN with fixed, untuned optimiser settings; crosses drawn just right of their budget | (c) | already: SI S6 third paragraph; the drawing offset deleted (d) |
| With one resample the intervals reflect test-host sampling only, and no test is made | (a) | already: SI S6 third paragraph |
| Dashed line $\delta$, dotted line zero | (d) | deleted (reference lines as in Figure 3) |

### Figure S7 (`fig:probe`)

| Removed | Class | Destination |
|---|---|---|
| A linear map fitted on the training hosts of each resample and budget, from the vectors the final step reads | (c) | already: SI S7 first paragraph; Methods `sec:methods-probe` |
| "(the registered random-initialisation control)"; the further untrained networks "show the spread of that control and are descriptive" | (c) | already: SI S7 second paragraph |
| Logarithmic axis; dotted zero line; host descriptors above the grey rule in (c) | (d) | deleted |
| The registered rule does not hold, so the probe is placed in the SI | (a) | already: SI S7 third paragraph; Results `sec:probe` |
| The collaborator's probe on v2 is post hoc and is not drawn | (b) | moved: SI S7 third paragraph ("not drawn in Figure S7") |

### Figure S8 (`fig:sno2`)

| Removed | Class | Destination |
|---|---|---|
| "as it enters the data set"; the planar three-fold coordination of oxygen in rutile | (a) | already: SI S8 first paragraph |
| Neighbours drawn enlarged, translucent triangle with dark edges, seen nearly edge-on | (c) | moved: SI S8 second (new) paragraph |
| The cell is shifted by lattice translations only so that the vacancy lies near the faces closest to the viewer | (c) | moved: SI S8 second paragraph |
| The structure is the pristine host, not the relaxed defect cell | (a) | already: SI S8 first paragraph |
| Same camera conventions, lights and materials as Figure 1b; Blender Cycles on the CPU with samples, denoising and dpi | (c) | moved: SI S8 second paragraph, with the existing macros `\numRenderSnOTwoSamples` and `\numRenderSnOTwoDpi` |

## 4. Captions before and after


### Figure `fig:schematic`

Source: `paper/sections/methods.tex` (line 21).

Before (239 words, 10 sentences):

> Models and input representation. (\textbf{a}) Every graph network starts from the pristine host supercell of the reference calculation, in which the oxygen atom to be removed stays in place and carries a binary vacancy flag. \textbf{S} predicts the neutral oxygen-vacancy formation energy $E_\mathrm{f}$ from the structure alone. \textbf{D} receives the same graph plus the DFT descriptors of the pristine host and site: the host-electronic class is appended to the initial global state and the site-electronic class to the initial features of the vacancy node. \textbf{P} is staged: P1, with the backbone and readout of S, predicts the standardised descriptors of D from the structure, and D, trained on true descriptors, maps the structure and the predicted descriptors to $E_\mathrm{f}$. The baselines are random forests on the descriptors of Kumagai et al.\ (\textbf{RF}) and the physics floor \textbf{B0}, a linear model in the oxide formation energy and the band gap. The solid, filled box is the primary backbone (v2); the dashed, open outline behind it is the originally registered backbone (v1), which differs only in its weight initialisation (Section~\ref{sec:backbones}). (\textbf{b}) The neutral oxygen vacancy in wurtzite ZnO as it enters the data set: the pristine PBEsol(+$U$) supercell of the database (\numStructureAuditZnoCifNAtoms{} atoms), with the removed oxygen site marked by the translucent amber sphere and its four nearest Zn neighbours joined into the coordination tetrahedron. Zn grey-blue, O red. The structure is the pristine host, not the relaxed defect cell.

After (70 words, 2 sentences):

> Models and inputs, with (\textbf{a}) the graph networks S, D and P and the baselines RF and B0, and (\textbf{b}) the pristine wurtzite ZnO supercell (\numStructureAuditZnoCifNAtoms{} atoms). The solid, filled box is the primary backbone (v2) and the dashed, open outline the originally registered backbone (v1), and in (\textbf{b}) the amber sphere marks the oxygen to be removed and the tetrahedron its Zn neighbours, with Zn grey-blue and O red.

### Figure `fig:learning_curves`

Source: `paper/sections/results.tex` (line 32).

Before (222 words, 8 sentences):

> Learning curves of the neutral oxygen-vacancy formation energy. Site-level MAE on held-out host oxides against the number of training hosts (logarithmic axis) for (\textbf{a}) the structure-only network S and (\textbf{b}) the network D, which also receives the DFT electronic descriptors of the pristine host and of the oxygen site. Solid lines, filled circles and filled bands: primary network (v2, post hoc); dashed lines, open circles and hatched bands: originally registered network (v1). The prediction for a site is the mean over networks trained from three sets of random starting weights; bands are two-sided intervals of the paired hierarchical bootstrap over outer resamples and test hosts, clipped at the axis limits. Squares on thinner lines: the training-mean predictor (dotted), the physics floor B0 and RF-Kumagai, which do not depend on the network. Circles on lines are the registered outer-resample design (the primary network evaluated on it is post hoc); diamonds are the precision extension (more resamples and seeds at the two largest budgets) and triangles grouped $K$-fold cross-validation at the mean fold training size, both extensions, drawn as unconnected points with interval bars (dashed for v1). The cross-validation tests every host once, including hosts that no outer resample tests, so its points are not directly comparable with the budget points. Source records, one per network where marked v*: \texttt{results/c1c2\_v*.json}, \texttt{results/diagnostics\_sweep.json}, \texttt{results/precision\_g1\_v*.json} and \texttt{results/cv\_g1\_v*.json}.

After (69 words, 3 sentences):

> Test MAE against training hosts for (\textbf{a}) S and (\textbf{b}) D, with the training mean, B0 and RF-Kumagai as squares. Filled markers and bands with solid lines show v2 (primary, post hoc), open markers and hatched bands with dashed lines and bars v1 (originally registered), circles the registered design, diamonds and triangles precision and cross-validation extensions, and bands and bars two-sided bootstrap intervals. Data: \texttt{results/c1c2\_v*.json}, \texttt{results/diagnostics\_sweep.json}, \texttt{results/precision\_g1\_v*.json} and \texttt{results/cv\_g1\_v*.json}.

### Figure `fig:advantage`

Source: `paper/sections/results.tex` (line 40).

Before (149 words, 6 sentences):

> Advantage of the explicit DFT electronic descriptors over structure alone, $A = \mathrm{MAE}_\mathrm{S} - \mathrm{MAE}_\mathrm{D}$ (positive when the descriptors lower the site error), against the number of training hosts (logarithmic axis). (\textbf{a}) All points; registered bands that reach beyond the axis are clipped. (\textbf{b}) The largest registered budgets and the extension points, where the decision on the tolerance is made; horizontal bars mark the one-sided upper bound of each point. The dashed line is the tolerance $\delta$ and the dotted line zero; $N^{*}$ is the smallest budget whose upper bound lies below $\delta$ there and at every larger budget. Line styles, markers and provenance labels as in Figure~\ref{fig:learning_curves}; the registered and precision points use the paired hierarchical bootstrap over resamples and test hosts, the cross-validation points a paired host-cluster bootstrap over all hosts. Source records, one per network where marked v*: \texttt{results/c1c2\_v*.json} (registered design, $N^{*}$ and the ceiling), \texttt{results/precision\_g1\_v*.json}, \texttt{results/cv\_g1\_v*.json} and \texttt{results/cv\_extended\_budget.json}.

After (64 words, 3 sentences):

> The advantage $A = \mathrm{MAE}_\mathrm{S} - \mathrm{MAE}_\mathrm{D}$ against training hosts, (\textbf{a}) at every point and (\textbf{b}) at the largest registered budgets and the extension points, with the tolerance $\delta$ (dashed), zero (dotted) and $N^{*}$. Markers, lines and provenance labels follow Figure~\ref{fig:learning_curves}, bands and bars are two-sided bootstrap intervals clipped at the axes, and horizontal bars in (\textbf{b}) mark one-sided upper bounds. Data: \texttt{results/c1c2\_v*.json}, \texttt{results/precision\_g1\_v*.json}, \texttt{results/cv\_g1\_v*.json} and \texttt{results/cv\_extended\_budget.json}.

### Figure `fig:staging`

Source: `paper/sections/results.tex` (line 97).

Before (181 words, 9 sentences):

> Staged prediction through predicted descriptors. In the staged model P, P1 predicts the DFT descriptors from the pristine host structure and passes them to the descriptor network D of the same resample, budget and seed; S is the structure-only network. Training hosts on a logarithmic axis. (\textbf{a}) Site-level MAE of S, D and P. (\textbf{b}) The two staging contrasts: $\mathrm{MAE}_\mathrm{D} - \mathrm{MAE}_\mathrm{P}$, the cost of predicting rather than computing the descriptors (negative: P worse than D), and $\mathrm{MAE}_\mathrm{P} - \mathrm{MAE}_\mathrm{S}$, staging against end-to-end learning (negative: P better than S). The dashed lines are the equivalence margins $\pm\delta_\mathrm{P}$ and the dotted line zero; the outcome of $\mathrm{MAE}_\mathrm{P} - \mathrm{MAE}_\mathrm{S}$ at each budget follows the four-outcome equivalence rule, which is post hoc. Solid lines, filled markers and filled bands: primary network (v2, post hoc); dashed lines, open markers and hatched bands: originally registered network (v1), the registered staging analysis. Bands are two-sided intervals of the paired hierarchical bootstrap, one draw set for all models, budgets and both networks; bands of D in (a) and of $\mathrm{MAE}_\mathrm{D} - \mathrm{MAE}_\mathrm{P}$ in (b) at the smallest budgets are clipped. Source records: \texttt{results/staging\_v2.json} and \texttt{results/staging\_v1.json}.

After (70 words, 3 sentences):

> (\textbf{a}) MAE of S, D and the staged model P and (\textbf{b}) the contrasts $\mathrm{MAE}_\mathrm{D} - \mathrm{MAE}_\mathrm{P}$ and $\mathrm{MAE}_\mathrm{P} - \mathrm{MAE}_\mathrm{S}$, with the margins $\pm\delta_\mathrm{P}$ (dashed) and zero (dotted), against training hosts. Filled markers, solid lines and filled bands show the primary network (v2, post hoc) and open markers, dashed lines and hatched bands the originally registered network (v1, registered), with two-sided bootstrap intervals as bands, clipped at the axes. Data: \texttt{results/staging\_v2.json} and \texttt{results/staging\_v1.json}.

### Figure `fig:geometry`

Source: `paper/sections/results.tex` (line 115).

Before (199 words, 6 sentences):

> Sensitivity of the predictions to relaxed host geometry, originally registered network (v1) at the registered budget of \numGeometryCThreeBNullRuleBudget{} training hosts. The networks were trained on DFT host geometry and evaluated, without retraining, on host cells relaxed with MACE-MP-0 (medium model, double precision, cell and positions) and tiled onto the release supercells, and on the same cells rescaled isotropically to the DFT volume. (\textbf{a}) Change in site-level MAE relative to DFT geometry, $\Delta\mathrm{MAE}$, for S, for D, which keeps its DFT descriptors so that its change isolates the structural input, and for the staged model P; circles, relaxed geometry; down triangles, rescaled geometry; bars, two-sided intervals of the paired hierarchical bootstrap; the dotted line is zero. (\textbf{b}--\textbf{d}) For S, D and P, the mean absolute change of the prediction of each test host against the isotropic strain $\varepsilon_v$ of its relaxation, the component with the largest coefficient for S and P in the joint regression on the three geometry components; the $y$ axes are logarithmic, and hosts whose change is exactly zero (D on the rescaled geometry only) are not drawn. All series are v1 (open markers, dashed bars); no evaluation of v2 on these relaxations exists. Source record: \texttt{results/geometry\_c3b.json}.

After (70 words, 3 sentences):

> Response of the originally registered network at \numGeometryCThreeBNullRuleBudget{} training hosts to MACE-MP-0 relaxed cells, as (\textbf{a}) $\Delta\mathrm{MAE}$ of S, D and P and (\textbf{b}--\textbf{d}) mean absolute prediction change per test host against its isotropic strain $\varepsilon_v$. Circles are relaxed and triangles volume-rescaled cells, all v1 with open markers and dashed bars (two-sided bootstrap intervals), zero is dotted, and hosts with no change are absent from the logarithmic axes. Data: \texttt{results/geometry\_c3b.json}.

### Figure `fig:within_host`

Source: `paper/sections/results.tex` (line 122).

Before (167 words, 7 sentences):

> Site resolution within a host. (\textbf{a}) Within-host skill of S (structure only) and D (structure plus the DFT descriptors of the pristine host and site) against the number of training hosts (logarithmic axis): the within-host residual MAE of a predictor that is constant within each host minus that of the model, on test hosts with at least two oxygen sites. Zero (dotted) means that the model places hosts but does not distinguish the sites of a host. (\textbf{b}) Within-host advantage of the descriptors, $A_\mathrm{within}$, the within-host residual MAE of S minus that of D, with the tolerance $\delta$ (dashed) and zero (dotted). Solid lines, filled circles and filled bands: primary network (v2, post hoc); dashed lines, open circles and hatched bands: originally registered network (v1); bands are two-sided intervals of the paired hierarchical bootstrap. Precision (diamonds) and cross-validation (triangles) points are extensions, as in Figure~\ref{fig:learning_curves}, and the cross-validation test sets differ from the registered ones. Source records: \texttt{results/c1c2\_v2.json}, \texttt{results/c1c2\_v1.json} and the extension records of Figure~\ref{fig:learning_curves}.

After (58 words, 3 sentences):

> (\textbf{a}) Within-host skill of S and D, the zero-skill within-host residual MAE minus that of the model, and (\textbf{b}) the within-host advantage $A_\mathrm{within}$, S minus D, against training hosts, with the tolerance $\delta$ (dashed) and zero (dotted). Markers, lines, bands, extension points and provenance labels follow Figure~\ref{fig:learning_curves}. Data: \texttt{results/c1c2\_v2.json}, \texttt{results/c1c2\_v1.json} and the extension records of Figure~\ref{fig:learning_curves}.

### Figure `fig:screening`

Source: `paper/sections/results_screening.tex` (line 37).

Before (185 words, 9 sentences):

> Out-of-sample neutral oxygen-vacancy formation energies of named oxides, both networks. One marker per oxygen site of the screened oxides present in the universe, ZnO, SnO$_2$, Ga$_2$O$_3$, TiO$_2$, ZrO$_2$, MgO and Al$_2$O$_3$, each held out in at least one outer resample; the model is S at \numScreeningDemoBudget{} training hosts. (\textbf{a})~Predicted against DFT formation energy with the line of equality; the markers of the two networks for one site are offset horizontally by a small fixed amount. (\textbf{b})~Predicted minus DFT, grouped by oxide in ascending order of its mean DFT energy; the dotted line is zero error. Filled markers and solid bars: primary network (v2, post hoc); open markers and dashed bars: originally registered network (v1, registered aggregation). Colour identifies the oxide. A marker is the mean over the outer resamples in which the host was held out of the seed-ensemble prediction, and a bar spans the smallest to the largest of those per-resample predictions; a site held out once has no bar. A structure render of an SnO$_2$ site is given as Supplementary Figure~S8. Sources: \texttt{figures/main/data/screening\_demo.json}, \texttt{results/screening\_c5.json} and, for the absent candidates, \texttt{results/screening\_absence.json}.

After (70 words, 3 sentences):

> Formation energies predicted by S at \numScreeningDemoBudget{} training hosts for screened sites, (\textbf{a}) against DFT with the line of equality and (\textbf{b}) as predicted minus DFT by oxide. Filled markers and solid bars show the primary network (v2, post hoc), open markers and dashed bars the originally registered network (v1, registered), and markers and bars the mean and range over resamples holding the host out. Data: \texttt{figures/main/data/screening\_demo.json}, \texttt{results/screening\_c5.json} and \texttt{results/screening\_absence.json}.

### Figure `fig:readout`

Source: `paper/si/sections/s2_training.tex` (line 23).

Before (154 words, 5 sentences):

> Readout of the structure-only network S and the points where D receives the DFT descriptors. The inputs are the initial features of the vacancy site \xvzero{} and of the other atoms \xizero{}, the bond features \eijzero{} and the global state of the cell \uzero{}; $n$ MEGNet blocks update them, each widening the coordination shell that informs every atom. The readout joins the final description of the vacancy site $\mathbf{h}_\mathrm{v}$, a pooled description of all atoms $\bar{\mathbf{h}}$ (Set2Set or mean, a tuned choice) and the final global state $u$, and a multilayer perceptron maps them to the formation energy $E_\mathrm{f}$ of the neutral vacancy. The host-level thermodynamic term is carried by $\bar{\mathbf{h}}$ and $u$, the local environment of the site by $\mathbf{h}_\mathrm{v}$. In D (D-state), the host-electronic descriptors are appended to \uzero{} and the site-electronic descriptors to \xvzero{} (green arrows), standardised with training-set statistics; the readout is unchanged and is the same for both networks.

After (69 words, 2 sentences):

> Readout of the structure-only network S, from the initial features of the vacancy site \xvzero{}, the other atoms \xizero{}, the bonds \eijzero{} and the cell \uzero{}, through $n$ MEGNet blocks, to the vacancy-site vector $\mathbf{h}_\mathrm{v}$, the pooled vector $\bar{\mathbf{h}}$ and the global state $u$ that a multilayer perceptron maps to $E_\mathrm{f}$. Green arrows mark where D (D-state) receives the host-electronic descriptors, at \uzero{}, and the site-electronic descriptors, at \xvzero{}.

### Figure `fig:cascade`

Source: `paper/si/sections/s3_splits.tex` (line 12).

Before (136 words, 5 sentences):

> Filter cascade that defines universe v1. From the completed neutral oxygen-vacancy entries of the release of Kumagai et al., the cascade keeps their neutral machine-learning subset, which already excludes the perturbed-host-state entries, the entries with undetermined band edges and the dynamically unstable hosts. Three filters follow in order: D1 removes the entries flagged as a split vacancy, an unknown defect type or a configuration different from the initial one; D2 removes the host Sr$_2$Zr$_7$O$_{16}$, whose site labels do not match the targets of the release; D3 keeps an entry of the two hosts with inconsistent cell metadata only if its vacancy site maps to an oxygen atom with a matching first cation shell, and removes nothing. Dashed boxes are the entries excluded at each step. Site and host counts after every step are in Table~\ref{tab:cascade}.

After (54 words, 2 sentences):

> Filter cascade that defines universe v1, from the completed neutral oxygen-vacancy entries of the release of Kumagai et al.\ through its neutral machine-learning subset and the filters D1 to D3 of this work. Dashed boxes are the entries excluded at each step, and Table~\ref{tab:cascade} gives the site and host counts after every step.

### Figure `fig:splits`

Source: `paper/si/sections/s3_splits.tex` (line 60).

Before (166 words, 8 sentences):

> Split designs, drawn as sets of hosts (dark: test; light: training; mid-grey: validation). Every split keeps all sites of a host on one side. Widths are schematic, not to scale. (\textbf{a}) Primary protocol: each outer resample holds out \numSplitMetaNTestHosts{} test hosts, stratified by host-mean $E_\mathrm{f}$, and orders the remaining pool so that the training set at budget $B$ is the first $B$ hosts; budgets are nested, and the learning curves are drawn against $B$. Validation hosts are carved out of each training set. (\textbf{b}) The published split of Kiyohara et al.: the networks train on its training hosts, stop early on its validation hosts and are tested on its test hosts. (\textbf{c}) Grouped $K$-fold cross-validation ($K = \numSplitCvKsItemOne{}$ and $\numSplitCvKsItemTwo{}$; extension): every host is tested exactly once, with training sets larger than the largest budget of (a). (\textbf{d}) Leave-one-chemistry-out: hosts are grouped into chemistry families (the set of periodic-table groups of the cations), and \numSplitLocoNFolds{} folds, each holding out whole families, test transfer to chemistries absent from training.

After (50 words, 2 sentences):

> Split designs drawn as sets of hosts, with (\textbf{a}) the primary grouped hold-out with nested training budgets $B$, (\textbf{b}) the published split of Kiyohara et al., (\textbf{c}) grouped $K$-fold cross-validation (extension) and (\textbf{d}) leave-one-chemistry-out folds. Dark, light and mid-grey sets are test, training and validation hosts, and widths are schematic.

### Figure `fig:withinhost`

Source: `paper/si/sections/s4_withinhost.tex` (line 76).

Before (230 words, 8 sentences):

> Site resolution within a host, by chemistry and site (extension). Within-host residual MAE of S (structure only, blue) and D (structure plus the DFT descriptors of the pristine host and site, green) at the largest training budget, for groups of test hosts or sites; lower is better. The grey tick in each row is the zero-skill value, the within-host residual MAE of any predictor that is constant within each host; a model point at or right of it has no within-host skill in that group. Circles: point values; horizontal bars: two-sided percentile intervals of the host-cluster bootstrap, paired across models and networks; no bar where too few hosts contribute. Filled circles and solid bars: primary network (v2), adopted after diagnostics of the originally registered network; open circles and dashed bars: originally registered network (v1). (\textbf{a}) Cation element, each host under every cation it contains; (\textbf{b}) $d$-electron class of the host, with all tested hosts as the top row; (\textbf{c}) hosts containing at least one of the cations with the highest perturbed-host-state rates, against the rest; (\textbf{d}) thirds of host stability (formation energy per atom); (\textbf{e}) thirds of the PBEsol(+$U$) band gap; (\textbf{f}) sites at the most negative, intermediate and least negative Bader charge of the vacancy oxygen within their host. Each site's prediction is the seed ensemble averaged over the registered resamples in which its host was tested. Values: \texttt{results/within\_host\_breakdown.json}.

After (70 words, 3 sentences):

> Within-host residual MAE of S (blue) and D (green) at the largest budget (extension) by (\textbf{a}) cation, (\textbf{b}) $d$-electron class, (\textbf{c}) perturbed-host-state-prone cations, (\textbf{d}) formation-energy thirds, (\textbf{e}) band-gap thirds and (\textbf{f}) vacancy-oxygen Bader-charge rank. Grey ticks mark zero skill, bars are two-sided host-cluster bootstrap intervals, filled circles and solid bars show the primary network (v2, post hoc) and open circles and dashed bars the originally registered network (v1). Data: \texttt{results/within\_host\_breakdown.json}.

### Figure `fig:gpu`

Source: `paper/si/sections/s5_hardware.tex` (line 65).

Before (196 words, 10 sentences):

> The advantage $A$ by GPU class of the training runs (extension, descriptive, no test). $A = \mathrm{MAE}_\mathrm{S} - \mathrm{MAE}_\mathrm{D}$ (eV) of single runs, averaged over the paired cells in which the S run and the D run of the same resample or fold, budget and seed ran on the same GPU class. (\textbf{a}, \textbf{b}) Precision extension at the two largest budgets; (\textbf{c}, \textbf{d}) grouped $K$-fold cross-validation at the two fold counts. The classes on the horizontal axis are the GPU models of the cluster pool, read from the run records, and ``sweep'', the registered sweep runs of the original resamples and seeds (precision only). GPU class was not randomised with respect to resample, fold or seed, so differences between classes are not separable from them and are not read as hardware effects. Markers: mean over the paired cells; bars: descriptive percentile intervals of a bootstrap over the cells; classes without a paired cell are not drawn. Filled markers and solid bars: primary network (v2), adopted after diagnostics of the originally registered network; open markers and dashed bars: originally registered network (v1). Diamonds: precision extension; triangles: grouped $K$-fold cross-validation. Dashed line: the tolerance $\delta$; dotted line: zero. Values in Table~\ref{tab:gpu_class}.

After (70 words, 3 sentences):

> Advantage $A$ by GPU class of paired runs (extension, descriptive) for (\textbf{a}, \textbf{b}) precision runs at the two largest budgets and (\textbf{c}, \textbf{d}) cross-validation runs at both fold counts, with $\delta$ dashed and zero dotted. Markers and bars are means over paired cells and descriptive bootstrap intervals, filled and solid for v2 (primary) and open and dashed for v1 (originally registered), with ``sweep'' the registered runs. Values in Table~\ref{tab:gpu_class}.

### Figure `fig:sens`

Source: `paper/si/sections/s6_sensitivities.tex` (line 53).

Before (245 words, 11 sentences):

> The advantage $A$ under the high-moment exclusion and the longer training cap, and an untuned CGCNN beside the MEGNet networks. (\textbf{a}) $A = \mathrm{MAE}_\mathrm{S} - \mathrm{MAE}_\mathrm{D}$ (eV; positive when the DFT descriptors lower the site error) at the largest training budget, from the seed-ensemble site MAE averaged over the registered outer resamples. ``Primary'': the primary result of each network. ``High moment'' (extension): S and D retrained with the entries whose defect magnetic moment exceeds the registered threshold removed from training and test sites, compared on the common test sites. ``Capped twins'' (post hoc): every primary run that stopped at the training cap replaced by its rerun with the longer cap. Both sensitivities exist for the originally registered network only. Markers: point estimates; bars: two-sided intervals of the hierarchical bootstrap of the primary analysis; short horizontal bars: one-sided upper bounds; dashed line: the tolerance $\delta$; dotted line: zero. (\textbf{b}) Seed-ensemble test MAE (eV) of S (blue) and D (green) on a single outer resample at three budgets, for the MEGNet networks (lines with bands) and for CGCNN with fixed, untuned optimiser settings (crosses, drawn just right of their budget). Bands and bars in (b) are two-sided intervals of a host-cluster bootstrap over the test hosts of that resample; with one resample they reflect test-host sampling only, and no test is made. Filled markers and solid lines: primary network (v2), adopted after diagnostics of the originally registered network; open markers and dashed lines: originally registered network (v1). Records: \texttt{results/sens\_high\_moment\_v1.json}, \texttt{results/sens\_capped\_post\_hoc.json}, \texttt{results/sens\_cgcnn.json}.

After (70 words, 3 sentences):

> (\textbf{a}) Advantage $A$ at the largest budget for the primary result, the high-moment exclusion (extension) and capped twins (post hoc), and (\textbf{b}) test MAE of S (blue) and D (green) for MEGNet and CGCNN (crosses). Bars are two-sided bootstrap intervals, horizontal bars one-sided upper bounds, filled markers and solid lines the primary network (v2) and open markers and dashed lines the originally registered network (v1). Data: \texttt{results/sens\_high\_moment\_v1.json}, \texttt{results/sens\_capped\_post\_hoc.json} and \texttt{results/sens\_cgcnn.json}.

### Figure `fig:probe`

Source: `paper/si/sections/s7_probe.tex` (line 63).

Before (221 words, 9 sentences):

> Latent probe: linear recovery of the DFT electronic descriptors from the learned description of the vacancy site and its host in the structure-only network (registered analysis on the originally registered network, v1). A linear map, fitted on the training hosts of each resample and budget, asks how well the learned vectors that the network's final step reads (vacancy site, pooled host, global state) predict each descriptor given to D, scored by \Rsq{} on the test sites. Trained probe: dashed line, open markers and hatched band (dashed bars in (c)). Controls in grey: the same probe with descriptor rows permuted among training hosts (shuffled labels; squares) and the probe on an untrained network of the same architecture (the registered random-initialisation control; triangles); two further untrained networks (light grey, dotted, no band) show the spread of that control and are descriptive. (\textbf{a}) Host-electronic and (\textbf{b}) site-electronic class-mean test \Rsq{} against training hosts on a logarithmic axis: means over the resamples with two-sided intervals of the resample bootstrap; the dotted line is zero. (\textbf{c}) Test \Rsq{} per descriptor at the largest budget, host-electronic descriptors above the grey rule and site-electronic below. The registered rule does not hold, so the probe is placed in the Supplementary Materials. The collaborator's probe on the primary network (v2) is post hoc and is not drawn. Records: \texttt{results/probe\_c4\_v1.json}, \texttt{results/probe\_descriptive.json}.

After (70 words, 3 sentences):

> Test \Rsq{} of a linear probe from the structure-only network's learned vectors (v1, registered) to DFT descriptors, for (\textbf{a}) host-electronic and (\textbf{b}) site-electronic class means against training hosts and (\textbf{c}) each descriptor at the largest budget. The trained probe is dashed with open markers, grey squares and triangles the shuffled-label and untrained controls, dotted light-grey lines further untrained networks, and bands and bars two-sided resample-bootstrap intervals. Data: \texttt{results/probe\_c4\_v1.json} and \texttt{results/probe\_descriptive.json}.

### Figure `fig:sno2`

Source: `paper/si/sections/s8_structures.tex` (line 38).

Before (152 words, 5 sentences):

> Structure render of rutile SnO$_2$ as it enters the data set. The pristine SnO$_2$ supercell of the database (host \mpsnotwo{}, \numRenderSnOTwoNAtoms{} atoms) with the oxygen atom to be removed (site O1) marked by the translucent amber sphere; its three nearest Sn neighbours (Table~\ref{tab:shell}), the planar three-fold coordination of oxygen in rutile, are drawn enlarged and joined into a translucent triangle with dark edges, seen here nearly edge-on. Sn grey-blue, O red; Sn--O bonds shorter than \numRenderSnOTwoCationOBondCutoffASn{}~\AA{} are drawn and bonds that cross the cell boundary are omitted; the cell is shifted by lattice translations only, so that the vacancy lies near the faces closest to the viewer. The structure is the pristine host, not the relaxed defect cell. Same camera conventions, lights and materials as \artfigoverview{}b of the article; Blender Cycles on the CPU with \numRenderSnOTwoSamples{} samples and denoising, rendered at \numRenderSnOTwoDpi{} dpi over the text width (parameters in \texttt{figures/si/structure\_sno2\_vacancy.render.json}).

After (61 words, 3 sentences):

> Pristine supercell of rutile SnO$_2$ from the database (host \mpsnotwo{}, \numRenderSnOTwoNAtoms{} atoms), with the oxygen to be removed (site O1) and its three nearest Sn neighbours (Table~\ref{tab:shell}) joined into a triangle. The amber sphere marks the removed oxygen, Sn is grey-blue and O red, and Sn--O bonds shorter than \numRenderSnOTwoCationOBondCutoffASn{}~\AA{} are drawn except across the cell boundary. Data: \texttt{figures/si/structure\_sno2\_vacancy.render.json}.

## 5. F3: word allowlist and restored encodings

`scripts/check_captions.py` keeps the 3-sentence cap for every caption and the 70-word cap by default. Four
captions that carry several networks, extensions or reference lines have an explicit allowlist (`LONG_CAPTIONS`)
with an 85-word cap: `fig:learning_curves`, `fig:screening`, `fig:sens` and `fig:probe`. The checker prints the
allowlist on every run and the cap of each caption beside its count (`70/85 words`).

Four class-d deletions of section 3 were restored, each inside the existing sentences; the other class-d drops stand.

| Figure | Label | Restored encoding | Sentences before | Sentences after | Words before | Words after |
|---|---|---|---|---|---|---|
| 2 | `fig:learning_curves` | bands and bars "clipped at the axes", the wording of Figures 3 and 4 | 3 | 3 | 69 | 73 |
| 7 | `fig:screening` | "with no bar for a site held out only once" | 3 | 3 | 70 | 80 |
| S6 | `fig:sens` | "with the tolerance $\delta$ (dashed line) and zero (dotted line)" in (a) | 3 | 3 | 70 | 80 |
| S7 | `fig:probe` | "zero \Rsq{} dotted, host-electronic descriptors above and site-electronic below the grey rule in (c)" | 3 | 3 | 70 | 84 |

The label of Supplementary Figure S4 is now `fig:si_withinhost_groups` (was `fig:withinhost`), matching its figure
file. Its two `\ref` sites are in `paper/si/sections/s4_withinhost.tex`; the article cites the figure as typed
"Supplementary Figure~S4" and has no `\ref` to it. Section 1.1 and the tables above keep the F2 label as recorded.

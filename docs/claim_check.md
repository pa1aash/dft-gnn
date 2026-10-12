# Claim check: prior art in the Introduction and Methods (J1)

Session J1, 2026-10-12. Each statement about earlier work in `paper/sections/introduction.tex` and
`paper/sections/methods.tex` was set against the source line quoted below. Sources were read headlessly:

| Tag | Source | Retrieved as |
|---|---|---|
| K21 | Kumagai et al., Phys. Rev. Materials 5, 123803 (2021), doi:10.1103/PhysRevMaterials.5.123803 | publisher PDF and Supplemental Material, text extracted in S01 (local cache, not tracked) |
| K25 | Kiyohara et al., Phys. Rev. Lett. 135, 246101 (2025), doi:10.1103/h66h-y5k6 | arXiv:2510.00513v2 PDF (`curl`, `pdftotext`); code repository `kumagai-group/ML_charged_defects` (raw.githubusercontent.com) |
| L26 | Linton, Singh and Aidhy, npj Comput. Mater. 12, 175 (2026), doi:10.1038/s41524-026-02037-6 | nature.com article HTML (`curl`, tags stripped) |

The K25 Supplemental Information on journals.aps.org returned a Cloudflare challenge page and was not
read in this session; the graph-construction details below rest on the main text and the released code,
as in `docs/provenance.md`.

Verdicts: **accurate** (the sentence says what the source says), **imprecise** (true but leaves out the
detail the claim turns on; reworded), **overstated** (says more than the source; reworded).

## (a) Kumagai et al. 2021: how the learning curve was built

Paper text before J1 (Introduction, paragraph 4):
"Kumagai et al. trained random forests on descriptors of the pristine host and vacancy site and reported
a learning curve, the error as the number of training oxides grows, with training and test sets separated
by oxide."

Source lines:

- K21 Sec. III D: "Therefore, we divided the dataset by the oxides rather than by the O sites. The total
  numbers of oxides were 824, 764, and 750 for q = 0, +, and 2+, respectively; 22, 70, 220, and 700 oxides
  were selected for the training sets, and 48 oxides for the test sets."
- K21 Fig. 5 caption: "(a) RF model convergence against the number of oxides in the training set. The model
  creation process was repeated 100 times with a different training set. Mean absolute errors and standard
  deviations are estimated from the test sets, which are represented by the circles and shaded areas,
  respectively."
- K21 Sec. II I (hyperparameters, not the curve): "The former was fixed to 400, while the latter was
  determined via grid search in conjunction with fourfold cross validation (CV)".

Reading: the curve is built from repeated draws of training oxides (100 per point, four sizes), with a
48-oxide test set and the split made by oxide. It is not a grouped K-fold cross-validation; the only
cross-validation in K21 is the fourfold one inside the hyperparameter grid search. K21 does not say
whether the 48 test oxides were redrawn with each training set.

Verdict: **imprecise**. "Separated by oxide" is right, but the sentence did not say that the curve
averages over repeated training draws rather than over grouped folds. Reworded to: "reported a learning
curve, the error as the number of training oxides grows, averaged over a hundred fits on different draws
of training oxides, with the data divided by oxide rather than by site."

Methods: names K21 only as the source of the descriptors and of the random-forest settings; it makes no
claim about the K21 learning curve. No change.

## (b) Kiyohara et al. 2025: graph construction, 0.29 eV at q = 0, no cross-validation, no learning curve

Paper text (Introduction, paragraph 4, unchanged):
"Kiyohara et al. trained a graph network on the crystal structure alone, with one model for several charge
states, and reported a mean absolute error of [0.29] eV at the neutral charge state on a single partition
into training, validation and test oxides, without cross-validation and without a learning curve."

Source lines (arXiv:2510.00513v2):

- Structure only, one model: "Using a single ML model and only structural information, we achieved
  improved accuracies of 0.29, 0.22, and 0.37 eV for the neutral, +1, and +2 charge states, respectively".
- Graph construction: "Crystal structures are modeled using the CGCNN framework, as shown in Fig. S2 in SI
  (see also Method for details). [...] We firstly encoded the atomic species and bond lengths, then passed
  them to convolutional layers. Subsequently, we extracted features at O sites at a pooling layer, and
  concatenated the charge state q. Finally, the data were fed into a fully connected neural network to
  predict an Ef[VO]."
- Graph construction, code: `cgcnn/pooling.py` defines `class SitePooling(Pooling)`, which returns
  `embedded_site_features[i] for i in self.target_site_indices`; the input record
  `oxy_vac_data/materials_coreAlign/ZnO.json` is a four-atom pristine cell (a = 3.175 Å). The graph is the
  pristine host with the vacancy marked only at readout.
- 0.29 eV at q = 0: "The prediction errors are 0.29, 0.22 and 0.37 eV for q=0, +1, and +2, respectively".
- Single partition: "To avoid the data leakage, we divided the dataset by the oxides rather than by the O
  sites as we did previously [6]. The dataset was split into training, validation, and test sets in a
  0.7:0.15:0.15 ratio for evaluating the accuracies."
- No cross-validation, no learning curve: absence claims. No fold count, repeated split or second
  training-set size appears in the main text; the released split files list one partition
  (646 / 138 / 139 formulas without PHS; `docs/provenance.md`, K25 protocol table).

Verdict: **accurate**. The paper text claims nothing about the K25 graph beyond "the crystal structure
alone", which the quoted lines support. The C0 discussion in Methods describes only the released split.
No change.

## (c) Linton, Singh and Aidhy 2026: what the method does, which materials

Paper text (unchanged):

- Introduction, paragraph 4: "The serial design, in which an electronic quantity is predicted first and
  passed to the energy model, has been used by Linton, Singh and Aidhy, who predict the Bader charge and
  then the vacancy energy in metallic face-centred-cubic high-entropy alloys; that is a precedent in a
  metal, not a benchmark for oxides."
- Methods, staged model: "D is trained on true descriptors, as in serial pipelines that first predict a
  charge descriptor and then the energy."

Source lines (L26):

- Method and materials (abstract): "we present a machine learning (ML) framework that eliminates the need
  for DFT calculations by predicting \({E}_{v}^{f}{\rm{s}}\) in HEAs using models trained on binary and
  ternary alloys. Our approach first relaxes face-centered cubic (FCC) structures using a fine-tuned CHGNet
  model and then uses the resulting configurations as input into a crystal graph convolutional neural
  network (CGCNN) to predict both Bader charges and \({E}_{v}^{f}{\rm{s}}\)."
- Serial order (Fig. 2 text): "Structures are relaxed via CHGNet for DFT-level accurate lattice distortions
  via Model 1. Bader charges are then predicted for these structures via Model 2. The predicted Bader
  charges and relaxed structure from Models 1 and 2 are then fed into Model 3 to predict
  \({E}_{v}^{f}{\rm{s}}\)."
- Energy model trained on true charges, predicted ones swapped in (Results, Fig. 5): "Since good
  predictions are obtained using DFT-obtained Bader charges, we substitute the DFT-obtained Bader charges
  with the CGCNN predicted Bader charges from above."

Verdict: **accurate** for both sentences. The Introduction leaves out the CHGNet relaxation step and the
training on binary and ternary alloys, but it does not overstate the source. The Methods analogy
(energy model trained on true descriptors, predictions substituted at inference) is what L26 does. No
change.

## Summary

| Claim | Location | Verdict | Change |
|---|---|---|---|
| (a) K21 learning curve | Introduction | imprecise | reworded (repeated training draws, divided by oxide) |
| (a) K21 | Methods | no claim about the curve | none |
| (b) K25 graph, 0.29 eV, single partition, no CV, no curve | Introduction, Methods | accurate | none |
| (c) L26 serial Bader-then-energy, FCC HEAs | Introduction, Methods | accurate | none |

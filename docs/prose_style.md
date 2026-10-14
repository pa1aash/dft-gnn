# Prose style of the manuscript

Every session that writes or revises prose in `paper/sections/` reads this file first. It fixes the register of the
paper; `paper/tools/README.md` fixes the number rules and `docs/provenance_labels.md` the labels.

## Reader and venue

The paper is written for Crystals (MDPI, section Inorganic Crystalline Materials) and should read like a paper in
npj Computational Materials, Chemistry of Materials or Physical Review Materials. The reader is a solid-state
chemist or a defect physicist. They know Kröger-Vink notation, supercell defect calculations, band gaps, Bader
charges and coordination polyhedra; they use machine learning as a tool and do not know what a loss function or an
epoch is. A sentence that needs machine-learning knowledge to parse is a sentence to rewrite.

## Machine learning through the chemistry it encodes

Describe each learned component by the chemical information it handles. Gloss a machine-learning term once, in
chemical or statistical language, at first use, and then use it sparingly and always in the same sense.

| Term | Say, or gloss as |
|---|---|
| graph network | a learned encoder of the local coordination environment |
| message passing, MEGNet block | aggregation of information over successive coordination shells |
| radius graph | the neighbour list of the crystal structure within a cutoff |
| vacancy flag | marks the oxygen site that is removed |
| training-set size, budget | the number of host oxides with DFT labels |
| learning curve | the sample complexity of the structure-to-energy mapping: error against the number of training hosts |
| test set, held-out set | oxides the model has never seen |
| grouped split | keeps every site of one compound on the same side, so no chemically identical compound is on both sides |
| descriptors | quantities from the pristine-cell electronic structure (band gap, dielectric response, O 2p band centre, Bader charge of the oxygen to be removed) |
| non-inferiority test | asks whether the electronic information still changes the prediction by more than a stated energy tolerance |
| epoch | one pass of the optimiser over the training hosts |
| backbone | the shared network architecture; "the originally registered network (v1)" and "the primary network (v2)" where that reads better |
| embedding | the learned vector that represents an atom, a site or the whole host |
| readout | the final step that maps the learned vectors to one energy |
| ensemble, seed ensemble | the mean prediction of networks trained from different random starting weights |
| bootstrap | resampling of test hosts (and resamples) with replacement to obtain an interval |

Never use "backbone v1/v2" without having defined it; Methods (`sec:backbones`) defines it.

## The chemistry of the target

- The target is the formation energy $E_\mathrm{f}$ (eV) of the neutral oxygen vacancy, $V_\mathrm{O}^{\times}$ in
  Kröger-Vink notation, at the oxygen-poor reference chemical potential of the release.
- Name hosts by formula with subscripts (`Ga$_2$O$_3$`; mhchem is not loaded, so no `\ce{}`).
- Use structural language: coordination number, first-shell cation, M-O bond length (Å), polyhedral environment,
  perturbed-host-state (shallow-donor) entries versus deep, localised vacancies.
- Units through the existing macros and text: eV, Å (`\AA{}`), `\eVsq{}`, `\evperang{}`.

## Voice and paragraphs

- Past tense for what was done and found; present tense for what a figure shows and for established facts.
- "We" sparingly; never "I". Active, concrete verbs.
- Paragraphs of four to eight sentences. The first sentence states the paragraph's one claim; the middle gives the
  evidence (number macros, figure panel); the last says what is and is not established.
- Connected prose with explicit transitions ("Because", "By contrast", "This does not imply"). No bullet lists in
  Results, no rhetorical questions, no headline fragments.
- Each Results subsection opens with the chemical question it answers and closes with what is and is not
  established. Mechanisms and physical readings belong to the Discussion; Results gives the measurement and at most
  a one-clause pointer ("see Discussion").

## Calibration

- A claim carries exactly the strength of its measurement: "consistent with", "within the stated tolerance",
  "no evidence of ..., given an interval of ...".
- Null and negative results are findings about the chemistry or the method, reported with the measured size and
  interval, with the same care as positive ones.
- Forbidden: novel, state-of-the-art, groundbreaking, crucial, pivotal, leverage, delve, showcase, remarkable,
  significantly (unless a test was run), outperform (state the difference and its interval), "AI", paradigm,
  empty superlatives, and any sentence that reads the same with its numbers removed. Never "redundant", "useless"
  or "descriptors do not matter".
- v2 is the primary network by author decision and is post hoc; v1 is the originally registered network. Never
  write that v2 was pre-registered. Label every result group (registered v1, post hoc, extension) compactly in the
  sentence or the figure reference.

## Numbers and citations

Every number is a macro from `paper/generated/numbers.tex` (find it in `paper/generated/numbers.tsv` by JSON
pointer); text constants with digits are defined in `paper/main.tex`. Cite only keys in `paper/refs.bib`.

## Reading-level check

After drafting a subsection, reread it as a defect chemist who has never trained a model. Rewrite every sentence
that requires machine-learning knowledge to follow.

## Six rewrites from this paper

1. Before (results stub): "The one-sided upper bound of the advantage first falls below the margin at N* training
   hosts."
   After: "Once the networks had seen N* host oxides, the electronic structure of the pristine host lowered the site
   error by less than the 0.05 eV tolerance, at the one-sided 95% level."

2. Before (Figure S7 caption): "a ridge regression maps the readout input vector of the seed-0 S checkpoint
   ([vacancy-node embedding, pooled node embeddings, global state]) to each descriptor given to D."
   After: "A linear map, fitted on the training hosts, asks how well the learned description of the vacancy site
   and its host predicts each DFT descriptor, such as the band gap or the Bader charge of the oxygen to be removed."

3. Before (A1 notes): "S reaches the 200-epoch cap more often than D."
   After: "Training of the structure-only network was stopped by the fixed limit of passes over the training hosts
   more often than training of the descriptor network, so its error at the largest data sizes may not have
   converged fully."

4. Before (Methods): "Linear recovery is said to hold if the class-mean coefficient of determination increases with
   budget and exceeds both controls."
   After: "The probe counts as evidence that training teaches the network the electronic structure only if the
   recovered fraction of descriptor variance grows with the number of training oxides and exceeds that of an
   untrained network reading the same geometry."

5. Before (A5 notes): "In all three families A is largest at B = 50 and smallest at B = 654."
   After: "In each of the three architectures, the energy that explicit electronic information saves per site is
   largest when the networks have seen 50 oxides and smallest at 654." (In the paper the counts are macros.)

6. Before (A1 notes, "not established" list): "Not established: that the descriptors are useless."
   After: "This does not show that the electronic descriptors carry no information about the vacancy: on the
   primary network they lower the error by a small amount whose interval excludes zero but lies below the
   tolerance."

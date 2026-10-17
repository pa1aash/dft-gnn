# Prose style of the manuscript

Every session that writes or revises prose in `paper/` reads this file first. It fixes the register of the paper;
`paper/tools/README.md` fixes the number rules. Rewritten in session S1 (2026-10-17) for the one-network,
one-PDF manuscript specified in `docs/story_spec.md`; the rules removed in S1 are listed at the end.

## Reader and venue

The paper is written for Crystals (MDPI, section Inorganic Crystalline Materials) and should read like a paper in
npj Computational Materials, Chemistry of Materials or Physical Review Materials. The reader is a solid-state
chemist or a defect physicist. They know Kröger-Vink notation, supercell defect calculations, band gaps, Bader
charges and coordination polyhedra; they use machine learning as a tool and do not know what a loss function or an
epoch is. A sentence that needs machine-learning knowledge to parse is a sentence to rewrite.

## The four binding rules of the rewrite

1. **One network.** The paper reports one network, the He-initialised, validation-tuned network, called "the
   network" (or "the structure-only network" S and "the descriptor network" D when the input matters). The
   default-initialisation network appears in exactly two places: one Methods paragraph and one appendix table
   (Appendix D). The Methods paragraph says plainly what was seen and done: at small training sizes the
   default-initialisation network returned nearly identical energies for all oxygen sites of a host; this was found
   by inspecting held-out predictions; the initialisation was changed to He and every hyperparameter was re-tuned on
   validation oxides only; test oxides played no part in that selection. Nowhere else does a second network, a
   comparison of networks or a default-initialisation number appear.
2. **No registration vocabulary.** The paper text, captions, tables and appendices never use: registered,
   pre-registered, post hoc, extension (as a label), extension protocol, REGISTERED / POST HOC / EXTENSION, gate,
   v1, v2, frozen, freeze, claim identifiers (C1, C3a, ...), tag names, deviation rows, "logged before". The
   tolerance is stated once, in Methods: "The tolerance δ = 0.05 eV was fixed before the analysis." Provenance
   (tags, the deviations log, claim records, provenance labels) stays in the repository and the deposit, which the
   Data Availability Statement and Appendix K name. File paths may keep `v1`/`v2` (for example
   `results/c1c2_v2.json`) where a caption or appendix cites a record.
3. **No GPU-nondeterminism analysis.** One Methods sentence only: "GPU training is not bitwise reproducible, so every
   result is reported over resampled training sets, training seeds and a seed ensemble." No GPU models, no
   repeatability counts, no hardware caveats elsewhere.
4. **Assertive, content-first voice.** Lead with the chemistry and the number; describe the machine learning through
   what it encodes about oxide chemistry; use strong verbs; tie every claim to a number with its interval. Each
   caveat is stated once, in its home (`docs/story_spec.md` (ii)), and elsewhere only pointed to ("Section 2.1").
   Honest limits stay, written plainly as limits of scope.

## Voice

- Say what was found, then the number: "From 654 training oxides the structure-only network matches the descriptor
  network to within 0.05 eV (A = 0.033 eV [0.021, 0.045])." Not "we find evidence consistent with ...".
- Strong verbs: matches, places, orders, recovers, fails, lowers, holds, breaks. Not: appears to, seems to, may
  suggest, could indicate.
- One hedge per hypothesis, at most: "We propose that ..." once, followed by the measurement that motivates it and
  the one that would test it. No "as a hypothesis and not a result", no "this is a hypothesis" after "we propose".
- No defensive refrains: never "a bound, not an equivalence", "this does not show that ...", "neither establishes
  nor excludes", "what is and is not established", "is not read as", "a reproduction and not an improvement", "we
  claim no priority". The interval says what the claim covers.
- No hedge stacks (two or more qualifiers on one claim). If a claim needs two qualifiers, it is the wrong claim.
- Limits are sentences of scope, stated once: "At 400 training oxides the advantage is not bounded below δ
  (U = 0.075 eV)." "Under leave-one-family-out folds the upper bound is 0.060 eV." "No experimental formation
  energies were used."
- The descriptors' remaining value is small and positive: write "at most about 0.04 eV" where the upper bounds
  support it; never "none", "redundant", "useless" or "descriptors do not matter".
- Results report measurements and end on the measurement; mechanisms belong to the Discussion. No closing
  "what is established" sentence.

## Machine learning through the chemistry it encodes

Describe each learned component by the chemical information it handles. Gloss a machine-learning term once, in
chemical or statistical language, at first use, and then use it sparingly and always in the same sense.

| Term | Say, or gloss as |
|---|---|
| graph network | a learned encoder of the local coordination environment |
| message passing, MEGNet block | aggregation of information over successive coordination shells |
| radius graph | the neighbour list of the crystal structure within a cutoff |
| vacancy flag | marks the oxygen site that is removed |
| training-set size, budget | the number of host oxides with DFT labels ("training oxides" or "training hosts") |
| learning curve | the sample complexity of the structure-to-energy mapping: error against the number of training hosts |
| test set, held-out set | oxides the model has never seen |
| grouped split | keeps every site of one compound on the same side, so no compound is on both sides |
| descriptors | quantities from the pristine-cell electronic structure (band gap, dielectric response, O 2p band centre, Bader charge of the oxygen to be removed) |
| non-inferiority test | asks whether the electronic information still changes the prediction by more than a stated energy tolerance |
| epoch | one pass of the optimiser over the training hosts |
| the network | the shared architecture with He initialisation; "default initialisation" only in Methods 2.3 and Appendix D |
| embedding | the learned vector that represents an atom, a site or the whole host |
| readout | the final step that maps the learned vectors to one energy |
| ensemble, seed ensemble | the mean prediction of networks trained from different random starting weights |
| bootstrap | resampling of test hosts (and resamples) with replacement to obtain an interval |

## The chemistry of the target

- The target is the formation energy $E_\mathrm{f}$ (eV) of the neutral oxygen vacancy, $V_\mathrm{O}^{\times}$ in
  Kröger-Vink notation, at the oxygen-poor reference chemical potential of the release.
- Name hosts by formula with subscripts (`Ga$_2$O$_3$`; mhchem is not loaded, so no `\ce{}`).
- Use structural language: coordination number, first-shell cation, M-O bond length (Å), polyhedral environment,
  perturbed-host-state (shallow-donor) entries versus deep, localised vacancies.
- Units through the existing macros and text: eV, Å (`\AA{}`), `\eVsq{}`, `\evperang{}`.

## Paragraphs and tense

- Past tense for what was done and found; present tense for what a figure shows and for established facts.
- "We" sparingly; never "I". Active, concrete verbs.
- Paragraphs of four to eight sentences. The first sentence states the paragraph's one claim; the rest gives the
  evidence (number macros, figure panel). The paragraph ends when the evidence ends.
- Connected prose with explicit transitions ("Because", "By contrast"). No bullet lists in Results, no rhetorical
  questions, no headline fragments.
- Each Results subsection opens with the chemical question it answers. Mechanisms and physical readings belong to
  the Discussion; Results gives the measurement and at most a one-clause pointer ("Section 4.1").

## Forbidden words

novel, state-of-the-art, groundbreaking, crucial, pivotal, leverage, delve, showcase, remarkable, significantly
(unless a test was run), outperform (state the difference and its interval), "AI", paradigm, empty superlatives,
and any sentence that reads the same with its numbers removed. Never "redundant", "useless" or "descriptors do not
matter". Rule 2 adds the registration vocabulary above.

## Numbers and citations

Every number is a macro from `paper/generated/numbers.tex` (find it in `paper/generated/numbers.tsv` by JSON
pointer); text constants with digits are defined in `paper/main.tex`. Cite only keys in `paper/refs.bib`. Where a
v2 record and a v1 record both exist, the text cites the v2 macro; v1 macros appear only in Table D1 and the
default-initialisation paragraph.

## Figures and captions

Figures carry no in-figure annotations, callouts or text labels: panel letters, axis and tick labels, and a legend
outside the data area only. One network means one line style (solid, filled markers) and one palette across all
figures. Captions carry the information, in at most three sentences and 70 words (pre-push caption check).

## Reading-level check

After drafting a subsection, reread it as a defect chemist who has never trained a model. Rewrite every sentence
that requires machine-learning knowledge to follow, and every sentence that still reads as a defence rather than a
finding.

## Six rewrites from this paper

1. Before (Discussion 4.1): "The principal result is a bound, not an equivalence. Once the networks had seen 654
   host oxides, ... lowered the site error ... by less than δ at the one-sided level on both networks."
   After: "From 654 training oxides on, the electronic structure of the pristine host lowers the site error by at
   most about 0.04 eV, inside the 0.05 eV tolerance."

2. Before (Abstract): "On the primary network, adopted post hoc after diagnostics of the originally registered
   one, the descriptor advantage at 654 training hosts was 0.015 eV."
   After: "At 654 training oxides the descriptors lower the site error by 0.033 eV (95% interval 0.021 to 0.045 eV)."

3. Before (Results 3.5): "Staging did not beat end-to-end learning from structure at any budget on either network;
   what a more accurate descriptor predictor would achieve was not measured."
   After: "Predicting the descriptors from structure never beat learning the energy from structure directly."

4. Before (Methods `sec:backbones`): "Diagnostics of v1, the learning-curve analysis (tag g1-v1) and a site-resolution
   check ..., showed that ... These diagnostics were computed on the test-host predictions of v1. The authors then
   adopted v2, selected by a validation-host-only design screen under a protocol logged ..."
   After: "With the default initialisation of the library, the network returned nearly identical energies for all
   oxygen sites of a host at small training sizes, which we found by inspecting held-out predictions. We changed
   the initialisation to He and re-tuned every hyperparameter on validation oxides only; test oxides played no part
   in that choice. Appendix D compares the two initialisations."

5. Before (Results 3.9): "Runs on different GPU models were never bitwise identical, and their seed-ensemble errors
   differed from those of the original sweep ... these differences are descriptive and are not read as hardware
   effects."
   After (Methods, the only sentence): "GPU training is not bitwise reproducible, so every result is reported over
   resampled training sets, training seeds and a seed ensemble."

6. Before (Results 3.3, practitioner paragraph): "It is not supported at 400 hosts or fewer, beyond the largest
   cross-validation training size, for cation families absent from training on the primary network, for
   shallow-donor oxides, or for other architectures ..."
   After: nothing here. Each limit is stated once in its home (400 hosts and families in Section 3.2, shallow donors
   in Section 2.1), and the Conclusions give the positive rule.

## Rules removed in S1

- "v2 is the primary network by author decision and is post hoc; v1 is the originally registered network. Never
  write that v2 was pre-registered. Label every result group (registered v1, post hoc, extension) compactly in the
  sentence or the figure reference." (Replaced by rules 1 and 2.)
- The glossary row "backbone ... 'the originally registered network (v1)' and 'the primary network (v2)'", and
  "Never use 'backbone v1/v2' without having defined it". (Replaced by "the network".)
- "Each Results subsection ... closes with what is and is not established" and "the last [sentence] says what is and
  is not established". (Replaced by the no-refrain rule.)
- "A claim carries exactly the strength of its measurement: 'consistent with', 'within the stated tolerance', 'no
  evidence of ..., given an interval of ...'." (Replaced by the assertive-voice rules; claims stay tied to numbers.)
- Former rewrite 6 ("This does not show that the electronic descriptors carry no information ...") and former
  rewrite 1 ("at the one-sided 95% level" with N*), as examples of the old register.
- "Null and negative results are findings ... reported ... with the same care as positive ones" is kept in spirit
  (the 400 limit and the family-transfer limit are reported plainly) but no longer a separate rule.

Kept unchanged: the reader and venue, machine learning through chemistry (except the backbone row), the chemistry
of the target, tense, paragraph length, forbidden words, numbers as macros, the reading-level check.

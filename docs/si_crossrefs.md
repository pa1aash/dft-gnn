# Cross-references from the article to the Supplementary Materials (W3)

Session W3, 2026-10-14. Every place in `paper/sections/*.tex` that cites the Supplementary Materials, checked
against the compiled SI (`paper/si/si.pdf`, numbers read from `paper/si/si.aux`). Main-text sections were not
edited; mismatches are reported, not fixed. Line numbers are those of `origin/main` at `3551b59` plus the W3
branch (no main-text section changed in W3). The article cites the SI as plain text ("Supplementary Figure S4"),
not by `\ref`, because the SI is a separate document.

## Numbered citations

| Article location | Citation as written | What the sentence needs | SI item | SI label (compiled number, page) | Status |
|---|---|---|---|---|---|
| `results.tex:84` (Section 3.4, site resolution) | Supplementary Figure S4 | breakdown of the within-host error by chemistry (extension) | Figure S4, `fig_si_withinhost_groups`, Section S4 with Table S7 | `fig:withinhost` (S4, p. 10) | match |
| `results.tex:128` (Section 3.7, latent probe) | Supplementary Figure S7 | the probe figure, moved to the SI because the registered rule fails | Figure S7, `fig6_probe`, Section S7 | `fig:probe` (S7, p. 16) | match |
| `results.tex:135` (Section 3.9, sensitivities and hardware) | Supplementary Figures S5 and S6 | high-moment exclusion, training-length limit, architecture (S6) and hardware (S5) | Figure S5 `fig_si_gpu_class` (Section S5); Figure S6 `fig_si_sensitivities` (Section S6) | `fig:gpu` (S5, p. 12); `fig:sens` (S6, p. 14) | match |
| `results.tex:139` (Section 3.9, hardware) | Supplementary Figure S5 | paired-cell A by GPU class | Figure S5, Table S9 | `fig:gpu` (S5, p. 12) | match |
| `results_screening.tex:37` (Figure 7 caption) | Supplementary Figure S8 | structure render of an SnO2 site | Figure S8, `structure_sno2_vacancy`, Section S8 with Table S10 | `fig:sno2` (S8, p. 18) | match |

Every numbered citation exists in the SI with the content the sentence asks for. No main-text sentence cites
Supplementary Figure S1, S2 or S3 by number, nor any Supplementary Table or Section.

## Unnumbered citations ("the Supplementary Materials")

| Article location | Citation as written | SI item that answers it | Status |
|---|---|---|---|
| `data.tex:14` | "the cascade is drawn in the Supplementary Materials" | Figure S2 (`fig_cascade`, Section S3; the counts also as Table S1, Section S1) | present; the text could cite "Supplementary Figure S2" |
| `methods.tex:33` | "A diagram of the readout is given in the Supplementary Materials" | Figure S1 (`fig_readout`, Section S2) | present; the text could cite "Supplementary Figure S1" (as `docs/figure_integration.md` section 2 proposes) |
| `methods.tex:90` | "the designs are drawn in the Supplementary Materials" | Figure S3 (`fig_splits`, Section S3) | present; the text could cite "Supplementary Figure S3" |
| `methods.tex:136` | "every departure from the registered plan is logged ... (`docs/deviations.md`); all are reported in the Supplementary Materials" | Section S9.4 summarises the deviations by kind and points to the full log in the code release; Table S12 lists the provenance label of every result group | MISMATCH in extent: the SI does not reproduce every deviation row, as the W3 brief specified (summary plus pointer). Either the sentence should say that the SI summarises them and the full log is in the repository, or the full log must be added to the SI. Author decision. |

## Back matter

`paper/main.tex` now carries the MDPI `\supplementary{...}` statement (one line, before the Author
Contributions), listing Sections S1 to S9, Figures S1 to S8 with short titles, and Tables S1 to S12; it matches the
compiled SI. The MDPI link `\linksupplementary{s1}` resolves only once the journal assigns the DOI.

## Consistency of the values cited in both documents

The article (Section 3.9) quotes the N1 seed-ensemble shifts from `results/nrp/n1_recompute.json`; Table S8 of the
SI uses `results/nrp/nrp_n1_gpu_repeat.json`. The five values cited in both were compared at full precision and are
identical. All other SI numbers are macros of the same records the article uses.

## To recheck after W2 merges

W2 edits the Discussion, Conclusions and Abstract in parallel. At the W3 merge these files contained no SI
citation; any later citation of a Supplementary Figure, Table or Section must be checked against the table above.

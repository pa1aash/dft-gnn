# Placeholders to fill at the final tag and the Zenodo upload (Q0)

Session Q0, 2026-10-15. Every occurrence of `[FINAL-TAG-TBD]` and `[ZENODO-DOI-TBD]` in the tracked files under `paper/`,
`deposit/` and `docs/` (this file excluded), found with `git grep -F` on the Q0 branch. None is filled here: the tag is
created at the results freeze and the DOI is reserved on the Zenodo draft (`docs/deposit_checklist.md`, steps 3 and 4).
Lines that only describe the placeholders, in the checklists and drafts, need no replacement; the others take the final
values. After filling, rerun `git grep -nF -e '[FINAL-TAG-TBD]' -e '[ZENODO-DOI-TBD]' -- paper deposit docs`, which should list
only the descriptive lines.

18 lines in 9 files.

| File | Line | Placeholder | Context |
|---|---|---|---|
| `deposit/.zenodo.json` | 18 | `[FINAL-TAG-TBD]` | 1aash/dft-gnn, cluster reference tag nrp-code-v1, final tag [FINAL-TAG-TBD]. README.md describes every file; FILES.sha256 lists the sha256 a |
| `deposit/CITATION.cff` | 4 | `[FINAL-TAG-TBD]`, `[ZENODO-DOI-TBD]` | # At the results freeze add: doi (the Zenodo DOI, [ZENODO-DOI-TBD]), version ([FINAL-TAG-TBD]), |
| `deposit/README.md` | 3 | `[FINAL-TAG-TBD]`, `[ZENODO-DOI-TBD]` | DRAFT for the Zenodo record. DOI: **[ZENODO-DOI-TBD]**. Final code tag: **[FINAL-TAG-TBD]**. Both |
| `deposit/README.md` | 28 | `[FINAL-TAG-TBD]` | \| 'dft-gnn-[FINAL-TAG-TBD].zip' \| code snapshot: 'git archive' of the final tag of https:// |
| `deposit/README.md` | 62 | `[FINAL-TAG-TBD]` | \| Code release, final \| tag '[FINAL-TAG-TBD]'; snapshot 'dft-gnn-[FINAL-TAG-TBD].zip' \| 'FILES.sha256' (compo |
| `docs/data_availability.md` | 8 | `[ZENODO-DOI-TBD]` | - **[ZENODO-DOI-TBD]**: the DOI of the Zenodo record. The DOI can be reserved before |
| `docs/data_availability.md` | 9 | `[FINAL-TAG-TBD]` | - **[FINAL-TAG-TBD]**: the final code tag. |
| `docs/data_availability.md` | 39 | `[ZENODO-DOI-TBD]` | his study are openly available in Zenodo at https://doi.org/[ZENODO-DOI-TBD] |
| `docs/data_availability.md` | 60 | `[FINAL-TAG-TBD]` | ag nrp-code-v1. The results reported here correspond to tag [FINAL-TAG-TBD], which is |
| `docs/data_availability.md` | 61 | `[ZENODO-DOI-TBD]` | > archived in the Zenodo record above (https://doi.org/[ZENODO-DOI-TBD]). |
| `docs/deposit_checklist.md` | 14 | `[FINAL-TAG-TBD]` | \| Final tag \| placeholder '[FINAL-TAG-TBD]' ('configs/config.yaml' names 'results-v1' as 'gates.G2_tag') \| |
| `docs/deposit_checklist.md` | 16 | `[ZENODO-DOI-TBD]` | \| Zenodo DOI \| placeholder '[ZENODO-DOI-TBD]' \| reserved in step 3 below \| |
| `docs/deposit_checklist.md` | 59 | `[FINAL-TAG-TBD]`, `[ZENODO-DOI-TBD]` | 1. Replace '[ZENODO-DOI-TBD]' with the reserved DOI, and '[FINAL-TAG-TBD]' with the tag name |
| `docs/mdpi_checklist.md` | 21 | `[ZENODO-DOI-TBD]` | ons/data_availability.tex:2' names Zenodo, the placeholder '[ZENODO-DOI-TBD]' and the Kumagai et al. database with its licence \| FIX at the |
| `paper/sections/data_availability.tex` | 2 | `[ZENODO-DOI-TBD]` | supporting this study are archived at Zenodo, DOI: \textbf{[ZENODO-DOI-TBD]}. Formation energies, descriptors and structures are taken from |
| `paper/sections/methods.tex` | 136 | `[FINAL-TAG-TBD]`, `[ZENODO-DOI-TBD]` | dated log is released with the code (final code tag \texttt{[FINAL-TAG-TBD]}; Zenodo deposit, DOI \textbf{[ZENODO-DOI-TBD]}). |
| `paper/si/sections/s9_reproducibility.tex` | 8 | `[FINAL-TAG-TBD]` | results{}, and the final code tag of the release is \texttt{[FINAL-TAG-TBD]}, to be set when the |
| `paper/si/sections/s9_reproducibility.tex` | 36 | `[ZENODO-DOI-TBD]` | d models are deposited in Zenodo under \ccby{} (DOI \texttt{[ZENODO-DOI-TBD]}, to be minted at |

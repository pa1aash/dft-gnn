# Author details

Purpose: one record of the author details used in the manuscript and the deposit, where each was
applied, and the draft contributor roles. The details were supplied by the authors.

## Details used

| Author | Affiliation | Email | ORCID | Corresponding |
|---|---|---|---|---|
| Palaash Gang | Indus International School, Pune, India | palaash.gang@indusschoolpune.com | 0009-0006-7448-9488 | yes |
| Aiden Lee | Westview High School, San Diego, CA, USA | aiden.lee.sd@gmail.com | 0009-0007-3281-8420 | no |

## Where each detail is applied

| File | Field | Status |
|---|---|---|
| `paper/main.tex` | `\orcidauthorB` and `\orcidB{}` after Aiden Lee in `\Author`, the same markup as Palaash's `\orcidauthorA` and `\orcidA{}` | applied in J3 |
| `paper/main.tex` | `\address` line 2: affiliation and email, replacing the AFFILIATION-TBD and EMAIL-TBD placeholders | applied in J3 |
| `paper/main.tex` | the corresponding-author asterisk and `\corres` stay on Palaash Gang only | unchanged |
| `deposit/CITATION.cff` | Aiden Lee's affiliation, email and ORCID | already applied in J2 (merge f5aa074); not touched in J3 |
| `deposit/.zenodo.json` | Aiden Lee's affiliation and ORCID | already applied in J2 (merge f5aa074); not touched in J3 |

The built PDF's first page shows both authors with affiliation marks 1 and 2, an ORCID icon after
each name (links to orcid.org/0009-0006-7448-9488 and orcid.org/0009-0007-3281-8420), and the
correspondence line for Palaash Gang only.

## Contributor roles (CRediT)

**DRAFT PENDING CONFIRMATION by both authors.** The same draft is printed in the manuscript from
`paper/sections/author_contributions.tex`, which keeps its own DRAFT marker until both authors
confirm.

| CRediT role | Palaash Gang (P.G.) | Aiden Lee (A.L.) |
|---|---|---|
| Conceptualization | yes | |
| Methodology | yes | |
| Software | yes | yes |
| Validation | | yes |
| Formal analysis | | yes |
| Investigation | | yes |
| Resources | | yes |
| Data curation | yes | |
| Writing, original draft | yes | |
| Writing, review and editing | | yes |
| Visualization | | yes |
| Supervision | yes | |

Before submission both authors confirm this table; then remove the DRAFT marker from
`paper/sections/author_contributions.tex` and from this file in the same commit.

# Data Availability and Code Availability: drafts

Session J2, 2026-10-12. These are drafts for the back matter of the Crystals (MDPI) article.
`paper/sections/data_availability.tex` is not changed here. Paste the agreed text there after the DOI is minted
(`docs/deposit_checklist.md`).

Placeholders, filled at the results freeze:
- **[ZENODO-DOI-TBD]**: the DOI of the Zenodo record. The DOI can be reserved before the record is published.
- **[FINAL-TAG-TBD]**: the final code tag.

## Rules applied (from `docs/venue.md`, section A4; back-matter order in section A1; statements in section A3)

- A Data Availability Statement is mandatory. It must say where the supporting data are, with links to archived
  datasets.
- Data and code go in a trusted repository, with:
  - long-term preservation;
  - a persistent identifier (DOI);
  - open access without login;
  - an open licence (CC0 or CC BY).

  Zenodo mints DataCite DOIs. The record uses CC BY 4.0 for data and MIT for code.
- Datasets are cited formally in the reference list. For a previously published dataset, cite both the dataset
  and its article. Here that means the Zenodo record, plus Kumagai et al. 2021, plus the pinned database
  repository.
- Use the templates for "public repository" and "derived from public-domain resources":
  - name the repository and its DOI or URL;
  - name the source resources.
- Novel code is released in a public repository such as GitHub. Software names and versions are given in
  Methods.
- Do not write "data not shown". Raw data should be deposited before submission, or at least be available to
  referees. MDPI's repository criteria include confidential reviewer access.
- MDPI's back-matter list has no separate Code Availability heading. Section A1 gives the order: Supplementary Materials, Author
  Contributions, Funding, IRB, Informed Consent, Data Availability Statement, Acknowledgments, Conflicts of
  Interest. So the code text below is written to be appended to the Data Availability Statement. It can also
  stand alone if the editorial office prefers.

## Data Availability Statement (draft)

> The data supporting this study are openly available in Zenodo at https://doi.org/[ZENODO-DOI-TBD]
> (reference [Zenodo record]), under the Creative Commons Attribution 4.0 International licence (CC BY 4.0).
> The record contains:
> - the processed site table (818 hosts, 1726 oxygen sites);
> - the graph store and its manifest;
> - the cross-validation splits and job specifications;
> - the per-site predictions and result records of every run;
> - the trained checkpoints made before the cluster stages;
> - a sha256 manifest of every file.
>
> All formation energies, descriptors and structures are derived from the oxygen-vacancy database of
> Kumagai et al. [Kumagai2021insights]. That database is available at
> https://github.com/kumagai-group/oxygen_vacancies_db (commit e310353) under CC BY 4.0.
>
> No new DFT calculations were performed. Checkpoints, relaxed structures and embeddings from the National
> Research Platform runs are too large for the record. They are listed by sha256 in the record and are available
> from the corresponding author on request.

## Code Availability (draft)

> The code used in this study is available at https://github.com/pa1aash/dft-gnn under the MIT licence.
> The cluster runs used tag nrp-code-v1. The results reported here correspond to tag [FINAL-TAG-TBD], which is
> archived in the Zenodo record above (https://doi.org/[ZENODO-DOI-TBD]).
>
> The MACE-MP-0 medium weights used for the MLIP relaxations are redistributed unchanged in the same record,
> under their MIT licence.

## Still to do before these drafts can go into the paper

- Add a reference-list entry for the Zenodo record. Fetch it from DataCite or doi.org content negotiation once
  the DOI resolves; do not type it by hand.
- Decide whether the database repository gets its own reference entry. It has no DOI, so it would be cited by URL
  and commit (`docs/provenance.md`, "Database release").
- Decide whether "available on request" is acceptable for the cluster artefacts. MDPI allows it as a template.
  It does depend on the NRP volume being kept, though (`docs/nrp_runbook.md`, section 5).

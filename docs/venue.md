# Venue: Crystals (MDPI), Inorganic Crystalline Materials section, with a ChemRxiv preprint

Session S01, retrieved 2026-10-05. All policy text is paraphrased; every fact carries its source URL.
Retrieval was headless throughout. www.mdpi.com refuses direct curl (HTTP 403), so MDPI pages were read
through the r.jina.ai text reader; chemrxiv.org sits behind a Cloudflare challenge, so ChemRxiv policy
was read from the identical static term files served by www.cambridge.org. Failed fetches are listed at
the end.

## Decision summary

| Item | Finding |
|---|---|
| APC | CHF 2100, invoiced only after acceptance (was CHF 2600 until mid-2024). |
| Waiver routes now listed | IOAP (institutional; not available to an independent researcher), reviewer vouchers, invited-paper discounts, affiliated-society (PC-KMTEC) discount, Editorial Board waiver. The need-based / LMIC waiver text present in Dec 2025 is no longer on the APC page; only an informal request to crystals@mdpi.com remains. |
| Abstract / keywords | One paragraph, about 200 words or fewer, no headings or citations; 3-10 keywords. |
| Mandatory back matter | Author Contributions (CRediT roles), Funding, Data Availability Statement, Conflicts of Interest; IRB/consent "Not applicable". |
| References | Numbered [1], ACS-based MDPI style, `mdpi.bst` for BibTeX. |
| Figures | Preferably at least 600 dpi; PNG/JPEG/TIFF; RGB. No MDPI-stated widths; class geometry gives text width about 138.6 mm and full width about 184.6 mm. |
| Supplementary | Figure S1 / Table S1 numbering; submission at most 120 MB; files over 250 MB go to a DOI-minting repository. |
| LaTeX template | https://res.mdpi.com/data/MDPI_template_ACS.zip?v=20260911 (671,712 B, `mdpi.cls` v6.5a, 2026-09-11). No licence in the zip; MDPI says templates are for journal submission only and not for preprint posting. Keep it out of the tracked tree (`paper/local/`). |
| Preprint | ChemRxiv is compatible. Disclose the preprint DOI and licence at submission; do not update it during review; do not also post to Preprints.org; do not post an MDPI-branded PDF. |
| ChemRxiv | Submitting author needs ORCID; licence CC BY 4.0, CC BY-NC 4.0 or CC BY-NC-ND 4.0 (no CC0); curator screening in 1-2 business days; no affiliation, supervisor or student rule found. Choose CC BY 4.0 to match the journal licence. |
| Affiliation | MDPI asks unaffiliated authors to list "Independent Researcher". |
| Best Special Issue | "Predictive Modelling of Inorganic Functional Materials" (section ICM), deadline 10 December 2026, Guest Editor R. A. Jackson. General (non-SI) submission to the section is always available. |

## Fetch methods used (legend)

- **[M-JINA]**: direct `curl` to www.mdpi.com returned HTTP 403 (Akamai "Access Denied") even with a desktop Chrome UA, `Accept: text/html` and `Accept-Language`. The bare `mdpi.com` host also returned 403. Pages were fetched headlessly with `curl https://r.jina.ai/<url>` (reader proxy, returns markdown). This worked for every www.mdpi.com page listed below.
- **[M-DIRECT]**: plain `curl -sL` with a desktop UA worked (mdpi-res.com / res.mdpi.com files, overleaf.com, www.cambridge.org assets).
- **[M-WAYBACK]**: `curl https://web.archive.org/web/<timestamp>/<url>`. This worked for older snapshots early in the session. Later the Internet Archive returned "Temporarily Offline" / HTTP 429.
- **[M-CAM-ASSET]**: chemrxiv.org sits behind a Cloudflare challenge (403 direct, and the reader proxy only got the challenge page, including with its browser engine). The ChemRxiv About/Policy/Submission pages are a JS app that loads static HTML "term" files. The same files are served without Cloudflare at `https://www.cambridge.org/engage/assets/public/chemrxiv/term/<name>.htm` (path found in the app's Nuxt state, where the `coe` partner key is swapped for `chemrxiv`). They were fetched with direct curl and returned HTTP 200. Caveat: these are the source files behind the live chemrxiv.org pages, not a render of chemrxiv.org itself.


---

## A. Manuscript requirements

Primary source: Crystals Instructions for Authors, https://www.mdpi.com/journal/crystals/instructions [M-JINA]. Supplemented by the MDPI Layout Style Guide, https://www.mdpi.com/authors/layout [M-JINA], and MDPI Research and Publication Ethics, https://www.mdpi.com/ethics [M-JINA].

### A1. Article type and structure
- An Article is original research. Its expected structure is Abstract, Keywords, Introduction, Materials and Methods, Results, Discussion, and Conclusions (optional). Source: instructions, "Types of Publications".
- Research manuscripts have three parts (instructions, "General Considerations"):
  - Front matter: title, author list, affiliations, abstract, keywords.
  - Body: Introduction, Materials and Methods, Results, Discussion, Conclusions (optional).
  - Back matter: Supplementary Materials, Author Contributions, Funding, Data Availability Statement, Acknowledgments, Conflicts of Interest, References.
- Back-matter order in the Layout Style Guide (section 8; no numbering on back-matter headings): Supplementary Materials, Author Contributions, Funding, Institutional Review Board Statement, Informed Consent Statement, Data Availability Statement, Acknowledgments, Conflicts of Interest/Disclaimer, Glossary/Nomenclature/Abbreviations, Appendix, References. Source: https://www.mdpi.com/authors/layout.
- Free-format first submission is accepted, but these sections must still be present: author information, abstract, keywords, introduction, methods, results, conclusions, figures/tables with captions, funding, author contributions, conflicts of interest and other ethics statements. Any consistent reference style is allowed at first submission. Journal formatting is required at the revision stage. Source: instructions, "Free Format Submission".
- Article length: the section page says there is no restriction on article length. Source: https://www.mdpi.com/journal/crystals/sections/inorganic_crystalline_materials [M-JINA].
- Methods must name the software and version used and say whether code is available. Source: instructions, "Research Manuscript Sections".
- File formats (instructions, "Accepted File Formats"):
  - Word: a single file.
  - LaTeX: one ZIP containing all sources and images so the office can recompile.
  - Total upload limit: 120 MB.
- Cover letter (instructions, "Cover Letter"):
  - It is mandatory. It should explain significance and fit to scope.
  - Any previous submission to an MDPI journal must be acknowledged.
  - Suggested and excluded reviewers go into the submission system, not the letter.
  - The letter must contain two near-verbatim confirmations: (1) the manuscript or its content is not under consideration or published elsewhere; (2) all authors approved it and agree to its submission to Crystals.
- Reviewer suggestions: three potential reviewers with full contact details. They must not be recent co-authors (within 3 years) or current collaborators, and must be from other institutions. Source: instructions, "Reviewer Suggestions".
- Affiliation:
  - Authors give their current affiliation and the one where the work was done.
  - Authors with no university, institution or company affiliation, now or during the work, should list themselves as "Independent Researcher".
  - Affiliations use the PubMed/MEDLINE address format: city, postcode, state/province, country.
  - Email addresses of all authors are shown on the published paper.
  - Source: instructions, "Author Affiliation", "Independent Researcher", and "Front Matter".
- Biography (300–1500 characters) is optional. ORCID is linked on publication. Source: instructions, "Author Identification".
- Chemical characterisation checklist: strongly encouraged when a paper reports synthesis or characterisation of compounds. A purely computational paper has nothing to fill in, but the inorganic-compound identity rules (XRD etc.) are written for new compounds. Source: instructions, "Correct Identification and Characterization of Chemical Compounds"; checklist at https://mdpi-res.com/data/crystals_cmpd-check-list-v3.pdf (link seen on the page; not downloaded).
- Statement of COI disclosure: there is an MDPI disclosure form, https://res.mdpi.com/data/mdpi-disclosure-form-20260828.pdf (curl -I returned 200, application/pdf) [M-DIRECT]. The COI summary sits just before the references. Source: instructions, "Conflicts of Interest".

### A2. Abstract and keywords
- Abstract (instructions, "Front Matter"):
  - About 200 words maximum, in one paragraph.
  - Structured style but without headings: background, methods, results, conclusions.
  - It must not contain results that are absent from the main text or overstate conclusions.
- The Layout Guide adds rules for the abstract: up to 200 words; no figures, tables, equations, links or citations; abbreviations defined inside it. Source: https://www.mdpi.com/authors/layout §2.4.
- Keywords: 3–10, after the abstract, specific but reasonably common in the field. Source: instructions, "Front Matter".
- Graphical abstract (optional):
  - PNG, JPEG or TIFF, minimum 560 × 1100 px (height × width).
  - It must not duplicate a body figure.
  - It must not carry the heading "Graphical Abstract".
  - Source: instructions, "General Considerations".
- Acronyms are defined at first use in each of three places: the abstract, the main text, and the first figure/table. Source: instructions.

### A3. Mandatory / standard back-matter statements
- **Author Contributions (CRediT).** Contributions are given with CRediT role terms: Conceptualization; Methodology; Software; Validation; Formal Analysis; Investigation; Resources; Data Curation; Writing—Original Draft Preparation; Writing—Review & Editing; Visualization; Supervision; Project Administration; Funding Acquisition. These are followed by author initials. The ethics page version ends with the sentence that all authors have read and agreed to the published version.
  - The instructions word the paragraph as required for papers "with several authors". The template and ethics page show the same paragraph form, so a sole author would normally still list roles with their own initials. This is an inference; no explicit sole-author rule was found.
  - CRediT explainer PDF: http://img.mdpi.org/data/contributor-role-instruction.pdf (curl -I returned 200, PDF) [M-DIRECT]. CRediT site: https://credit.niso.org/ (200) [M-DIRECT]. The Layout Guide also links https://casrai.org/credit/ (not fetched).
  - Sources: instructions "Back Matter"; https://www.mdpi.com/ethics "Authorship / Author Contributions".
- **Funding.** All funding must be disclosed. Near-verbatim standard forms: "This research received no external funding" or "This research was funded by [funder], grant number [x]". Funder names follow the Crossref Funder Registry (https://search.crossref.org/funding). Source: instructions "Back Matter".
- **Institutional Review Board Statement / Informed Consent Statement.** These apply only to human or animal studies. "Not applicable" may be stated, or the statement omitted, for studies without humans or animals. Sources: https://www.mdpi.com/authors/layout §8.4–8.5; template.tex in the LaTeX zip.
- **Data Availability Statement.** Mandatory for research articles. Details in A4.
- **Acknowledgments.** For support that does not qualify for authorship. Use full names without titles. Generative-AI use goes here too; see ai_policy_raw.md. Sources: instructions; layout §8.7.
- **Conflicts of Interest.** Mandatory, placed just before the references. Near-verbatim no-conflict form: "The authors declare no conflicts of interest." Any funder role must be stated; if funders had no role, a standard sentence says so. Source: instructions "Conflicts of Interest"; template.tex.
- **Abbreviations.** Optional glossary section. Source: layout §8.9; template.tex `\abbreviations{}`.
- **Appendix.** Optional. Numbered A, B…; figures inside are Figure A1 and so on. Source: layout §8.10.
- **Supplementary Materials.** If used, there is a back-matter paragraph listing each item as "Figure S1: title; Table S1: title; …". Source: instructions "Back Matter"; template.tex `\supplementary{}`.
- **Dual-use statement (`\durcstatement`).** Present but commented out in the template; only for dual-use research of concern. Source: template.tex.

### A4. Data Availability Statement rules (MDPI Research Data Policies)
- Location: https://www.mdpi.com/ethics, section "MDPI Research Data Policies" [M-JINA]. The same text appears on the Crystals instructions page under "Supplementary Materials, Data Deposit and Software Source Code". The guessed URL https://www.mdpi.com/authors/data returned "Error 404" (see Failed fetches).
- A DAS is required for all MDPI research articles. It must say where the supporting data are, with links to archived datasets. A statement is still needed when no new data were created or when data are restricted.
- Data should follow FAIR principles. Data and code should go in a trusted repository. Repository criteria:
  - long-term preservation;
  - persistent identifiers, usually DOIs;
  - open access without login;
  - open licences, with CC0 or CC BY required in most cases;
  - confidential reviewer access.
- re3data.org and fairsharing.org are suggested for finding repositories. An institutional repository is fine if it mints DataCite DOIs.
- Datasets should be formally cited in the reference list. For previously published datasets, cite both the dataset and its article. Editorial staff check this.
- Recommended DAS templates cover these situations: public repository; on request because of restrictions; third-party data; embargo; restricted datasets; data derived from public-domain resources; not applicable (no new data / purely theoretical); data in the article/supplement; on request from the authors.
  - Relevant to this project: the "derived from public-domain resources" template names the repository, URL/DOI and the source resources. The "public repository" template names the repository and DOI.
- Data preservation: authors are encouraged to keep data for at least 5 years. If a repository disappears, MDPI may ask for re-deposit plus a correction.
- Code: novel code should be released in a public repository such as GitHub or as supplementary information. Give the name, version and maker of all software and all run parameters. Source: instructions "Computer Code and Software".
- Large data: files over 250 MB must be deposited externally (DataCite-type repository preferred). The paper must give the repository name, URL and accession/DOI. Source: instructions "Remote Hosting and Large Data Sets".
- "Data not shown" should be avoided. Source: instructions "Unpublished Data".
- Raw data should preferably be deposited before submission and must at least be available to referees. Source: instructions "Publication Ethics Statement".

### A5. Reference style
- Crystals uses the MDPI ACS-based style:
  - numbered in order of first appearance (including captions);
  - in-text numbers in square brackets placed before punctuation, e.g. [1], [1–3], [1,3];
  - full article titles, as in the ACS guide.
  - Source: instructions "References".
- Journal reference pattern: Author, A.B.; Author, C.D. Title. *Abbrev. Journal* **Year**, *Volume*, pages. Websites: Title. Available online: URL (accessed on day month year). Source: instructions.
- Journal names are abbreviated per ISO 4 (ISSN LTWA). If unsure, give the full title and the office abbreviates it. Source: https://www.mdpi.com/authors/references [M-JINA].
- Full style guide PDF: https://res.mdpi.com/data/mdpi-acs-references-guide-v11-2025.12.pdf (link seen on references page; not downloaded).
- Reference managers:
  - EndNote style: http://endnote.com/downloads/style/mdpi.
  - Zotero/CSL style: https://www.zotero.org/styles/multidisciplinary-digital-publishing-institute (curl -I returned 200, CSL XML) [M-DIRECT].
  - LaTeX users should use BibTeX with the template's `mdpi.bst`.
  - Sources: instructions; references page.
- References cited only in the supplement must also appear in the main reference list. Source: instructions; layout §8.1.
- Layout Guide: the reference list should cite static content. Changeable things such as GitHub project pages may be put in the main text instead. Source: layout §8.11.

### A6. Preprint-related manuscript items (see F for the full preprint policy)
- Template disclaimer, Crystals instructions: the Word/LaTeX templates are only for submission to the journal. They may not be used to post online on preprint servers or other websites.
- This conflicts with a comment in the template.tex inside the current zip. That comment says a `preprints` journal option can be used to post an early version as a preprint.
- Safe reading: post the ChemRxiv PDF without MDPI/Crystals branding or the journal option.

---

## B. Figure specifications and supplementary material

### B1. Figures
- Crystals instructions, "Preparing Figures, Schemes and Tables" (https://www.mdpi.com/journal/crystals/instructions) [M-JINA]:
  - Quality "preferably no less than 600 dpi".
  - Formats: PNG, JPEG or TIFF.
  - Colour (RGB, 8 bits per channel) is encouraged and free.
  - Images should be combined, with no editable parts.
  - Table fonts no smaller than 8 pt.
  - Figures go near their first citation, numbered in order.
  - Text in figures is English only, with correct minus signs and decimal points.
  - Numbers of five or more digits get commas.
  - Every symbol must be explained in the caption.
  - Reprinted or adapted figures need a copyright note.
- Layout Style Guide §7.1 (https://www.mdpi.com/authors/layout) [M-JINA]:
  - Recommended minimum is 600 dpi. Any common format (tif, jpg, png) is allowed.
  - All fonts embedded; aspect ratio locked.
  - Panels labelled a, b, c… and each described in the caption. Prefer letters over left/right.
  - No "[xx]" reference callouts inside images. No watermarks. QR codes discouraged.
  - Use proper scientific notation, not 3.7e5 or E-notation.
  - Leading zero before decimals.
  - Production converts all figures to TIFF for publication.
  - Captions are mandatory, below figures, and self-explanatory.
  - Do not abbreviate "Figure" as "Fig." in text.
- Original images: the office may ask for original, unprocessed images. These are at least 1000 px or 300 dpi, uploaded as supplementary files. This is aimed at micrographs, gels and similar images. Source: instructions "Original Images Requirements".
- Column widths: neither the instructions nor the Layout Guide gives width values in mm or pt. Values derived from the LaTeX class geometry (`Definitions/mdpi.cls` v6.5a, 2026-09-11, in the zip) for A4, journal mode:
  - Left margin 5.87 cm (it includes a 4.1 cm side column plus 0.51 cm separation). Right margin 1.27 cm.
  - So `\textwidth` is about 21 − 5.87 − 1.27 = **13.86 cm (138.6 mm)**.
  - Full-page-width figures use `adjustwidth{-\extralength}{0cm}` with `\extralength` = 4.61 cm. That gives about **18.46 cm (184.6 mm)**, which matches `\fulllength` = 21 − 2×1.27 cm in the class.
  - The template's example figure uses `width=8.0 cm` (normal) and four 7.0 cm subfloats in the wide example.
  - Status: derived, not an MDPI-stated spec.
  - Source: zip downloaded from https://mdpi-res.com/data/MDPI_template_ACS.zip [M-DIRECT].
- In preprint mode the class uses 2.7 cm left and right margins, so text width is about 15.6 cm. Source: same class file.

### B2. Supplementary material
- Any file format is allowed; common, non-proprietary formats are recommended. Files are uploaded as "Supplementary Files" and are visible to referees. Source: instructions "Supplementary Material".
- Total submission is at most 120 MB. Files over 250 MB must go to an external repository. The Layout Guide notes MDPI-hosted files may have size limits, and the office can offer alternatives. Sources: instructions; layout §8.1.
- Naming and referencing:
  - Supplementary items use the S prefix: Figure S1, Table S1, Equation S2, Video S1.
  - They must be cited in the main text.
  - The back-matter "Supplementary Materials" paragraph lists each item with its title.
  - Sources: instructions "Back Matter"; layout §8.1; template.tex.
- Externally hosted supplements must use a repository with DOIs (DataCite or equivalent) and a preservation policy; a personal website is not suitable. List the link in "Supplementary Materials" with an access date. Source: layout §8.1.
- References cited in the supplement must be in the main reference list. Otherwise add a note such as "References [x,y] are cited in the supplementary materials". Source: layout §8.1; instructions.
- Appendix vs supplement: appendices sit inside the article, labelled A, B…; supplements are separate files. Source: layout §8.10.

---

## C. LaTeX template

- Template page: https://www.mdpi.com/authors/latex [M-JINA]. Three zips are offered, each "last updated 11 September 2026":
  - ACS citation style (the one Crystals uses): https://res.mdpi.com/data/MDPI_template_ACS.zip?v=20260911. The Crystals instructions link the same URL.
  - APA: https://res.mdpi.com/data/MDPI_template_APA.zip?v=20260911.
  - Chicago: https://res.mdpi.com/data/MDPI_template_Chicago.zip?v=20260911.
  - LyX: https://res.mdpi.com/data/MDPI_template_lyx.zip?v=20260911.
  - LaTeX support: latex@mdpi.com.
- `curl -sIL` checks [M-DIRECT]:
  - `https://res.mdpi.com/data/MDPI_template_ACS.zip?v=20260911`: 301 redirect, then 200, `application/zip`, content-length 671712 bytes, Last-Modified Fri, 11 Sep 2026 10:21:58 GMT.
  - `https://mdpi-res.com/data/MDPI_template_ACS.zip`: 200, `application/zip`, 671712 bytes, same Last-Modified.
  - SHA-256 of the downloaded zip: 62744425fbcec9cd3e58147cbee65bdec2e2ff0440f29792c26edc97a11b6c70. Downloaded only to the scratchpad for inspection.
- Zip contents:
  - `template.tex`.
  - `Definitions/`: `mdpi.cls`, `mdpi.bst`, `mdpi_chicago.bst`, `mdpi_apacite.bst`, `mdpi_apacite.sty`, `journalnames.tex`, `unicode.tex`, and logos.
  - `mdpi.cls` identifies itself as v6.5a dated 2026-09-11 (the v6.0 layout change was December 2025).
  - The class option for Crystals is `crystals`. For a single author the class comment says to use the option `oneauthor` instead of `moreauthors`.
- **Licence.** The zip has no README, LICENSE or LPPL notice. The header of `mdpi.cls` only lists contributors, version history and the support email. No licence text was found in `template.tex`, `mdpi.cls` or `mdpi.bst`. The only usage terms found are the instructions-page disclaimer: templates are only for journal submission and not for posting on preprint servers or websites.
  - Status: licence not stated; treat as MDPI-proprietary submission tooling and do not redistribute it in the tracked repo. If needed, ask latex@mdpi.com.
- Overleaf: https://www.overleaf.com/latex/templates/mdpi-article-template/fcpwsspfzsph returned 200 [M-DIRECT].
  - The gallery page says author MDPI, "Last Updated: 3 months ago", and licence "Creative Commons CC BY 4.0".
  - Its blurb says it is the official MDPI template "as of December 2022". This text may be stale relative to the 2026-09-11 zip.
  - The MDPI LaTeX page recommends Overleaf and its "Submit to an MDPI journal" route.
  - The Crystals instructions also mention a writeLaTeX gallery URL, https://www.writelatex.com/templates/mdpi-article-template/fvjngfxymnbr (not fetched).

---

## D. Inorganic Crystalline Materials section: scope and editors

- Section page: https://www.mdpi.com/journal/crystals/sections/inorganic_crystalline_materials [M-JINA].
- Aims (paraphrase): a forum for nucleation, growth, processing, structure and property characterisation, and applications of inorganic crystalline materials. Mechanical, chemical, electronic, magnetic and optical properties are all in scope. The journal welcomes experimental, theoretical and computational results in reproducible detail, with no length limit.
- Subject areas listed:
  - Bulk or thin-film inorganic crystals: semiconductors, magnetic systems, superconductors, graphene, photonic, piezoelectric, ferroelectric, optical (including NLO and laser) and scintillating crystals.
  - Growth techniques and characterisation techniques (XRD, PL, electron microscopy, neutron diffraction, and others).
  - Fundamental research in solid-state physics and chemistry, crystalline surfaces, crystal structure, interfaces, and crystallisation mechanisms.
- Fit note (interpretation): computational defect energetics of oxides fits under "solid-state physics and chemistry" and "computational results". Point defects are not named explicitly.
- Section Editor-in-Chief: **Dr. Zongyou Yin**, Research School of Chemistry, ANU, Canberra, Australia. Sources: https://www.mdpi.com/journal/crystals/sections [M-JINA]; https://www.mdpi.com/journal/crystals/editors [M-JINA, HTML return format used to recover names].
- Journal Editor-in-Chief: **Prof. Dr. Alessandra Toncelli**, Department of Physics, University of Pisa, Italy. Source: https://www.mdpi.com/journal/crystals/editors.
- Section editorial board link: https://www.mdpi.com/journal/crystals/sectioneditors/inorganic_crystalline_materials (not fetched).
- Section size: 3069 articles; 35 Special Issues currently open in this section. Source: sections page.
- Topical Collections: the sections page shows **no Topical Collection for Inorganic Crystalline Materials**. Crystals' Topical Collections page lists only three, none relevant: Mineralogical Crystallography; Liquid Crystals and Their Applications; Feature Papers in Biomolecular Crystals. Source: https://www.mdpi.com/journal/crystals/topical_collections [M-JINA].
- A Crystals Special Issue page (15th Anniversary) states an Impact Factor of 2.4 and JCR Q2 (Crystallography). Source: https://www.mdpi.com/journal/crystals/special_issues/98A9S65GYQ [M-JINA].

---

## E. Costs: APC and every discount or waiver route

- **Crystals APC: CHF 2100 (Swiss francs)**, charged only after acceptance.
  - It covers peer review, copyediting, typesetting, archiving and management.
  - Payment is accepted in CHF, EUR, USD, GBP, JPY or CAD.
  - Local VAT or sales tax is added where applicable.
  - Only invoices from @mdpi.com are valid.
  - Source: https://www.mdpi.com/journal/crystals/apc [M-JINA].
- APC history [M-WAYBACK]:
  - CHF 2600 in snapshots of https://www.mdpi.com/journal/crystals/apc from 2024-02-13 and 2024-06-16.
  - CHF 2100 in snapshots from 2025-01-04 and 2025-07-16, and on the live page (2026-10-05).
  - So the APC fell from CHF 2600 to CHF 2100 between mid-2024 and January 2025, and has been unchanged since. The 2024-09-14 snapshot did not contain the APC string.
- The APC includes only minor English editing. Extensive editing is not included and may delay the paper. Sources: instructions "Extensive English Editing"; https://www.mdpi.com/about/apc.
- Discount and waiver routes on the current MDPI APC page (https://www.mdpi.com/about/apc, "Discounts and Waivers") [M-JINA]. Support ranges from partial discounts to full waivers and varies by journal and pathway. The routes listed are:
  1. **IOAP (Institutional Open Access Program).**
     - Authors at participating institutions get an APC discount; central or flat-fee deals may cover the APC fully or partly.
     - Only one IOAP discount per paper. It can be combined with reviewer vouchers.
     - IOAP members also get 10% off book/chapter charges and 15% off language editing.
     - Over 1000 institutions take part.
     - Not applicable to an "Independent Researcher" affiliation.
     - Sources: https://www.mdpi.com/about/apc; https://www.mdpi.com/about/ioap [M-JINA, fetched in text return format because the markdown version dropped the intro].
  2. **Reviewer vouchers.**
     - Selected reviewers may get a voucher for each review.
     - The voucher is tied to the reviewer's email and applied at or after submission but before acceptance; not after the invoice is issued.
     - It cannot be transferred and can be revoked for misuse.
     - It can be combined with other vouchers and with IOAP or society discounts.
     - It can also pay for MDPI English editing.
     - Sources: https://www.mdpi.com/about/apc; https://www.mdpi.com/reviewers [M-JINA].
  3. **Invited submissions.** Editorial offices may give discounts or waivers for personally invited papers to a journal or Special Issue. Source: https://www.mdpi.com/about/apc.
  4. **Affiliated-society members.** Members of societies affiliated with the journal get discounts. Crystals' listed affiliated society is the Professional Committee of Key Materials and Technology for Electronic Components (PC-KMTEC), China. Members should contact the society representative. Sources: https://www.mdpi.com/journal/crystals/apc; https://www.mdpi.com/journal/crystals/societies [M-JINA].
  5. **Editorial Board Members.** May get up to one full APC waiver per year for their service. Source: https://www.mdpi.com/about/apc ("Editorial Compensation").
- **Need-based / low- and middle-income country (LMIC) waivers: policy change.**
  - The December 2025 snapshot of https://www.mdpi.com/about/apc (web.archive.org 20251230034330) [M-WAYBACK] said:
    - MDPI waived about 25–27% of APCs a year.
    - LMIC authors could get waivers or discounts case by case.
    - Applications made before submission were judged by the Managing Editor on research quality and ability to pay.
    - Waivers could be discussed with the Editorial Office at submission.
  - The **current (2026-10-05) APC page no longer mentions LMIC or need-based waivers**. It lists only IOAP, reviewer vouchers and invited-submission discounts, plus the editor and society items above. No separate waiver-application route was found.
  - Practical reading (inference): a need-based request is now only possible informally, by asking the Crystals editorial office (crystals@mdpi.com) before or at submission. Nothing on the current pages guarantees it.
- "Discounts for previous authors": no such scheme was found on any page fetched.
- Editorial independence: academic editors do not see APC, waiver or discount information. Source: https://www.mdpi.com/about/apc; instructions.
- Interesting Images articles: CHF 550 (not relevant to us). Source: about/apc footnote.

---

## F. Preprints

### F1. MDPI / Crystals preprint policy
- Crystals accepts submissions already posted as preprints, provided they have not been peer reviewed. Source: instructions "Preprints and Conference Papers" [M-JINA].
- MDPI ethics page, "Preprints" (https://www.mdpi.com/ethics) [M-JINA]:
  - Preprints are accepted if not peer reviewed. Preprints of prior publications that would block publication are not considered.
  - **Authors must disclose the preprint, including its DOI and licence, at submission or at any later stage.**
  - **Do not update the preprint with any version of the paper while it is under peer review**, because review is confidential.
  - Disclose any authorship changes between the preprint and the submitted version.
  - Cite relevant preprints used during the research.
  - After publication, authors are encouraged to update the preprint record with the journal DOI and link.
  - The policy follows COPE best practice on preprints.
- MDPI runs Preprints.org. Posting there can be chosen after journal submission, from the Manuscript Information Overview page in SuSy, and does not affect review. Sources: instructions; https://www.preprints.org/instructions-for-authors [M-JINA]. The old path /instructions_for_authors returned 404.
- Conclusion: posting on ChemRxiv **is compatible**. It must be disclosed (DOI plus licence) at submission, and the preprint should not be revised while under review.
- Licence note (interpretation): MDPI publishes under CC BY 4.0 with authors keeping copyright. Choosing CC BY 4.0 on ChemRxiv avoids any conflict. CC BY-NC or CC BY-NC-ND preprints are also generally fine because the author keeps copyright, but this is not stated by MDPI.
- Template caution: see A6. Do not post the preprint in MDPI-branded template form.
- Preprints.org itself advises against posting the same paper on several preprint servers. Since ChemRxiv will be used, do not also tick the Preprints.org option in SuSy. Source: https://www.preprints.org/instructions-for-authors.

### F2. ChemRxiv requirements
Sources: ChemRxiv term files at https://www.cambridge.org/engage/assets/public/chemrxiv/term/{about,policy,submission-guide,author-faq,faq,terms-of-submission}.htm [M-CAM-ASSET]. The chemrxiv.org rendered pages are blocked (see Failed fetches).

- Scope (about.htm): any area of the chemical sciences. Relevant categories include Materials science, Inorganic chemistry, Physical chemistry, and Theoretical and computational chemistry. Pure physics or maths belongs on arXiv.
- Cost: free to post and read. Source: author-faq.htm.
- Who can post (author-faq.htm): ChemRxiv is global and "all interested authors" can submit.
  - **No page states that an institutional affiliation, supervisor or sponsor is needed.** None of the policy, submission guide, FAQ or terms has any rule specific to students or sole authors.
  - The submission form asks each author for an institution (up to five, each at most 512 characters). It also asks whether the submitter is a sole author or has co-authors.
  - Terms of Submission require the submitter to be the sole author or an authorised co-author, and to give accurate identity, position and affiliation information.
  - Inference: an unaffiliated author should enter an honest value such as "Independent Researcher" with a location. Not stated explicitly.
- **ORCID is required for the submitting author** (log-in is via ORCID). Co-authors do not need one. Sources: policy.htm; submission-guide.htm; author-faq.htm.
- Licence options: **CC BY 4.0, CC BY-NC 4.0, or CC BY-NC-ND 4.0** only. **CC0 is not offered.** The author keeps copyright; ChemRxiv gets a non-exclusive hosting and distribution right. Sources: submission-guide.htm; author-faq.htm; terms-of-submission.htm.
- Format:
  - Main file is a PDF; supplementary files may be any format, and links to repositories can be added.
  - Abstract up to 500 words.
  - Up to three categories plus subcategories, and keywords.
  - Content type "Working Paper" for original research.
  - Figures embedded in the text; at least 300 dpi recommended.
  - There is no copyediting, so the uploaded PDF is what appears.
  - Sources: submission-guide.htm; author-faq.htm.
- Required declarations on the form: competing interests (required), funding (encouraged), and ethics approvals where relevant. A Data Availability Statement inside the PDF is encouraged under FAIR principles. Source: policy.htm.
- Moderation:
  - Every upload is screened by PhD-chemist curators, which is not peer review. It usually takes 1–2 business days.
  - Grounds for decline:
    - not scholarly;
    - wrong manuscript type;
    - clinical-practice impact;
    - outside the subject categories;
    - plagiarism (iThenticate is used);
    - already accepted or published after peer review;
    - not in English;
    - infringing content or an unauthorised uploader;
    - libellous, unlawful, inappropriate, confidential or harmful content.
  - Acceptability criteria also include standard manuscript length and structure, new results, no excessive self-citation, original work, and **not posted on another preprint server**.
  - Appeals go to support@chemrxiv.org.
  - Sources: submission-guide.htm; author-faq.htm; policy.htm.
- Originality: content already posted elsewhere, including another preprint server, cannot be uploaded. Content with a final journal acceptance cannot be uploaded either. Source: policy.htm.
- Ordering with the journal: ChemRxiv accepts work that is submitted to a journal but not yet accepted. The author must check that this does not clash with the journal's policy. Source: author-faq.htm.
- Versions and removal:
  - New versions are allowed, but journal policies may forbid updates during review (MDPI does; see F1).
  - Posts cannot be deleted. Retraction is only for errors or misconduct, never just because of journal publication.
  - The journal article can be linked once published, by request with both DOIs.
  - Sources: author-faq.htm; policy.htm.
- AI: covered in ai_policy_raw.md.

---

## G. Currently open Special Issues relevant to point defects, oxides, defect chemistry, computational or ML materials

Method:
- The keyword search `https://www.mdpi.com/journal/crystals/special_issues?search=<term>` was tried via the reader proxy for: defect, oxide, machine+learning, machine-learning, first-principles, DFT, vacancy, computational, point+defect, data-driven.
- Several queries (oxide, DFT, machine+learning, data-driven) returned the same unfiltered default page. Others (first-principles, machine-learning, point+defect, vacancy) gave no parsable SI entries. The search results are therefore unreliable.
- Instead, the full "currently open" lists on all 13 section pages (https://www.mdpi.com/journal/crystals/sections/<section>) were harvested. That gave 105 open SIs. Each shortlisted SI page was then opened to confirm the deadline and guest editors [M-JINA, 2026-10-05].

Deadline-date caveat: on some SI pages the sidebar shows a date one day earlier than the headline or listing (e.g. 19 vs 20 January 2027). This looks like a timezone artefact of the proxy render. Both dates are given where they differ; plan to the earlier one.

| # | Special Issue (section) | Deadline (confirmed on SI page) | Guest Editor(s) | URL | Relevance |
|---|---|---|---|---|---|
| 1 | **Predictive Modelling of Inorganic Functional Materials: From Fundamentals to Device Applications** (Inorganic Crystalline Materials) | 10 December 2026 | Dr. Robert A. Jackson (Keele University, UK; interests include defects and dopants) | https://www.mdpi.com/journal/crystals/special_issues/9Q3W1G4LCT | Best fit. Covers DFT and ML interatomic potentials, metal oxides, and defect structure / dopant modelling, in our section. |
| 2 | **Feature Papers on "Inorganic Crystalline Materials"** (Inorganic Crystalline Materials) | 20 January 2027 (sidebar: 19 January 2027) | Prof. Dr. Thomas Schleid (University of Stuttgart) | https://www.mdpi.com/journal/crystals/special_issues/0ZGOLO5VA0 | General section showcase. Keywords are material classes (semiconductors, ion conductors, catalysts, …). Defect energetics of oxides fits, but feature papers often come by invitation. |
| 3 | **Crystal Structure and Physical Properties of Functional Materials** (Inorganic Crystalline Materials) | 20 February 2027 | Dr. Shixin Jin; Dr. Wenyi Wang; Dr. Jiali Yu; Dr. Zijian Wang | https://www.mdpi.com/journal/crystals/special_issues/N51356HP52 | Broad structure–property scope in our section. Editors lean towards nanomaterials and bio-inspired materials, so the fit is moderate. |
| 4 | **Thermodynamics and Kinetics of Crystalline Materials Through Advanced Characterization and Simulation** (Inorganic Crystalline Materials) | 27 May 2027 | Dr. Mehmet Das; Prof. Dr. Ebru Akpınar (Fırat University, Türkiye) | https://www.mdpi.com/journal/crystals/special_issues/1CETK0ROJ9 | Invites simulation and data-driven/ML work on thermodynamics of crystals, but the emphasis is on nanofluids and heat transfer. Weak to moderate fit. |
| 5 | **Synthesis and Crystal Structures of Novel Solid-State Materials and Their Applications** (Inorganic Crystalline Materials) | 20 April 2027 | Dr. Silvana Moris López; Dr. Patricia Barahona | https://www.mdpi.com/journal/crystals/special_issues/H1JEZ0WT7W | Solid-state inorganic structures in our section. Synthesis-focused, so weak for a purely computational paper. |
| 6 | **DFT-Guided Functional Materials** (Materials for Energy Applications) | 20 October 2026 | Dr. Juan Manuel Ramirez-de-Arellano; Prof. Dr. Roxana Mitzayé del Castillo Vázquez; Dr. Kwun Nam Hui | https://www.mdpi.com/journal/crystals/special_issues/2T728A7453 | First-principles electronic properties; editors list doping/defect engineering. The focus is 2D materials for sensors. The deadline is only 15 days away and it is in a different section. |
| 7 | **Research on Complex Oxide Nanomaterials** (Materials for Energy Applications) | 20 October 2026 (from the section listing; the SI page render was truncated and showed no deadline) | Dr. Katerina L. Zaharieva; Dr. Irina D. Stambolova | https://www.mdpi.com/journal/crystals/special_issues/BM4IYUC15A | Oxides, but synthesis, photocatalysis and nanomaterials. Imminent deadline. Weak fit. |
| 8 | **Advanced Functional Ceramics for Energy, Dielectric and Electromagnetic Applications** (Polycrystalline Ceramics) | 31 May 2027 (sidebar: 30 May 2027) | Dr. Zhilun Lu; Dr. Ge Wang | https://www.mdpi.com/journal/crystals/special_issues/P3A8MXM287 | Mentions defect-chemistry flexibility of oxide ceramics and ML-assisted design. Different section. |
| 9 | **Crystals: 15th Anniversary** (General) | 31 December 2026 (sidebar: 30 December 2026) | Prof. Dr. Alessandra Toncelli; Prof. Dr. Jesús Sanmartín-Matalobos; Dr. José Gavira; Prof. Dr. Heike Lorenz | https://www.mdpi.com/journal/crystals/special_issues/98A9S65GYQ | Journal-wide anniversary issue, open scope, guest-edited by the EiC. |
| 10 | **Advances in Wide Bandgap Semiconductor Materials** (Materials for Energy Applications) | 20 November 2026 (sidebar: 19 November 2026) | Dr. Sanjie Liu; Prof. Dr. Xinhe Zheng; Dr. Yangfeng Li; Prof. Dr. Francisco M. Morales | https://www.mdpi.com/journal/crystals/special_issues/DA06T9ZKI6 | Includes Ga2O3 and other UWBG oxides. Defects matter there, but the focus is growth and devices. Weak fit. |

Also seen open but judged less relevant:
- Perovskites: Crystal Structure, Properties and Applications. Deadline 10 September 2027 (sidebar 9 September). Guest editors: Dr. Kais Iben Nassar, Dr. Ben Salem Imen, Dr. Manuel Pedro Fernandes Graça. https://www.mdpi.com/journal/crystals/special_issues/B4M53W14O4
- Perovskite Materials: Structure, Properties and Applications. Deadline 20 March 2027. Guest editors: Dr. Xiangqian Shen, Dr. Hua Zhou, Dr. Heinz Christoph Neitzert. https://www.mdpi.com/journal/crystals/special_issues/874G92781W
- Machine Learning for Material and Process Optimization in Additive Manufacturing. Deadline 20 February 2027. Guest editors: Dr. Haining Zhang, Dr. Joon Phil Choi, Dr. Xingchen Liu. https://www.mdpi.com/journal/crystals/special_issues/E1H2A29RM9. This is ML for AM processes, not defects.
- Exploring New Materials for the Transition to Sustainable Energy (2nd Edition). Deadline 20 May 2027. Guest editor: Dr. Raluca Mereu. https://www.mdpi.com/journal/crystals/special_issues/VS0XQS2B8I
- Advanced Research in Electronic Materials and Devices. Deadline 20 March 2027. Guest editors: Dr. Ren Sheng, Dr. Rui Han, Dr. Jintao Wang. https://www.mdpi.com/journal/crystals/special_issues/5QK55G25B7
- Computational Phase Stabilities and Phase Tailoring of Alternative and Sustainable Hard Magnetic Materials (Inorganic Crystalline Materials). Deadline 10 November 2026. Magnetic materials, so out of scope for non-magnetic oxides. https://www.mdpi.com/journal/crystals/special_issues/N5X281S50U (SI page not opened).
- Polymorphism and Phase Transitions in Crystal Materials. Deadline 10 October 2026, too close. https://www.mdpi.com/journal/crystals/special_issues/2OQ9303L8V (SI page not opened).

Notes:
- An SI belongs to a fixed section. SIs 6–10 and the extras sit outside Inorganic Crystalline Materials, so the paper would be handled in that section. Only SIs 1–5 keep it in Inorganic Crystalline Materials.
- No Topical Collection exists for the Inorganic Crystalline Materials section (see D).
- A regular, non-SI submission to the section is always possible.

---

## FAILED FETCHES

| URL | Method(s) tried | Result |
|---|---|---|
| https://www.mdpi.com/journal/crystals/instructions (and every other www.mdpi.com page) | direct curl, desktop Chrome UA, `Accept: text/html`, `Accept-Language` | HTTP 403 Akamai "Access Denied". Recovered via r.jina.ai. |
| https://mdpi.com/journal/crystals/instructions | direct curl, desktop UA | HTTP 403. Recovered via r.jina.ai on www host. |
| https://www.mdpi.com/authors/data | r.jina.ai | Page title "Error 404 File not found". The data policy was found instead at https://www.mdpi.com/ethics ("MDPI Research Data Policies"). |
| https://www.preprints.org/instructions_for_authors | r.jina.ai | 404. Correct URL https://www.preprints.org/instructions-for-authors fetched OK. |
| https://www.mdpi.com/journal/crystals/special_issues?search={defect,oxide,machine+learning,machine-learning,first-principles,DFT,vacancy,computational,point+defect,data-driven} | r.jina.ai | Fetched (HTTP 200) but results were unfiltered or unparsable for several terms. Not used as evidence; section pages used instead. |
| https://www.mdpi.com/journal/crystals/special_issues/BM4IYUC15A | r.jina.ai (twice) | Truncated render (~4.8 KB): description, keywords and guest editors present, deadline missing. Deadline taken from the section listing. |
| https://www.mdpi.com/journal/crystals/special_issues/P3A8MXM287 | r.jina.ai | First attempt HTTP 429 (proxy rate limit). Retry OK. |
| https://web.archive.org/web/20240914020337/https://www.mdpi.com/journal/crystals/apc | Wayback | Fetched, but no APC amount found in the snapshot. |
| https://web.archive.org/cdx/search/cdx?url=mdpi.com/about/apc… | Wayback CDX | HTTP 502 Bad Gateway. Got the snapshot via https://web.archive.org/web/2025/https://www.mdpi.com/about/apc instead. |
| https://chemrxiv.org/engage/chemrxiv/about-information | direct curl (desktop UA); r.jina.ai; r.jina.ai with `X-Engine: browser` | Cloudflare "Just a moment…" challenge (403). Content recovered from the www.cambridge.org term assets. |
| https://chemrxiv.org/engage/chemrxiv/about-information?show=about-policies | r.jina.ai (browser engine); Wayback 2026 (redirected to 20250718115825) | Challenge page. The Wayback copy is a JS shell with no policy text. |
| https://chemrxiv.org/engage/chemrxiv/submission-information | direct curl; r.jina.ai | 403 / challenge. |
| https://chemrxiv.org/ | direct curl; r.jina.ai | 403 / challenge. |
| https://chemrxiv.org/engage/chemrxiv/faqs | direct curl | 403. |
| https://chemrxiv.org/engage/chemrxiv/public-api/v1/items?limit=1 | direct curl | 403 (Cloudflare). |
| https://chemrxiv.org/engage/assets/public/chemrxiv/term/{about,policy,submission-guide,author-faq,faq,terms-of-submission}.htm | direct curl | 403. The same files on www.cambridge.org returned 200. |
| https://www.cambridge.org/engage/chemrxiv/public-api/v1/items?limit=1 | direct curl | Returned a Cambridge Open Engage "Error" HTML page, not JSON. |
| https://web.archive.org/cdx/search/cdx?url=chemrxiv.org/… (several patterns) | Wayback CDX | Internet Archive "Temporarily Offline". |
| https://archive.org/wayback/available?url=chemrxiv.org/engage/chemrxiv/about-information | curl | HTTP 429 Too Many Requests. |
| https://www.mdpi.com/journal/crystals/sectioneditors/inorganic_crystalline_materials | not attempted | Not needed: the Section EiC was confirmed from the sections and editors pages. |
| https://mdpi-res.com/data/crystals_cmpd-check-list-v3.pdf; https://res.mdpi.com/data/mdpi-acs-references-guide-v11-2025.12.pdf; https://casrai.org/credit/; writeLaTeX gallery URL | not fetched | Links recorded only. |

# Zenodo deposit: manual checklist for Palaash

Session J2, 2026-10-12. Every step that touches Zenodo is manual and is done by Palaash in a browser. The agent
uploads, publishes and creates nothing. The archive content is described in `deposit/README.md`, and every file is
hashed in `deposit/FILES.sha256`.

## What stays pending until the results freeze

| Item | State on 2026-10-12 | Done when |
|---|---|---|
| Cluster result branches merged | Merged: `nrp/n0-checkout` and `nrp/n1-gpu-repeat`. `nrp/precision` is pushed but not merged (2 commits, 65 run records so far, 104 checkpoints listed in `results/nrp/artefacts/precision.sha256`). No branch yet for relax, peval, embed, geomeval, moment, cgcnn, capped or cv. | every `nrp/<stage>` has passed `scripts/nrp/ingest_batch.sh` and is merged (`docs/nrp_runbook.md`, section 8), and the spec totals are reached (2852 jobs) or the shortfall is logged in `docs/deviations.md` |
| Final predictions and result records | 1650 parquet files and 1721 result JSONs tracked | the analyses are rerun on the merged files and every claim has its row in `docs/claims.yaml` |
| Cluster artefact and embedding manifests | none merged | `results/nrp/artefacts/<stage>.sha256` is present for every stage that keeps files on NRP, `embed.sha256` included |
| Final tag | placeholder `[FINAL-TAG-TBD]` (`configs/config.yaml` names `results-v1` as `gates.G2_tag`) | the tag is created on main and pushed |
| Number of files in the record | 15 planned: `README.md`, `CITATION.cff`, `FILES.sha256`, the snapshot zip, `INPUTS_MANIFEST.txt`, `MACE-MP-0_LICENSE.txt`, and the 9 bundle files (3 bundles x tar, member manifest, tar manifest) | fixed once the snapshot exists. The row counts in `FILES.sha256` (code members, results) change with the merges |
| Zenodo DOI | placeholder `[ZENODO-DOI-TBD]` | reserved in step 3 below |

## Steps

### 1. Freeze the repository (Mac)

```bash
cd ~/Desktop/dft-gnn && git switch main && git pull --ff-only
# merge each remaining cluster branch (runbook section 8), then rerun the analyses and update docs/claims.yaml
git status --short          # must be empty
```

### 2. Rehash the archive (Mac)

The bundles stay the same as release `inputs-v1`. Rehash anyway: the code rows change with every merge.

```bash
OMP_NUM_THREADS=3 nice -n 15 conda run -n dftgnn python deposit/make_files_manifest.py --data-root .
```

The output must report `record problems: 0`. Check `banned-string hits` too: any path listed there needs a
decision before upload. History is never rewritten.

### 3. Create the Zenodo draft and reserve the DOI (browser)

1. Sign in to https://zenodo.org with your own account and start a new upload.
2. Copy the metadata from `deposit/.zenodo.json`:
   - resource type: Dataset;
   - title;
   - both creators, with affiliations and ORCIDs;
   - description;
   - licence: CC BY 4.0. If the form allows a second licence, add MIT for the code;
   - keywords;
   - the three related identifiers: the GitHub repository (is supplement to), the Kumagai DOI (is derived
     from) and the NRP DOI (references);
   - the funding and acknowledgement note (no external funding; NRP sentence).

   The file is a draft for the form. It is not uploaded, and it is not at the repository root, so the GitHub
   integration does not pick it up.
3. Reserve the DOI on the form, before publishing. Save the draft. Do not upload yet.

### 4. Fill the placeholders and tag (Mac)

1. Replace `[ZENODO-DOI-TBD]` with the reserved DOI, and `[FINAL-TAG-TBD]` with the tag name, in:
   - `deposit/README.md`;
   - `deposit/.zenodo.json`;
   - `docs/data_availability.md`;
   - `paper/sections/data_availability.tex`;
   - `paper/sections/methods.tex` (Provenance Labels and Reproducibility);
   - `paper/si/sections/s9_reproducibility.tex`.

   The full list with line numbers is in `docs/placeholders.md`.

   In `deposit/CITATION.cff`, add `doi`, `version`, `commit` and `date-released`.
2. Validate the metadata. Fetch the two schemas as described in the header of `deposit/validate_metadata.py`,
   then run:
   `conda run -n dftgnn python deposit/validate_metadata.py --schemas <dir>`. Both files must print `valid`.
3. Rehash (step 2), commit, then create and push the annotated final tag:
   `git tag -a <tag> -m "<tag>: results freeze"` and `perl -e 'alarm 120; exec @ARGV' -- git push origin <tag>`.

### 5. Build the snapshot and the staging folder (Mac)

```bash
mkdir -p .local/deposit
git archive --format=zip --prefix=dft-gnn-<tag>/ -o .local/deposit/dft-gnn-<tag>.zip <tag>
OMP_NUM_THREADS=3 nice -n 15 conda run -n dftgnn python deposit/make_files_manifest.py --data-root . \
    --snapshot .local/deposit/dft-gnn-<tag>.zip
cp deposit/README.md deposit/CITATION.cff deposit/FILES.sha256 .local/deposit/
cp .local/nrp_inputs/INPUTS_MANIFEST.txt .local/nrp_inputs/MACE-MP-0_LICENSE.txt .local/nrp_inputs/nrp_*.tar \
   .local/nrp_inputs/nrp_*.sha256 .local/deposit/
ls .local/deposit | wc -l      # 15
```

The second run adds the `snapshot` row. That `FILES.sha256` differs from the copy inside the snapshot only by
that row. Commit it afterwards as `chore(deposit): FILES.sha256 with the snapshot hash`.

### 6. Upload and publish (browser)

1. In the saved draft, upload the 15 files from `.local/deposit/`. Compare the checksums Zenodo shows with
   `FILES.sha256`; Zenodo may show MD5 rather than sha256. If it does, check with `md5 <file>` locally.
2. Preview the record. Check the authors, ORCIDs, licence and the DOI.
3. Publish. Once published, files cannot be replaced; a correction needs a new version, with a new version DOI.

### 7. After publishing (Mac)

1. Check that the DOI resolves. Download one bundle from the record and verify it against its `.tar.sha256`.
2. Fetch the record's citation from DataCite or doi.org content negotiation into `paper/refs.bib`, with the usual
   `% source:` line, and cite it in the Data Availability Statement.
3. Move the agreed text from `docs/data_availability.md` into `paper/sections/data_availability.tex`.
4. Optionally, link the GitHub repository README to the DOI.

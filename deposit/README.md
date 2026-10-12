# Archive: oxygen-vacancy formation energies in non-magnetic oxides (data, models and code)

DRAFT for the Zenodo record. DOI: **[ZENODO-DOI-TBD]**. Final code tag: **[FINAL-TAG-TBD]**. Both
placeholders are filled at the results freeze (`docs/deposit_checklist.md`).

This record supports the article "Oxygen-vacancy formation energies in non-magnetic oxides: how much do
explicit electronic descriptors add to graph networks as training data grows?" by Palaash Gang and Aiden Lee.
The study asks how accurately graph networks predict the formation energy of the neutral oxygen vacancy, and how
much explicit DFT electronic descriptors add as the number of training hosts grows. It uses only the published
DFT data of Kumagai et al. No new DFT calculations were performed.

## Authors

| Name | Affiliation | ORCID | Contact |
|---|---|---|---|
| Palaash Gang (corresponding author) | Indus International School, Pune, India | [0009-0006-7448-9488](https://orcid.org/0009-0006-7448-9488) | palaash.gang@indusschoolpune.com |
| Aiden Lee | Westview High School, San Diego, CA, USA | [0009-0007-3281-8420](https://orcid.org/0009-0007-3281-8420) | aiden.lee.sd@gmail.com |

## Record layout

The record holds a few top-level files. Each bundle unpacks to paths relative to the repository root.

| File | What it is |
|---|---|
| `README.md` | this file |
| `CITATION.cff` | citation metadata |
| `FILES.sha256` | sha256 and size of every file in the record and of every member of each bundle and of the snapshot |
| `dft-gnn-[FINAL-TAG-TBD].zip` | code snapshot: `git archive` of the final tag of https://github.com/pa1aash/dft-gnn (PENDING) |
| `nrp_inputs.tar`, `nrp_inputs.sha256`, `nrp_inputs.tar.sha256` | processed inputs (832 members, below) |
| `nrp_checkpoints.tar`, `nrp_checkpoints.sha256`, `nrp_checkpoints.tar.sha256` | the 583 checkpoints trained before the cluster stages (below) |
| `nrp_mace.tar`, `nrp_mace.sha256`, `nrp_mace.tar.sha256` | MACE-MP-0 medium weights, unchanged |
| `INPUTS_MANIFEST.txt` | sha256 and size of each bundle asset |
| `MACE-MP-0_LICENSE.txt` | MIT licence of the MACE-MP-0 weights |

The three bundles and their manifests are the assets of the GitHub release `inputs-v1`
(https://github.com/pa1aash/dft-gnn/releases/tag/inputs-v1). Tag `inputs-v1` points at the same commit as
`nrp-code-v1` (`ffd86cedc3cc87a6fc842b04fda0d86d6b6a58af`). The record carries the bundles unchanged, byte for
byte. `FILES.sha256` was checked against `INPUTS_MANIFEST.txt` and against each bundle's member manifest.

## Contents

Hashes are sha256. "Snapshot" means the code snapshot zip; paths are repository-relative.

| Item | Location | Files | Size (bytes) | sha256 / record | Licence | Status |
|---|---|---:|---:|---|---|---|
| Processed universe table: one row per oxygen site, 1726 sites in 818 hosts | `data/processed/universe_v1.parquet` in `nrp_inputs.tar` | 1 | 556,032 | `781fe8228ab7786e58055df81a3056c210cca584b89ed04ab8f0eb308b873d98` | CC BY 4.0 (derived) | final |
| Site and host ID list of the universe | `data/universe_v1_ids.csv` in the snapshot | 1 | 183,693 | `66e377c46f5801549600e73a1d5430cad190d447ae60fce16dd2866b511e2d49` (also in `data/universe_v1_ids.csv.sha256`) | CC BY 4.0 (derived) | final |
| Graph store: MEGNet graphs of the pristine release supercells, 5 Å cutoff, vacancy site flagged | `data/processed/graphs_v1/` in `nrp_inputs.tar` (9 host shards, `sites.pt`, `meta.json`) | 11 | listed in `FILES.sha256` | per-file hashes in the manifest below | CC BY 4.0 (derived) | final |
| Graph-store manifest | `data/graphs_v1_manifest.sha256` in the snapshot | 1 | 1,069 | `be5e5cfd5c3a5ad7fed3ee841c8a308292adefdd6b2fca909c377db1ae6d3713` (the value every spec manifest records as `graphs_manifest_sha256`) | CC BY 4.0 | final |
| DFT unit cells and supercell tiling map (MLIP stage inputs) | `data/processed/unit_cells_v1.json`, `data/processed/tiling_map_v1.parquet` in `nrp_inputs.tar` | 2 | listed in `FILES.sha256` | `nrp_inputs.sha256` | CC BY 4.0 (derived) | final |
| Release supercell CIFs, redistributed as released | `data/raw/unpacked/oxygen_vacancies_db/site_info/<formula>/supercell.cif` in `nrp_inputs.tar` | 818 | listed in `FILES.sha256` | `nrp_inputs.sha256`; download pinned in `data/MANIFEST.sha256` | CC BY 4.0 (Kumagai et al.) | final |
| Splits: 10 outer resamples, Kiyohara split, LOCO folds, CV, RF curve, extra resamples | `splits/` in the snapshot | 23 | 987,908 | `splits/MANIFEST.sha256` (sha256 `62595259d38dce0381172b7e78377b2ca887c48fc3b2ac9d942767f0b3f2acf3`), `splits/loco/MANIFEST.sha256` | CC BY 4.0 | final |
| Job specs of the 11 cluster stages (2852 jobs; run ids computed with `nrp-code-v1`) | `specs/<stage>.jsonl`, `specs/<stage>.manifest.json` in the snapshot | 22 | 2,281,445 | each `.manifest.json` holds the sha256 of its `.jsonl` | MIT | final |
| Tracked prediction tables (one parquet per run: per-site predictions) | `results/**/*.parquet` in the snapshot | 1650 now | 75,793,615 now | per-file rows in `FILES.sha256` | CC BY 4.0 | PENDING: grows when the cluster branches are merged |
| Result records (JSON written by `write_result`, each with config, git sha, package versions, seeds and timestamp) | `results/**/*.json` in the snapshot | 1721 now | 62,559,623 now | per-file rows in `FILES.sha256` | CC BY 4.0 | PENDING: grows when the cluster branches are merged |
| Checkpoint manifest for the checkpoints trained before the cluster stages (each cross-checked against the checkpoint hash in its result record) | `results/checkpoint_manifest.json` in the snapshot | 1 | 77,337 | `e1fff08d93f332d0426da2307ad49752da26d0d1467c1c558cadb7ae1592a183`; lists 583 files, 1,009,555,553 bytes, none missing, none mismatched | MIT | final |
| Checkpoints trained before the cluster stages (the S09 set of release `inputs-v1`) | `checkpoints/*.pt` in `nrp_checkpoints.tar` | 583 | 1,009,555,553 (tar 1,011,247,616) | tar `e10b4180ea3b245267448a18e4002c4b81301739576b6fe3c46d7932918164a7`; members in `nrp_checkpoints.sha256` | MIT | final, included (rule below) |
| Checkpoint and artefact manifests of the cluster stages | `results/nrp/artefacts/<stage>.sha256` in the snapshot (sha256, size, path per artefact) | 0 merged | - | one line per file kept on NRP | MIT | PENDING: arrives with each `nrp/<stage>` branch |
| Embedding manifest (S readout embeddings, stage embed) | `results/nrp/artefacts/embed.sha256` and the records in `results/embeddings_v1/` in the snapshot | 0 merged | - | one line per embedding file kept on NRP | CC BY 4.0 | PENDING: stage embed not yet returned |
| MACE-MP-0 medium weights (`2023-12-03-mace-128-L1_epoch-199.model`, release `mace_mp_0`) | `.cache/mace/20231203mace128L1_epoch199model` in `nrp_mace.tar` | 1 | 44,422,970 | `01bfe22100139f424713cf921144e5509cbe353d67aa9fa1be9c6e1e0ed35845` (identity check in `results/mace_model.json`) | MIT (ACEsuit), text in `MACE-MP-0_LICENSE.txt` | final |
| Code release, cluster reference | tag `nrp-code-v1` = commit `ffd86cedc3cc87a6fc842b04fda0d86d6b6a58af` | - | - | - | MIT | final |
| Code release, final | tag `[FINAL-TAG-TBD]`; snapshot `dft-gnn-[FINAL-TAG-TBD].zip` | `FILES.sha256` (components `code` and `deposit`) lists 3826 tracked files now | about 163 MB now (exact totals in the `FILES.sha256` header) | sha256 of the zip added at the freeze | MIT (code); CC BY 4.0 (data and results) | PENDING |

The source database itself is not redistributed. The 818 supercell CIFs are the only exception. Download it from
https://github.com/kumagai-group/oxygen_vacancies_db at commit `e310353ecbf698499c85a5ec5416b76e82dcecfd`.
`data/MANIFEST.sha256` in the snapshot lists the sha256, size and source URL of every downloaded file.

### Checkpoints rule

Checkpoints go in the record only if their total is under 2 GB. The 583 checkpoints trained before the cluster
stages total 1,009,555,553 bytes, 1.01 GB, so they are included as `nrp_checkpoints.tar`.

The cluster checkpoints are not in the record. These are the checkpoints, MACE relaxed structures and embeddings
written by the National Research Platform stages. They stay on NRP storage for two reasons:

- They are large. The first partial return of one stage (precision, unmerged) already lists 104 checkpoints,
  207,838,257 bytes. The full set would push the total well over 2 GB.
- The runbook keeps them on the cluster (`docs/nrp_runbook.md`, section 0).

Each one is listed with its sha256, size and path in `results/nrp/artefacts/<stage>.sha256` in the snapshot.

**How to request cluster artefacts.** Write to the corresponding author (palaash.gang@indusschoolpune.com).
Name the stage and the run ids or paths, as listed in `results/nrp/artefacts/<stage>.sha256`. The second author
holds the files on NRP storage and can copy them out. Check every file you receive against its listed sha256.

## How to verify and reproduce

1. Verify the record. On Linux, run `sha256sum -c` over the bundle manifests. On macOS, use `shasum -a 256 -c`.
   Each `.tar.sha256` checks its tar. After unpacking at the checkout root, `nrp_<name>.sha256` checks every
   member. `FILES.sha256` lists every file in tab-separated form: sha256, size, component, path.
2. Unpack the code snapshot. Then unpack the three bundles at its root; each member lands at its expected path.
3. Build the environment. Run `make env` (conda environment `dftgnn`, from `env/environment-local.yml`), then
   `make test`. GPU training uses `env/environment-gpu.yml` or `env/Dockerfile.gpu`. The cluster used the lock
   file `env/lock-nrp-rtx2080ti.txt`.
4. Re-run a cluster stage. Follow `docs/nrp_runbook.md`, sections 3 and 4. For each stage,
   `scripts/queue/make_specs.py --stage <stage> --check` must reproduce the spec file byte for byte. Workers then
   rerun jobs by run id, and every rerun writes a result record that can be compared with the archived one.
5. Analysis rules, deviations and claims are in the snapshot:
   - `docs/ANALYSIS_PLAN.md` (pre-registered; tag `prereg-v1`);
   - `docs/deviations.md` (every departure, dated, before the affected run);
   - `docs/claims.yaml` (one row per claim in the article, with its result record).

Every result record stores its git sha, host name, package versions and seeds. Cluster records also store the
GPU model, UUID, driver and node. Bit-identical retraining on other hardware is not expected.

## Licences and attribution

- **Source data.** All formation energies, descriptors and structures come from the oxygen-vacancy database of
  Y. Kumagai, N. Tsunoda, A. Takahashi and F. Oba, "Insights into oxygen vacancies from high-throughput
  first-principles calculations", Phys. Rev. Materials 5, 123803 (2021),
  doi:[10.1103/PhysRevMaterials.5.123803](https://doi.org/10.1103/PhysRevMaterials.5.123803). The database is
  released under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Cite the article when you use any
  derived file.
- **Derived data.** These are the processed tables, graphs, splits, predictions and result records. They are
  released under CC BY 4.0, with the attribution above.
- **Code.** MIT (`LICENSE` in the snapshot; copyright 2026 Palaash Gang). The spec files and checkpoints are
  outputs of that code and are released under the same terms.
- **MACE-MP-0 weights.** MIT License of ACEsuit/mace-foundations, redistributed unchanged. The licence text is in
  `MACE-MP-0_LICENSE.txt`, fetched from https://github.com/ACEsuit/mace-foundations/blob/main/LICENSE.

## Funding and acknowledgement

No external funding was received.

This work used resources available through the National Research Platform (NRP) at the University of California, San Diego. NRP has been developed, and is supported in part, by funding from National Science Foundation, from awards 1730158, 1540112, 1541349, 1826967, 2112167, 2100237, and 2120019, as well as additional funding from community partners. (Weitzel et al., "The National Research Platform: Stretched, Multi-Tenant, Scientific Kubernetes
Cluster", PEARC '25, doi:[10.1145/3708035.3736060](https://doi.org/10.1145/3708035.3736060)).

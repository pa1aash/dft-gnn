# N3 artefacts on the Mac (2026-10-14)

The relaxed structures, MLIP graphs and frozen-backbone embeddings from the `nrp-code-v2` N3 rerun existed only on the
NRP volume. They were published as assets of the draft release "NRP N3 artefacts: relaxed structures and embeddings
(nrp-code-v2)" in `pa1aash/dft-gnn` (release id 412334955, intended tag `nrp-n3-artefacts`, still a draft, URL
`releases/tag/untagged-5f4196b6d15b088bc3c0`). They were downloaded headless with
`gh api -H "Accept: application/octet-stream" repos/pa1aash/dft-gnn/releases/assets/<id>` and unpacked so that analyses
A3 (geometry) and A4 (probe) find them at the paths the code uses (`src/dftgnn/tasks.py`, `src/dftgnn/embeddings.py`,
`src/dftgnn/mlip/geomeval.py`).

## Downloaded assets

| asset | id | bytes |
|---|---|---|
| `nrp_n3_mlip_v1.tar` | 639200418 | 683,048,960 |
| `nrp_n3_mlip_v1.tar.sha256` | 639200415 | 85 |
| `nrp_n3_mlip_v1.sha256` | 639200416 | 346,814 |
| `nrp_n3_embeddings_v1.tar` | 639200420 | 165,120,000 |
| `nrp_n3_embeddings_v1.tar.sha256` | 639200413 | 91 |
| `nrp_n3_embeddings_v1.sha256` | 639200488 | 54,560 |

Every downloaded size equals the release listing. Both tars pass their `.tar.sha256`
(`a2021a14…fdea` mlip, `e75cbb84…1917` embeddings). The per-file manifests in the release list the same
(sha256, path) pairs as the tracked `results/nrp/artefacts/relax.sha256` and `embed.sha256`. They differ only in
layout: the tracked files also carry a size column. Each tar contains exactly the manifest paths, all regular files,
with no absolute or parent-relative member.

## Local layout

| path | files | bytes (manifest) | on disk |
|---|---|---|---|
| `data/processed/mlip_v1/` | 3,272 (818 hosts × record, `_uc.json`, `_sc.json`, `_graphs.pt`) | 680,507,760 | 656 MB |
| `data/processed/embeddings_v1/` | 480 (240 npz + 240 json sidecars) | 164,773,568 | 159 MB |
| `data/downloads/n3/` (the six assets) | 6 | 848,570,510 | 814 MB |

`data/processed/` is gitignored and `data/downloads/` is excluded locally, so none of this is tracked. Neither target
directory existed before extraction, and the tars were unpacked with `tar -xk`, so no file was overwritten.

## Verification

- Against the tracked manifests: 3,272 of 3,272 relax files and 480 of 480 embed files found, every sha256 and size
  matches, no missing files and no extras in either directory.
- Embeddings: all 240 npz load with `allow_pickle=False` and carry `site_ids`, `host_ids`, `split`, `block_bounds`,
  `block_names` and `embeddings`. `embeddings` is a finite float32 2-D array. The id and split vectors have one entry
  per row, the split labels are within train/val/test, and `block_bounds` starts at 0, ends at the embedding width and
  is strictly increasing. Each json sidecar agrees with its npz (sha256, shape, block bounds, per-split counts).
- Relaxed cells: all 818 host records parse. The unit-cell and supercell sha256 values recorded inside each record match
  the files, and so does the graphs sha256. All 1,636 unit cells and supercells load as pymatgen `Structure`. Graph files
  were checked by hash only. The records' `converged` flag is true for 811 of 818, as reported in `n3_ingest.md`.

No MAE, probe or geometry statistic was computed here. Those belong to A3 and A4.

# N3: ingest of the relax, embed and geomeval branches (2026-10-14)

Three results branches from the `nrp-code-v2` rerun (MACE-MP-0 relaxation of the host cells, frozen-backbone
embeddings, and S/D/P evaluation on DFT and MLIP geometries) were checked on the Mac with
`scripts/nrp/ingest_batch.sh <branch> --no-fetch` and merged into `main` with `--no-ff`, one at a time, in this order:

| stage | branch | tip | records | merge commit |
|---|---|---|---|---|
| relax | `nrp/relax` | `7746e77` | 818 | `d037c89` |
| embed | `nrp/embed` | `99c4dcb` | 240 | `0620dbd` |
| geomeval | `nrp/geomeval` | `dc0d04d` | 180 | `aa9fa3d` |

Every branch passed all five checks of the script: identities (all commits authored and committed by the
collaborator identity), no banned string in messages, added lines or paths, no change under `src/ scripts/ configs/
splits/ specs/` relative to the pinned tag, every recorded artefact sha256 verified, and result counts equal to the
spec counts. Each branch adds files only, all under `results/`: relax adds 818 records plus
`results/nrp/artefacts/relax.sha256`; embed adds 240 records plus `results/nrp/artefacts/embed.sha256`; geomeval adds
180 records and their 180 prediction parquets, which are committed, so it has no NRP artefact manifest by design.

## Code check against nrp-code-v2

These runs used `nrp-code-v2` (`fa0e970`, the F1 fix set: relax NaN point_op and checkpoint device). The ingest script
pins `nrp-code-v1`, and check 3 passed against it. It did not flag the F1 fix set: all three branches were cut from
`nrp-code-v1` itself (merge base `ffd86ce`), so their tracked code equals v1, and they do not contain the v2 tag.
Against `nrp-code-v2`, the branch trees differ by exactly the reverse of the F1 fix set (8 files). The branch tree is
only the base the results were committed onto. The executed code is recorded per record: all 1,238 records (818 + 240
+ 180) carry `git_sha` `fa0e97064a32` (= `nrp-code-v2`) with `git_dirty` false. Run ids and spec `code_ref` still
name `nrp-code-v1`, as intended (`CODE_REF_SUCCESSORS`). The merges add files under `results/` only, so the code on
`main` is unchanged: `git diff nrp-code-v2 main -- src scripts configs splits specs` is empty after all three merges.

## What lives only on NRP

Large artefacts are not in git. Only their sha256, size and path are, in the tracked manifests:

| artefact | path | files | size | manifest |
|---|---|---|---|---|
| relaxed structures and MLIP graphs | `data/processed/mlip_v1/` | 3,272 | 0.68 GB | `results/nrp/artefacts/relax.sha256` |
| frozen-backbone embeddings | `data/processed/embeddings_v1/` | 480 | 0.16 GB | `results/nrp/artefacts/embed.sha256` |

They sit on the NRP volume under the rerun checkout (`/workspace/dft-gnn-v2`). Analyses A3 (geometry) and A4
(probe) need them. Before either analysis, download them into the same paths in the checkout and verify them against
the manifests. No analysis may read an artefact that fails verification.

### Verification recipe

Each manifest line is `<sha256>  <bytes>  <path>`, with paths relative to the repository root. From the repository
root, after the download:

```bash
for st in relax embed; do
  m=results/nrp/artefacts/$st.sha256
  awk -F'  ' '{print $1"  "$3}' "$m" | shasum -a 256 -c --quiet && echo "$st: hashes OK"
  awk -F'  ' '{ if (system("test \"$(stat -f %z \"" $3 "\")\" = " $2)) bad++ } END { print FILENAME ": " NR " lines, " bad+0 " size mismatches" }' "$m"
done
ls data/processed/mlip_v1 | wc -l        # 3272
ls data/processed/embeddings_v1 | wc -l  # 480
```

`shasum -c --quiet` prints only failures. On Linux, use `sha256sum -c --quiet` and `stat -c %s`. A file count above
the manifest count means stale files from an earlier run are present. Remove them before the analysis.

## Hardware

Per-record `hardware` blocks (GPU model, UUID, driver, node):

| stage | A10 | TITAN RTX | RTX 4090 | nodes |
|---|---|---|---|---|
| relax | 548 | 239 | 31 | 6 |
| embed | 159 | 71 | 10 | 6 |
| geomeval | 63 | 114 | 3 | 6 |

Quadro RTX 6000 was allowed by the job spec but received no jobs. N1 (`docs/nrp/n1.md`) tested neither TITAN RTX nor
Quadro RTX 6000, so their run-to-run behaviour relative to the N1 classes is untested. Relax ran in float64
(`mlip.dtype` in the recorded config) on mixed GPU classes. No relaxed cell was repeated on a second card, so the
cross-card reproducibility of the relaxed geometries is not measured.

## Convergence and failures

811 of 818 relaxations converged (fmax 0.01 eV/A). Seven stopped at the 500-step cap without converging. They are
kept and flagged (`converged: false` in the record). A sensitivity without them belongs to A3, not to this ingest.

| run id | host |
|---|---|
| `53c6d1d3c2b419b0` | mp-30298 |
| `6cc3737a3e737dc3` | mp-561725 |
| `92ab37787fe6c9d9` | mp-504510 |
| `9a78b2ad855f728f` | mp-1211443 |
| `ce878bcd9cf9e6d2` | mp-3635 |
| `ec09de7fae4a3e3c` | mp-557871 |
| `f645367543848e30` | mp-562441 |

No job failed in any of the three stages.

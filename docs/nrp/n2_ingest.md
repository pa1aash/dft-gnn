# N2: ingest of the NRP batch branches (2026-10-14)

Six results branches pushed from the cluster were checked on the Mac with `scripts/nrp/ingest_batch.sh` and merged
into `main` with `--no-ff`, one at a time, in this order:

| stage | branch | tip | merge commit |
|---|---|---|---|
| moment | `nrp/moment` | `e09e559` | `4155aa5` |
| cgcnn | `nrp/cgcnn` | `9144a10` | `1cfd0ec` |
| capped | `nrp/capped` | `82dd03c` | `956f6a9` |
| peval | `nrp/peval` | `4b997ac` | `6b477ed` |
| cv | `nrp/cv` | `664cf62` | `3c3daab` |
| precision | `nrp/precision` | `7cef547` | `be6de7d` |

Every branch passed all five checks of the script: identities (all commits authored and committed by the
collaborator identity), no banned string in messages, added lines or paths, no change under `src/ scripts/ configs/
splits/ specs/` since `nrp-code-v1`, every recorded artefact sha256 verified (prediction parquets from the branch,
checkpoints against `results/nrp/artefacts/<stage>.sha256`), and result counts equal to the spec counts. Each branch
adds files only, all under `results/`. The `peval` stage trains nothing, so it records no checkpoints and has no NRP
artefact manifest.

## Hardware variation

The runs mix four GPU classes: NVIDIA A10, GeForce RTX 3090, GeForce RTX 4090 and L4 (per-record `hardware`
block: GPU model, UUID, driver, node). N1 (`docs/nrp/n1.md`) showed that the same spec gives bitwise identical
predictions on the same GPU model and driver, but that runs on different GPU models never give identical
predictions (0 of 12 bitwise matches for every pair of classes), because the floating-point summation order changes
the training trajectory and the early-stopping epoch. Predictions in these stages therefore carry a hardware
component that is not separable from seed and resample variation run by run. RTX 4090 was not among the N1 classes,
so its run-to-run behaviour relative to the other three is untested; it appears only in `precision`.

| stage | GPU classes (records) |
|---|---|
| moment | A10 (17), L4 (25), RTX 3090 (18) |
| cgcnn | A10 (1), L4 (11), RTX 3090 (6) |
| capped | A10 (12), L4 (12), RTX 3090 (9) |
| peval | A10 (183) |
| cv | A10 (185), L4 (54), RTX 3090 (121) |
| precision | A10 (450), L4 (117), RTX 3090 (246), RTX 4090 (147) |

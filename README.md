# Oxygen-vacancy formation energies in non-magnetic oxides: data efficiency and pipeline design for graph networks

## Scope
This repository studies how well graph neural networks predict the formation energy of the neutral oxygen
vacancy in non-magnetic oxides, and how that accuracy depends on the number of training hosts. Four models
share a MEGNet backbone: a descriptor baseline (RF), a structure-only network (S), a network that also receives
DFT electronic descriptors (D, the oracle), and a staged descriptor-to-energy network (P). A two-parameter
physics-floor baseline provides the reference. Learning curves are measured against training budget in hosts,
with grouped cross-validation by chemical formula. No new DFT calculations are performed.

## Data source
The data are the oxygen-vacancy database released with:

Y. Kumagai, N. Tsunoda, A. Takahashi, F. Oba, "Insights into oxygen vacancies from high-throughput
first-principles calculations", Phys. Rev. Materials 5, 123803 (2021),
doi:[10.1103/PhysRevMaterials.5.123803](https://doi.org/10.1103/PhysRevMaterials.5.123803).
The database is distributed under the Creative Commons Attribution 4.0 International licence
(CC BY 4.0, https://creativecommons.org/licenses/by/4.0/). Any derived tables here carry the same attribution.
The BibTeX record is in `paper/refs.bib`.

## Layout
- `src/dftgnn/`: package (`config`, `io`, `data`, `graphs`, `models`, `train`, `stats`, `probe`, `mlip`, `viz`, `report`)
- `configs/`: central `config.yaml`
- `scripts/`: entry-point scripts
- `results/`: JSON results written with full provenance
- `figures/`: `main/`, `si/`, `demo/`
- `blender/`, `schematics/`: rendering and schematic sources
- `paper/`: manuscript sources
- `docs/`: notes (`env-notes.md`, `provenance.md`, `literature.md`, `venue.md`)
- `env/`: conda and container specifications
- `tests/`: pytest suite

## Reproduce
```
make env
make test
```
The local environment is named `dftgnn`. GPU training uses `env/environment-gpu.yml` or `env/Dockerfile.gpu`.

## Licence
Code: MIT (see `LICENSE`). Data: CC BY 4.0 as above.

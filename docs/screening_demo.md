# Screening demonstration (M8): Figure 7 and the Results subsection

Claim C5 (`docs/claims.yaml`, ANALYSIS_PLAN section 13) is a demonstration, not a claim; its status stays
`planned`. The subsection is `paper/sections/screening.tex`, included from `paper/sections/results.tex`.

## Inputs

| Input | Role |
|---|---|
| `results/screening_c5.json` | registered sites, DFT targets and per-site means of S (v1, `S_eV`) and S-v2 (`S_v2_eV`) at B = 654; the two registered MAEs. Holds no per-resample predictions and no interval. |
| `results/screening_absence.json` | why each absent candidate is absent; release counts |
| S run records and prediction parquets of `results/` (v1) and `results/v2_sweep/` (v2) | per-resample seed-ensemble predictions, read through `scripts/diagnostics_sweep.py` (`run_index`, `ensemble`), unchanged |
| `data/processed/universe_v1.parquet` and the host supercell CIFs under `data/raw/` | read only, from the main checkout (`--data-root`) |

## What `figures/code/screening_data.py` adds

`figures/main/data/screening_demo.json` (a `write_result` record, `results_dir=figures/main/data`) holds, for each
of the ten sites: the DFT value; for each backbone the mean over the resamples in which the host was held out (the
registered aggregation, asserted equal to `screening_c5.json` to 1e-9), the minimum and maximum over those
resamples, and their number; the first cation shell of the vacancy oxygen (cations within 1.2 times the nearest,
the shell of the renders), its size and mean distance; the host band gap, formation energy per atom and other
universe descriptors; the space group of the host supercell (pymatgen, `symprec` 0.1 A). Summary per backbone: MAE with
a host-cluster percentile bootstrap interval (`stats.bootstrap_n` draws, seed 0, hosts as clusters), signed bias,
largest error, the within-host pair concordance, the Spearman correlation across sites. Descriptive Spearman
correlations of the DFT energy with host band gap, host formation energy, first-shell size and distance. Within-host
pair differences. These are new numbers derived from existing records; none is a claim.

## Decisions

- The error bar of Figure 7 is the minimum to maximum of the per-resample predictions, not a standard deviation:
  hosts were held out in between one and five resamples (four of ten sites in one), so a standard deviation would
  be undefined or meaningless for most sites. A site held out once has no bar.
- The MAE interval is new. The registered result file has none; the hierarchical bootstrap of `dftgnn.stats` needs
  per-resample test sets that these sites do not provide. The interval is over the seven hosts and is stated as such.
- The derived record lives under `figures/main/data/`, not `results/`, because this session may touch only
  `paper/sections/`, `paper/tools/make_numbers.py`, `paper/refs.bib`, `figures/` and `docs/`.
  `paper/tools/make_numbers.py` reads named records of `figures/main/data/` (`FIGURE_RECORD_DIRS`), prefix `ScreeningDemo`.
- Panel (b) of the optional structure render was not added: the SnO2 render is a raster and Figure 7 must pass
  `qa_figure.py` (no raster images). The render is cited as a Supplementary figure.
- The TiO2 host of the release is a monoclinic polymorph (space group number 12, four inequivalent oxygen sites with
  two-, three-, three- and four-fold coordination), not rutile. `paper/sections/data.tex` and the TiO2 remark in
  `docs/limitations_notes.md` call it rutile; `screening.tex` does not, and does not repeat that wording.

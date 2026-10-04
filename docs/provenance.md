# Data provenance and verification of planning facts

Verification session S01, 2026-10-05. Every fact below was checked against a primary source retrieved
headlessly (GitHub REST API, raw.githubusercontent.com, arXiv, APS). Locators refer to the documents
listed in "Sources". The full Kumagai dataset (per-formula tarballs, ~2 GB unpacked) was **not**
downloaded; only the README, the repository tree, the three ML CSV tables (~3 MB), and the
`site_info.tar.gz` archive (1.7 MB) were read.

## Sources

| Tag | Document | Identifier / URL | Retrieved as |
|---|---|---|---|
| K21 | Y. Kumagai, N. Tsunoda, A. Takahashi, F. Oba, "Insights into oxygen vacancies from high-throughput first-principles calculations", Phys. Rev. Materials 5, 123803 (2021) | doi:10.1103/PhysRevMaterials.5.123803 | publisher PDF (open access, CC BY 4.0), 12 pp. |
| K21-SM | Supplemental Material to K21 | https://journals.aps.org/prmaterials/supplemental/10.1103/PhysRevMaterials.5.123803/SM_submitted.pdf | PDF, 26 pp. |
| K25 | S. Kiyohara, C. Shibui, S. Bae, Y. Kumagai, "Machine Learning Prediction of Charged Defect Formation Energies from Crystal Structures", Phys. Rev. Lett. 135, 246101 (2025); arXiv:2510.00513v2 | doi:10.1103/h66h-y5k6 | arXiv v2 PDF, 14 pp. (v2 journal_ref = PRL 135, 246101) |
| K25-SI | Supplemental Information to K25 | https://journals.aps.org/prl/supplemental/10.1103/h66h-y5k6/defect_ML_SI_v3.pdf | PDF, 7 pp. |
| DB | Oxygen-vacancy database release (K21 ref. [16], [78]) | https://github.com/kumagai-group/oxygen_vacancies_db (branch `master`, HEAD e310353ecb, last push 2022-11-16) | GitHub API tree + raw files |
| DB-README | README.md of DB | https://raw.githubusercontent.com/kumagai-group/oxygen_vacancies_db/master/README.md | 124 lines |
| K25-code | Code and data of K25 (K25 ref. [38]) | https://github.com/kumagai-group/ML_charged_defects (branch `main`, HEAD 39db6d2d8f, last push 2025-12-16) | GitHub API tree + raw files |

## Verification table

| # | Claimed fact | Verified value | Source | Locator | Status |
|---|---|---|---|---|---|
| 1 | 932 non-magnetic hosts | 932 is the number stated by K25 for the database it used. K21 reports **937** oxides with completed vacancy calculations; DB ships 937 per-formula tarballs and 937 `site_info/` folders. K25-code ships 924 host JSON files per data variant. | K25; K21; DB | K25 Methods p. 10 ("non-magnetic 932 oxides with 2090 inequivalent sites"); K21 abstract, Sec. III A, Fig. 1, K21-SM Fig. S1; DB tree `oxygen_vacancies_db_data/` (937 files) | CORRECTED (932 is K25's working count; release covers 937) |
| 2 | 2090 inequivalent O sites | 2090 stated by K25 for 932 oxides. K21 implies 6327/3 = 2109 sites over 937 oxides (step O runs three charge states per site). `site_info/*/cell_info.txt` lists 2121 irreducible O entries over 937 supercells (two hosts list 8 and 12, above K21's four-site cap, which suggests supercell-symmetry splitting). | K25; K21; DB | K25 p. 10; K21 Fig. 1 caption and Sec. III A ("6327 calculations"); DB `site_info.tar.gz` | CONFIRMED as K25's figure; counts differ by source (see Discrepancies) |
| 3 | 1734 neutral entries after PHS removal, 2045 before (Kiyohara et al.) | 1734 (2045) for q = 0; also 1676 (2014) for q = +1 and 1416 (1637) for q = +2, after removing migrated, split-type and dynamically-unstable-host vacancies. | K25 | Methods p. 10 | CONFIRMED |
| 4 | DFT: PBEsol+U, U_eff = 5 eV on Cu/Zn d and Ce f | PBEsol with Hubbard U on Cu and Zn d and Ce f orbitals, U_eff = 5 eV; VASP 6.2.0, PAW, 520 eV (lattice) / 400 eV (other) cutoff. | K21; K25 | K21 Sec. II F, II E; K25 Methods p. 10 | CONFIRMED |
| 5 | Band edges from non-self-consistent dielectric-dependent hybrid | Band-edge positions from non-self-consistent dielectric-dependent (nsc-dd) hybrid calculations; mixing parameter from the averaged electronic dielectric constant. | K21; K25 | K21 Sec. II F, III A (step K); K25 Methods p. 10 | CONFIRMED |
| 6 | O chemical potential = half the total energy of triplet O2 | **Source-dependent.** K25 states half the total energy of spin-triplet O2. K21 states the O standard state is the calculated O-atom energy plus the *experimental* O2 binding energy (PBEsol overbinds: 3.3 vs 2.6 eV/atom), and Fig. 4 uses this standard state. The released neutral numbers are identical in both releases for every host checked (ZnO 4.96530 eV; Ga2O3 O1/O2/O3; MgO; Al2O3), so the two descriptions cannot both be literal. | K21; K25 | K21 Sec. II G, Fig. 4 caption; K25 Methods p. 10; DB `charge0.csv` vs K25-code `materials_coreAlign/*.json` | CORRECTED (claim matches K25 text only; K21 text and data disagree with it) |
| 7 | README: `vacancy_formation_energy` aligned at the O-site local potential, Fermi origin at ZnO VBM | README says the column is "aligned at the O site local potential, and the origin of the Fermi level is set to the VBM in ZnO". For q = 0 alignment is irrelevant (no Fermi-level term). | DB-README | lines 43-44 | CONFIRMED |
| 8 | README: supercell CIFs in `site_info.tar.gz` | README says the archive "contains the site information in the supercells" and "the cif files describe the supercell structures". Archive holds 937 folders, each with `supercell.cif` and `cell_info.txt` (space group, transformation matrix, Wyckoff sites, coordination). | DB-README; DB | lines 26-28; `site_info.tar.gz` (1,708,018 B) | CONFIRMED |
| 9 | Kumagai 2021 RF: 0.27-0.44 eV by charge state | MAE at 700 training oxides, mean over 100 resampled training sets: **q = 0: 0.34 eV; q = +1: 0.27 eV; q = +2: 0.44 eV**. Learning curve at N = 22, 70, 220, 700 training oxides; extrapolated N to infinity (aN^-0.5 + b): 0.19 / 0.18 / 0.33 eV. Neutral RF vs Deml-descriptor linear model: 0.32 vs 0.71 eV. | K21 | abstract; Sec. III D; Fig. 5(a) (read from the rendered figure); K21-SM Fig. S10 | CONFIRMED (range); per-q values added |
| 10 | Kiyohara et al., arXiv:2510.00513: structure-only CGCNN, MAE 0.29/0.22/0.37 eV for q = 0/+1/+2, oxide-level split | Confirmed: single CGCNN for all three charge states, MAEs 0.29, 0.22, 0.37 eV on the test set; split by oxide 0.7:0.15:0.15. Now published as PRL 135, 246101 (2025). | K25 | p. 2 (intro), p. 6 and Fig. 3(a); Methods p. 10 | CONFIRMED (citation updated to PRL) |
| 11 | Exclusion flag: PHS | PHS identified automatically from band-edge-like states (orbital dissimilarity < 0.4; CBM-like occupation > 0.2 e or VBM-like < 0.8 e). 924 V_O flagged with PHS in K21. | K21; DB-README | K21 Sec. II H, III A; README lines 64-66 | CONFIRMED |
| 12 | Exclusion flag: vacancy split | README "defect type ... *vacancy spit* [sic] or *unknown*"; split-type V_O discussed in K21 and excluded by K25. | DB-README; K21; K25-SI | README lines 71-72; K21 Sec. III C, Fig. 3; K25-SI Note 1 | CONFIRMED |
| 13 | Exclusion flag: unknown defect type | README: "unknown" type "usually accompanies large atomic reconstruction". | DB-README | lines 71-72 | CONFIRMED |
| 14 | Exclusion flag: not same config from init | README: atomic configuration differs from the initial structure by atom mapping with 1 Å cutoff (migrated vacancies; 58 in K21). | DB-README; K21 | README lines 74-75; K21 Sec. III C | CONFIRMED |
| 15 | Exclusion flag: supergroup | README: final structure has a supergroup relation to the initial site symmetry (16 cases, all split-type, all q = 2+). | DB-README; K21 | README line 73; K21 Sec. III C; K21-SM Table S5 | CONFIRMED |
| 16 | Exclusion flag: energy strange | README: "formation energy is anomalous". K21 links anomalous values to 21 V_O in three dynamically unstable hosts. | DB-README; K21 | README line 76; K21 Sec. III A | CONFIRMED |
| 17 | Exclusion: dynamically unstable hosts | K2Cd2O3, Ba2Ti(GeO4)2 and Cs2O show imaginary phonon modes away from Gamma; 21 V_O removed from analyses but kept in the release. None of the three appears in the ML CSVs. K25 also removes such hosts. | K21; K21-SM; K25-SI; DB | K21 Sec. III A; K21-SM Fig. S4; K25-SI Note 1; `charge{0,1,2}.csv` | CONFIRMED |
| 18 | Additional flag (not in claim): band edges undetermined | 59 V_O whose band edges could not be determined were removed. | K21 | Sec. III A | CONFIRMED (add to filter list) |
| 19 | Data licence CC BY 4.0 | README: "All the data is licensed under a CC BY 4.0 license" with a link to creativecommons.org/licenses/by/4.0/. The repository has no LICENSE file (GitHub API `license: null`). K21 itself is published under CC BY 4.0. K25-code states no licence. | DB-README; K21 | README line 24; K21 p. 1 footer | CONFIRMED (DB); K25-code licence UNVERIFIABLE (none stated) |
| 20 | Earlier audit: 1745 entries / 824 hosts with vacancy-local Bader columns | `vacancy_formation_energy_ml/charge0.csv` has 1745 rows over 824 formulas, which is K21's neutral ML set (K21 Fig. 4(a) ndata = 1,745; Sec. III D "824, 764, and 750" oxides). Columns include `bader_charge`, `bader_volume`, `nn_ave/max/min_bader_charge`. q = +1: 1689 rows / 764 formulas; q = +2: 1613 rows / 750 formulas. No missing Bader values. | DB; K21 | CSV headers and row counts; K21 Sec. II I, III D, Fig. 4 | CONFIRMED (both counts are real; they describe different filtered subsets) |

## Discrepancies

1. **Host count, 937 vs 932 vs 924.** K21 and the release cover 937 oxides. K25 reports 932 (consistent
   with removing a few hosts, e.g. the three dynamically unstable ones plus others, but K25 does not list
   them). K25-code ships 924 host files per variant, and its split files list 923 formulas (646/138/139)
   without PHS and 924 (646/138/140) with PHS. The K21 ML CSVs cover 824 hosts at q = 0. Our host
   count must be derived in S02 from the filters we apply, not quoted.
2. **Site count, 2090 vs 2109 vs 2121.** K25: 2090 sites (932 hosts). K21: 6327 vacancy calculations
   = 3 x 2109 sites (937 hosts). `site_info` cell files: 2121 irreducible O entries. The paper should
   quote the count from our own filtered table.
3. **Neutral entry count, 1734 vs 1745.** K25: 1734 neutral V_O after PHS removal (2045 before).
   K21 ML CSV: 1745 neutral rows. Both exclude PHS. K21 keeps vacancies with n_rm <= 2 (removed-atom
   count), while K25 additionally drops migrated and split-type vacancies. The 11-entry difference is
   plausibly these filters, but neither paper reconciles the two numbers. S02 should reproduce both
   from the raw release.
4. **O chemical potential definition** (row 6). K21 text: O-atom energy plus experimental O2 binding
   energy. K25 text: half the triplet-O2 total energy. Released neutral values agree to < 1e-6 eV
   across the two releases for every host checked. One of the two method descriptions does not match
   the shipped numbers, and from the papers alone we cannot tell which. A uniform mu_O shift does not
   affect MAE, but it does affect any absolute E_f quoted (e.g. a physics floor with an intercept, or a
   screening threshold). We must state which reference our numbers use, namely "as released by K21".
5. **Kumagai RF test-set size.** K21 text: 48 test oxides. Released `machine_learning.py` (lines 40,
   190): `test_size=50` formulas. Minor; quote the paper.
6. **Kiyohara is no longer only a preprint.** Cite PRL 135, 246101 (2025), doi:10.1103/h66h-y5k6; the
   arXiv record v2 carries this journal_ref.
7. **Per-charge MAE ordering.** The claimed "0.27-0.44 eV by charge state" is correct as a range, but
   the neutral value is 0.34 eV, not 0.27 eV (0.27 is q = +1). For C0 the like-for-like neutral
   baselines are RF 0.34 eV (K21, N = 700 oxides) and CGCNN 0.29 eV (K25, about 650 training oxides).
8. **K25 hyperparameter table (K25-SI Table S1)** lists search ranges for learning rate 0.1-0.3 and
   dropout 0.003-0.03, but the optimised values in Table S2 (0.003-0.014 and 0.10-0.17) fall outside
   them; the two ranges appear to be swapped or mis-scaled. Noted only; not needed for our protocol.
9. **README typo**: "vacancy spit" for "vacancy split" (line 72). The flag string in the data
   files must be read from the data, not from the README.

## Bader quantities and RF descriptor values (resolution of the earlier conflict)

- **Per-site Bader quantities are documented and released.** K21 Sec. II I defines the second
  descriptor class as on-site properties of the O atom to be removed: Bader charge and Bader volume
  (Henkelman code, all-electron density), spherically averaged Born effective charge, and the
  O-2p-centre-to-VBM offset. The third class adds Voronoi-solid-angle-weighted neighbour averages,
  and maxima and minima over neighbours with weight > 1/12, of Bader charge, BEC and
  electronegativity. The README (lines 30-45) documents the `vacancy_formation_energy_ml/`
  directory, but it does not enumerate the descriptor columns. The column names are visible only in
  the CSV/pickle headers. So: documented in the paper, present in the release, not itemised in
  the README.
- **The RF descriptor values are released**, in `vacancy_formation_energy_ml/charge{0,1,2}.csv` (generated
  from the pickled DataFrames `df_charge{0,1,2}.pcl`, README line 41), one row per (host, O site), keyed by
  `formula` and `full_name` (e.g. `ZnO_Va_O1`), with target `vacancy_formation_energy`. 70 descriptor
  columns for q = 0 and +1, 69 for q = +2; the paper states "70 descriptors". Coverage is K21's ML
  subset only (1745 / 1689 / 1613 rows), not every calculated vacancy.

### Full K21 random-forest descriptor list (CSV column -> physical definition)

Bulk (host) properties:

| Column | Definition |
|---|---|
| `band_gap` | PBEsol(+U) band gap of the host (eV) |
| `ave_ele_diele` | spherically averaged electronic (ion-clamped) dielectric constant, DFPT |
| `ave_ion_diele` | spherically averaged ionic dielectric constant, DFPT |
| `formation_energy` | host formation energy per atom from the Materials Project (MP2020-corrected) (eV/atom) |
| `vbm_s`, `vbm_p`, `vbm_d`, `vbm_f` | fractional s/p/d/f orbital character of the VBM state |
| `cbm_s`, `cbm_p`, `cbm_d`, `cbm_f` | fractional s/p/d/f orbital character of the CBM state |

On-site properties of the O atom to be removed:

| Column | Definition |
|---|---|
| `bader_charge` | Bader charge of the O site (e) |
| `bader_volume` | Bader volume of the O site (A^3) |
| `ave_bec` | spherically averaged Born effective charge of the O site |
| `o2p_center_from_vbm` | centre of the O-2p partial density of states relative to the VBM (eV), after Deml et al. |

Neighbour properties (Voronoi solid-angle weights; max/min over neighbours with weight > 1/12):

| Column | Definition |
|---|---|
| `nn_ave_bader_charge`, `nn_max_bader_charge`, `nn_min_bader_charge` | weighted mean / max / min Bader charge of neighbours |
| `nn_ave_ave_bec`, `nn_max_ave_bec`, `nn_min_ave_bec` | weighted mean / max / min spherically averaged BEC of neighbours |
| `nn_ave_eleneg`, `nn_max_eleneg`, `nn_min_eleneg` | weighted mean / max / min electronegativity of neighbours (cations and anions, including O) |
| 45 element columns (`Ag`, `Al`, ..., `Zr`, `O`) | w_X: fraction of the O-site Voronoi cell's solid angle facing atoms of element X |

25 physical columns plus 45 element-weight columns give the 70 descriptors. K21 used 400 trees, grid
search over `max_features` in [20, 45) with fourfold ShuffleSplit CV, scikit-learn 0.24.1, and
permutation importance. Most important for q = 0: CBM p-character, host formation energy, band
gap, max neighbour electronegativity (K21 Fig. 5(b)).

**Implication for model D and the physics floor:** every DFT electronic descriptor that D would use
(band gap, dielectric constants, band-edge orbital character, O-site Bader charge, volume and BEC,
O-2p centre) is available per site in the release, but only for K21's ML subset. Note that
`band_gap` is the PBEsol(+U) gap, not the nsc-dd hybrid gap.

## Kiyohara et al. (K25): protocol extraction (comparability for C0)

| Item | K25 protocol | Locator |
|---|---|---|
| Split | Single random split **by oxide** (no O-site leakage) into train/val/test 0.7 : 0.15 : 0.15. Split lists released: without PHS 646 / 138 / 139 formulas; with PHS 646 / 138 / 140. Splitter: `numpy.random.shuffle` with a fixed seed (`DatasetSampler`). | Methods p. 10; K25-code `oxy_vac_data/{train,val,test}_w{o}_PHS.txt`; `cgcnn/data.py` |
| Fold count | **No cross-validation**: one train/val/test partition. Fig. 3 reports "average MAEs" on the test set of about 140 oxides; the paper does not say whether the average runs over seeds or over sites. | Fig. 3 caption p. 7 |
| Sizes | Entries: q = 0 1734, q = +1 1676, q = +2 1416 (PHS removed). Oxides: 646 train / 138 val / 139 test. | Methods p. 10; split files |
| Graph: cell | **Pristine host unit cell** (e.g. ZnO: 4 atoms, PBEsol+U-relaxed lattice a = 3.175 A), **not** a supercell and not the relaxed defect geometry. | K25-SI Fig. S2 caption ("The input is a unitcell structure and an index of an inequivalent oxygen site"); K25-code `materials_coreAlign/ZnO.json` |
| Graph: vacancy marking | No atom is removed and no node flag is added. The O atom stays in the graph, and the vacancy is identified **only at readout**: `SitePooling` takes the convolved embedding of the target O node, then q is concatenated and passed to the fully connected layers. | K25 p. 6; K25-SI Fig. S2; `cgcnn/pooling.py` (SitePooling), `cgcnn/cgcnn_module.py` |
| Node features | Original CGCNN 92-dim element embedding (`atom_init.json`), keyed by Z. | Methods p. 10; `cgcnn/featurizer.py` |
| Edge features | 12 nearest neighbours within 8 A; distances expanded in Gaussians exp(-eta (r - R_s)^2) with eta in {0.5, 1.0, 1.5}, R_s in {1, 2, 3, 4, 5} A (15 features), following Witman et al. | K25-SI Note 2; `cgcnn/parameters.py` |
| Training | 150 epochs, batch 32, Adam, Optuna-tuned (conv layers 2, embedding 64, hidden 48, lr 0.013, dropout 0.10 for the core-aligned model). | K25-SI Tables S1-S2 |
| Fermi-level alignment | Eigenvalues aligned by **O core potentials**; Fermi level set to the ZnO VBM; then a single constant shift of epsilon_F chosen to minimise the summed pairwise difference of charge-state means (Eq. 1), and the whole target distribution standardised. For q = 0 the alignment is immaterial. Alternative variant: Fermi level at each compound's VBM (`materials_vbmAlign`). | p. 3, Eq. (1), Fig. 1; K25-SI Fig. S1; `cgcnn/normalizer.py` |
| PHS treatment | Excluded; including PHS data worsens MAE by 0.02-0.03 eV despite about 10 % more data. | p. 6; K25-SI Fig. S3 |
| Learning curve / size dependence | **None reported** (single training-set size). | whole paper and SI |
| Code / data availability | https://github.com/kumagai-group/ML_charged_defects: CGCNN code (PyTorch Lightning) plus four JSON data variants (`materials_coreAlign`, `materials_coreAlign_with_PHS`, `materials_vbmAlign`, `materials_VBM`), 924 hosts each, and the split lists. No licence file. | K25 ref. [38]; README |

**Comparability verdict for C0.** K25's representation is "pristine host plus vacancy-site
readout", which matches the concept of our structure-only model S. It differs in three implementation
details: (i) it uses the unit cell, not the K21 supercell; (ii) it marks the site by readout pooling,
not by a node feature; (iii) it trains one model jointly on q = 0, +1, +2. Point (i) does not change the
graph for a local, periodic message-passing network: the neighbour lists of a pristine periodic
crystal are identical in the unit cell and in any supercell. Points (ii) and (iii) are design
choices. Two further differences matter: K25 uses one fixed split rather than grouped CV, and it
trains on all charge states. Its q = 0 MAE (0.29 eV) is therefore a benchmark under a different
protocol. A like-for-like C0 should either rerun K25's released split (`*_wo_PHS.txt`) with S, or
report S under our GroupKFold alongside K25's split.

## Database release: canonical location, files and licence

- **Canonical URL:** https://github.com/kumagai-group/oxygen_vacancies_db (cited as K21 refs. [16]
  and [78]). The repository was created 2021-08-05 and last pushed 2022-11-16 (HEAD e310353ecb).
- **DOI:** none for the dataset itself. Zenodo API searches (repository name; author and title
  terms) and a figshare API search returned no matching record, and neither K21 nor the README cites a mirror. The citable DOI is the article,
  doi:10.1103/PhysRevMaterials.5.123803. Recommendation: pin the commit hash in the paper's Data
  Availability Statement.
- **Licence text location:** DB-README line 24 (CC BY 4.0, linking
  https://creativecommons.org/licenses/by/4.0/). The repository has no LICENSE file.
- **File list** (966 tree entries, from the GitHub API, not truncated):
  - `README.md` (7,100 B), `add_data.ipynb` (124,343 B), `requirements.txt` (121 B), `site_info.tar.gz` (1,708,018 B)
  - `oxygen_vacancies_db_data/`: 937 files `<formula>.tar.gz` (0.3-2.7 MB each). Each unpacks to
    `<formula>/` containing `bulk_visual_data.json`, `defect_visual_data.json`, `chem_pot_diag.json`,
    and per vacancy and charge `<formula>_Va_O<n>_<q>.vesta` plus `<formula>_Va_O<n>_<q>.tar.gz`
    (relaxed `CONTCAR-finish` and binned PARCHG files) (README lines 107-124; ZnO listed as example).
  - `site_info.tar.gz`: `site_info/<formula>/supercell.cif` and `cell_info.txt` for 937 hosts.
  - `vacancy_formation_energy_ml/`: `charge0.csv` (1,153,900 B), `charge1.csv` (1,118,053 B),
    `charge2.csv` (1,062,370 B), `df_charge{0,1,2}.pcl`, `machine_learning.py`, `test.ipynb`.
  - `programs/`: Dash/Crystal Toolkit GUI (`create_app.py`, `create_layout.py`, `components.py`,
    `structure_component.py`, `bulk_dataclass.py`, `defect_dataclass.py`, `callbacks.py`,
    `create_defect_layout.py`, `create_homepage.py`, `assets/`).

The K25 companion release (https://github.com/kumagai-group/ML_charged_defects) holds `cgcnn/` (14
Python modules plus `atom_init.json`), `oxy_vac_data/` (4 x 924 JSON host files and six split lists),
`README.md` and `requirements.txt`. Each host JSON is a `Material` object: unit-cell `structure`,
`target_site_names`, `target_site_indices`, `target_vals`, `charges`.

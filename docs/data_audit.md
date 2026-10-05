# Data audit of the Kumagai oxygen-vacancy release (S02)

Audit only. No filtering decision, no model, no descriptor-target analysis. Every number below is
written by `scripts/run_s02_audit.py` through `write_result` into `results/` (names in brackets).
Sources are cited as in `docs/provenance.md`: K21 (Kumagai et al., PRM 5, 123803), K21-SM, K25
(Kiyohara et al., PRL 135, 246101), DB (the release), K25-code.

## 1. Acquisition

| Item | Value |
|---|---|
| Release | `kumagai-group/oxygen_vacancies_db` at commit `e310353ecbf698499c85a5ec5416b76e82dcecfd` (master HEAD, pushed 2022-11-16). No dataset DOI exists, so the commit is the pin. |
| Companion | `kumagai-group/ML_charged_defects` at commit `39db6d2d8f5653d6452c7877ecb2e296f04a7a01` (main HEAD, 2025-12-16) |
| Retrieval | `curl` against `codeload.github.com` tarballs at the pinned commits (`scripts/fetch_data.sh`) |
| Size | 21 917 files, 4.48 GB after unpacking the 937 per-host archives and `site_info.tar.gz` (the archive itself ships one stray `.DS_Store`, kept) |
| Manifest | `data/MANIFEST.sha256`: 21 917 entries (sha256, size, path, source URL) plus pinned commits and the download timestamp. `scripts/fetch_data.sh --verify-only` passes. |
| Reproducibility | Re-downloading the 3.1 MB companion archive reproduced its sha256 byte for byte. The 956 MB release archive was not re-downloaded. |

The inner per-defect archives (`<host>_Va_O<n>_<q>.tar.gz`, relaxed `CONTCAR-finish` and PARCHG
files) stay packed. Only ZnO's were opened, for the pristine-versus-relaxed test in section 5.

## 2. Inventory [`data_inventory`]

Full per-file list (path, format, size, rows): `results/data_inventory.json`. File classes:
`docs/file_class_inventory.csv`. Every column of every tabular file: `docs/column_inventory.csv`.
Every field of the four JSON families: `docs/json_schema_inventory.csv`.

| Class | Files | Rows or content |
|---|---|---|
| `vacancy_formation_energy_ml/charge{0,1,2}.csv` | 3 | 1745 / 1689 / 1613 rows; 73 / 73 / 72 columns; no nulls |
| `vacancy_formation_energy_ml/df_charge{0,1,2}.pcl` | 3 | same shape as the CSVs; element-weight columns hold NaN where the CSV holds 0.0 (72 764 NaN cells at q = 0); all other cells agree to 1.4e-14 |
| `oxygen_vacancies_db_data/<host>.tar.gz` | 937 | unpack to 3 JSON files plus per-defect archives and VESTA files |
| per host: `defect_visual_data.json`, `bulk_visual_data.json`, `chem_pot_diag.json` | 937 each | nested schemas, 1522 / 1058 / 9885 distinct key paths |
| per defect: `*_Va_O<n>_<q>.tar.gz`, `.vesta` | 6274 each | 6232 completed calculations plus 42 foreign files (see section 8) |
| `site_info/<host>/supercell.cif`, `cell_info.txt` | 937 each | 60-480 atoms; 2121 irreducible O entries |
| K25 `oxy_vac_data/materials_*/<host>.json` | 4 x 924 | per-host unit cell, target site indices, targets, charges |
| K25 split lists | 6 | train / val / test, with and without PHS |

README coverage. The README documents the file layout and the GUI panels but no column schema.
Only `full_name` and `vacancy_formation_energy` are described, and `formula` is mentioned inside the
`full_name` sentence. The other 70 descriptor columns are documented only in K21 Sec. II I. The
JSON fields are not documented in the README at all. A column named `formation_energy` exists in the
CSVs and means the host formation energy per atom, not the vacancy target.

## 3. Universe reconciliation [`universe_reconciliation`]

Join keys. `formula` (release directory name, unique over 937 hosts), `mp_id` (unique over 937 hosts),
`full_name = <formula>_Va_O<n>` (the site; `O<n>` is the irreducible-O label of `cell_info.txt` and of the
`sites` field of `bulk_visual_data.json`) and `q` (a list index in `defect_energies`, a suffix in
the flag keys). One neutral entry is one (formula, site) pair.

Sets. (a) all neutral entries with a completed calculation in the release; (b) the K21 neutral ML
subset (`charge0.csv`); (c) the 937 release hosts; (d) the K25 sets, rebuilt from the K25 host JSON files.

| Set | Neutral entries | Hosts |
|---|---|---|
| (a) release, completed neutral | 2103 | 935 |
| (a') release, neutral attempted (18 fizzled) | 2121 | 937 |
| (b) K21 ML subset (b is a subset of a) | 1745 | 824 |
| (c) release hosts | n/a | 937 (935 with a completed neutral entry; Cs2HfO3 and KBa4Sb3O have none) |
| (d1) K25 with PHS | 2045 | 918 (924 host files) |
| (d2) K25 without PHS | 1734 | 822 (923 host files) |
| (a) minus (b) | 358 | 220 |
| (b) and (d2) | 1726 | |
| (b) minus (d2) | 19 | |
| (d2) minus (b) | 8 | |
| (d1) minus (b) | 319 | |
| (a) minus (d1) | 58 | |
| (b) after dropping its 15 flagged entries | 1730 | 819 |

K25's 2045 and 1734 reproduce exactly from the release. K25's 932 hosts and 2090 sites do not
(section 3.2).

### 3.1 Exclusion flags

Where each flag lives: PHS is `defect_energies[...].is_shallow` (equal to membership of the `shallows`
list; 941 true over all charges); the four defect-type flags are the values of `unusual_defects`
(vocabulary: `vacancy_split`, `unknown`, `not same config from init`, `energy strange`); "band edges
undetermined" is `is_shallow = null`; dynamic instability is not a field and is applied by host name
(K2Cd2O3, Ba2Ti(GeO4)2, Cs2O; K21 Sec. III A). The string `supergroup` never occurs in any
`unusual_defects` value, although the README lists it. No magnetism field exists.

| Flag | (a) neutral | (b) neutral | (a) minus (b) |
|---|---|---|---|
| entries | 2103 | 1745 | 358 |
| PHS | 345 | 0 | 345 |
| band edges undetermined | 8 | 0 | 8 |
| vacancy split | 7 | 4 | 3 |
| unknown defect type | 19 | 11 | 8 |
| not same config from init | 28 | 15 | 13 |
| supergroup | 0 | 0 | 0 |
| energy strange | 1 | 0 | 1 |
| host dynamically unstable | 4 | 0 | 4 |
| magnetic host | no field | no field | |
| neutral calculation spin-polarised (two spin channels stored) | 264 | 96 | 168 |
| any of the first eight rows | 369 | 15 | 354 |
| none of the first eight rows | 1734 | 1730 | 4 |

Every vacancy-split and unknown entry also carries `not same config from init`; no entry carries one of
the three without it, so the 15 flagged entries in (b) are 4 split plus 11 unknown, all also
not-same-config. Over all charges the flag counts are 52 / 367 not-same-config at q = +1 / +2 and
367 / 229 PHS at q = +1 / +2 (PHS at q = 0: 345).

**Is the ML subset pre-filtered?** Yes for PHS (0 of 345 flagged entries appear in (b)), for the
band-edge-undetermined entries (0 of 8), for energy strange (0 of 1) and for the three
dynamically unstable hosts (0 of 4 entries). No for the defect-type flags: 15 flagged entries
remain in (b) at q = 0 (4 split, 11 unknown, all 15 not-same-config). The filter that built the
ML tables is not released (`add_data.ipynb` only copies files; the dataframe construction is
absent), so this is inferred from membership.

### 3.2 Explanation of every count difference

- **2121 attempted, 2103 completed (a), 18.** Fizzled neutral calculations (`defect_states`).
  Completed neutral entries cover 935 hosts; Cs2HfO3 and KBa4Sb3O have none.
- **(a) 2103 to (b) 1745, 358 removed.** 345 PHS, 8 band-edge-undetermined, 1 entry of a
  dynamically unstable host that is neither (Ba2Ti(GeO4)2_Va_O4; the other 3 entries of the
  unstable hosts are PHS and already counted), and 4 clean entries of Sr2Zr7O16 (O5-O8) with
  no flag. **The Sr2Zr7O16 exclusion is unexplained**: K21 gives no criterion that covers them.
- **(a) 2103 to K25 with PHS 2045, 58 removed.** 27 flagged entries (split, unknown or
  not-same-config) in hosts that K25 ships, plus 31 entries in the 13 release hosts that K25 does not
  ship: Ba2Ti(GeO4)2, Cs2O, K2Cd2O3 (dynamically unstable, 4 entries), Cs2HfO3 (none), and
  Ba3Sb2O, Ba4Bi2O, Ba4Nb2WO12, Cd(CuO2)2, KPd2O3, Na2Pd3O4, PtO2, Rb12Sn2As6O, Sr2Zr7O16 (27
  entries). K25 states no reason for the nine hosts beyond the unstable ones. Ba4Nb2WO12 and
  Sr2Zr7O16 are two of the three hosts with inconsistent cell metadata (section 5), which is a
  plausible but unconfirmed reason.
- **K25 2045 to 1734, 311 removed.** PHS entries inside K25's hosts: 345 minus 34 that fall in
  excluded hosts or flagged entries. The 1734 includes the 8 band-edge-undetermined entries, which
  K25 does not drop (its PHS test is the flag value `True`).
- **(b) 1745 to K25 1734.** minus 15 flagged, minus 4 Sr2Zr7O16 entries (host not shipped by K25), plus 8
  band-edge-undetermined entries that K21 dropped and K25 kept: 1745 - 19 + 8 = 1734. Exact.
- **Release neutral set with no flag of any kind: 1734**, the same number as K25's final set but not
  the same set (K25's contains the 8 undetermined entries and lacks 8 others from the unflagged
  Sr2Zr7O16 and Ba4Nb2WO12 hosts).
- **937 hosts versus 932 (K25 text) versus 924 (K25 files) versus 824 (b).** 932 equals 937 minus the 3
  unstable hosts minus the 2 hosts with no completed neutral entry, a coincidence of
  arithmetic that K25 does not confirm. K25 ships 924. (b) holds 824: 113 release hosts have no
  entry in (b), made of the 2 with no neutral, and hosts whose entries are all PHS, undetermined or
  excluded.
- **2090 sites (K25) versus 2121 / 2115 / 2111 / 2109.** 2121 attempted irreducible O sites over 937 hosts;
  2115 with one completed calculation at any charge; 2111 in the 932-host reading; 2109 in
  those hosts with a completed calculation (also K21's 6327/3). K25's own files carry 2071 distinct
  sites over 924 hosts. **2090 is not reproduced and the difference is unexplained.**
- **PHS 941 (all charges) versus K21's 924.** Unexplained; K21 may count at a different stage.

## 4. Descriptors [`descriptor_provenance`]

`docs/descriptor_taxonomy.csv` classifies all 70 columns. Result: **no column is DEFECT-DERIVED.**
Evidence, over 1745 rows: bader charge, PBEsol(+U) gap, both dielectric constants and the 45 element
weights are recomputed from the pristine unit cell shipped in `bulk_visual_data.json` to better than 1e-14;
the weighted neighbour means of Bader charge and electronegativity are recomputed to 6e-15; the O-2p centre is
reproduced from the pristine site-projected DOS (largest deviation 0.13 eV; the integration window is
undocumented); all 70 columns are identical across the q = 0, +1, +2 tables, which a defect-cell
quantity would not be. The neighbour maxima and minima are partly reproduced (nn_max_bader 99.8 %,
nn_min_eleneg 97.7 %, nn_max_eleneg 74.3 %, nn_min_bader 72.8 % of rows within 1e-3), because the exact
selection rule (K21: weight above 1/12) is not documented to the precision needed.

Bader columns, as asked.

| Question | Answer |
|---|---|
| Whose charge is `bader_charge`? | The O atom that will be removed. It equals the pristine unit-cell Bader charge of that O site (1745 of 1745 rows, max diff 2.2e-16). |
| Which calculation? | The pristine host unit cell (all-electron density, Henkelman grid code; K21 Sec. II I). Not the defect supercell. |
| `nn_*_bader_charge` neighbours? | Periodic Voronoi neighbours of the O site in the pristine unit cell, including O neighbours. Weights are the Voronoi solid-angle fractions (sum 1). `ave` is the weighted mean, `max` and `min` use neighbours above a weight threshold (K21: 1/12). |
| Units and sign | `bader_charge`, `nn_*`: e, net ionic charge, negative for anions (ZnO O1: -1.0427). `bader_volume`: A^3. `ave_bec`: e, negative for O. |

The three descriptor-side hazards are not leakage but matter for S03: the CSV column
`formation_energy` is the host formation energy per atom (not the target); `band_gap` is the PBEsol(+U)
gap, not the hybrid gap that `bulk_visual_data.band_gap` holds (differs by up to 4.8 eV); BEC columns and
`bader_volume` have no pristine counterpart in the release, so they were checked for q-invariance only.

## 5. Structures [`structure_audit`]

- **Join coverage.** 2103 / 2103 of (a) and 1745 / 1745 of (b) map to a CIF (host directory) and to an
  irreducible-O label in `cell_info.txt`. 23 entries of (a) and 7 of (b) lie in the three hosts with
  inconsistent cell metadata (below).
- **Pristine, not defect-relaxed.** 936 of 937 CIFs have exactly (unit-cell atoms) x (supercell
  multiplicity) atoms, hence no vacancy; the 937 pass an O-label coverage check (the labelled equivalent atoms
  are exactly the O atoms). The generation code preserved in `add_data.ipynb` (commented out, last cell) writes
  `SupercellInfo.structure`, the perfect supercell, to the CIF. For ZnO the CIF has 300 atoms (Zn150 O150) while the relaxed
  defect cell has 299 (Zn150 O149).
- **Supercell, not unit cell.** 60-480 atoms (median 224; 5th-95th percentile 72-448). Transformation
  multiplicity 3-108 (median 12). The structure is the PBEsol(+U)-relaxed host, symmetrised.
- **Lattice parameters (A).** a 8.04-24.7 (median 14.8); b 7.56-25.3 (15.0); c 7.20-37.5 (14.8).
  Angles: alpha 64-101, beta 68-135, gamma 61-120 degrees. Shortest interatomic distance 1.31-2.90 A (the
  1.31-1.33 A contacts are the B-O bonds of the borates NaBO2, KBO2, RbBO2, CsBO2 and Ba2Ca(BO2)6, a
  normal bond length).
- **Unit-cell sizes (host JSON).** 2-30 atoms, which is K21's criterion (iv).
- **Vacancy site identification.** Unambiguous by label. `full_name` carries `O<n>`; `cell_info.txt` lists, for each
  irreducible O, its Wyckoff letter, site symmetry, the supercell atom indices of all equivalent
  sites (e.g. `150..299` for ZnO) and the fractional coordinates of the representative. For all 2121
  O entries the first listed index is an O atom whose position matches the listed coordinates, all listed
  indices are O, and together they cover every O atom in the cell. Marking the site then means choosing
  index `equiv_first` (or any member). This holds for all but three hosts, where the unit-cell and
  supercell descriptions disagree on the site multiplicities: Ba4Nb2WO12 (342-atom cell from a 19-atom
  cell, multiplicity 18), Sr2Zr7O16 (450 from 25, 18) and Sr2SnO4 (112-atom cell from a 28-atom cell with
  multiplicity 8, so the supercell is half the expected volume, i.e. it was built from the primitive
  cell). **Sr2Zr7O16 has a confirmed label mismatch in the ML table**: in `charge0.csv` rows O3 and
  O4 carry the targets of release sites O7 and O8 (6.8630 and 6.5422 eV versus 6.7924 and 7.4228 eV
  for release O3 and O4), while their descriptors match the unit-cell labels O3 and O4.
- **ZnO end to end** (`scripts/audit_zno.py`, `results/structure_audit.json`). Row `ZnO_Va_O1`
  (target 4.965302 eV, band gap 1.4597 eV, bader charge -1.0427 e) maps to `site_info/ZnO/supercell.cif`
  (P6_3mc host, 5x5x3 cell, a = 15.876 A, c = 15.348 A, 300 atoms) and to cell_info entry O1 (Wyckoff b,
  site symmetry 3m., atoms 150..299). Atom 150 is O at fractional (0.0667, 0.1333, 0.1266),
  Cartesian (0.000, 1.833, 1.944) A. Its first shell is four Zn at 1.934, 1.934, 1.934 and 1.942 A with
  Zn-O-Zn angles 108.6 (x3) and 110.4 (x3) degrees: ideal wurtzite tetrahedral coordination, as
  expected for ZnO. All 150 O atoms have coordination 4. In the relaxed q = 0 defect cell the one
  missing atom is O at pristine index 150, and 16 atoms moved more than 0.05 A (largest 0.17 A),
  confirming both that the CIF is pristine and that the label picks the vacancy.
- **Non-magnetic.** The release carries no magnetisation or spin field. Non-magnetism rests on K21
  Sec. II A (selection criterion iii; Mn-Ni excluded) and Sec. III A (the nonmagnetic state verified from ferromagnetic
  starts). Consistently, no host contains Mn, Fe, Co or Ni. Note that 264 neutral calculations (96 in
  (b)) keep two spin channels, which K21 Sec. II E (end of the section, before II F) retains when the magnetisation exceeds 0.1 muB during
  relaxation; a local moment on a neutral vacancy is not a statement about the host.
- **Polymorphs.** 0 formulas have more than one polymorph in the release: 937 formulas, 937 reduced
  formulas and 937 MP IDs are all distinct. GroupKFold by formula therefore equals grouping by host here.
- **Chemistry families (counts only, no decision).** Cations are all elements except O (44 cation elements
  plus O in the release). Hosts per cation count: 34 single-cation, 570 two, 321 three, 12 four.

| Definition | 937 hosts | 935 hosts of (a) | 824 hosts of (b) |
|---|---|---|---|
| (i) same cation set | 750 | 748 | 679 |
| (ii-a) cation periodic-table group pattern, set of distinct groups | 141 | 141 | 133 |
| (ii-b) same, multiset over cations | 174 | 174 | 165 |

Lanthanides and actinides are assigned group 3 in (ii).

## 6. Kiyohara split [`k25_split`]

Released: yes. `oxy_vac_data/{train,val,test}_{wo,w}_PHS.txt` list formulas (one per line) and contain
no entry keys. Sizes 646 / 138 / 139 hosts without PHS and 646 / 138 / 140 with; the lists are disjoint,
every formula is in the release, and the sets equal the hosts of the corresponding JSON variant. The
seed that generated the split is not in the release (`DatasetSampler` takes `random_seed` as an
argument; no value is stored), so the lists, not the seed, are the record.

| Split (without PHS) | Hosts | K25 neutral entries | Hosts in (b) | Entries in (b) | (b) entries in these hosts |
|---|---|---|---|---|---|
| train | 646 | 1197 | 573 | 1193 | 1201 |
| val | 138 | 262 | 121 | 261 | 262 |
| test | 139 | 275 | 128 | 272 | 276 |
| total | 923 | 1734 | 822 | 1726 | 1739 |

`1739 = 1201 + 262 + 276`; 6 of (b)'s 1745 entries (2 hosts) are in no split host. Overlap with (b) at host
level: 822 of 824 hosts of (b) have at least one entry in a K25 split host (the 2 others are
Sr2Zr7O16, in no K25 list, and VAg3O4, which appears only in the with-PHS lists), and at entry level 1726 of 1745.

Reported by K25 (K25 p. 6, Fig. 3(a)): q = 0 test MAE 0.29 eV on the test set of about 140 oxides
(139 listed; 275 neutral entries in them under our reconstruction). Charged states 0.22 eV (q = +1) and
0.37 eV (q = +2).

## 7. Target sanity [`target_sanity`]

Neutral E_f over (b), eV: n = 1745, mean 5.285, sd 1.410, min 1.410, max 8.303; quantiles 1 % 2.24,
5 % 2.86, 25 % 4.19, 50 % 5.31, 75 % 6.47, 95 % 7.35, 99 % 7.69; skew -0.23, excess kurtosis -0.83.
**No entry lies beyond 4 sd, and none beyond 3 sd.** Outliers exist only outside (b): the full
release has K2Cd2O3_Va_O1 at -143.3 eV (PHS, energy-strange host), beyond 4 sd of (a).

- **Units and reference.** eV per vacancy. The released neutral value is the formation energy at the
  reference oxygen chemical potential (Delta mu_O = 0); the A and B chemical-potential limits are separate
  fields (`rel_chem_pots`). The README does not state this; it is inferred from ZnO (4.965 eV for
  Delta mu_O = 0 and 1.38 eV at the Zn-rich limit, Delta mu_O = -3.58 eV). The O reference definition
  differs between K21 and K25 text (`docs/provenance.md`, row 6) and the numbers do not settle it.
- **Fermi-level independence.** Confirmed. For all 2103 neutral entries the point-charge and alignment
  terms are exactly 0, and each site has one value, so neutral E_f has no Fermi-level term.
- **ML table versus release.** 1743 of 1745 targets match the release for the same site to 1e-9 eV.
  The two mismatches are the Sr2Zr7O16 label swap of section 5 (differences 0.071 and -0.881 eV; the
  values belong to release sites O7 and O8).
- **K25 versus release.** All 2045 neutral K25 targets equal the release value (max difference 9e-16 eV).

## 8. Hazards found during the audit

1. `formation_energy` in the CSVs is a host property, not the target.
2. `bulk_visual_data.band_gap` is the hybrid gap; the CSV `band_gap` is PBEsol(+U).
3. The pickles hold NaN in element-weight columns where the CSVs hold 0.0.
4. 14 host directories whose formula is a prefix of another (CsAgO, CsAuO, CsCuO, KAgO, KCuO, KTlO,
   LiAgO, LiCuO, NaAgO, NaCuO, NaTlO, RbAgO, RbAuO, RbTlO) also contain the 3 defect archives and 3 VESTA
   files of the longer formula (14 x 6 = 84 foreign files, from a prefix glob in the packaging code). Keep to the
   per-host JSON files and never glob `<formula>*`.
5. Sr2Zr7O16 label mismatch in the ML table; Ba4Nb2WO12 and Sr2SnO4 cell-metadata inconsistencies.
6. The `supergroup` flag does not exist in the data.
7. The hosts' K25 coverage differs from the release (13 hosts missing from K25).

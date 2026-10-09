# Tiling map notes (S11)

`scripts/mlip/build_tiling.py` maps each DFT unit cell (release `bulk_visual_data.json`) onto its release
supercell by an integer matrix and one global translation (`src/dftgnn/mlip/tiling.py`). Result: 797 of 818
hosts ok (median maximum residual 9.5e-8 A, largest 6.8e-4 A); 21 fail and are flagged `excluded_from_C3b`
(`data/tiling_summary_v1.csv`, `results/tiling_v1.json`). In every failing host the matrix is integer to
better than 1e-9; the failure is the atom correspondence.

Sr2SnO4 (known metadata inconsistency) tiles cleanly: its 28-atom DFT cell maps by M = diag(2, 2, 1) onto
the 112-atom release supercell (residual 5e-8 A). The release transformation matrix [[2,0,2],[0,-2,-2],[1,1,0]]
refers to the primitive cell and does not apply to the stored unit cell.

## Diagnosis of the 21 failures (diagnostic only; the map is unchanged)

A search over integer lattice point operations W (entries in {-1, 0, 1}, |det W| = 1, preserving the supercell
metric) applied to the tiled fractional coordinates, followed by the same translation matching, finds for each
failing host one W that gives a bijection with maximum residual about 1e-7 A:

| host | reason | W (supercell fractional basis) | det W |
|---|---|---|---:|
| NaNbO3 | residual_above_tolerance | [[-1, -1, 0], [0, 1, 0], [0, 0, -1]] | 1 |
| Ba2MgGe2O7 | no_bijection | [[-1, 0, 0], [0, -1, 0], [0, 0, -1]] | -1 |
| Ba2Cd(BO2)6 | no_bijection | [[-1, -1, 0], [0, 1, 0], [0, 0, -1]] | 1 |
| Ba2ZnGe2O7 | no_bijection | [[-1, 0, 0], [0, -1, 0], [0, 0, -1]] | -1 |
| Sr2ZnSi2O7 | no_bijection | [[-1, 0, 0], [0, -1, 0], [0, 0, -1]] | -1 |
| NaBi(MoO4)2 | no_bijection | [[-1, 0, 0], [0, -1, 0], [0, 0, -1]] | -1 |
| Ba2CdGe2O7 | no_bijection | [[-1, 0, 0], [0, -1, 0], [0, 0, -1]] | -1 |
| NaLa(MoO4)2 | no_bijection | [[-1, 0, 0], [0, -1, 0], [0, 0, -1]] | -1 |
| CaSn(BO3)2 | residual_above_tolerance | [[-1, -1, 0], [0, 1, 0], [0, 0, -1]] | 1 |
| Sr2ZnGe2O7 | no_bijection | [[-1, 0, 0], [0, -1, 0], [0, 0, -1]] | -1 |
| La2Be2GeO7 | no_bijection | [[-1, 0, 0], [0, -1, 0], [0, 0, -1]] | -1 |
| NaBiO3 | residual_above_tolerance | [[-1, -1, 0], [0, 1, 0], [0, 0, -1]] | 1 |
| TiNb3O6 | residual_above_tolerance | [[-1, -1, 0], [0, 1, 0], [0, 0, -1]] | 1 |
| MgTiO3 | residual_above_tolerance | [[-1, -1, 0], [0, 1, 0], [0, 0, -1]] | 1 |
| CaSnO3 | residual_above_tolerance | [[-1, -1, 0], [0, 1, 0], [0, 0, -1]] | 1 |
| Li8SnO6 | residual_above_tolerance | [[-1, -1, 0], [0, 1, 0], [0, 0, -1]] | 1 |
| Y2Be2GeO7 | no_bijection | [[-1, 0, 0], [0, -1, 0], [0, 0, -1]] | -1 |
| Sr2MgSi2O7 | no_bijection | [[-1, 0, 0], [0, -1, 0], [0, 0, -1]] | -1 |
| Y2Be2SiO7 | no_bijection | [[-1, 0, 0], [0, -1, 0], [0, 0, -1]] | -1 |
| Ba2MgSi2O7 | residual_above_tolerance | [[-1, 0, 0], [0, -1, 0], [0, 0, -1]] | -1 |
| Sr2MgGe2O7 | no_bijection | [[-1, 0, 0], [0, -1, 0], [0, 0, -1]] | -1 |

det W = -1 (12 hosts, all non-centrosymmetric): the release supercell is the inversion image of the stored
unit cell. det W = +1 (9 hosts, rhombohedral or trigonal): a two-fold rotation, the obverse/reverse
relation. Both are isometries, so an MLIP relaxation of either orientation gives the same energy and
strain; only the atom correspondence needs the operation. Extending the match to one lattice point
operation would recover all 21 hosts for C3b. That extension is not applied: the S11 rule allows one
global translation only, and changing it is the author's decision (to be logged as a clarification before
any geomeval run).

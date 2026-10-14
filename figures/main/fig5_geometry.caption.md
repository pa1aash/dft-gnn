**Figure 5. Geometry robustness: models trained on DFT host geometry evaluated on MACE-MP-0 relaxed hosts.** The
pristine host unit cells were relaxed with MACE-MP-0 (medium model, double precision; cell and positions) and tiled onto the release
supercells (`docs/deviations.md`: the geometry, relaxation and tiling rows); the models are not retrained. Three
inference conditions: (i) DFT geometry, (ii) MLIP geometry and (iii) MLIP geometry isotropically rescaled to the DFT
volume. S is the structure-only model, D the descriptor model, which keeps its DFT descriptors under every condition
(a fixed oracle, so its change isolates the graph input), and P the staged model (predicted descriptors into D).
Values: `results/geometry_c3b.json`, the registered geometry analysis; every `payload` key below belongs to that
record unless another file is named. All series are the originally registered backbone (v1), drawn with open markers and dashed interval bars, at the
registered budget (key `payload.budgets.654`); the descriptive extra budget is under `payload.budgets.200` and is not
drawn. (**a**) ΔMAE = MAE(condition) − MAE(DFT geometry) of the seed-ensemble predictions on the same test sites, for
MLIP geometry (circles) and MLIP geometry rescaled to the DFT volume (down triangles), with two-sided 95% intervals of
the paired hierarchical bootstrap over resamples and test hosts named in `payload.estimator`: key
`payload.budgets.654.delta_mae.<S|D|P>.<mlip|mlip_rescaled>` (`mean`, `ci95`); the marginal MAE of each condition is
under `payload.budgets.654.mae`. The dotted line is zero. The null rule of the geometry section of
`docs/ANALYSIS_PLAN.md` and its outcome are under `payload.null_rule` (`outcome`, `median_internal_rmsd_A`,
`intervals_excluding_zero`). (**b**–**d**) For S (**b**), D (**c**) and P (**d**), each point is one test host: the
mean over its test sites and resamples of the absolute change of the seed-ensemble prediction from DFT geometry,
under MLIP geometry (circles) and under the rescaled MLIP geometry (down triangles), against the isotropic strain
ε_v of the host's relaxation (`results/analysis/geometry_host_change.parquet`, hashed in `payload.input.host_change`).
ε_v is drawn because it carries the largest joint-fit coefficient for S and P in the pooled regression of the
per-host change on the three geometry components (`payload.regression.strata.pooled.<S|P>_654.joint.coef_per_sd`);
the deviatoric-strain and internal-RMSD fits, the d-electron strata and the non-converged sensitivity are under
`payload.regression` and `payload.nonconverged_sensitivity`. The y axes are logarithmic; hosts whose change is
exactly zero (D under the rescaled condition only) cannot be drawn on them and are listed in the parquet file. The
distributions of the three components, by d-electron bin and by GPU class of the relaxation, are in
`results/geometry_descriptive.json`. No v2 geometry evaluation on these relaxations (ours, of every host of the universe) exists; the collaborator's
v2 evaluation on his own relaxations is a post hoc descriptive cross-check (`payload.cross_check_809` of
`results/geometry_descriptive.json`) and is not drawn. Script: `figures/code/fig5_geometry.py`.

**Figure. Site resolution within a host, by chemistry and site (EXTENSION).** Within-host residual MAE of S
(structure only, blue) and D (structure plus the DFT descriptors of the pristine host and site, green) at the
largest training budget, for groups of test hosts or sites; lower is better. The grey tick in each row is the
zero-skill value, the within-host residual MAE of any predictor that is constant within each host (the mean
absolute deviation of the true energies from their host mean); a model point at or right of it has no
within-host skill in that group. Circles: point values; horizontal bars: two-sided percentile intervals of
the host-cluster bootstrap, paired across models and backbones (`payload.bootstrap`); no bar where fewer
hosts contribute than `payload.definitions.small_n` requires. Filled circles and solid bars: primary
backbone (v2), adopted after diagnostics of the originally registered backbone; open circles and dashed
bars: originally registered backbone (v1). (**a**) Cation element, each host under every cation it contains,
elements as in `payload.definitions.cation`; (**b**) d-electron class of the host (`data/host_dbins_v1.csv`),
with all tested hosts as the top row; (**c**) hosts containing at least one of the cations with the
highest measured perturbed-host-state rates against the rest (`payload.definitions.phs_prone`); (**d**) host
stability terciles (formation energy per atom; edges in `payload.definitions.terciles`); (**e**) PBEsol(+U)
band gap terciles; (**f**) sites at the most negative, intermediate and least negative Bader charge of the
vacancy oxygen within their host (`payload.definitions.bader_rank`). Each site's prediction is the seed
ensemble averaged over the registered resamples in which its host was tested. Values from
`results/within_host_breakdown.json`, entries of `payload.groups` (`variable`, `group`), keys
`v2|v1.S|D.within_host_mae` (`point`, `ci95`) and `v2.S.zero_skill_mae.point`; group sizes in `n_hosts`,
`n_sites`, `n_hosts_by_metric` and small groups in `flag`. Analysis rule: the within-host breakdown row of
`docs/deviations.md`, logged before computing. Script:
`figures/code/fig_si_withinhost_groups.py`.

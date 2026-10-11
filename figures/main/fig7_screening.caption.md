**Figure 7. Out-of-sample neutral oxygen-vacancy formation energies of named oxides, both backbones.** One marker
per oxygen site of the screening oxides present in universe v1 (ZnO, SnO$_2$, Ga$_2$O$_3$, TiO$_2$, ZrO$_2$, MgO and
Al$_2$O$_3$), for hosts that were held out in at least one outer resample; the model is S at the screening budget
`payload.budget`. (**a**) Predicted against DFT formation energy with the dashed line y = x; the two backbones of one
site are offset horizontally by a fixed small amount so that their bars do not overlap. (**b**) Predicted minus DFT
for the same sites, grouped by oxide in ascending order of the oxide's mean DFT energy; the dotted line is zero error.
Filled markers with solid bars: primary backbone (v2), adopted after diagnostics of the originally registered
backbone; open markers with dashed bars: originally registered backbone (v1). Colour identifies the oxide. A marker is
the mean over the outer resamples in which the host was held out of the seed-ensemble prediction (`mean_over_resamples_tested`,
as in `results/screening_c5.json`, keys `payload.sites[].S_eV` for v1 and `S_v2_eV` for v2, `dft_eV`); a bar runs from the
smallest to the largest of those per-resample predictions (`min_eV`, `max_eV`, counts in `n_resamples`), and a site held
out in one resample has no bar. Values for every marker: `figures/main/data/screening_demo.json`, keys
`payload.sites.<site>.{dft_eV, v2, v1}`, built by `figures/code/screening_data.py` from the S run records of `results/`
(v1) and `results/v2_sweep/` (v2); the screening MAE of each backbone with its host-cluster interval is in
`payload.summary.<v1|v2>.{mae_eV, mae_ci}` of that file. The candidate oxides absent from the release or removed by the
perturbed-host-state filter are listed in `results/screening_absence.json`, key `payload.candidates`. Structure render of
an SnO$_2$ site: `figures/si/structure_sno2_vacancy.png`. Script: `figures/code/fig7_screening.py`.

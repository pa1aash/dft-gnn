**Figure 1. Models and input representation.** (**a**) Every graph network starts from the pristine host
supercell of the reference calculation, in which the oxygen atom to be removed (orange) stays in place and
carries a binary vacancy flag; the relaxed defect geometry is never used, because it is unknown at deployment.
The supercell becomes a periodic radius graph (cutoff `configs/config.yaml`, `graph.cutoff_A`) read by a
MEGNet backbone. **S** predicts the neutral oxygen-vacancy formation energy E_f from the structure alone.
**D** receives the same graph plus the DFT descriptors of the pristine host and site: the host-electronic
class is appended to the initial global state and the site-electronic class to the initial features of the
vacancy node (D-state injection). **P** is staged: P1, with the backbone and readout of S, predicts the
standardised descriptors of D from the structure, and D, trained on true descriptors, maps the structure and
the predicted descriptors to E_f. The baselines are a random forest on the Kumagai descriptors (**RF**) and the
physics floor **B0**, a linear model in the oxide formation energy and the band gap. The solid, filled box
of each graph network is the primary backbone (v2), adopted after diagnostics of the originally registered
backbone; the dashed, open outline offset behind it is the originally registered backbone (v1), which differs
only in its weight initialisation. The key at the lower right of (a) states this convention, the one of every
results figure (v2 solid, v1 dashed). (**b**) The neutral oxygen vacancy in wurtzite ZnO as it
enters the data set: the pristine PBEsol(+U) supercell of the database (host and atom counts:
`figures/main/fig1_zno_vacancy.render.json`, keys `formula`, `n_atoms`), with the removed oxygen site
(`vacancy_atom_index`) marked by the translucent amber sphere and its nearest Zn neighbours (`first_shell`,
with distances) joined into the coordination tetrahedron. Zn grey-blue, O red; only Zn-O bonds shorter than
`cation_O_bond_cutoff_A` are drawn, and bonds that cross the supercell boundary are omitted. The structure is
the pristine host, not the relaxed defect cell. Orthographic view along `direction` (Cartesian), c axis up;
Blender Cycles on CPU, OpenImageDenoise, `samples` samples, rendered at `dpi` dpi over `width_mm` mm
(`px`), and embedded in panel (b) resampled to 600 dpi at the panel width (0.45 of the text width). Full
render description: `figures/main/fig1_zno_vacancy.caption.md`.
Composite: `figures/code/fig1_overview.py` (panel (a) vector; panel (b) embedded raster).

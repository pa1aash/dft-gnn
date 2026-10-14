# Figure style and QA (M3, M3b)

One visual language for every figure of the paper. Plot code imports `figures/code/style_paper.py`
(which wraps `src/dftgnn/viz/style.py` without changing it) and reads its inputs through
`figures/code/inputs_paper.py`; vector composites go through `figures/code/composite_paper.py` (pdfLaTeX);
structure renders go through `blender/render_host.py` (see `blender/README.md`).

## Plots

| Item | Convention |
|---|---|
| Width | 138.6 mm (`single`, MDPI text width) or 184.6 mm (`full`), from the mdpi.cls geometry in `docs/venue.md`. Height free. |
| Format | Vector PDF, fonts embedded as TrueType (Type 42), no creation date (byte-stable reruns). |
| Font | Arial for all text, including mathtext (no DejaVu or Computer Modern fallback). 8 pt labels, 7 pt ticks and legend, 9 pt bold panel letters. Composites built with pdfLaTeX use TeX Gyre Heros, the schematics' family. |
| Model colours | B0 grey `#7F7F7F`, RF-Kumagai orange `#E69F00`, S blue `#0072B2`, D bluish green `#009E73`, P reddish purple `#CC79A7` (Okabe-Ito); advantage A black; published reference lines and the training-mean predictor dark grey `#4D4D4D`. |
| Backbone (author decision 2026-10-11, `docs/deviations.md`) | Primary backbone (v2): solid line, filled markers, filled band. Originally registered backbone (v1): dashed line (4, 2), open markers, hatched band without fill. Legend wording exactly "primary backbone (v2)" and "originally registered backbone (v1)" (`BACKBONE_LABELS`); backbones are named only in the legend and the caption, never in the plot. Captions never call v2 pre-registered; where chronology matters they say v2 was adopted after diagnostics of v1. |
| Baselines | Backbone-independent baselines (B0, RF-Kumagai, training mean) on thinner lines (0.9 pt) with square markers and filled bands; the training mean dotted. |
| Extension series | EXTENSION results (grouped K-fold CV, precision extension) as unconnected points with 95% interval bars: diamonds for precision (drawn just left of their budget), triangles for CV (at the mean fold training size; squares until F2, changed because the baselines also use squares); filled markers and solid interval bars for v2, open markers and dashed (4, 2) interval bars for v1 (dashed since F1c; solid before), as every other v1 series; legend labels carry "(EXTENSION)". When an extension is drawn, the legend also shows a circle labelled "registered outer resamples" (`series_handles`), so registered, precision and CV series differ by marker shape and legend only. Never a third line style. |
| Marks | circles 3 pt, model lines 1.2 pt, reference lines 0.7 pt (published: dashes (4, 2) or (1.5, 1.5); margin delta: (4, 2); zero: dotted (1, 2)); bands are two-sided 95% intervals at alpha 0.22 (hatch line width 0.35 pt); one-sided 95% upper bounds as short horizontal bars; parity points 4 pt^2 at alpha 0.45. |
| Axes | Learning curves: log x axis in training hosts, ticks at 25, 50, 100, 200, 400, 654 (widened, not re-ticked, when CV points lie beyond 654). Parity: square, shared limits, y = x line. Top and right spines off. |
| Text | Only axis labels, tick labels, panel letters (a), (b) outside the top-left corner, and one legend below the panels. No panel titles. Numbers, n, definitions and statistics go in `<figure>.caption.md`, which names the result file and key of every plotted value instead of typing it. |
| Legend | One figure legend from explicit proxy handles (model colour, backbone line style, references, extension markers). `legend_handles` drops columns until it fits the page width and raises the axes bottom until the labels clear it; `save` refuses a figure whose legend leaves the page or overlaps an axes. |

Helpers: `figure`, `band_curve`, `baseline_curve`, `ext_points`, `ext_x`, `learning_curve_panel`,
`advantage_panel`, `parity_panel`, `reference_line`, `budget_axis`, the proxy handles (`model_handle`,
`baseline_handle`, `backbone_handle`, `ext_handle`, `registered_handle`, `series_handles`, `reference_handle`), `legend_handles`, `legend_below`,
`panel_letters`, `check_legends`, `save`.

## Figure set (M3b)

| Figure | Output | Script | Registered inputs (required) |
|---|---|---|---|
| Figure 1, models and input representation | `figures/main/fig1_overview.pdf` | `figures/code/fig1_overview.py` | `schematics/fig_pipeline.pdf`, `figures/main/fig1_zno_vacancy.png` |
| Figure 2, learning curves of S and D | `figures/main/fig2_learning_curves.pdf` | `figures/code/fig2_learning_curves.py` | `results/c1c2_v2.json`, `results/c1c2_v1.json`, `results/diagnostics_sweep.json` |
| Figure 3, advantage A (extended since F2: precision and CV points, upper bounds of every point in panel (b)) | `figures/main/fig3_advantage.pdf` | `figures/code/fig3_advantage.py` | `results/c1c2_v2.json`, `results/c1c2_v1.json` (extension records optional, see below) |
| Figure 7, screening demonstration (M8) | `figures/main/fig7_screening.pdf` | `figures/code/fig7_screening.py` | `figures/main/data/screening_demo.json` (from `figures/code/screening_data.py`: `results/screening_c5.json`, `results/screening_absence.json`, the S run records of `results/` and `results/v2_sweep/`) |
| G1 learning curves (ANALYSIS_PLAN §14), unnumbered, not cited (moved to the SI folder in F1c) | `figures/si/fig_g1_learning_curves.pdf` (+ PNG preview) | `figures/code/fig_g1_learning_curves.py` | `results/g1_primary.json` (v1), `results/c1c2_v2.json` (v2) |
| Figure 6, site resolution within a host (within-host skill and A_within; numbered in F1c) | `figures/main/fig6_within_host.pdf` (copy under the old name `fig_within_host.pdf`, `docs/figure_numbering.md`) | `figures/code/fig_within_host.py` | `results/c1c2_v2.json`, `results/c1c2_v1.json` |
| SI, readout schematic (Figure S1; S3 before F1c) | `figures/si/fig_readout.pdf` | `figures/code/fig_si_readout.py` | `schematics/fig_readout.pdf` |
| SI, filter cascade (Figure S2) and split designs (Figure S3), added in F1b (S1 and S2 before F1c) | `figures/si/fig_cascade.pdf`, `figures/si/fig_splits.pdf` | `figures/code/fig_si_schematics.py` | `schematics/fig_cascade.pdf`, `schematics/fig_splits.pdf` (natural widths 137.4 and 136.3 mm, centred on a 138.6 mm page) |

Every plot script takes `--results-root DIR` and `--out-dir DIR` (defaults `results/`, `figures/main/`) and
writes its caption file beside the PDF; the SI scripts and G1 write to `figures/si/` when `--out-dir` is left at
its default. The final figure numbers are in `docs/figure_numbering.md` and `docs/figure_inventory.md`. The registered inputs are the 10-resample x 3-seed records. The
scripts superseded by these (`scripts/make_figures.py`, `scripts/analysis/fig_g1.py`,
`figures/code/fig_g1_v2style.py`) are kept unchanged; rerunning the first two overwrites the M3b PDFs with
the old style. Manuscript integration: `docs/figure_integration.md`.

### Optional extension inputs

The four plot scripts draw the K-fold CV and precision extensions when their analysis records exist, and
otherwise build without them and print which inputs are missing. They never aggregate run records
themselves (results come only from `write_result` records). Expected records, written under the analysis
rules of the `docs/deviations.md` row of 2026-10-11 (§7, §11):

| Extension | Analysis record read by the figures | Run records |
|---|---|---|
| precision, v1 | `results/precision_g1_v1.json` | `results/precision/` |
| precision, v2 | `results/precision_g1_v2.json` | `results/precision_v2/` |
| grouped CV, v1 | `results/cv_g1_v1.json` | `results/cv/` |
| grouped CV, v2 | `results/cv_g1_v2.json` | `results/cv_v2/` |

Payload schema: that of `results/c1c2_<arm>.json`: `budgets` (point keys, e.g. `"400"`, `"654"` or `"k10"`,
`"k20"`), `mae.<key>.<S|D-state>.<mae|within_host_skill>.{mean, ci}`,
`A_mae.<key>.{A, ci95, upper_one_sided_95}`, `A_within_host.<key>.{A, ci95}`, plus
`x_training_hosts.<key>` (the mean fold training size for CV; may be omitted when the key is the budget).
For precision, the payload's top-level estimates are the pooled 30 x 5 values. All four records exist at
`results-v1`, and the four scripts are built from them (F2 rebuild; QA below).

## Figures 4 to 6 (built in A2 to A4)

Not built in M3b; each was drawn once its registered v1 result existed (steps A2, A3 and A4 of 2026-10-14). The v2
records beside them are POST HOC and are drawn as the primary backbone only where a v2 result on the same inputs
exists. Status at the results freeze (tag `results-v1`, `docs/freeze_notes.md`): all three built, captions name
their records, QA below.

| Figure | Claim | Output | Script | Result records | Status |
|---|---|---|---|---|---|
| Figure 4, staging | C3a, C3a-v2 | `figures/main/fig4_staging.pdf` | `figures/code/fig4_staging.py` | `results/staging_v1.json` (registered staging analysis, v1), `results/staging_v2.json` (POST HOC, v2) | built (A2) |
| Figure 5, geometry | C3b | `figures/main/fig5_geometry.pdf` | `figures/code/fig5_geometry.py` | `results/geometry_c3b.json` (v1, our 818 relaxations), `results/geometry_descriptive.json`, `results/analysis/geometry_host_change.parquet` | built (A3); v1 only: no v2 geometry evaluation on our relaxations exists. The collaborator's 809-host evaluation (`results/mlip/`, `results/mlip_eval_v2.json`) is excluded from C3b by the `docs/deviations.md` row of 2026-10-11 (§9) and is not drawn. The caption names `results/geometry_c3b.json` and its keys (file name added in F1b) |
| Figure 6 when built, Figure S7 since F1c, latent probe | C4, C4-v2 | `figures/si/fig6_probe.pdf` (moved to the SI under the §10 rule) | `figures/code/fig6_probe.py` | `results/probe_c4_v1.json` (v1), `results/probe_descriptive.json` (`payload.s_v2`, POST HOC) | built (A4), SI |

## QA

`python figures/code/qa_figure.py <pdf> [...]` checks, on page 1: no raster images; every font embedded;
one font family; width 138.6 or 184.6 mm (+/- 0.5 mm; or `--width-mm`); and no text whose box centre lies
inside an axes (axes found from the clip rectangles matplotlib writes for data artists; a PDF without any
axes fails this check, because the rule needs at least one). Exit status 0 only if all checks pass.

Status of every PDF in `figures/main/` and `figures/si/` on 2026-10-14 (F1c, after the dashed v1 extension bars in
Figure 2, Figure 3, Figure 6 and G1, and the final numbering; `python figures/code/qa_figure.py figures/main/*.pdf
figures/si/*.pdf`, 16 PDFs). The frozen copy of the earlier table in `results/freeze_table.json`
(`payload.checks.figures`) is not edited; every file it holds under the same name has the same outcome here (G1 is
now under `si/`, same outcome).

| Figure | Placement | vector | fonts | one_family | width (mm) | height (mm) | no_text_in_axes | Result |
|---|---|---|---|---|---|---|---|---|
| `main/fig1_overview.pdf` (W3: rebuilt with the keyed schematic) | Figure 1 | FAIL (1 raster: the ZnO render, by design) | ok | ok (TeX Gyre Heros) | 138.6 | 142.9 | FAIL (no axes: schematic and render, nothing to check) | accepted with reason (documented exception) |
| `main/fig2_learning_curves.pdf` (F1c: dashed v1 extension bars) | Figure 2 | ok | ok | ok (Arial) | 138.6 | 84.0 | ok | PASS |
| `main/fig3_advantage.pdf` (F1c: dashed v1 extension bars) | Figure 3 | ok | ok | ok (Arial) | 138.6 | 72.0 | ok | PASS |
| `main/fig4_staging.pdf` | Figure 4 | ok | ok | ok (Arial) | 138.6 | 84.0 | ok | PASS |
| `main/fig5_geometry.pdf` | Figure 5 | ok | ok | ok (Arial) | 138.6 | 128.0 | ok | PASS |
| `main/fig6_within_host.pdf` (F1c: renamed from `fig_within_host.pdf`; dashed v1 extension bars) | Figure 6 | ok | ok | ok (Arial) | 138.6 | 82.0 | ok | PASS |
| `main/fig7_screening.pdf` | Figure 7 | ok | ok | ok (Arial) | 138.6 | 80.0 | ok | PASS |
| `main/fig_within_host.pdf` (byte-identical copy of Figure 6 under the old name) | copy of Figure 6 | ok | ok | ok (Arial) | 138.6 | 82.0 | ok | PASS |
| `si/fig_readout.pdf` | Figure S1 | ok | ok | ok (TeX Gyre Heros) | 138.6 | 53.9 | FAIL (no axes: schematic, nothing to check) | accepted with reason (documented exception): vector, fonts, one family and width pass; the axes rule has no axes to test |
| `si/fig_cascade.pdf` | Figure S2 | ok | ok | ok (TeX Gyre Heros) | 138.6 | 22.2 | FAIL (no axes: schematic, nothing to check) | accepted with reason (documented exception, as the readout) |
| `si/fig_splits.pdf` | Figure S3 | ok | ok | ok (TeX Gyre Heros) | 138.6 | 65.2 | FAIL (no axes: schematic, nothing to check) | accepted with reason (documented exception, as the readout) |
| `si/fig_si_withinhost_groups.pdf` | Figure S4 | ok | ok | ok (Arial) | 138.6 | 205.0 | ok | PASS |
| `si/fig_si_gpu_class.pdf` | Figure S5 | ok | ok | ok (Arial) | 138.6 | 118.0 | ok | PASS |
| `si/fig_si_sensitivities.pdf` | Figure S6 | ok | ok | ok (Arial) | 138.6 | 82.0 | ok | PASS |
| `si/fig6_probe.pdf` | Figure S7 | ok | ok | ok (Arial) | 138.6 | 172.0 | ok | PASS |
| `si/fig_g1_learning_curves.pdf` (F1c: moved from `main/`; dashed v1 extension bars) | unnumbered, not cited | ok | ok | ok (Arial) | 138.6 | 94.0 | ok | PASS |

Totals: 12 PASS, 4 documented exceptions (Figure 1 and the three SI schematics), as in F1b. Figure S8, the SnO2
render, is a PNG and is outside the PDF check.

W3 (2026-10-14), Figure 1 backbone convention. `schematics/fig_pipeline.tex` had been relabelled on 2026-10-11
(`829ffc9`: the dashed outline style renamed from `v2` to `v1`, caption of record changed to "v2 solid, v1
dashed"), but `schematics/fig_pipeline.pdf` and `figures/main/fig1_overview.pdf` were not rebuilt and the figure
carried no key, so the convention lived only in the captions, and `figures/main/fig1_overview.caption.md` still
said that the dashed outline marked v2. W3 drew the convention into the schematic: the solid, filled box in
front of each graph network is the primary backbone (v2), the dashed, open outline behind it the originally
registered backbone (v1), and a key outside the data area (lower right, beside P's output) reads "primary network
(v2)" (solid, filled swatch) and "originally registered network (v1)" (dashed, open swatch), in the neutral
reference grey because it applies to every model colour. The schematic stays 137.5 mm wide (height 81.5 to 82.4
mm). Rebuilt with `sh schematics/render.sh fig_pipeline` (latexmk) and `python figures/code/fig1_overview.py`;
`qa_figure.py figures/main/fig1_overview.pdf` gives the same outcome as before: vector FAIL (the ZnO render, by
design) and no_text_in_axes FAIL (no axes), fonts, one family (TeX Gyre Heros) and width (138.6 mm) ok, so Figure
1 keeps its documented exceptions. Both caption files now say v2 solid, v1 dashed and name the key; the paper
caption in `paper/sections/methods.tex` already said so and was not edited.

The structure renders (`figures/main/fig1_zno_vacancy.png`, `figures/si/structure_sno2_vacancy.png`) are PNG by
design and are outside the PDF check (see Structure renders).

Backbone audit (F1b, Figure 7 and every SI figure; figure numbers as in F1b): v2 solid with filled markers and bands, v1 dashed with open
markers and hatched bands or dashed bars; legend wording exactly "primary backbone (v2)" and "originally
registered backbone (v1)" where a backbone is drawn (Figure 6 draws v1 only; the schematics none); no text inside
an axes; widths 138.6 mm. Deviations fixed in F1b: the GPU-class figure drew v1 bars solid and its backbone legend
entries as markers without a line; Figure 6 (c) drew the v1 trained-probe bars solid; Figure 7 used a (3, 1.6)
dash for v1 bars instead of the style's (4, 2).

F2 rebuilt Figure 2, Figure 3, G1, within-host and the SI GPU-class figure (CV marker change) with all four
extension records drawn; Figure 2, G1 and within-host grew in height (74 to 84, 88 to 94, 72 to 82 mm) so the
legend, now one entry longer, does not shrink the panels. `figures/main/fig3_advantage_extended.pdf` is no longer
in `figures/main` (see `docs/figure_integration.md`). Their captions name records and keys and contain no typed
numbers outside file names, keys and figure identifiers; the SI GPU-class caption, which still typed its design
points and GPU class names after F2, was rewritten in the same key-only style in F1b.

F1c: `style_paper.ext_points` draws the v1 precision and K-fold CV interval bars dashed (the backbone dash),
closing the F1b open issue, so the extension points in Figure 2, Figure 3, Figure 6 and G1 follow the same rule
as the SI bars. The four figures were regenerated from the same records; every plotted array (line data, band
polygons, bar segments) is identical before and after, and only the line style of the v1 bar collections changed.
In G1 the extension intervals are shorter than the markers, so its PNG preview is unchanged at 300 dpi.

Figures 2, 3, G1 and within-host replace the versions that failed in M3 (Computer Modern or DejaVu fallback,
widths of 164.0 and 81.5 mm, a legend inside the data area, panel titles in the plot). The M3 style exercise
`fig_g1_learning_curves_v2style.pdf` was removed: the rebuilt G1 figure supersedes it, and it drew v1 solid.

## Structure renders

Cycles PNG on a white background, RGB, at most 128 samples, at the MDPI text width (138.6 mm). The ZnO render
`figures/main/fig1_zno_vacancy.png` was re-rendered in M3b at 600 dpi with the README command (`--dpi 600`,
128 samples): 3274 x 2591 px, 3.5 MB (under the 8 MB limit, so the 600 dpi file is the committed one). The
frame is fitted to the projected cell (height/width 0.79; the M3 render used 0.75). It ran at memory pressure
level 2 by author instruction (the gate in `blender/render_host.py` was bypassed for this run only; 517 s).
Figure 1 embeds it downsampled (Lanczos) to 600 dpi at the 0.45-width panel (1473 px over 62.37 mm).
Element colours, vacancy marker and camera conventions: `blender/README.md`.

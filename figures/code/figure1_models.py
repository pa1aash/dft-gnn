"""Figure 1 (W2b): models and input representation, one network.

Same composite as figures/code/fig1_overview.py (layout, widths, render resampling), with panel (a) built from
figures/code/figure1_pipeline.tex: the schematic of schematics/fig_pipeline.tex without the dashed outline behind
each graph network and without the key that explained it. Everything else is unchanged.

    (a) figures/code/figure1_pipeline.tex (with schematics/common.tex), compiled by pdfLaTeX, included as vector
    (b) figures/main/fig1_zno_vacancy.png, resampled (Lanczos) to 600 dpi at the panel width and embedded

The raster panel is intended: qa_figure.py reports "vector" and "no_text_in_axes" (no axes) as failed for this
figure only, the documented exceptions of the former Figure 1.

    python figures/code/figure1_models.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import composite_paper as cp
import fig1_overview as f1  # read-only reuse: BODY, resample, RENDER, PANEL_B_FRACTION, DPI
import network_style as ns

HERE = Path(__file__).resolve().parent
PIPELINE_TEX = HERE / "figure1_pipeline.tex"
COMMON = cp.ROOT / "schematics" / "common.tex"
SUB, STEM = "main", "figure1_models"


def pipeline(tmp: Path) -> Path:
    """Compile panel (a) with the schematics' settings (pdfLaTeX, reproducible metadata)."""
    shutil.copy(PIPELINE_TEX, tmp / "pipeline_src.tex")
    shutil.copy(COMMON, tmp / "common.tex")
    env = {**os.environ, "SOURCE_DATE_EPOCH": "1791676800", "FORCE_SOURCE_DATE": "1"}
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "pipeline_src.tex"], cwd=tmp,
                   check=True, capture_output=True, env=env)
    return tmp / "pipeline_src.pdf"


def main() -> Path:
    out = ns.out_path(SUB, STEM).with_suffix(".pdf")
    wb = round(cp.WIDTH_MM * f1.PANEL_B_FRACTION, 2)
    with tempfile.TemporaryDirectory() as tmp:
        src = pipeline(Path(tmp))
        cp.build(f1.BODY % {"w": cp.WIDTH_MM, "wb": wb}, {"pipeline.pdf": src}, out,
                 prepare=lambda t: f1.resample(f1.RENDER, t / "render.png", wb, f1.DPI))
    ns.write_caption(SUB, STEM, CAPTION)
    return out


CAPTION = """
**Figure 1. Models and input representation.** (**a**) Each graph network reads the pristine host supercell as a
radius graph, with a vacancy flag on the removed oxygen (orange). S uses structure alone, D adds DFT
descriptors of the pristine host and site, P feeds descriptors predicted by P1 into D, and RF (random forest on
Kumagai descriptors) and the linear floor B0 are baselines. (**b**) The neutral oxygen vacancy in wurtzite
ZnO, removed site translucent.
"""


if __name__ == "__main__":
    print(main())

"""Appendix figures that move without redrawing (W2b): copy each file under its appendix name and write its caption.

The source files stay in place until the paper cites the new names; the copies are byte-identical.

    Figure A1  figures/si/fig_cascade.pdf             -> figures/si/figureA1_cascade.pdf
    Figure B1  figures/si/fig_readout.pdf             -> figures/si/figureB1_readout.pdf
    Figure C1  figures/si/fig_splits.pdf              -> figures/si/figureC1_splits.pdf
    Figure I1  figures/si/structure_sno2_vacancy.png  -> figures/si/figureI1_sno2_vacancy.png (and .render.json)

    python figures/code/figure_moves.py
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import network_style as ns

SI = ns.ROOT / "figures" / "si"
MOVES = {
    "figureA1_cascade": ("fig_cascade", (".pdf",)),
    "figureB1_readout": ("fig_readout", (".pdf",)),
    "figureC1_splits": ("fig_splits", (".pdf",)),
    "figureI1_sno2_vacancy": ("structure_sno2_vacancy", (".png", ".render.json")),
}

CAPTIONS = {
    "figureA1_cascade": """
**Figure A1. Filter cascade from the database release to the final dataset.** From the completed neutral
oxygen-vacancy entries of the Kumagai et al. release and its neutral machine-learning subset, D1 removes
vacancy-split, unknown-type and reconfigured entries, D2 removes the host Sr$_2$Zr$_7$O$_{16}$, whose site labels
do not match the release targets, and D3 checks the site mapping of two hosts with inconsistent cell metadata.
Dashed boxes are the entries excluded at each step, with counts in Table A1 and `results/filter_cascade.json`.
""",
    "figureB1_readout": """
**Figure B1. Readout of the structure-only network and the descriptor injection points.** After the MEGNet blocks,
the readout joins the final vacancy-node embedding, a pooling of all node embeddings and the global state, and a
multilayer perceptron maps them to the formation energy, so that the host and the local environment of the vacancy
enter separately. In D the host-electronic descriptors join the initial global state and the site-electronic
descriptors the initial vacancy-node features (green arrows), with the readout unchanged.
""",
    "figureC1_splits": """
**Figure C1. Split designs.** Hosts are drawn as sets (test hosts dark, training hosts light, validation hosts
mid-grey), and every split groups by formula, so no host contributes sites to both sides. (**a**) Grouped
hold-out with nested training sizes, (**b**) the published split of Kiyohara et al., (**c**) grouped K-fold
cross-validation, in which every host is tested once, and (**d**) leave-one-family-out folds that hold out whole cation families.
""",
    "figureI1_sno2_vacancy": """
**Figure I1. Neutral oxygen vacancy in rutile SnO2.** Pristine SnO2 supercell of the Kumagai et al. database with
the removed oxygen marked by the translucent amber sphere and its three nearest Sn neighbours enlarged and joined
into a translucent triangle, seen nearly edge-on (Sn grey-blue, O red). Camera, lights and materials are those of
the ZnO render, with render parameters in `figures/si/figureI1_sno2_vacancy.render.json`.
""",
}


def main() -> list[Path]:
    out = []
    for stem, (src, suffixes) in MOVES.items():
        for suf in suffixes:
            dst = SI / f"{stem}{suf}"
            shutil.copyfile(SI / f"{src}{suf}", dst)
            out.append(dst)
        out.append(ns.write_caption("si", stem, CAPTIONS[stem]))
    return out


if __name__ == "__main__":
    for p in main():
        print(p.relative_to(ns.ROOT))

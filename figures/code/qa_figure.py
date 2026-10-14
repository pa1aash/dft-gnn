"""QA for a paper figure PDF (M3). Uses the poppler command-line tools (pdfinfo, pdffonts, pdfimages,
pdftotext) and reads the content streams for the axes clip rectangles.

Checks (first page):
  vector        no raster image objects
  fonts         every font embedded
  one_family    one font family (subset prefix and style suffixes ignored)
  width         page width equals an MDPI width (138.6 or 184.6 mm, docs/venue.md) within 0.5 mm,
                or the --width-mm value
  no_text_in_axes
                no text inside an axes. Axes are the clip rectangles ("x y w h re W n") that matplotlib
                sets for data artists; text whose box centre lies inside one (shrunk by 0.5 pt) is a
                violation. Tick labels, axis labels and panel letters sit outside the axes by construction,
                so the rule "nothing but those" reduces to "nothing inside".

    python figures/code/qa_figure.py figures/si/fig_g1_learning_curves.pdf [--width-mm 138.6] [--json]

Exit code 0 when every check passes, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import zlib
from pathlib import Path
from xml.etree import ElementTree

MM_PER_PT = 25.4 / 72
MDPI_WIDTHS_MM = (138.6, 184.6)
WIDTH_TOL_MM = 0.5
SHRINK_PT = 0.5
STYLE_SUFFIX = re.compile(r"[-,]?(Bold|Italic|Oblique|BoldItalic|BoldOblique|Regular|MT|PSMT|PS)+$")


def _run(*cmd: str) -> str:
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def page_size_pt(pdf: Path) -> tuple[float, float]:
    m = re.search(r"Page size:\s+([\d.]+) x ([\d.]+) pts", _run("pdfinfo", str(pdf)))
    return float(m.group(1)), float(m.group(2))


def fonts(pdf: Path) -> list[dict]:
    rows = _run("pdffonts", str(pdf)).splitlines()[2:]
    out = []
    for r in rows:
        parts = r.split()
        # name type... encoding emb sub uni objnum gen: emb/sub/uni are the 5th-3rd fields from the end
        out.append({"name": parts[0], "emb": parts[-5] == "yes"})
    return out


def family(name: str) -> str:
    name = name.split("+", 1)[-1]
    while True:
        new = STYLE_SUFFIX.sub("", name)
        if new == name:
            return name
        name = new


def n_images(pdf: Path) -> int:
    return max(0, len(_run("pdfimages", "-list", str(pdf)).splitlines()) - 2)


def axes_rects(pdf: Path, page_w: float, page_h: float) -> list[tuple[float, float, float, float]]:
    """Distinct clip rectangles (x0, y0, x1, y1; PDF points, origin bottom-left) smaller than the page."""
    raw = pdf.read_bytes()
    rects = set()
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", raw, re.DOTALL):
        try:
            s = zlib.decompress(m.group(1)).decode("latin1")
        except zlib.error:
            s = m.group(1).decode("latin1")
        for x, y, w, h in re.findall(r"(-?[\d.]+) (-?[\d.]+) (-?[\d.]+) (-?[\d.]+) re\s+W\s+n", s):
            x, y, w, h = map(float, (x, y, w, h))
            if w * h < 0.9 * page_w * page_h:
                rects.add((round(x, 2), round(y, 2), round(x + w, 2), round(y + h, 2)))
    return sorted(rects)


def words(pdf: Path) -> tuple[list[dict], float]:
    """Words with boxes in PDF points (origin bottom-left)."""
    xml = _run("pdftotext", "-bbox", "-f", "1", "-l", "1", str(pdf), "-")
    xml = re.sub(r"<!DOCTYPE[^>]*>", "", xml)
    xml = re.sub(r'\sxmlns="[^"]*"', "", xml, count=1)
    root = ElementTree.fromstring(xml)
    page = root.find(".//page")
    h = float(page.get("height"))
    out = []
    for w in page.iter("word"):
        x0, y0, x1, y1 = (float(w.get(k)) for k in ("xMin", "yMin", "xMax", "yMax"))
        out.append({"text": w.text or "", "x0": x0, "y0": h - y1, "x1": x1, "y1": h - y0})
    return out, h


def check(pdf: Path, width_mm: float | None = None) -> dict:
    pdf = Path(pdf)
    w_pt, h_pt = page_size_pt(pdf)
    w_mm = w_pt * MM_PER_PT
    fts = fonts(pdf)
    fams = sorted({family(f["name"]) for f in fts})
    rects = axes_rects(pdf, w_pt, h_pt)
    ws, _ = words(pdf)
    inside = []
    for wd in ws:
        cx, cy = (wd["x0"] + wd["x1"]) / 2, (wd["y0"] + wd["y1"]) / 2
        for x0, y0, x1, y1 in rects:
            if x0 + SHRINK_PT < cx < x1 - SHRINK_PT and y0 + SHRINK_PT < cy < y1 - SHRINK_PT:
                inside.append({"text": wd["text"], "centre_pt": [round(cx, 1), round(cy, 1)], "axes": [x0, y0, x1, y1]})
    targets = (width_mm,) if width_mm else MDPI_WIDTHS_MM
    imgs = n_images(pdf)
    checks = {
        "vector": {"ok": imgs == 0, "raster_images": imgs},
        "fonts": {"ok": bool(fts) and all(f["emb"] for f in fts), "fonts": [f["name"] for f in fts],
                  "not_embedded": [f["name"] for f in fts if not f["emb"]]},
        "one_family": {"ok": len(fams) == 1, "families": fams},
        "width": {"ok": any(abs(w_mm - t) <= WIDTH_TOL_MM for t in targets), "width_mm": round(w_mm, 2),
                  "height_mm": round(h_pt * MM_PER_PT, 2), "allowed_mm": list(targets)},
        "no_text_in_axes": {"ok": bool(rects) and not inside, "n_axes": len(rects), "n_words": len(ws),
                            "violations": inside},
    }
    return {"pdf": str(pdf), "ok": all(c["ok"] for c in checks.values()), "checks": checks}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pdf", nargs="+", type=Path)
    ap.add_argument("--width-mm", type=float, default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    reports = [check(p, a.width_mm) for p in a.pdf]
    if a.json:
        print(json.dumps(reports, indent=1))
    else:
        for r in reports:
            print(f"{'PASS' if r['ok'] else 'FAIL'}  {r['pdf']}")
            for name, c in r["checks"].items():
                detail = {k: v for k, v in c.items() if k != "ok"}
                print(f"  {'ok  ' if c['ok'] else 'FAIL'} {name:16s} {json.dumps(detail)}")
    return 0 if all(r["ok"] for r in reports) else 1


if __name__ == "__main__":
    sys.exit(main())

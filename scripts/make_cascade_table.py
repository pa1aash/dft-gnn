"""Write paper/tables/filter_cascade.tex (booktabs tabular, no float or caption) from
results/filter_cascade.json. Columns: Step | Criterion | Sites | Hosts | Formulas."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "results" / "filter_cascade.json"
OUT = ROOT / "paper" / "tables" / "filter_cascade.tex"
STEP_NAMES = {"release": "Release", "ml_subset": "ML subset", "final": "Final"}
FORMULA = re.compile(r"\b(?:[A-Z][a-z]?\d*){2,}\b")


def latex(text: str) -> str:
    text = text.replace("\\", r"\textbackslash{}")
    for ch in "&%$#_{}":
        text = text.replace(ch, "\\" + ch)
    text = re.sub(r"\b(\w+(?:\\_)?\w*\.csv)\b", lambda m: r"\texttt{" + m.group(1) + "}", text)
    return FORMULA.sub(lambda m: re.sub(r"(\d+)", r"$_{\1}$", m.group(0))
                       if re.search(r"\d", m.group(0)) else m.group(0), text)


def main() -> None:
    steps = json.loads(SRC.read_text())["payload"]["steps"]
    lines = [r"\begin{tabular}{llrrr}", r"\toprule",
             r"Step & Criterion & Sites & Hosts & Formulas \\", r"\midrule"]
    for s in steps:
        if s["step"] == "final":
            lines.append(r"\midrule")
        name = STEP_NAMES.get(s["step"], s["step"])
        lines.append(f"{name} & {latex(s['criterion'])} & {s['sites']} & {s['hosts']} & "
                     f"{s['formulas']} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", ""]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()

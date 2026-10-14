"""Check the figure captions of the article and the Supplementary Materials (docs/caption_trim.md).

A caption describes its figure only: what is plotted (sentence 1), how to read it (sentence 2) and, optionally,
where the data come from (sentence 3). This script parses every printed figure caption, that is every \\caption{...}
inside a figure environment of paper/sections/*.tex and paper/si/sections/*.tex, and fails on

- more than 3 sentences, or more than 70 words (85 for the labels in LONG_CAPTIONS, which carry several
  networks, extensions or reference lines and are printed in every run of the check);
- an interpretation or comparison phrase (FORBIDDEN);
- a semicolon, or a colon outside a leading provenance label ("Data:", "Source:", ...), the two ways of chaining
  several sentences into one;
- a typed number, by the rule of paper/tools/check_macros.py.

A sentence ends at ". ", "? " or "! " followed by an uppercase letter or a LaTeX command, optionally after an
opening parenthesis, so "(\\textbf{b})" after a full stop starts a sentence. Decimals, macros, "Fig.", "e.g.",
"i.e.", "vs." and "et al." do not end one. A word is a whitespace-separated token with a letter or digit once
labels are dropped, each inline formula and each \\texttt{...} counts as one token and command names are removed.

The caption files beside the figures (figures/*/*.caption.md, schematics/*.caption.md) are written by the figure
code and are not printed; --figure-files reports their counts without failing on them.

Usage: python scripts/check_captions.py [--root DIR] [--figure-files] [--json]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ("paper/sections", "paper/si/sections")
FIGURE_FILES = ("figures/main", "figures/si", "schematics")
MAX_SENTENCES = 3
MAX_WORDS = 70
LONG_CAPTIONS = ("fig:learning_curves", "fig:screening", "fig:sens", "fig:probe")
MAX_WORDS_LONG = 85
FORBIDDEN = ("shows that", "show that", "showing that", "indicates", "indicate", "indicating",
             "consistent with", "suggests", "suggest", "suggesting", "demonstrates", "demonstrate", "reveals",
             "reveal", "confirms", "confirm", "implies", "imply", "means that", "better", "worse",
             "outperform", "superior", "inferior")
PROVENANCE = ("Data", "Source", "Sources", "Values", "Record", "Records")
ABBREVIATIONS = ("Fig.", "Figs.", "e.g.", "i.e.", "vs.", "et al.")
SENTENCE_END = re.compile(r"(?<=[.?!])\s+(?=[(`'\"]?[A-Z\\])")


def load_typed_rule(root: Path):
    """prose() and the digit pattern of check_macros.py, so captions follow the paper's typed-number rule."""
    path = root / "paper" / "tools" / "check_macros.py"
    spec = importlib.util.spec_from_file_location("check_macros", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.prose, re.compile(r"(?<![A-Za-z])(?<![A-Za-z]-)[0-9]+")


def braced(text: str, start: int) -> tuple[str, int]:
    """The content of the brace group opening at text[start] and the index after its closing brace."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{" and text[i - 1] != "\\":
            depth += 1
        elif text[i] == "}" and text[i - 1] != "\\":
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
    raise ValueError(f"unbalanced braces from offset {start}")


def tex_captions(path: Path) -> list[dict]:
    """Every \\caption{...} inside a figure environment of one .tex file, with its line and label."""
    text = "\n".join(re.sub(r"(?<!\\)%.*", "", ln) for ln in path.read_text().splitlines())
    out = []
    for env in re.finditer(r"\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}", text, re.DOTALL):
        body_start = env.start(1)
        for m in re.finditer(r"\\caption\{", env.group(1)):
            content, _ = braced(text, body_start + m.end() - 1)
            label = re.search(r"\\label\{([^}]*)\}", env.group(1))
            out.append({"source": path, "line": text.count("\n", 0, body_start + m.start()) + 1,
                        "label": label.group(1) if label else "", "text": content})
    return out


def md_caption(path: Path) -> dict:
    text = path.read_text()
    text = re.sub(r"^\*\*Figure [^*]*\*\*\s*", "", text.strip())
    return {"source": path, "line": 1, "label": path.name, "text": text}


def plain(text: str) -> str:
    """Caption text with labels dropped and formulas, paths and references reduced to single tokens."""
    s = re.sub(r"\\label\{[^}]*\}", "", text)
    s = re.sub(r"\\texttt\{[^{}]*\}", "PATH", s)
    s = re.sub(r"`[^`]*`", "PATH", s)
    s = re.sub(r"\$[^$]*\$", "MATH", s)
    s = re.sub(r"\\(?:ref|eqref|cite[pt]?)\{[^}]*\}", "REF", s)
    s = s.replace("~", " ").replace("\\ ", " ")
    return re.sub(r"\s+", " ", s).strip()


def sentences(text: str) -> list[str]:
    s = plain(text)
    for i, abbr in enumerate(ABBREVIATIONS):
        s = s.replace(abbr, f"ABBR{i}ABBR")
    parts = [p for p in SENTENCE_END.split(s) if p.strip()]
    for i, abbr in enumerate(ABBREVIATIONS):
        parts = [p.replace(f"ABBR{i}ABBR", abbr) for p in parts]
    return parts


def words(text: str) -> int:
    s = plain(text)
    s = re.sub(r"\\(?:textbf|textit|emph|mathrm)\{([^{}]*)\}", r"\1", s)  # formatting: keep the argument
    s = re.sub(r"\\[A-Za-z]+\*?(?:\{\})?", "W", s)  # any other command (\numX{}, \AA{}) is a word
    s = re.sub(r"[{}]", "", s)
    return sum(1 for t in s.split() if re.search(r"[A-Za-z0-9]", t))


def max_words(label: str) -> int:
    return MAX_WORDS_LONG if label in LONG_CAPTIONS else MAX_WORDS


def problems(cap: dict, typed_rule) -> list[str]:
    prose, digit = typed_rule
    text, out = cap["text"], []
    sents = sentences(text)
    n_words = words(text)
    if len(sents) > MAX_SENTENCES:
        out.append(f"{len(sents)} sentences (max {MAX_SENTENCES})")
    if n_words > max_words(cap["label"]):
        out.append(f"{n_words} words (max {max_words(cap['label'])})")
    low = plain(text).lower()
    for phrase in FORBIDDEN:
        if re.search(rf"\b{re.escape(phrase)}\b", low):
            out.append(f"forbidden phrase '{phrase}'")
    if ";" in plain(text):
        out.append("semicolon")
    for sent in sents:
        body = re.sub(rf"^(?:{'|'.join(PROVENANCE)}):", "", sent.strip())
        if ":" in re.sub(r"PATH|MATH", "", body):
            out.append(f"colon in '{sent[:40]}...'")
    flat = " ".join(text.splitlines())
    for _, line in prose(flat):
        for m in digit.finditer(line):
            out.append(f"typed number '{m.group()}'")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this checkout)")
    ap.add_argument("--figure-files", action="store_true",
                    help="also report the caption files beside the figures (never fails on them)")
    ap.add_argument("--json", action="store_true", help="print one JSON record per caption")
    a = ap.parse_args(argv)
    root = a.root.resolve()
    typed_rule = load_typed_rule(root)

    caps = [c for d in SOURCES for f in sorted((root / d).glob("*.tex")) for c in tex_captions(f)]
    extra = [md_caption(f) for d in FIGURE_FILES for f in sorted((root / d).glob("*.caption.md"))] \
        if a.figure_files else []
    failures = 0
    records = []
    for cap in caps + extra:
        enforced = cap in caps
        found = problems(cap, typed_rule)
        rec = {"source": str(cap["source"].relative_to(root)), "line": cap["line"], "label": cap["label"],
               "sentences": len(sentences(cap["text"])), "words": words(cap["text"]),
               "max_words": max_words(cap["label"]), "enforced": enforced, "problems": found}
        records.append(rec)
        if enforced and found:
            failures += 1
        if a.json:
            continue
        status = ("FAIL" if found else "ok") if enforced else "info"
        cap_note = f"/{max_words(cap['label'])}" if enforced else ""
        print(f"{status:4} {rec['source']}:{rec['line']} {rec['label']}: {rec['sentences']} sentences, "
              f"{rec['words']}{cap_note} words" + (f" ({'; '.join(found)})" if found else ""))
    if a.json:
        print(json.dumps(records, indent=1))
    print(f"check_captions: word cap {MAX_WORDS}, {MAX_WORDS_LONG} for the allowlist {', '.join(LONG_CAPTIONS)}",
          file=sys.stderr)
    print(f"check_captions: {len(caps)} printed figure captions, {failures} failures", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

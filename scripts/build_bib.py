"""Build paper/refs.bib from the identifier list in paper/bib_ids.txt.

BibTeX is obtained only from doi.org content negotiation
(Accept: application/x-bibtex) or the arXiv BibTeX export. Record text is
kept as served; only the citation key is rewritten to AuthorYYYYfirstword
(first author surname, year, first title word that is not a/an/the), with a
letter suffix on collision. Each record is preceded by a "% source:" comment.

Usage: python scripts/build_bib.py [--ids paper/bib_ids.txt] [--out paper/refs.bib]
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

UA = "dft-gnn-bib/0.1"
SKIP_WORDS = {"a", "an", "the"}


def http_get(url: str, accept: str | None = None, tries: int = 3) -> str:
    headers = {"User-Agent": UA}
    if accept:
        headers["Accept"] = accept
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"GET {url} failed: {last}")


def fetch(ident: str) -> tuple[str, str]:
    """Return (bibtex, source_url) for 'doi:...' or 'arxiv:...'."""
    kind, _, val = ident.partition(":")
    if kind == "doi":
        url = f"https://doi.org/{val}"
        return http_get(url, accept="application/x-bibtex"), url
    if kind == "arxiv":
        url = f"https://arxiv.org/bibtex/{val}"
        return http_get(url), url
    raise ValueError(f"unknown identifier type: {ident}")


def ascii_fold(s: str) -> str:
    s = re.sub(r"\\[`'^\"~=.uvHcdbtk]\{?([A-Za-z])\}?", r"\1", s)  # LaTeX accents
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if c.isascii())


def field(bib: str, name: str) -> str | None:
    m = re.search(rf"\b{name}\s*=\s*", bib, flags=re.IGNORECASE)
    if not m:
        return None
    i = m.end()
    if bib[i] == "{":
        depth, j = 0, i
        while j < len(bib):
            if bib[j] == "{":
                depth += 1
            elif bib[j] == "}":
                depth -= 1
                if depth == 0:
                    return bib[i + 1 : j]
            j += 1
        return None
    if bib[i] == '"':
        j = bib.index('"', i + 1)
        return bib[i + 1 : j]
    m2 = re.match(r"[^,}\s]+", bib[i:])
    return m2.group(0) if m2 else None


def make_key(bib: str) -> str:
    author = field(bib, "author") or "Anon"
    first = author.split(" and ")[0].strip()
    surname = first.split(",")[0] if "," in first else first.split()[-1]
    surname = re.sub(r"[^A-Za-z]", "", ascii_fold(surname)) or "Anon"
    year = re.sub(r"\D", "", field(bib, "year") or "") or "nd"
    title = ascii_fold(field(bib, "title") or "untitled")
    words = [re.sub(r"[^A-Za-z0-9]", "", w) for w in title.split()]
    words = [w for w in words if w]
    word = next((w for w in words if w.lower() not in SKIP_WORDS), "untitled")
    return f"{surname[0].upper()}{surname[1:]}{year}{word.lower()}"


def set_key(bib: str, key: str) -> str:
    return re.sub(r"^\s*@(\w+)\s*\{\s*[^,]*,", rf"@\1{{{key},", bib.strip(), count=1)


def norm_doi(bib: str) -> str | None:
    d = field(bib, "doi")
    return d.strip().lower() if d else None


def parse_existing(path: Path) -> list[str]:
    """Split an existing .bib into records (each starting with @)."""
    if not path.exists():
        return []
    text = path.read_text()
    return [("@" + p).strip() for p in re.split(r"^\s*@", text, flags=re.M)[1:]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="paper/bib_ids.txt")
    ap.add_argument("--merge", default="paper/refs-fetched.bib")
    ap.add_argument("--out", default="paper/refs.bib")
    a = ap.parse_args()

    today = dt.date.today().isoformat()
    ids = []
    for line in Path(a.ids).read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            ids.append(line)

    records: list[tuple[str, str]] = []  # (source comment, bib)
    failures = []
    for ident in ids:
        try:
            bib, url = fetch(ident)
        except Exception as e:  # noqa: BLE001
            failures.append(f"{ident}: {e}")
            continue
        if not bib.lstrip().startswith("@"):
            failures.append(f"{ident}: response is not BibTeX")
            continue
        method = "doi.org content negotiation" if ident.startswith("doi:") else "arXiv BibTeX export"
        records.append((f"% source: {url} ({method}, fetched {today})", bib))
        time.sleep(0.5)

    # fold in previously fetched records not already covered
    seen = {norm_doi(b) for _, b in records if norm_doi(b)}
    for bib in parse_existing(Path(a.merge)):
        d = norm_doi(bib)
        if d and d in seen:
            continue
        src = f"https://doi.org/{d}" if d else a.merge
        records.append((f"% source: {src} (doi.org content negotiation, folded in from {a.merge})", bib))
        if d:
            seen.add(d)

    # dedupe by DOI, then by arXiv eprint
    out, used, seen_doi, seen_eprint = [], set(), set(), set()
    for src, bib in records:
        d, e = norm_doi(bib), (field(bib, "eprint") or "").strip().lower() or None
        if (d and d in seen_doi) or (e and e in seen_eprint):
            continue
        if d:
            seen_doi.add(d)
        if e:
            seen_eprint.add(e)
        key = base = make_key(bib)
        n = 0
        while key in used:
            n += 1
            key = base + "abcdefghijklmnopqrstuvwxyz"[n]
        used.add(key)
        out.append(f"{src}\n{set_key(bib, key)}\n")

    Path(a.out).write_text("\n".join(out))
    print(f"wrote {len(out)} records to {a.out}")
    for f in failures:
        print("FAILED", f, file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

"""Re-resolve every DOI and arXiv identifier in a .bib file.

DOIs are checked against the doi.org handle API (responseCode 1 means the
handle exists); arXiv identifiers against the arXiv query API. Records with
neither identifier are reported as unverifiable. Exits non-zero if any
identifier fails to resolve or any record lacks an identifier.

Usage: python scripts/verify_bib.py [paper/refs.bib]
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = "dft-gnn-bib/0.1"
ARXIV_RE = re.compile(r"(\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})(v\d+)?", re.I)


def get(url: str, tries: int = 3) -> bytes:
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return e.read()
            last = e
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
        time.sleep(3 * (i + 1))
    raise RuntimeError(str(last))


def doi_ok(doi: str) -> bool:
    body = get("https://doi.org/api/handles/" + urllib.parse.quote(doi, safe="/"))
    return json.loads(body).get("responseCode") == 1


def arxiv_ok(aid: str) -> bool:
    body = get(f"https://export.arxiv.org/api/query?id_list={aid}").decode()
    entries = re.findall(r"<entry>(.*?)</entry>", body, flags=re.S)
    return any("<title>Error</title>" not in e and "<id>" in e for e in entries)


def records(text: str) -> list[str]:
    return [("@" + p) for p in re.split(r"^\s*@", text, flags=re.M)[1:]]


def fieldval(rec: str, name: str) -> str | None:
    m = re.search(rf"\b{name}\s*=\s*[{{\"]([^}}\"]+)[}}\"]", rec, flags=re.I)
    return m.group(1).strip() if m else None


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "paper/refs.bib")
    recs = records(path.read_text())
    fails, n_ok = [], 0
    for rec in recs:
        key = re.match(r"@\w+\s*\{\s*([^,]+),", rec).group(1)
        doi = fieldval(rec, "doi")
        aid = None
        if (fieldval(rec, "archivePrefix") or "").lower() == "arxiv" or fieldval(rec, "eprint"):
            m = ARXIV_RE.search(fieldval(rec, "eprint") or "")
            aid = m.group(1) if m else None
        if not aid:
            m = re.search(r"arxiv\.org/abs/([^\s}\"]+)", rec, flags=re.I)
            aid = m.group(1) if m else None
        checks = []
        if doi:
            checks.append(("doi", doi, doi_ok))
        if aid:
            checks.append(("arxiv", aid, arxiv_ok))
        if not checks:
            fails.append(f"{key}: no DOI or arXiv identifier")
            continue
        for kind, ident, fn in checks:
            try:
                ok = fn(ident)
            except Exception as e:  # noqa: BLE001
                ok, ident = False, f"{ident} ({e})"
            if ok:
                n_ok += 1
                print(f"OK    {key:40s} {kind}:{ident}")
            else:
                fails.append(f"{key}: {kind}:{ident} did not resolve")
            time.sleep(0.4)
    for f in fails:
        print("FAIL  " + f)
    print(f"{len(recs)} records, {n_ok} identifiers resolved, {len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

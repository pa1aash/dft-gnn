"""Hash every file proposed for the Zenodo archive and write deposit/FILES.sha256.

Read-only apart from the output file: it lists, sizes and hashes files, checks each hash against the record
that already exists for it, and scans each file for the project's banned strings. It never edits, moves or
uploads anything.

Components
- deposit: the files under deposit/ (uploaded at the top level of the record; also inside the snapshot)
- code: every other tracked file at HEAD (the members of the code snapshot; provisional until the final tag)
- bundle: the assets of the GitHub release inputs-v1, checked against INPUTS_MANIFEST.txt
- inputs, checkpoints, mace: the members of the three bundles, hashed from the local data root and checked
  against nrp_<bundle>.sha256
- snapshot: the code snapshot zip of the final tag, when --snapshot is given (at the results freeze)

Usage (from the repository root):
    nice -n 15 python deposit/make_files_manifest.py --data-root ../dft-gnn
"""

from __future__ import annotations

import argparse
import codecs
import hashlib
import re
import subprocess
import sys
from pathlib import Path

OUT_NAME = "deposit/FILES.sha256"
CHUNK = 1 << 20
# the banned strings, stored rot13-encoded so that this file does not itself contain them
_BANNED_ROT13 = ("pynhqr", "naguebcvp", "pb-nhguberq-ol")
BANNED = re.compile(
    "|".join(re.escape(codecs.decode(w, "rot13")) for w in _BANNED_ROT13).encode(), re.IGNORECASE
)
OVERLAP = max(len(codecs.decode(w, "rot13")) for w in _BANNED_ROT13) - 1
BUNDLES = ("inputs", "checkpoints", "mace")


def hash_and_scan(path: Path) -> tuple[str, int, bool]:
    """Return (sha256, size, banned_hit) in one pass over the file."""
    h = hashlib.sha256()
    size = 0
    hit = False
    tail = b""
    with path.open("rb") as fh:
        while chunk := fh.read(CHUNK):
            h.update(chunk)
            size += len(chunk)
            if not hit and BANNED.search(tail + chunk):
                hit = True
            tail = chunk[-OVERLAP:]
    return h.hexdigest(), size, hit


def read_member_manifest(path: Path) -> dict[str, str]:
    """`sha256  path` lines -> {path: sha256}."""
    out = {}
    for line in path.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            digest, rel = line.split(maxsplit=1)
            out[rel.strip()] = digest
    return out


def read_inputs_manifest(path: Path) -> dict[str, tuple[str, int]]:
    """INPUTS_MANIFEST.txt `sha256  name  size` lines -> {name: (sha256, size)}."""
    out = {}
    for line in path.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            digest, name, size = line.split()
            out[name] = (digest, int(size))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=Path, default=Path("."), help="repository root (default: .)")
    ap.add_argument("--data-root", type=Path, required=True,
                    help="checkout that holds the gitignored data/processed, data/raw, checkpoints and .cache")
    ap.add_argument("--bundles", type=Path, default=None,
                    help="directory with the inputs-v1 assets (default: <data-root>/.local/nrp_inputs)")
    ap.add_argument("--snapshot", type=Path, default=None,
                    help="code snapshot zip of the final tag (git archive), hashed as component 'snapshot'")
    args = ap.parse_args()
    repo = args.repo.resolve()
    data_root = args.data_root.resolve()
    bundles = (args.bundles or data_root / ".local" / "nrp_inputs").resolve()

    git = ["git", "-C", str(repo)]
    dirty = subprocess.run(git + ["status", "--porcelain", "--untracked-files=no"],
                           capture_output=True, text=True, check=True).stdout.strip()
    if dirty:
        print("refusing: tracked files differ from HEAD:\n" + dirty, file=sys.stderr)
        return 2
    head = subprocess.run(git + ["rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    tracked = subprocess.run(git + ["ls-files", "-z"], capture_output=True, text=True,
                             check=True).stdout.split("\0")
    tracked = sorted(p for p in tracked if p and p != OUT_NAME)

    rows: list[tuple[str, int, str, str]] = []
    hits: list[str] = []
    problems: list[str] = []

    def add(component: str, label: str, path: Path, expect: str | None = None, expect_size: int | None = None):
        if not path.is_file():
            problems.append(f"missing: {component} {label}")
            return
        digest, size, hit = hash_and_scan(path)
        if expect is not None and digest != expect:
            problems.append(f"sha256 mismatch: {component} {label}")
        if expect_size is not None and size != expect_size:
            problems.append(f"size mismatch: {component} {label}")
        if hit:
            hits.append(f"{component} {label}")
        rows.append((digest, size, component, label))

    for rel in tracked:
        add("deposit" if rel.startswith("deposit/") else "code", rel, repo / rel)

    assets = read_inputs_manifest(bundles / "INPUTS_MANIFEST.txt")
    add("bundle", "INPUTS_MANIFEST.txt", bundles / "INPUTS_MANIFEST.txt")
    for name, (digest, size) in sorted(assets.items()):
        add("bundle", name, bundles / name, digest, size)

    if args.snapshot is not None:
        add("snapshot", args.snapshot.name, args.snapshot.resolve())

    for b in BUNDLES:
        for rel, digest in sorted(read_member_manifest(bundles / f"nrp_{b}.sha256").items()):
            add(b, rel, data_root / rel, digest)

    totals: dict[str, list[int]] = {}
    for _, size, comp, _ in rows:
        t = totals.setdefault(comp, [0, 0])
        t[0] += 1
        t[1] += size

    out = repo / OUT_NAME
    with out.open("w") as fh:
        fh.write("# FILES.sha256: every file proposed for the Zenodo archive, written by deposit/make_files_manifest.py\n")
        fh.write(f"# repository HEAD when hashed: {head} (the code rows are provisional until the final tag)\n")
        fh.write("# this file is not listed in itself\n")
        fh.write("# components: deposit = top-level record files; code = members of the code snapshot;\n")
        fh.write("#   bundle = assets of release inputs-v1; inputs, checkpoints, mace = members of those bundles;\n")
        fh.write("#   snapshot = code snapshot zip of the final tag (absent until the results freeze)\n")
        for comp, (n, size) in totals.items():
            fh.write(f"# total {comp}: {n} files, {size} bytes\n")
        fh.write(f"# record checks (hash and size against existing manifests): {len(problems)} problems\n")
        for p in problems:
            fh.write(f"#   {p}\n")
        fh.write(f"# banned-string scan (case-insensitive, every byte of every file): {len(hits)} files\n")
        for p in hits:
            fh.write(f"#   {p}\n")
        fh.write("# columns (tab separated): sha256, size_bytes, component, path\n")
        for digest, size, comp, label in rows:
            fh.write(f"{digest}\t{size}\t{comp}\t{label}\n")

    for comp, (n, size) in totals.items():
        print(f"{comp}: {n} files, {size} bytes")
    print(f"record problems: {len(problems)}")
    for p in problems:
        print(f"  {p}")
    print(f"banned-string hits: {len(hits)}")
    for p in hits:
        print(f"  {p}")
    print(f"wrote {out}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

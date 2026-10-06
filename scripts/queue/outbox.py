"""Pack finished runs into outbox/<name>.tar.gz for rsync back to the Mac (no git needed).

    python scripts/queue/outbox.py pack [--stage smoke]
    python scripts/queue/outbox.py unpack outbox/<name>.tar.gz

The tarball holds, for every done job: its result JSON, its predictions parquet, its checkpoint and
the done/ job record, at their repo-relative paths, plus OUTBOX_MANIFEST.sha256 listing every member.
``pack`` also writes ``<name>.tar.gz.sha256`` next to the tarball. ``unpack`` checks the tarball
hash, extracts into the repo root (results/ and the gitignored checkpoints/) and re-verifies every
member against the inner manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import tarfile
import time
from pathlib import Path

from _common import OUTBOX, QUEUE, ROOT

MANIFEST = "OUTBOX_MANIFEST.sha256"


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def members(queue: Path, stage: str | None) -> list[Path]:
    out = []
    for f in sorted((queue / "done").glob("*.json")):
        job = json.loads(f.read_text())
        if stage and job.get("stage") != stage:
            continue
        res = Path(job["result"])
        pay = json.loads(res.read_text())["payload"]
        out += [res, ROOT / pay["predictions"]["path"], f]
        if pay.get("checkpoint"):
            out.append(ROOT / pay["checkpoint"]["path"])
    return out


def pack(queue: Path, outbox: Path, stage: str | None) -> Path:
    files = members(queue, stage)
    if not files:
        raise SystemExit("no done jobs to pack")
    outbox.mkdir(parents=True, exist_ok=True)
    name = f"outbox_{stage or 'all'}_{time.strftime('%Y%m%dT%H%M%S')}.tar.gz"
    tar_path = outbox / name
    rel = [f.resolve().relative_to(ROOT) for f in files]
    manifest = "".join(f"{_sha(ROOT / r)}  {r}\n" for r in rel).encode()
    with tarfile.open(tar_path, "w:gz") as tar:
        for r in rel:
            tar.add(ROOT / r, arcname=str(r))
        info = tarfile.TarInfo(MANIFEST)
        info.size = len(manifest)
        tar.addfile(info, io.BytesIO(manifest))
    tar_path.with_name(name + ".sha256").write_text(f"{_sha(tar_path)}  {name}\n")
    print(f"{tar_path} ({len(rel)} files)")
    return tar_path


def unpack(tar_path: Path, dest: Path = ROOT) -> int:
    side = tar_path.with_name(tar_path.name + ".sha256")
    if side.exists() and side.read_text().split()[0] != _sha(tar_path):
        raise SystemExit(f"tarball hash mismatch: {tar_path}")
    with tarfile.open(tar_path, "r:gz") as tar:
        names = tar.getnames()
        for n in names:
            if n.startswith("/") or ".." in Path(n).parts:
                raise SystemExit(f"unsafe member path {n}")
        manifest = tar.extractfile(MANIFEST).read().decode()
        tar.extractall(dest, members=[m for m in tar.getmembers() if m.name != MANIFEST], filter="data")
    bad = [r for sha, r in (ln.split("  ", 1) for ln in manifest.splitlines()) if _sha(dest / r) != sha]
    if bad:
        raise SystemExit(f"hash mismatch after unpack: {bad}")
    n = len(manifest.splitlines())
    print(f"unpacked and verified {n} files into {dest}")
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pack")
    p.add_argument("--stage")
    p.add_argument("--queue", default=str(QUEUE))
    p.add_argument("--outbox", default=str(OUTBOX))
    u = sub.add_parser("unpack")
    u.add_argument("tarball")
    a = ap.parse_args()
    if a.cmd == "pack":
        pack(Path(a.queue), Path(a.outbox), a.stage)
    else:
        unpack(Path(a.tarball))


if __name__ == "__main__":
    main()

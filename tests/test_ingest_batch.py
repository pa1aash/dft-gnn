"""scripts/nrp/ingest_batch.sh on a synthetic repository: a clean results branch passes; a wrong artefact hash, a
foreign identity, a banned word or a code change fails; nothing is merged. The hook here uses a dummy pattern."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
P = ("Palaash Gang", "palaashgang@gmail.com")
A = ("aidenlee", "aiden.lee.sd@gmail.com")
RID = "0123456789abcdef"
HOOK = """#!/bin/sh
PAT='forbiddenword'
rng="$1"
if git log --format='%an%n%ae%n%cn%n%ce%n%B' $rng | grep -Eiq "$PAT"; then exit 1; fi
bad=$(git log --format='%h|%an|%ae|%cn|%ce' $rng | awk -F'|' '
  function ok(n, e) { return (n=="Palaash Gang" && e=="palaashgang@gmail.com") || (n=="aidenlee" && e=="aiden.lee.sd@gmail.com") }
  !ok($2,$3) || !ok($4,$5)')
[ -z "$bad" ] || exit 1
exit 0
"""
pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git missing")


def git(repo: Path, *args: str, who=P) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": who[0], "GIT_AUTHOR_EMAIL": who[1], "GIT_COMMITTER_NAME": who[0],
           "GIT_COMMITTER_EMAIL": who[1]}
    return subprocess.run(["git", "-c", "core.hooksPath=/dev/null", *args], cwd=repo, env=env, check=True,
                          capture_output=True, text=True).stdout


def make_repo(tmp: Path) -> Path:
    repo = tmp / "repo"
    (repo / "scripts" / "nrp").mkdir(parents=True)
    (repo / "specs").mkdir()
    (repo / "src").mkdir()
    shutil.copy(ROOT / "scripts" / "nrp" / "ingest_batch.sh", repo / "scripts" / "nrp" / "ingest_batch.sh")
    (repo / "src" / "a.py").write_text("x = 1\n")
    (repo / "specs" / "cv.jsonl").write_text(json.dumps({"run_id": RID, "stage": "cv"}) + "\n")
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "base")
    git(repo, "tag", "-a", "nrp-code-v1", "-m", "pin")
    hooks = repo / ".git" / "hooks"
    hooks.mkdir(exist_ok=True)
    (hooks / "_audit.sh").write_text(HOOK)
    (hooks / "_audit.sh").chmod(0o755)
    git(repo, "checkout", "-qb", "nrp/cv")
    return repo


def add_result(repo: Path, pred: bytes = b"PARQUET", recorded: str | None = None, extra: str = "") -> None:
    d = repo / "results" / "cv"
    (d / "predictions").mkdir(parents=True, exist_ok=True)
    (d / "predictions" / f"{RID}.parquet").write_bytes(pred)
    pay = {"run_id": RID, "code_ref": "nrp-code-v1", "spec": {"code_ref": "nrp-code-v1"}, "note": extra,
           "predictions": {"path": f"results/cv/predictions/{RID}.parquet",
                           "sha256": recorded or hashlib.sha256(pred).hexdigest()}, "checkpoint": None}
    (d / f"{RID}.json").write_text(json.dumps({"payload": pay}))


def run(repo: Path) -> subprocess.CompletedProcess:
    git(repo, "update-ref", "refs/remotes/origin/nrp/cv", "HEAD")
    return subprocess.run(["bash", "scripts/nrp/ingest_batch.sh", "nrp/cv", "--no-fetch"], cwd=repo,
                          capture_output=True, text=True, check=False)


def test_clean_branch_passes_and_merges_nothing(tmp_path):
    repo = make_repo(tmp_path)
    add_result(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "results(cv): one run", who=A)
    main_before = git(repo, "rev-parse", "main")
    r = run(repo)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "cv             1 / 1" in r.stdout and "INGEST CHECK PASSED" in r.stdout
    assert git(repo, "rev-parse", "main") == main_before


@pytest.mark.parametrize("case", ["hash", "identity", "banned", "code"])
def test_failures(tmp_path, case):
    repo = make_repo(tmp_path)
    who = A
    if case == "hash":
        add_result(repo, recorded="0" * 64)
    elif case == "banned":
        add_result(repo, extra="a forbiddenword here")
    else:
        add_result(repo)
    if case == "identity":
        who = ("someone", "someone@example.org")
    if case == "code":
        (repo / "src" / "a.py").write_text("x = 2\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "results(cv)", who=who)
    r = run(repo)
    assert r.returncode == 1, r.stdout
    assert "INGEST CHECK FAILED" in r.stdout


def test_export_then_ingest_with_outbox(tmp_path):
    """Cluster side: export_stage.sh commits the tracked files to nrp/cv in a separate worktree and packs the
    outbox; Mac side: ingest_batch.sh --outbox places the gitignored checkpoint and passes every check."""
    repo = make_repo(tmp_path)
    git(repo, "checkout", "-q", "main")
    (repo / "scripts" / "queue").mkdir()
    for f in ("outbox.py", "_common.py"):
        shutil.copy(ROOT / "scripts" / "queue" / f, repo / "scripts" / "queue" / f)
    shutil.copy(ROOT / "scripts" / "nrp" / "export_stage.sh", repo / "scripts" / "nrp" / "export_stage.sh")
    (repo / ".gitignore").write_text("checkpoints/\njobs/\noutbox/\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "tools")
    git(repo, "tag", "-f", "-a", "nrp-code-v1", "-m", "pin")
    git(repo, "branch", "-D", "nrp/cv")
    # a finished cv run in the live checkout: result, predictions (tracked), checkpoint (gitignored), done record
    add_result(repo)
    (repo / "checkpoints").mkdir()
    ck = b"CHECKPOINT"
    (repo / "checkpoints" / f"{RID}.pt").write_bytes(ck)
    res = repo / "results" / "cv" / f"{RID}.json"
    rec = json.loads(res.read_text())
    rec["payload"]["checkpoint"] = {"path": f"checkpoints/{RID}.pt", "sha256": hashlib.sha256(ck).hexdigest()}
    res.write_text(json.dumps(rec))
    (repo / "jobs" / "done").mkdir(parents=True)
    (repo / "jobs" / "done" / f"{RID}.json").write_text(json.dumps({"run_id": RID, "stage": "cv", "result": str(res)}))
    git(repo, "config", "user.name", A[0])
    git(repo, "config", "user.email", A[1])
    env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null"}
    r = subprocess.run(["bash", "scripts/nrp/export_stage.sh", "cv", "--no-push"], cwd=repo, env=env,
                       capture_output=True, text=True, check=False)
    assert r.returncode == 0, r.stdout + r.stderr
    assert git(repo, "branch", "--show-current").strip() == "main"          # the live checkout did not move
    files = git(repo, "ls-tree", "-r", "--name-only", "nrp/cv", "--", "results").split()
    assert sorted(files) == sorted([f"results/cv/predictions/{RID}.parquet", f"results/cv/{RID}.json"])
    tar = next((repo / "outbox").glob("outbox_cv_*.tar.gz"))
    # the Mac: a fresh clone without the checkpoint
    mac = tmp_path / "mac"
    subprocess.run(["git", "clone", "-q", "-b", "main", str(repo), str(mac)], check=True, capture_output=True)
    git(mac, "fetch", "-q", "origin", "nrp/cv:refs/remotes/origin/nrp/cv", "--tags")
    (mac / ".git" / "hooks" / "_audit.sh").write_text(HOOK)
    (mac / ".git" / "hooks" / "_audit.sh").chmod(0o755)
    base = ["bash", "scripts/nrp/ingest_batch.sh", "nrp/cv", "--no-fetch"]
    r = subprocess.run(base, cwd=mac, capture_output=True, text=True, check=False)
    assert r.returncode == 1 and "MISSING checkpoints/" in r.stdout              # checkpoint not yet placed
    r = subprocess.run([*base, "--outbox", str(tar)], cwd=mac, capture_output=True, text=True, check=False)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (mac / "checkpoints" / f"{RID}.pt").read_bytes() == ck
    assert not (mac / "results" / "cv").exists()                                  # tracked members left to the branch

"""Write the job specs of one cluster stage (docs/nrp_runbook.md; ``dftgnn.train.nrp``).

    python scripts/queue/make_specs.py --stage cv --code-ref nrp-code-v1 --backbone v1 --out specs/cv.jsonl
    python scripts/queue/make_specs.py --stage relax --hosts-file specs/relax_hosts.txt --out specs/relax.jsonl
    python scripts/queue/make_specs.py --stage cv --check            # regenerate and compare, write nothing

Writes ``specs/<stage>.jsonl`` (one queue job per line, sorted by priority; canonical JSON) and
``specs/<stage>.manifest.json`` (counts and the sha256 of the jsonl; no time stamp). Pure: no GPU, no network.
Run ids use ``--code-ref`` in place of the commit SHA. The count must equal the expected count of the stage, run ids
must be unique, and every job must pass the test-host leakage check, or nothing is written.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _common import ROOT

from dftgnn.train import nrp


def generate(stage: str, code_ref: str, backbone: str, hosts_file: str | None, tuned: str, out: Path):
    hosts = nrp.read_hosts_file(Path(hosts_file)) if hosts_file else None
    jobs = sorted(nrp.build_stage(stage, code_ref=code_ref, backbone=backbone, hosts=hosts, tuned_path=Path(tuned)),
                  key=lambda j: j["priority"])
    ids = [j["run_id"] for j in jobs]
    if len(set(ids)) != len(ids):
        raise SystemExit(f"{stage}: {len(ids) - len(set(ids))} duplicate run ids")
    want = nrp.expected_count(stage, hosts)
    if len(jobs) != want:
        raise SystemExit(f"{stage}: {len(jobs)} jobs, expected {want}")
    for j in jobs:
        nrp.check_no_leakage(j)
    body = nrp.dumps_jsonl(jobs)
    man = nrp.manifest(stage, jobs, body, jsonl_name=out.name, code_ref=code_ref, backbone=backbone,
                       hosts_file=Path(hosts_file) if hosts_file else None, tuned_path=Path(tuned))
    return jobs, body, (json.dumps(man, indent=1, sort_keys=True) + "\n").encode()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=nrp.STAGES)
    ap.add_argument("--code-ref", default=nrp.CODE_REF)
    ap.add_argument("--backbone", default="v1", choices=nrp.BACKBONES)
    ap.add_argument("--hosts-file", help="relax / geomeval: host ids to relax (the top-up list), one per line")
    ap.add_argument("--tuned", default=str(ROOT / "configs" / "tuned_v1.yaml"))
    ap.add_argument("--out", help="default specs/<stage>.jsonl (specs/<stage>_v2.jsonl for --backbone v2)")
    ap.add_argument("--check", action="store_true", help="regenerate and compare with the files; write nothing")
    a = ap.parse_args()
    out = Path(a.out) if a.out else nrp.SPECS_DIR / f"{a.stage}{'_v2' if a.backbone == 'v2' else ''}.jsonl"
    man_path = out.with_name(out.name.removesuffix(".jsonl") + ".manifest.json")
    _jobs, body, man = generate(a.stage, a.code_ref, a.backbone, a.hosts_file, a.tuned, out)
    if a.check:
        if out.read_bytes() != body or man_path.read_bytes() != man:
            raise SystemExit(f"{out} or {man_path} differs from regeneration")
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(body)
        man_path.write_bytes(man)
    m = json.loads(man)
    print(f"{a.stage} ({m['group']}, {m['label']}, backbone {a.backbone}): {m['count']} jobs "
          f"{m['counts_by_model']}; sha256 {m['sha256']}; code_ref {a.code_ref}"
          + ("; files match" if a.check else f"; wrote {out.name} and {man_path.name}"))


if __name__ == "__main__":
    main()

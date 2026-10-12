"""Validate deposit/CITATION.cff and deposit/.zenodo.json against their published JSON schemas.

The schemas are not stored here. Fetch them headlessly at the pinned commits, then pass the directory:

    mkdir -p <dir>
    curl -sSfL -o <dir>/cff_schema.json \
      https://raw.githubusercontent.com/citation-file-format/citation-file-format/dd51afe18fe23b4daaaf923d305e3046415b2c7c/schema.json
    curl -sSfL -o <dir>/zenodo_legacyrecord.json \
      https://raw.githubusercontent.com/zenodo/zenodo/2d0bd3527dcb851613a00391d674be1d004c9459/zenodo/modules/deposit/jsonschemas/deposits/records/legacyrecord.json
    python deposit/validate_metadata.py --schemas <dir>

The Zenodo developer documentation (https://developers.zenodo.org/, GitHub section) names this legacy deposit
schema as the one a .zenodo.json file is validated against. Read-only: prints the result and writes nothing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import jsonschema
import yaml

SCHEMAS = {
    "cff_schema.json": "17bc7993c67b95eec988dadca78b65cb29cd489d1fceba71040a141dfb9791df",
    "zenodo_legacyrecord.json": "e275ddb915367510c4809db54b672fdd1fd31d133b55d9509eb2460022073562",
}


def load_schema(directory: Path, name: str) -> dict:
    raw = (directory / name).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SCHEMAS[name]:
        raise SystemExit(f"{name}: sha256 {digest} differs from the pinned {SCHEMAS[name]}")
    return json.loads(raw)


def check(label: str, instance: object, schema: dict) -> int:
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    validator = cls(schema, format_checker=cls.FORMAT_CHECKER)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    print(f"{label}: {'valid' if not errors else f'{len(errors)} errors'} ({cls.__name__})")
    for e in errors:
        print(f"  /{'/'.join(map(str, e.absolute_path))}: {e.message}")
    return len(errors)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--schemas", type=Path, required=True, help="directory holding the two fetched schemas")
    ap.add_argument("--deposit", type=Path, default=Path(__file__).resolve().parent)
    args = ap.parse_args()
    cff = yaml.safe_load((args.deposit / "CITATION.cff").read_text())
    zen = json.loads((args.deposit / ".zenodo.json").read_text())
    n = check("CITATION.cff", cff, load_schema(args.schemas, "cff_schema.json"))
    n += check(".zenodo.json", zen, load_schema(args.schemas, "zenodo_legacyrecord.json"))
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())

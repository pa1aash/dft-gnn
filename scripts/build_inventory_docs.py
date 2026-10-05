"""Flatten results/data_inventory.json into tracked CSVs under docs/."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
inv = json.loads((ROOT / "results/data_inventory.json").read_text())["payload"]
cols = [{"table": t, "rows": v["rows"], **{k: c.get(k) for k in ("column", "dtype", "nulls", "unique", "min", "max")},
         "examples": json.dumps(c["examples"]), "documented_in_readme": c["in_readme"]}
        for t, v in inv["tables"].items() for c in v["inventory"]]
pd.DataFrame(cols).to_csv(ROOT / "docs/column_inventory.csv", index=False)
sch = [{"file": f, **{k: x[k] for k in ("field", "type", "n_files", "n_files_total", "example")},
        "name_appears_in_readme_prose": x["in_readme"]} for f, v in inv["json_schemas"].items() for x in v]
pd.DataFrame(sch).to_csv(ROOT / "docs/json_schema_inventory.csv", index=False)
classes = [{"file_class": k, **v} for k, v in inv["file_classes"].items()]
pd.DataFrame(classes).to_csv(ROOT / "docs/file_class_inventory.csv", index=False)
print(len(cols), len(sch), len(classes))

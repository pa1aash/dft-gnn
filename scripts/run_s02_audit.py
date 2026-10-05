"""Run the S02 data audit end to end and write every result through write_result."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import audit_descriptor_provenance as dprov  # noqa: E402
import audit_extract  # noqa: E402
import audit_inventory  # noqa: E402
import audit_k25_split  # noqa: E402
import audit_misc  # noqa: E402
import audit_reconcile  # noqa: E402
import audit_structures  # noqa: E402
import audit_targets  # noqa: E402
import audit_zno  # noqa: E402
import pandas as pd  # noqa: E402

from dftgnn.io.results import write_result  # noqa: E402

AUD = audit_reconcile.AUD


def main() -> None:
    audit_extract.main()
    audit_structures.main()
    sa = pd.read_csv(AUD / "structure_audit.csv")
    desc = ["n_atoms_sc", "n_atoms_uc", "multiplicity", "a", "b", "c", "alpha", "beta", "gamma", "min_dist"]
    structure = {
        "pristine_tests": {c: sa[c].value_counts().to_dict() for c in (
            "n_atoms_equals_uc_times_mult", "composition_equals_uc_times_mult", "labels_cover_all_O_exactly",
            "first_equiv_matches_frac", "equiv_atoms_all_O", "equiv_counts_match_uc_times_mult")},
        "distributions": {c: {k: float(v) for k, v in sa[c].describe(percentiles=[.05, .25, .5, .75, .95]).items()}
                          for c in desc},
        "O_sites_total": int(sa.n_O_labels.sum()),
        "zno": audit_zno.main(),
        **audit_misc.main(),
    }
    write_result("structure_audit", structure)
    write_result("data_inventory", audit_inventory.main())
    write_result("universe_reconciliation", audit_reconcile.main())
    write_result("descriptor_provenance", dprov.main())
    write_result("k25_split", audit_k25_split.main())
    write_result("target_sanity", audit_targets.main())


if __name__ == "__main__":
    main()

# N4 staging swap-in on the final network (session I1, 2026-10-19)

Record: `results/swapin/swapin_v2.json` (cluster, CPU, code `nrp-code-v4`, final network `configs/tuned_v2.yaml`).
The check: the staged model P (P1 then D) is run with the true DFT descriptors put in place of P1's predicted ones,
and compared with D on the same test sites. If the staging pipeline passes descriptors to D correctly, the two
predictions must be identical.

**Scope versus the rule.** The rule (`docs/deviations.md`, row of 2026-10-14, item g) asks for 3 drawn cells per
backbone with a tolerance of 1e-5 eV. The cluster record covers every P/D pair of the final network instead: 183
pairs. These are the 180 outer cells (resamples 0-9, seeds 0-2, budgets 25, 50, 100, 200, 400 and 654) and the 3
Kiyohara-split cells at 571 training hosts. The 3 cells of the rule are among them.

## Pairs and per-budget maximum difference

| Training hosts | Pairs | Max abs difference, staged-with-true-descriptors minus D (eV) |
|---|---|---|
| 25 | 30 | 0.0 |
| 50 | 30 | 0.0 |
| 100 | 30 | 0.0 |
| 200 | 30 | 0.0 |
| 400 | 30 | 0.0 |
| 571 (Kiyohara split) | 3 | 0.0 |
| 654 | 30 | 0.0 |
| all | 183 | 0.0 (0 missing pairs) |

Every pair also records its P1 and D checkpoints with sha256 and the run ids, and these match the records on main.
Test sites per pair range from 272 (Kiyohara) to 359.

## Rescaling finding

StagedP maps P1's output from P1's descriptor standardisation into D's through an affine map (scale, shift). In all
183 pairs that map is the identity: the largest |scale - 1| is 0.0 and the largest |shift| is 0.0
(`rescaling.n_identity` 183, `n_not_identity` 0). P1 and D of the final network therefore standardise the 22
descriptors identically. The true descriptors reach D unchanged, and the difference is exactly zero, not merely
below 1e-5 eV. The v1 check (`results/staging_swapin_check.json`, 3 of 3 cells passed, max deviation 0.0) gave the
same answer.

Identical standardisation makes this a plumbing check of the staged pipeline, not a test of whether staging can win.

## Status

The v2 "not run" entry of `results/staging_swapin_check.json` is now covered by this record. The staging conclusion
(P - S per budget, `results/staging_v2.json`) is unchanged by the check: it only confirms that P's error comes from
P1's predicted descriptors and not from the way they are handed to D.

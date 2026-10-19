# N4 ingest: moment_v2 and swapin (session I1, 2026-10-19)

Two cluster branches from the N4 job were ingested into main with `--no-ff` merges:

| Branch | Tip | Commits | Added files | Merge commit on main |
|---|---|---|---|---|
| `nrp/moment_v2` | 4b93f3f | 28 | 60 records, 60 prediction parquets, `results/nrp/artefacts/moment_v2.sha256` | e2356ae |
| `nrp/swapin` | d5e1ffb | 1 | `results/swapin/swapin_v2.json` | fac4bd4 |

Both branches start at `nrp-code-v1` (merge base ffd86ce) and only add files under `results/`. After the merges
`git diff --stat nrp-code-v4 -- src scripts configs splits specs` is empty, and
`git diff --name-status results-v1 -- results` shows only added files (130). `make audit-history` is clean, and so is
`.git/hooks/_audit.sh` over `--branches origin/main origin/nrp/moment_v2 origin/nrp/swapin`.

## moment_v2: rule applied = `scripts/nrp/ingest_batch.sh nrp/moment_v2`, all five checks passed

Script output: identities and messages OK (author set `aidenlee <aiden.lee.sd@gmail.com>`); banned pattern in
added lines and paths OK; code unchanged since nrp-code-v1 OK; 60 records checked with 0 problems and 0 missing
artefacts (60 checkpoints listed as kept on NRP); counts `moment_v2 60 / 60`.

The following were also checked by hand (all as expected):

| Check | Result |
|---|---|
| records | 60, each file named after its run id |
| run ids | 60 unique, equal to `specs/moment_v2.jsonl` |
| collision with existing results | none (no existing `results/**/<run_id>.json`) |
| `code_ref` | `nrp-code-v1` in all 60 |
| `git_dirty` | false in all 60; `git_sha` = bfbdd8e (`nrp-code-v4`) in all 60 |
| checkpoint hashes file | `results/nrp/artefacts/moment_v2.sha256`, 60 entries, paths equal the records' checkpoints |
| predictions | 60 parquets, 20,508 rows, 0 non-finite values |
| exclusion list | identical in all 60 specs and set-equal to that of `specs/moment.jsonl` (10 entries) |
| models | S 30, D-state 30 (resamples 0-9, seeds 0-2, B = 654) |
| runs at the 200-epoch cap | 4, all S: a7d70fc64d35f0c8, 4f4fcd4874ca44df, 8dd956bdfe4e07c4, aee1a01ca0787cad |
| GPU models | A10 31, TITAN RTX 12, L4 10, Quadro RTX 6000 4, RTX 3090 3 |

`analysis/n4/high_moment_final.py` checks the records again before using them: prediction sha256 against the record,
recorded MAE against the stored predictions (to 1e-9), every test site minus the excluded entries exactly once,
targets and hosts equal to the universe, and train+val counts without the excluded entries.

## swapin: rule applied = hand verification, because the script refuses the record by design

`ingest_batch.sh nrp/swapin` passed checks 1-3 (identities and messages, banned pattern, code unchanged since
nrp-code-v1). It failed 4-5 with "0 result records checked": `swapin_v2` is a check record, not a run record. Its
payload has no `run_id`, and the name is in no spec file, so the script's `n == 0` guard refuses it. The script was
not edited. The same verification was done by hand instead:

| Check | Result |
|---|---|
| author and committer of the one commit | `aidenlee <aiden.lee.sd@gmail.com>` for both (script check 1, confirmed with `git log`) |
| banned strings in the message, added lines and paths | 0 (script checks 1-2) |
| change under src scripts configs splits specs against nrp-code-v1 | none (script check 3) |
| added files | one, `results/swapin/swapin_v2.json` (status A) |
| record fields | `name` = `swapin_v2`, matching the file; `git_dirty` false; `git_sha` = bfbdd8e (`nrp-code-v4`); `backbone` v2; `tuned` `configs/tuned_v2.yaml`; device cpu |
| internal consistency | `n_pairs` 183 = the length of `pairs` = the sum of `n_pairs_by_budget`; `n_missing` 0; `max_abs_diff_eV` and `max_abs_diff_eV_by_budget` equal the maxima over the pairs; `rescaling.n_identity` 183 equals the number of pairs with scale-1 = 0 and shift = 0 |
| referenced records | all 183 `d_record` (180 `results/v2_sweep/`, 3 `results/v2_kiyohara/`) and 183 `p1_record` (`results/p1_v2/`) exist on main; every recorded checkpoint sha256 and run id equals the one in the referenced record |

The checkpoints themselves are on NRP storage only, so their hashes cannot be checked on the Mac. The record's
hashes agree with the records that wrote the checkpoints.

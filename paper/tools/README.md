# paper/tools

Build helpers for the manuscript `paper/main.tex` (Crystals, MDPI). Build from the repository root with
`make -C paper`, which runs, in order, `fetch_template.sh` (only if the template is missing),
`make_numbers.py`, `check_macros.py` and `latexmk`.

| file | role |
|---|---|
| `fetch_template.sh` | Downloads the MDPI LaTeX template (ACS style) from the URL in `docs/venue.md` into `paper/template/`, records URL, time, size and sha256 in `paper/template/FETCHED.txt`, and links `paper/Definitions` to `template/Definitions`. The template has no licence and is for journal submission only, so `paper/template/` is in `.git/info/exclude` and the symlink is in `paper/.gitignore`. Override the URL with `MDPI_TEMPLATE_URL`. |
| `make_numbers.py` | Writes `paper/generated/numbers.tex` (one `\newcommand` per number) and `paper/generated/numbers.tsv` (macro, rendered value, raw value, JSON pointer into the source record). `paper/generated/` is rebuilt on every build and not tracked. |
| `check_macros.py` | Lists the `\num...` macros used in `paper/sections/*.tex` (`--list`), fails if any is undefined, and fails if the section prose contains a typed number. |

## Sources of the numbers

Every `results/<name>.json` whose stem equals its record's `name` field and which has a `payload` is read:
the named analysis records written by `write_result` (for example `g1_primary`, `g1_within_host`,
`g1_cap_sensitivity`, `g1_variance`, `filter_cascade`, `variance_decomposition`, `c0_official`,
`b0_physics_floor`, `baselines_summary`, and every other named record found). The per-run records, named by
a 16-hex-digit run id, are skipped. Only the `payload` is flattened.

Inside a payload:

- every finite numeric leaf becomes one macro; booleans and strings are skipped;
- the subtrees `config`, `package_versions`, `seeds`, `input`, `inputs` and every key containing
  `per_resample` are skipped;
- a two-element numeric list under a key named `ci` (or `*_ci`, `ci_*`) gives two macros, suffixes `Lo` and `Hi`;
- any other numeric list of at most 12 items gives one macro per item, suffixes `ItemOne`, `ItemTwo`, ...;
- a list of objects is flattened when every object carries the same identifying key (`step`, `name`, `id`,
  `model`, `element`, `site_label`, `formula` or `budget`, first match) with unique values; that value
  becomes the name component and the key itself is dropped. Other lists are skipped.

Two further sources follow the top-level records, so they never displace one of their names:

- the named records in `results/nrp/` (the N1 GPU-repeatability records); a list of objects without one
  unique identifying key is flattened by the joined values of the keys `class`, `model`, `B`, `node`,
  `pass`, `a`, `b` that every item carries (for example `per_class` items become `ATenSSixHundredFiftyFour`);
- protocol constants, which are settings rather than results: `configs/config.yaml` (prefix `Cfg`),
  `configs/tuned_v1.yaml` (`TunedVOne`), `configs/tuned_v2.yaml` (`TunedVTwo`), and selected top-level keys of
  `splits/meta.json` (`SplitMeta`), `splits/loco_v1.json` (`SplitLoco`), `splits/cv_v1.json` (`SplitCv`) and
  `splits/resamples_10_29.json` (`SplitExt`). Their source pointer is `<file>#/<key path>`.

## Naming scheme

`\num` + `Name(record)` + `Name(key 1)` + `Name(key 2)` + ...

`Name(s)` splits `s` at every character that is not a letter or digit, capitalises the first letter of each
letter run (the rest is kept as is) and spells each digit run as an English number in CamelCase. In a
decimal key every fractional digit is spelled, so `0.05` and `0.5` stay distinct. Examples:

| JSON pointer | macro |
|---|---|
| `g1_primary.json#/payload/c2_ceiling/A` | `\numGOnePrimaryCTwoCeilingA` |
| `g1_primary.json#/payload/c2_ceiling/ci` (lower end) | `\numGOnePrimaryCTwoCeilingCiLo` |
| `g1_primary.json#/payload/per_budget/654/MAE_S/mean` | `\numGOnePrimaryPerBudgetSixHundredFiftyFourMAESMean` |
| `g1_primary.json#/payload/n_star/n_star` | `\numGOnePrimaryNStarNStar` |
| `variance_decomposition.json#/payload/host/icc` | `\numVarianceDecompositionHostIcc` |
| `filter_cascade.json#/payload/steps/[step=final]/sites` | `\numFilterCascadeStepsFinalSites` |
| `target_sanity.json#/payload/quantiles/0.05` | `\numTargetSanityQuantilesZeroPointZeroFive` |

To find a macro, search `paper/generated/numbers.tsv` by JSON pointer. If two pointers map to the same name,
the first is kept and the clash is printed on stderr.

## Formatting

Each macro expands to `\ensuremath{...}`, so it works in text and in math:

- integers (and floats with an integral value) are printed exactly; five or more digits get thousands
  separators (MDPI style), e.g. `20{,}261{,}008`;
- other values with magnitude at least 0.001 and below 1000 get three decimals (`0.273`, `-0.012`);
  magnitude 1000 or more is rounded to an integer with separators; magnitude below 0.001 is written as
  `m\times10^{e}` with two significant figures;
- negative values carry a math minus sign; positive values carry no sign.
- training-host counts (leaves under `x_training_hosts`, `HOST_COUNT_KEYS`) are printed as the nearest
  integer, because the cross-validation values are mean fold sizes (736.2 prints as 736).

Write a macro followed by `{}` before a space (`\numVarianceDecompositionHostIcc{} of`) so the space is kept.
A number that needs a different rounding or a derived value (a percentage, a difference not stored in a
record) must first be written to a result record by an analysis script; it is never typed into the prose.

## The typed-number check

`check_macros.py` reports any digit left in the section prose after removing comments, optional arguments
(`[...]`), the arguments of referencing commands (`\cite`, `\ref`, `\label`, `\input`, `\includegraphics`,
`\figph`, `\url`, ...), chemical-formula subscripts (`O$_{2}$`), the `\num...` macros, and digits glued to a
name (`B0`, `D3`, `MACE-MP-0`). Text quoted verbatim from a third party (the NRP acknowledgement) sits between
`% verbatim-begin` and `% verbatim-end` lines and is exempt. Text constants that contain digits but are not
results (the licence name) are macros defined in `main.tex` (`\ccby`).

## One-network names (`net_macros.py`)

The rewrite names one network, so `net_macros.py` adds curated names after every generic macro: `\numNet...`
for the final network (He-initialised, validation-tuned; v2 in the repository) and `\numAbl...` for the
default-initialisation ablation of Appendix D (v1). Each is one JSON pointer into a record (the C1 tables in
`results/derived_c1/`, the W2 diagnostics in `results/derived_w2/`, and the top-level records of the final
network), listed with its source in `numbers.tsv`. A missing pointer stops the build, and a curated name may never
displace a generic one (a clash stops the build), so the generic macros are unchanged.

Name = `\numNet` or `\numAbl` + row + field. Rows of the C1 table: training hosts in words (`TwentyFive` ...
`SixHundredFiftyFour`), `FourHundredThirtyByFive` and `SixHundredFiftyFourThirtyByFive` (30 resamples x 5 seeds),
`CvTen`, `CvTwenty` (grouped cross-validation) and `Loco` (leave one family out). Fields: `MaeS`, `MaeD`, `MaeP`,
`MaeRf`, `MaeBZero` (suffixes `Lo`, `Hi` for the two-sided 95% interval), `A`, `ALo`, `AHi`, `AUpper` (one-sided
95% bound), `AInside`, `AUpperBelow`, `AExcludesZero` (the words yes or no) and `Hosts`. `\numNetHeadlineA...` is
the 30 x 5 estimate at 654 hosts. Other groups: `NetRepro...` (formula-grouped reproduction of the published
error), `NetLoco...` (family breakdown), `NetWithin...`, `NetStaging...` (`...Outcome` is a word),
`NetGeom...` (809 relaxed, 802 evaluated; energy changes with four decimals), `NetProbe...`, `NetScreen...`
(per site: oxide and site label with digits spelled, e.g. `NetScreenGaTwoOThreeOTwoPred`), `NetCross...`,
`NetSpread...`, `NetCap...`, `NetDsmall...` (W2 diagnostics), `AblKiyohara...` and `AblSpreadRatio...`.

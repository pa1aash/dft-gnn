# Limitations notes (seed material for the manuscript)

## Screening candidates absent from universe v1

The screening list of `docs/ANALYSIS_PLAN.md` §13 names 15 oxides. Eight are not in universe v1. The reason
for each was traced in the release (`scripts/screening_absence.py`, `results/screening_absence.json`):
release host directories were matched by reduced formula, and every completed neutral entry was checked
for the perturbed-host-state flag (PHS, `is_shallow`), the defect-type flags and membership of Kumagai's
neutral ML subset.

| Candidate | Why absent | Evidence |
|---|---|---|
| In2O3 | not in the release | no host directory with this reduced formula |
| CeO2 | not in the release | no host directory with this reduced formula |
| SrTiO3 | PHS-flagged | both neutral sites (O1, O2) are PHS; no defect-type flag; neither is in the ML subset |
| BaTiO3 | PHS-flagged | its single neutral site (O1) is PHS; no defect-type flag; not in the ML subset |
| WO3 | not in the release | no host directory with this reduced formula |
| MoO3 | not in the release | no host directory with this reduced formula |
| Nb2O5 | not in the release | no host directory with this reduced formula |
| LaAlO3 | not in the release | no host directory with this reduced formula |

No candidate is lost to another flag or to an unexplained ML-subset exclusion. The release does not record
why a material was not selected for calculation, so the six "not in the release" cases carry no stated
reason. A related loss affects a candidate that stays in the universe: three of the four neutral sites of
TiO2 (O1, O2, O3) are PHS, so only O4 enters universe v1.

## What the PHS filter implies about the domain of applicability

Physically, a PHS entry is a vacancy whose two donor electrons do not stay in a localised in-gap state but
perturb the host band edge. In other words, it is a shallow donor whose electrons delocalise into the host
conduction band. Removing these entries leaves a universe of deep or localised neutral vacancies. Our
hypothesis is that this filter mainly removes oxides with a low-lying, empty cation-d conduction band.

The counts in `results/screening_absence.json` (2103 completed neutral entries in the release, 345 PHS)
are consistent with that hypothesis, but they do not prove it:

- The PHS rate is 0.46 in entries of hosts containing Nb and 0.43 with W. It is 0.34 with Ti, 0.33 with V,
  0.28 with Ta and 0.23 with Mo, against 0.14-0.16 for the rest of the release.
- For Zr and Hf, which are also d0 cations but have a higher-lying d band, the rate is only 0.07 and 0.03.
  For the s-band conductors Zn, Ga, Sn and In it is 0.02-0.12.
- The PHS rate falls with the host's hybrid band gap: 0.37-0.44 between 1 and 3 eV, against 0.09 above
  5 eV. The median gap is 4.6 eV for PHS entries and 5.9 eV for the rest.
- The two candidates removed by PHS, SrTiO3 and BaTiO3, are Ti4+ perovskites. TiO2 keeps only one of its
  four sites.

Prediction for any oxide whose neutral vacancy would be a shallow donor is therefore outside the domain of
the models. The candidates most likely affected are the early-transition-metal d0 oxides and other
small-gap oxides. These counts describe the release; they do not by themselves establish the electronic
mechanism of any individual entry.

## S10b scope

The S10b site-resolution check moved the vacancy flag across the labelled vacancy sites of the test hosts only. The sweep placing the flag on every oxygen atom of each supercell was not run. The verdict (no implementation error in S) rests on the labelled-site pass and the flag-path unit tests and does not depend on that sweep, but within-host resolution at unlabelled oxygen sites is untested.

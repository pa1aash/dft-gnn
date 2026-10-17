# Hedge audit of the main-text rewrite (R3)

Session R3, 2026-10-17. Hedge words counted per 1,000 words of prose in the main-text files, Abstract to Conclusions
(`paper/sections/abstract.tex`, `introduction.tex`, `data.tex`, `methods.tex`, `results.tex`,
`results_screening.tex`, `discussion.tex`, `conclusions.tex`), before (main at `0817281`, the W2a merge) and after
the rewrite. Comments are dropped, number macros count as one word, citation and reference commands are dropped and
other command names are removed; words are runs of letters. Hedge list (whole words, case-insensitive): may, might,
suggest, suggests, suggesting, appear, appears, appeared, somewhat, possibly, perhaps, tentative, tentatively,
caution, cautious, cautiously.

| Text | Words | Hedge words | Per 1,000 words | Hits |
|---|---|---|---|---|
| Before (`0817281`) | 15,437 | 8 | 0.52 | may 5, appear 2, appears 1 |
| After (R3) | 7,063 | 0 | 0.00 | none |

Per file, after: Abstract 195 words, Introduction 794, Data and Domain 556, Methods 1,653, Results 1,835, Screening
629, Discussion 1,220, Conclusions 181; no hedge word in any of them.

The rewrite marks each physical reading once with "We propose" (twice in the prose: Discussion 4.1, host
thermodynamics, and 4.2, bonding and relaxation within a host; the d-shell reading of 4.2 follows from the second),
each followed by the measurement that motivates it and the one that would test it, as `docs/prose_style.md`
requires. Defensive refrains of the former text ("a bound, not an equivalence", "neither establishes nor excludes",
"what is and is not established", "this is a hypothesis") are absent: a search for "not established", "is a
hypothesis", "not an equivalence" and "neither" over the eight files returns one hit, the plain statement "neither
network captures most of that variation" (Discussion 4.2).

# paper/si: Supplementary Materials

`si.tex` builds the Supplementary Materials of the Crystals article as one PDF, `paper/si/si.pdf` (not tracked):
sections S1 to S9, Figures S1 to S8 in the final numbering of `docs/figure_numbering.md`, and Tables S1 onwards.

```sh
make -C paper template          # once: the MDPI template (its bibliography style is used here)
make -C paper/si PYTHON=python  # numbers, SI tables, macro check, latexmk
```

| path | role |
|---|---|
| `si.tex` | front matter and the order of the sections |
| `sisetup.sty` | layout (Palatino, 138.6 mm text block, S numbering) and text constants that contain digits |
| `sections/s*.tex` | the prose of S1 to S9, with figure captions reworded from `figures/si/*.caption.md` |
| `sections/tab_*.tex` | tables of results and protocol values, every number a macro (generated) |
| `tables/*.tex` | static text tables transcribed from `docs/` (descriptor classes, provenance labels, tags; generated) |
| `tools/make_si_tables.py` | writes both kinds of table; a JSON pointer without a macro is an error |

`paper/tools/check_macros.py` scans `paper/si/*.tex` and `paper/si/sections/*.tex` as it scans the article
sections; `tables/` is `\input` and not scanned, like `paper/tables/`.

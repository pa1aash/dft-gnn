# Build the Supplementary Materials (si.pdf). Run from the repository root as `make -C paper/si`.
# The MDPI template must exist (make -C paper template); numbers come from the result records.
PYTHON ?= python3
NICE ?= nice -n 15

.PHONY: all pdf numbers tables check clean

all: pdf

numbers:
	cd ../.. && $(PYTHON) paper/tools/make_numbers.py

tables: numbers
	cd ../.. && $(PYTHON) paper/si/tools/make_si_tables.py

check: tables
	cd ../.. && $(PYTHON) paper/tools/check_macros.py

pdf: check
	$(NICE) latexmk -r latexmkrc si.tex

clean:
	latexmk -C -r latexmkrc si.tex
	rm -f si.bbl

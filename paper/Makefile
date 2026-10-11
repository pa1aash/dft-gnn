# Build the manuscript. Run from the repository root as `make -C paper` (the root Makefile is frozen).
PYTHON ?= python3
NICE ?= nice -n 15

.PHONY: all pdf numbers check template clean

all: pdf

template/Definitions/mdpi.cls:
	sh tools/fetch_template.sh

template: template/Definitions/mdpi.cls

numbers:
	cd .. && $(PYTHON) paper/tools/make_numbers.py

check: numbers
	cd .. && $(PYTHON) paper/tools/check_macros.py

pdf: template check
	$(NICE) latexmk -pdf main.tex

clean:
	latexmk -C main.tex
	rm -f main.bbl

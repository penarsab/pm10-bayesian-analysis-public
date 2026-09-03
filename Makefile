.PHONY: install figures tables publication-assets validate clean-generated

PYTHON ?= python

install:
	$(PYTHON) -m pip install -e .

figures:
	$(PYTHON) scripts/generate_all_figures.py

tables:
	$(PYTHON) scripts/generate_all_tables.py

publication-assets: figures tables validate

validate:
	$(PYTHON) scripts/validate_release.py

clean-generated:
	rm -f figures/generated/main/*
	rm -f figures/generated/supplementary/*
	rm -f tables/generated/*.tex
	rm -f tables/machine_readable/*.csv

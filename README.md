# PM10 Bayesian Analysis Public Replication Package

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3110/)
[![License: MIT](https://img.shields.io/badge/Code%20license-MIT-yellow.svg)](LICENSE)
[![Content: CC BY 4.0](https://img.shields.io/badge/Content%20license-CC%20BY%204.0-lightgrey.svg)](LICENSE-CONTENT.md)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22287111.svg)](https://doi.org/10.5281/zenodo.22287111)

[![Preprint](https://img.shields.io/badge/Preprint-Preprints.org-blue.svg)](https://www.preprints.org/manuscript/202607.1392)

Public replication package for the accepted manuscript figures and tables for
the PM10 Bayesian forecasting analysis at the Krakow Zloty Rog station.

Paper title: *Bayesian Modeling of PM10 in Krakow Using Meteorological and
Seasonal Factors*

The package preserves the accepted plotting and table artefacts and uses frozen
analytical outputs to regenerate the manuscript asset set. It does not rerun the
full Stan sampling workflow by default and does not include local posterior
NetCDF archives or raw CmdStan chain outputs.

## Scope

This package reproduces the final main-text and supplementary figure/table asset
set used by the manuscript:

- 7 main figure assets, including the LaTeX/TikZ model DAG;
- 5 supplementary figures;
- 5 main manuscript tables;
- 12 supplementary manuscript tables.

The accepted manuscript assets are stored under `figures/reference/` and
`tables/reference/`. Regenerated release assets are written to
`figures/generated/` and `tables/generated/`.

The model-DAG source is regenerated as `figures/generated/main/dag.tex`. When a
local LaTeX toolchain is available, the release script renders
`figure2_model_dags.pdf` and `figure2_model_dags.png` from that TikZ source;
otherwise it restores the accepted PDF rendering from `figures/reference/` and
keeps the included generated PNG preview.

## Structure

- `data/frozen_results/`: frozen CSV inputs used to reproduce figures and tables;
- `data/data_sources.csv`: source inventory for GIOS and Open-Meteo inputs;
- `configs/`: palette, rendering, figure-size, and reproduction configuration;
- `src/figures/publication/`: accepted figure-generation code;
- `figures/reference/`: final accepted figure assets from the manuscript;
- `figures/generated/`: generated/copied figure assets created by this package;
- `tables/reference/`: final accepted LaTeX tables from the manuscript;
- `tables/generated/`: generated/copied LaTeX tables created by this package;
- `tables/machine_readable/`: CSV representations of all manuscript tables;
- `scripts/`: release-generation and validation entry points;
- `docs/`: provenance, scope, figure manifest, table manifest, and validation records.

## Installation

Python 3.11 is the supported reproduction version.

```bash
conda env create -f environment.yml
conda activate pm10-bayesian-analysis-public
```

Alternatively:

```bash
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pip install -e .
```

On Windows, Conda users should run figure generation from an activated Conda
environment or via `conda run` so that Matplotlib can locate the required
runtime libraries.

## Dataset

The original working `data/raw` and `data/processed` trees are not
redistributed. The default reproduction workflow is self-contained because it
uses frozen accepted CSV and JSON inputs under `data/frozen_results/`.

PM10 measurements originate from the GIOS archival air-quality API for the
Krakow Zloty Rog PM10 sensor. Meteorological variables originate from the
Open-Meteo Historical Weather API at the same latitude and longitude. Source
details and processing notes are recorded in `data/README.md`,
`data/data_sources.csv`, and `docs/DATA_PROVENANCE.md`.

## Generate Assets

Generate all manuscript figures:

```bash
python scripts/generate_all_figures.py
```

Generate all manuscript tables:

```bash
python scripts/generate_all_tables.py
```

Generate and validate the complete public asset set:

```bash
make publication-assets
```

The workflow is deterministic. No Stan sampling, posterior simulation,
subsampling, or bootstrap resampling is performed by the public scripts.

## Validate

```bash
python scripts/validate_release.py
```

Validation checks required main and supplementary assets, required frozen source
CSV files, prohibited private/work files, NetCDF exclusion, and machine-specific
paths.

## Citation

If you use this replication package, cite the associated article:

Sabina Penar and Jerzy Baranowski, *Bayesian Modeling of PM10 in Krakow Using
Meteorological and Seasonal Factors*, Preprints.org,
https://www.preprints.org/manuscript/202607.1392.

Machine-readable citation metadata are provided in `CITATION.cff`. The archived
release DOI is `10.5281/zenodo.22287111`.

## Licence and contact

Software, scripts, and configuration files are licensed under MIT; see
`LICENSE`. Original documentation, figures, and tables are licensed under CC BY
4.0 except where otherwise noted; see `LICENSE-CONTENT.md`.

The content licence does not cover third-party source services or raw data
outside this repository. The raw source data are not redistributed and remain
subject to their original providers' terms; see `data/README.md`.

Correspondence: Jerzy Baranowski, `jb@agh.edu.pl`.

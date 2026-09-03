# Validation report

Build date: 2026-09-03

Lifecycle status: public GitHub release archived by Zenodo. The associated
article preprint URL is recorded in `CITATION.cff`.

## Commands and results

Executed in the public package:

```bash
python scripts/generate_all_tables.py
conda run -n pm10-bayesian-analysis python scripts/generate_all_figures.py
conda run -n pm10-bayesian-analysis python scripts/validate_release.py
```

Additional table identity check:

```bash
git diff --no-index --exit-code tables/reference tables/generated
```

Results:

- all 17 generated LaTeX tables match their reference LaTeX files
  byte-for-byte;
- all configured figure assets were generated or restored through the public
  figure workflow;
- `scripts/validate_release.py` passed with zero missing required files and zero
  prohibited files;
- no `src/revision` file is present in the tracked public snapshot;
- no `__pycache__`, NetCDF file, private `results/` directory, raw-data
  directory, agent file, or internal review directory is included.

## Figure validation

The public figure workflow generated the main and supplementary figure set under
`figures/generated/`. The generated main outputs include the PM10 series and
split figure, the model DAG assets, model comparison, forecast-window zooms,
coefficient comparison, high-pollution comparison, and LOO/Pareto diagnostics.
The supplementary outputs include prior predictive checks, residual diagnostics,
LOO/Pareto diagnostics, sensitivity comparison, and the high-pollution
persistence-safeguard figure.

The model DAG generator writes `figures/generated/main/dag.tex`. When a local
LaTeX/ImageMagick toolchain is unavailable, it restores the accepted reference
rendering for `figure2_model_dags.pdf` and keeps the included generated PNG
preview.

## Table validation

The table generator wrote 17 manuscript-ready LaTeX files to
`tables/generated/` and 17 machine-readable CSV files to
`tables/machine_readable/`. The generated LaTeX files were compared against
`tables/reference/` and matched exactly.

## Package validation

The release validator checked required reference figures, required generated
figures, required reference and generated tables, required frozen source files,
machine-readable tables, prohibited private paths, NetCDF exclusion, and Python
cache exclusion. The validation status was `passed`.

`release_manifest.csv` records the current public package file inventory and is
rewritten by `scripts/validate_release.py`.

## Warnings and unresolved items

No unresolved release-package validation items remain.

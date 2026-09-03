# Reproducibility

The supported reference environment is Python 3.11. The public package is built
to regenerate manuscript figures and tables from frozen accepted analytical
outputs without downloading data or rerunning model sampling.

The current local validation was run with:

- Python 3.11.15;
- NumPy 2.4.6;
- pandas 3.0.5;
- Matplotlib 3.11.1;
- PyYAML 6.0.3;
- statsmodels 0.14.6.

The workflow is deterministic. No Stan sampling, posterior simulation, random
subsampling, bootstrap resampling, or stochastic plotting jitter is run by the
public scripts.

From the repository root:

```bash
python scripts/generate_all_figures.py
python scripts/generate_all_tables.py
python scripts/validate_release.py
```

Conda users can create the environment from `environment.yml`. On Windows,
running through an activated Conda environment or `conda run` is recommended so
that Matplotlib can locate the required runtime DLLs:

```bash
conda run -n pm10-bayesian-analysis python scripts/generate_all_figures.py
```

Figure outputs are written to `figures/generated/main/` and
`figures/generated/supplementary/`. Table outputs are written to
`tables/generated/` and `tables/machine_readable/`.

Validation checks:

- required reference figures exist;
- required generated figures exist;
- required reference, generated, and machine-readable tables exist;
- required frozen source CSV and JSON files exist;
- generated table LaTeX is byte-identical to the reference table LaTeX;
- prohibited private directories and files are absent;
- NetCDF files and Python cache files are absent from the public package;
- obvious machine-specific paths are not included in the release inventory.

Exact PDF hashes are not treated as the main reproducibility authority because
PDF metadata and renderer details can vary across platforms. The frozen inputs,
table identity checks, required asset checks, and release validation report are
the release-level checks.

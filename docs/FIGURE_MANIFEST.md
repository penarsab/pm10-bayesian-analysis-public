# Figure manifest

All figures are generated from frozen accepted analytical artefacts under
`data/frozen_results/`. The public scripts do not rerun Stan sampling. Generated
assets are written to `figures/generated/`, while accepted manuscript reference
assets are stored under `figures/reference/`.

## Main Figure 1 - `figure1_pm10_series_and_splits`

- Module: `src.figures.publication.figure1_pm10_series_and_splits`
- Inputs: `pm10_series.csv` and `model_metadata/splits.json`
- Raw data required: no
- Caveat: datetimes are parsed for plotting, but the frozen PM10 series is not
  refit or resampled.

Full PM10 time series with the accepted rolling-origin cross-validation and
final held-out test split structure.

## Main Figure 2 - `figure2_model_dags`

- Module: `src.figures.publication.model_dag`
- Inputs: embedded LaTeX/TikZ DAG source and reference rendering fallback
- Raw data required: no
- Caveat: if a local LaTeX/ImageMagick toolchain is unavailable, the script
  restores the accepted reference rendering.

Graphical model summary for the manuscript model family. The generated TikZ
source is written as `figures/generated/main/dag.tex`.

## Main Figure 3 - `figure3_model_comparison`

- Module: `src.figures.publication.figure3_model_comparison`
- Inputs: `test_metrics.csv` and `cv_metrics.csv`
- Raw data required: no
- Caveat: metrics are read from frozen accepted CSV files; no metric is
  recomputed from posterior draws.

Overall comparison of forecasting models across final-test and cross-validation
metrics.

## Main Figure 4 - `figure4_test_forecast_windows`

- Module: `src.figures.publication.figure4_test_forecast_window`
- Inputs: `test_predictions.csv` and `high_pollution_metrics.csv`
- Raw data required: no
- Caveat: the public generator preserves the accepted layout: a calm week, a
  winter-smog episode, and a transition-season rapid-increase week.

Three final-test forecast-window zooms comparing observed PM10 with selected
forecast summaries.

## Main Figure 5 - `figure5_coefficient_comparison`

- Module: `src.figures.publication.figure5_coefficient_comparison`
- Inputs: `multiplicative_effects.csv`
- Raw data required: no
- Caveat: posterior effects are frozen accepted summaries and are not
  recomputed.

Comparison of meteorological multiplicative effects for the accepted M1 and M3
models.

## Main Figure 6 - `figure6_high_pollution_comparison`

- Module: `src.figures.publication.figure6_high_pollution_comparison`
- Inputs: `high_pollution_metrics.csv` and `test_metrics.csv`
- Raw data required: no
- Caveat: CRPS is not fabricated for the high-pollution subset when it is not
  present in the corrected frozen pipeline.

High-pollution subset performance compared with overall final-test
performance.

## Main diagnostic figure - `figure6_loo_pareto_diagnostics`

- Source module: `src.figures.publication.supplementary.s3_pareto_k_diagnostics`
- Inputs: `loo_waic_comparison.csv`
- Raw data required: no
- Caveat: the main diagnostic asset is copied from the generated S3 diagnostic
  rendering to the accepted main-figure filename.

PSIS-LOO elpd comparison and Pareto-k diagnostic summary for the Bayesian model
set.

## Supplementary Figure S1 - `s1_prior_predictive_checks`

- Module: `src.figures.publication.supplementary.s1_prior_predictive_checks`
- Inputs: `prior_predictive_summary.csv` and `data_audit.csv`
- Raw data required: no
- Caveat: prior simulations are not rerun.

Prior predictive checks for M0-M3 against observed PM10 summary ranges.

## Supplementary Figure S2 - `s2_residual_diagnostics`

- Module: `src.figures.publication.supplementary.s2_residual_diagnostics`
- Inputs: `test_predictions.csv`
- Raw data required: no
- Caveat: residual diagnostics are computed from frozen final-test prediction
  summaries.

Residual diagnostics for M0-M3 on the final held-out test period.

## Supplementary Figure S3 - `s3_pareto_k_diagnostics`

- Module: `src.figures.publication.supplementary.s3_pareto_k_diagnostics`
- Inputs: `loo_waic_comparison.csv`
- Raw data required: no
- Caveat: LOO and WAIC summaries are frozen from the accepted NetCDF-based
  analysis.

PSIS-LOO elpd comparison and Pareto-k diagnostic summary.

## Supplementary Figure S4 - `s4_sensitivity_comparison`

- Module: `src.figures.publication.supplementary.s4_sensitivity_comparison`
- Inputs: `sensitivity_metrics.csv` and `sensitivity_coefficients.csv`
- Raw data required: no
- Caveat: sensitivity variants are not refit.

M3 sensitivity to prior width and likelihood family.

## Supplementary Figure S5 - `s5_high_pollution_safeguard`

- Module: `src.figures.publication.supplementary.s5_high_pollution_safeguard`
- Inputs: `test_predictions.csv`, `modeling_table.csv`, and
  `model_metadata/splits.json`
- Raw data required: no
- Caveat: safeguard predictions are rebuilt from frozen public inputs and the
  accepted final split, not from the private revision workflow.

Persistence-safeguard comparison for high-pollution final-test hours.

Configured output paths are also listed in `figure_manifest.yaml`.

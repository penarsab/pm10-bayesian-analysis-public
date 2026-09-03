# Data Inputs

This public replication package does not expose the original working
`data/raw` and `data/processed` tree. Instead, it ships the frozen CSV inputs
needed to reproduce the accepted manuscript figures and tables.

## Layout

- `data/data_sources.csv`: source inventory for the GIOS PM10 and Open-Meteo
  meteorological data pulls.
- `data/frozen_results/figure_sources/`: CSV inputs used by the figure
  generators, including the PM10 series, final-test predictions, model metrics,
  posterior effect summaries, prior predictive summaries, LOO/WAIC summaries,
  and sensitivity summaries.
- `data/frozen_results/table_sources/`: CSV inputs corresponding to every
  main-text and supplementary manuscript table.
- `data/frozen_results/model_metadata/`: non-CSV split/scaler metadata required
  to reproduce the exact final split and selected derived diagnostics.

## Source Provenance

PM10 measurements originate from the GIOS archival air-quality API for the
Krakow, ul. Zloty Rog PM10 sensor. Meteorological variables originate from the
Open-Meteo Historical Weather API at the same latitude and longitude used for
the Zloty Rog monitoring point. The article uses hourly observations covering
2020-01-01 00:00:00 through 2024-12-31 23:00:00.

The frozen files preserve the accepted analytical state used for the article.
They are the intended public inputs for reproducing the released figures and
tables without rerunning the full data download, preprocessing, Stan sampling,
or NetCDF-based posterior-summary workflow.

# Data provenance

The release follows this path:

```text
GIOS and Open-Meteo public data sources
-> private preprocessing and accepted Bayesian analysis
-> frozen public CSV and JSON summaries
-> generated manuscript figures and tables
```

PM10 measurements originate from the GIOS archival air-quality API:

- sensor id: `16786`;
- station code: `MpKrakZloRog-PM10-1g`;
- station description: Krakow, ul. Zloty Rog;
- latitude: `50.081197`;
- longitude: `19.895358`;
- frequency: hourly;
- study interval: 2020-01-01 00:00:00 through 2024-12-31 23:00:00;
- download date recorded in the source inventory: 2026-06-26.

Meteorological variables originate from the Open-Meteo Historical Weather API
at the same latitude and longitude. The public source inventory records
temperature at 2 m, relative humidity at 2 m, wind speed at 10 m, and surface
pressure. The `surface_pressure` variable is intentionally named after the
Open-Meteo physical quantity and is not sea-level pressure.

The public package does not recompute the accepted preprocessing pipeline.
Instead, it ships the frozen files under `data/frozen_results/`:

- `figure_sources/`: inputs used by figure generators, including PM10 series,
  model predictions, model metrics, high-pollution metrics, LOO/WAIC summaries,
  posterior effect summaries, prior predictive summaries, and sensitivity
  summaries;
- `table_sources/`: CSV inputs corresponding to every main-text and
  supplementary manuscript table;
- `model_metadata/`: split and final-holdout metadata required to reproduce the
  exact accepted split structure.

The source inventory is recorded in `data/data_sources.csv`. The release file
inventory is recorded in `release_manifest.csv`.

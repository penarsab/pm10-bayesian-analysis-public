# Provisional Data Availability Statement

Hourly PM10 observations used in this study originate from the public GIOS
archival air-quality API for the Krakow, ul. Zloty Rog PM10 sensor
(`sensor_id=16786`; station code `MpKrakZloRog-PM10-1g`). Hourly meteorological
variables originate from the Open-Meteo Historical Weather API at the same
latitude and longitude used for the air-quality monitoring point.

The public replication repository provides frozen analytical CSV inputs,
metadata, scripts, and accepted reference artefacts required to reproduce all
manuscript figures and tables:

```text
https://github.com/penarsab/pm10-bayesian-analysis-public
```

The archived release is available at:

```text
https://doi.org/10.5281/zenodo.22287111
```

The package does not redistribute the original raw working `data/raw` and
`data/processed` trees. Instead, it distributes the frozen public inputs used to
regenerate the accepted manuscript asset set without rerunning data download,
preprocessing, Stan sampling, or NetCDF-based posterior summarisation.

# Analytical scope

This repository is a public figure-and-table replication package for the
accepted PM10 Bayesian forecasting manuscript. It reproduces the final
main-text and supplementary manuscript assets from frozen accepted analytical
outputs.

The package intentionally focuses on reproducibility of the released artefacts,
not on rerunning the full research workflow. It includes the plotting and table
generation code, frozen CSV inputs, split metadata, accepted reference assets,
and validation checks needed to regenerate the manuscript figure and table set.

It intentionally excludes:

- raw GIOS and Open-Meteo download files;
- intermediate processed data outside the frozen public inputs;
- posterior NetCDF archives and raw CmdStan chain outputs;
- Stan fitting runs, failed-run history, and exploratory model-development
  material;
- internal plans, prompts, review notes, comments, and agent files;
- manuscript drafting and reviewer-response files;
- claims of real-time operational deployment or public-warning validation.

The reproduced analysis is a one-hour-ahead forecasting study for hourly PM10
at the Krakow Zloty Rog station over 2020-01-01 00:00:00 through
2024-12-31 23:00:00. The public package preserves the accepted split structure,
model labels, metric summaries, posterior-effect summaries, diagnostic
summaries, and high-pollution subset definitions used in the manuscript.

The frozen files are the authority for this release. Regeneration should
preserve the accepted table text exactly and should recreate the configured
figure assets without requiring access to private modelling outputs.

# Table manifest

The public package includes 5 main manuscript tables and 12 supplementary
manuscript tables. Reference LaTeX files are stored in `tables/reference/`.
Regenerated LaTeX files are written to `tables/generated/`, and corresponding
machine-readable CSV files are written to `tables/machine_readable/`.

All generated LaTeX table files currently match the corresponding reference
table files byte-for-byte.

| Table | Class | Source CSV | Output |
|---|---|---|---|
| `table1_data_summary` | computed | `data/frozen_results/table_sources/table1_data_summary.csv` | `tables/generated/table1_data_summary.tex` |
| `table2_model_definitions` | curated/model definition | `data/frozen_results/table_sources/table2_model_definitions.csv` | `tables/generated/table2_model_definitions.tex` |
| `table3_test_performance` | computed | `data/frozen_results/table_sources/table3_test_performance.csv` | `tables/generated/table3_test_performance.tex` |
| `table4_bootstrap_comparisons` | computed | `data/frozen_results/table_sources/table4_bootstrap_comparisons.csv` | `tables/generated/table4_bootstrap_comparisons.tex` |
| `table5_meteorological_effects` | computed | `data/frozen_results/table_sources/table5_meteorological_effects.csv` | `tables/generated/table5_meteorological_effects.tex` |
| `table_s1_mcmc_diagnostics` | computed diagnostic | `data/frozen_results/table_sources/table_s1_mcmc_diagnostics.csv` | `tables/generated/table_s1_mcmc_diagnostics.tex` |
| `table_s2_loo_waic` | computed diagnostic | `data/frozen_results/table_sources/table_s2_loo_waic.csv` | `tables/generated/table_s2_loo_waic.tex` |
| `table_s3_sensitivity` | computed sensitivity | `data/frozen_results/table_sources/table_s3_sensitivity.csv` | `tables/generated/table_s3_sensitivity.tex` |
| `table_s4_sensitivity_assessment` | computed sensitivity | `data/frozen_results/table_sources/table_s4_sensitivity_assessment.csv` | `tables/generated/table_s4_sensitivity_assessment.tex` |
| `table_s5_yearly_holdouts` | computed sensitivity | `data/frozen_results/table_sources/table_s5_yearly_holdouts.csv` | `tables/generated/table_s5_yearly_holdouts.tex` |
| `table_s6_fourier_sensitivity` | computed sensitivity | `data/frozen_results/table_sources/table_s6_fourier_sensitivity.csv` | `tables/generated/table_s6_fourier_sensitivity.tex` |
| `table_s7_phi_diagnostics` | computed diagnostic | `data/frozen_results/table_sources/table_s7_phi_diagnostics.csv` | `tables/generated/table_s7_phi_diagnostics.tex` |
| `table_s8_phi_parameterization` | computed/model definition | `data/frozen_results/table_sources/table_s8_phi_parameterization.csv` | `tables/generated/table_s8_phi_parameterization.tex` |
| `table_s9_missingness_audit` | computed audit | `data/frozen_results/table_sources/table_s9_missingness_audit.csv` | `tables/generated/table_s9_missingness_audit.tex` |
| `table_s10_gap_filtered_metrics` | computed sensitivity | `data/frozen_results/table_sources/table_s10_gap_filtered_metrics.csv` | `tables/generated/table_s10_gap_filtered_metrics.tex` |
| `table_s11_meteorological_scale` | computed audit | `data/frozen_results/table_sources/table_s11_meteorological_scale.csv` | `tables/generated/table_s11_meteorological_scale.tex` |
| `table_s12_high_pollution_safeguard` | computed safeguard audit | `data/frozen_results/table_sources/table_s12_high_pollution_safeguard.csv` | `tables/generated/table_s12_high_pollution_safeguard.tex` |

Output convention:

```text
tables/reference/<table_id>.tex
tables/generated/<table_id>.tex
tables/machine_readable/<table_id>.csv
```

Generate all tables:

```bash
python scripts/generate_all_tables.py
```

Configured output paths are also listed in `table_manifest.yaml`.

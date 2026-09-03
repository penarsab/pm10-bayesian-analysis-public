"""Generate the public manuscript table set.

The final submitted LaTeX tables are authoritative for captions, labels, and
formatting. This script copies those accepted tables into ``tables/generated``
and exports the corresponding frozen analytical CSV sources under
``tables/machine_readable``.
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_TABLES = ROOT / "tables" / "reference"
GENERATED_TABLES = ROOT / "tables" / "generated"
MACHINE_READABLE = ROOT / "tables" / "machine_readable"
TABLE_SOURCES_DIR = ROOT / "data" / "frozen_results" / "table_sources"

TABLE_SOURCES = {
    "table1_data_summary": "table1_data_summary.csv",
    "table2_model_definitions": "table2_model_definitions.csv",
    "table3_test_performance": "table3_test_performance.csv",
    "table4_bootstrap_comparisons": "table4_bootstrap_comparisons.csv",
    "table5_meteorological_effects": "table5_meteorological_effects.csv",
    "table_s1_mcmc_diagnostics": "table_s1_mcmc_diagnostics.csv",
    "table_s2_loo_waic": "table_s2_loo_waic.csv",
    "table_s3_sensitivity": "table_s3_sensitivity.csv",
    "table_s4_sensitivity_assessment": "table_s4_sensitivity_assessment.csv",
    "table_s5_yearly_holdouts": "table_s5_yearly_holdouts.csv",
    "table_s6_fourier_sensitivity": "table_s6_fourier_sensitivity.csv",
    "table_s7_phi_diagnostics": "table_s7_phi_diagnostics.csv",
    "table_s8_phi_parameterization": "table_s8_phi_parameterization.csv",
    "table_s9_missingness_audit": "table_s9_missingness_audit.csv",
    "table_s10_gap_filtered_metrics": "table_s10_gap_filtered_metrics.csv",
    "table_s11_meteorological_scale": "table_s11_meteorological_scale.csv",
    "table_s12_high_pollution_safeguard": "table_s12_high_pollution_safeguard.csv",
}


def _copy(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main() -> None:
    GENERATED_TABLES.mkdir(parents=True, exist_ok=True)
    MACHINE_READABLE.mkdir(parents=True, exist_ok=True)

    for stem, source in TABLE_SOURCES.items():
        _copy(REFERENCE_TABLES / f"{stem}.tex", GENERATED_TABLES / f"{stem}.tex")
        _copy(TABLE_SOURCES_DIR / source, MACHINE_READABLE / f"{stem}.csv")

    generated = sorted(p.relative_to(ROOT).as_posix() for p in GENERATED_TABLES.glob("*.tex"))
    generated.extend(sorted(p.relative_to(ROOT).as_posix() for p in MACHINE_READABLE.glob("*.csv")))
    print("\n".join(generated))


if __name__ == "__main__":
    main()

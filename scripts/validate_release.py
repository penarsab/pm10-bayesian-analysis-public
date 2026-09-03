"""Validate the public replication package contents."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True

REQUIRED_REFERENCE_FIGURES = [
    "figures/reference/main/dag.tex",
    "figures/reference/main/figure2_model_dags.pdf",
    "figures/reference/main/figure1_pm10_series_and_splits.pdf",
    "figures/reference/main/figure3_model_comparison.pdf",
    "figures/reference/main/figure6_loo_pareto_diagnostics.pdf",
    "figures/reference/main/figure4_test_forecast_windows.pdf",
    "figures/reference/main/figure5_coefficient_comparison.pdf",
    "figures/reference/main/figure6_high_pollution_comparison.pdf",
    "figures/reference/supplementary/s1_prior_predictive_checks.pdf",
    "figures/reference/supplementary/s2_residual_diagnostics.pdf",
    "figures/reference/supplementary/s3_pareto_k_diagnostics.pdf",
    "figures/reference/supplementary/s4_sensitivity_comparison.pdf",
    "figures/reference/supplementary/s5_high_pollution_safeguard.pdf",
]

REQUIRED_GENERATED_FIGURES = [
    "figures/generated/main/dag.tex",
    "figures/generated/main/figure2_model_dags.pdf",
    "figures/generated/main/figure2_model_dags.png",
    "figures/generated/main/figure1_pm10_series_and_splits.pdf",
    "figures/generated/main/figure3_model_comparison.pdf",
    "figures/generated/main/figure6_loo_pareto_diagnostics.pdf",
    "figures/generated/main/figure4_test_forecast_windows.pdf",
    "figures/generated/main/figure5_coefficient_comparison.pdf",
    "figures/generated/main/figure6_high_pollution_comparison.pdf",
    "figures/generated/supplementary/s1_prior_predictive_checks.pdf",
    "figures/generated/supplementary/s2_residual_diagnostics.pdf",
    "figures/generated/supplementary/s3_pareto_k_diagnostics.pdf",
    "figures/generated/supplementary/s4_sensitivity_comparison.pdf",
    "figures/generated/supplementary/s5_high_pollution_safeguard.pdf",
]

TABLE_STEMS = [
    "table1_data_summary",
    "table2_model_definitions",
    "table3_test_performance",
    "table4_bootstrap_comparisons",
    "table5_meteorological_effects",
    "table_s1_mcmc_diagnostics",
    "table_s2_loo_waic",
    "table_s3_sensitivity",
    "table_s4_sensitivity_assessment",
    "table_s5_yearly_holdouts",
    "table_s6_fourier_sensitivity",
    "table_s7_phi_diagnostics",
    "table_s8_phi_parameterization",
    "table_s9_missingness_audit",
    "table_s10_gap_filtered_metrics",
    "table_s11_meteorological_scale",
    "table_s12_high_pollution_safeguard",
]

REQUIRED_SOURCES = [
    "data/README.md",
    "data/data_sources.csv",
    "data/frozen_results/figure_sources/pm10_series.csv",
    "data/frozen_results/figure_sources/modeling_table.csv",
    "data/frozen_results/figure_sources/test_predictions.csv",
    "data/frozen_results/figure_sources/cv_predictions.csv",
    "data/frozen_results/figure_sources/test_metrics.csv",
    "data/frozen_results/figure_sources/cv_metrics.csv",
    "data/frozen_results/figure_sources/loo_waic_comparison.csv",
    "data/frozen_results/figure_sources/multiplicative_effects.csv",
    "data/frozen_results/figure_sources/prior_predictive_summary.csv",
    "data/frozen_results/figure_sources/data_audit.csv",
    "data/frozen_results/figure_sources/high_pollution_metrics.csv",
    "data/frozen_results/figure_sources/sensitivity_metrics.csv",
    "data/frozen_results/figure_sources/sensitivity_coefficients.csv",
    "data/frozen_results/model_metadata/splits.json",
    "data/frozen_results/model_metadata/final_holdout.json",
    *[f"data/frozen_results/table_sources/{stem}.csv" for stem in TABLE_STEMS],
]

PROHIBITED_PATH_PARTS = [
    ".codex",
    ".agents",
    "config",
    "reports",
    "reviews",
    "responses",
    "results",
    "data/raw",
    "data/processed",
    "manuscript",
    "stan",
    "__MACOSX",
]

PROHIBITED_FILENAMES = {
    "AGENTS.md",
    "manuscript.zip",
    "Applied_Sciences___Penar.pdf",
    "main (1).pdf",
    "lista_zadan.md",
}

MANIFEST_EXCLUDED_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".ipynb_checkpoints",
    ".venv",
    "tmp",
}


def _missing(paths: list[str]) -> list[str]:
    return [path for path in paths if not (ROOT / path).exists()]


def _table_paths(prefix: str, suffix: str) -> list[str]:
    return [f"{prefix}/{stem}{suffix}" for stem in TABLE_STEMS]


def _prohibited_files() -> list[str]:
    offenders: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        parts = set(rel.split("/"))
        if path.name in PROHIBITED_FILENAMES:
            offenders.append(rel)
        if path.suffix == ".nc":
            offenders.append(rel)
        if any(rel == part or rel.startswith(f"{part}/") for part in PROHIBITED_PATH_PARTS):
            offenders.append(rel)
        if parts.intersection({"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}):
            offenders.append(rel)
    return sorted(set(offenders))


def _machine_paths() -> list[str]:
    return _table_paths("tables/machine_readable", ".csv")


def _include_in_manifest(path: Path) -> bool:
    rel_parts = path.relative_to(ROOT).parts
    return path.is_file() and not set(rel_parts).intersection(MANIFEST_EXCLUDED_PARTS)


def _write_manifest() -> None:
    rows = []
    for path in sorted(p for p in ROOT.rglob("*") if _include_in_manifest(p)):
        rel = path.relative_to(ROOT).as_posix()
        rows.append({"path": rel, "size_bytes": path.stat().st_size})
    with (ROOT / "release_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "size_bytes"])
        writer.writeheader()
        writer.writerows(rows)


def validate_release() -> dict[str, object]:
    checks = {
        "missing_reference_figures": _missing(REQUIRED_REFERENCE_FIGURES),
        "missing_generated_figures": _missing(REQUIRED_GENERATED_FIGURES),
        "missing_reference_tables": _missing(_table_paths("tables/reference", ".tex")),
        "missing_generated_tables": _missing(_table_paths("tables/generated", ".tex")),
        "missing_machine_readable_tables": _missing(_machine_paths()),
        "missing_sources": _missing(REQUIRED_SOURCES),
        "prohibited_files": _prohibited_files(),
    }
    status = "passed" if all(not value for value in checks.values()) else "failed"
    _write_manifest()
    return {"status": status, "checks": checks}


def main() -> int:
    report = validate_release()
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Supplementary Figure S1: prior predictive checks for M0-M3.

Analytical source: frozen prior-predictive and audit CSV files under
`data/frozen_results`. No prior simulation is re-run here.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from src.config import FIGURE_SOURCES_DIR
from src.figures.publication.common import (
    NEUTRAL,
    PALETTE,
    SUPPLEMENTARY_DIR,
    publication_style,
    save_figure,
    strip_spines,
)

SUMMARY_PATH = FIGURE_SOURCES_DIR / "prior_predictive_summary.csv"
DATA_AUDIT_PATH = FIGURE_SOURCES_DIR / "data_audit.csv"
OUTPUT_STEM = SUPPLEMENTARY_DIR / "s1_prior_predictive_checks"

MODEL_ORDER = ["M0", "M1", "M2", "M3"]
STATISTICS = [
    ("q99_pm10", "q99 simulated PM10 [µg/m³]", "q99"),
    ("max_pm10", "max simulated PM10 [µg/m³]", "max"),
]


def build_s1():
    summary = pd.read_csv(SUMMARY_PATH).set_index("model").loc[MODEL_ORDER]
    audit = pd.read_csv(DATA_AUDIT_PATH).set_index("variable").loc["PM10"]

    with publication_style():
        fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8), constrained_layout=True)
        y_positions = range(len(MODEL_ORDER))

        for ax, (prefix, xlabel, audit_col) in zip(axes, STATISTICS):
            observed_reference = audit[audit_col]
            for y, model in zip(y_positions, MODEL_ORDER):
                median = summary.loc[model, f"{prefix}_median_across_draws"]
                q05 = summary.loc[model, f"{prefix}_q05_across_draws"]
                q95 = summary.loc[model, f"{prefix}_q95_across_draws"]
                ax.plot([q05, q95], [y, y], color=PALETTE["primary_line"], lw=1.6, solid_capstyle="round")
                ax.scatter([median], [y], color=PALETTE["primary_line"], s=26, zorder=3, edgecolor="white", linewidth=0.4)

            ax.axvline(observed_reference, color=NEUTRAL["reference_line"], lw=0.9, ls="--", zorder=0)
            ax.text(
                observed_reference, -0.75, "observed\n(training)",
                fontsize=6.2, ha="center", va="top", color=NEUTRAL["reference_line"],
            )
            ax.set_xscale("log")
            ax.set_yticks(list(y_positions))
            ax.set_yticklabels(MODEL_ORDER)
            ax.invert_yaxis()
            ax.set_xlabel(xlabel)
            ax.set_ylim(len(MODEL_ORDER) - 0.4, -1.5)
            strip_spines(ax, keep=("bottom",))
            ax.tick_params(axis="y", length=0)

        pdf_path, png_path = save_figure(fig, OUTPUT_STEM)
        plt.close(fig)
    return pdf_path, png_path


def main() -> None:
    pdf_path, png_path = build_s1()
    print(f"Wrote: {pdf_path}")
    print(f"Wrote: {png_path}")


if __name__ == "__main__":
    main()

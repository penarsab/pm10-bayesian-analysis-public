"""Figure 6: high-pollution-subset performance vs. overall-test performance.

Analytical source: frozen high-pollution and overall-test metric CSV files under
`data/frozen_results`.
CRPS is not available in `high_pollution_metrics.csv` for the corrected
pipeline and is therefore not shown (not fabricated).
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from src.config import FIGURE_SOURCES_DIR
from src.figures.publication.common import (
    FIGURES_DIR,
    MODEL_LABELS,
    NEUTRAL,
    PALETTE,
    publication_style,
    save_figure,
    strip_spines,
)

HIGH_POLLUTION_PATH = FIGURE_SOURCES_DIR / "high_pollution_metrics.csv"
TEST_METRICS_PATH = FIGURE_SOURCES_DIR / "test_metrics.csv"
OUTPUT_STEM = FIGURES_DIR / "figure6_high_pollution_comparison"

PRIMARY_MODEL_ORDER = ["B1_persistence", "B2_arx", "M0_dynamic_only", "M3_dynamic_regression"]
PANELS = [("mae", "mae_high", "MAE [µg/m³]"), ("rmse", "rmse_high", "RMSE [µg/m³]")]


def _load() -> tuple[pd.DataFrame, pd.DataFrame]:
    high = pd.read_csv(HIGH_POLLUTION_PATH)
    high = high[(high["dataset"] == "test") & (high["model"].isin(PRIMARY_MODEL_ORDER))]
    overall = pd.read_csv(TEST_METRICS_PATH)
    overall = overall[overall["model"].isin(PRIMARY_MODEL_ORDER)]
    return high.set_index("model"), overall.set_index("model")


def _panel(ax, high: pd.DataFrame, overall: pd.DataFrame, overall_col: str, high_col: str, xlabel: str) -> None:
    y_positions = range(len(PRIMARY_MODEL_ORDER))
    for y, model in zip(y_positions, PRIMARY_MODEL_ORDER):
        overall_value = overall.loc[model, overall_col]
        high_value = high.loc[model, high_col]
        ax.plot([overall_value, high_value], [y, y], color=NEUTRAL["subtle_grid"], lw=1.4, zorder=1)
        ax.scatter([overall_value], [y], color=NEUTRAL["contextual_line"], s=26, zorder=2, edgecolor="white", linewidth=0.3)
        ax.scatter([high_value], [y], color=PALETTE["primary_line"], s=30, zorder=3, edgecolor="white", linewidth=0.3)
        ax.text(
            high_value + (1.2 if high_value >= overall_value else -1.2),
            y,
            f"{high_value:.1f}",
            fontsize=6.8,
            ha="left" if high_value >= overall_value else "right",
            va="center",
            color=PALETTE["primary_line"],
        )

    ax.set_yticks(list(y_positions))
    ax.set_yticklabels([MODEL_LABELS[m] for m in PRIMARY_MODEL_ORDER])
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.set_ylim(len(PRIMARY_MODEL_ORDER) - 0.4, -0.6)
    strip_spines(ax, keep=("bottom",))
    ax.tick_params(axis="y", length=0)


def build_figure6():
    high, overall = _load()

    with publication_style():
        fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.6), constrained_layout=True)
        for ax, (overall_col, high_col, xlabel) in zip(axes, PANELS):
            _panel(ax, high, overall, overall_col, high_col, xlabel)

        fig.legend(
            handles=[
                plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=NEUTRAL["contextual_line"], markersize=6, label="Overall test set (n=8,565)"),
                plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=PALETTE["primary_line"], markersize=6, label="High-pollution subset (n=636, PM10 above training 90th pct.)"),
            ],
            loc="outside upper center",
            ncol=1,
            frameon=False,
            fontsize=7.2,
        )

        pdf_path, png_path = save_figure(fig, OUTPUT_STEM)
        plt.close(fig)
    return pdf_path, png_path


def main() -> None:
    pdf_path, png_path = build_figure6()
    print(f"Wrote: {pdf_path}")
    print(f"Wrote: {png_path}")


if __name__ == "__main__":
    main()

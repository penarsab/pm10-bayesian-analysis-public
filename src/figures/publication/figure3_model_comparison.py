"""Figure 3: overall model comparison across MAE, RMSE, CRPS, and 90% coverage.

Analytical source: frozen metric CSV files under `data/frozen_results`. No
metric is recomputed here.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from src.config import FIGURE_SOURCES_DIR
from src.figures.publication.common import (
    FIGURES_DIR,
    MODEL_LABELS,
    MODEL_ORDER,
    NEUTRAL,
    PALETTE,
    PRIMARY_MODELS,
    publication_style,
    save_figure,
    strip_spines,
)

TEST_METRICS_PATH = FIGURE_SOURCES_DIR / "test_metrics.csv"
CV_METRICS_PATH = FIGURE_SOURCES_DIR / "cv_metrics.csv"
OUTPUT_STEM = FIGURES_DIR / "figure3_model_comparison"

PANELS = [
    ("mae", "MAE [µg/m³]", "{:.2f}"),
    ("rmse", "RMSE [µg/m³]", "{:.2f}"),
    ("crps", "CRPS [µg/m³]", "{:.2f}"),
    ("coverage_90", "90% interval coverage", "{:.3f}"),
]


def _load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    test = pd.read_csv(TEST_METRICS_PATH)
    test = test.set_index("model").loc[MODEL_ORDER].reset_index()

    cv = pd.read_csv(CV_METRICS_PATH)
    cv_mean = cv.groupby("model")[["mae", "rmse", "crps", "coverage_90"]].mean()
    cv_mean = cv_mean.loc[MODEL_ORDER].reset_index()
    return test, cv_mean


def _panel(ax, test: pd.DataFrame, cv_mean: pd.DataFrame, metric: str, xlabel: str, fmt: str) -> None:
    y_positions = range(len(MODEL_ORDER))
    values = [test.loc[test["model"] == m, metric].iloc[0] for m in MODEL_ORDER]
    data_range = max(values) - min(0, min(values))
    dx = max(data_range, 1e-6) * 0.045

    for y, model, value in zip(y_positions, MODEL_ORDER, values):
        cv_value = cv_mean.loc[cv_mean["model"] == model, metric].iloc[0]
        is_primary = model in PRIMARY_MODELS
        color = PALETTE["primary_line"] if is_primary else NEUTRAL["contextual_line"]
        marker_size = 30 if is_primary else 22

        ax.scatter(
            [cv_value],
            [y],
            marker="|",
            s=80,
            color=NEUTRAL["subtle_grid"],
            linewidths=1.6,
            zorder=1,
        )
        ax.scatter([value], [y], s=marker_size, color=color, zorder=3, edgecolor="white", linewidth=0.4)
        ax.text(
            value + dx,
            y,
            fmt.format(value),
            fontsize=6.6,
            ha="left",
            va="center",
            color=color,
        )

    ax.set_xlim(left=max(0, min(values) - dx * 3.0), right=max(values) + dx * 6.5)

    if metric == "coverage_90":
        ax.axvline(0.90, color=NEUTRAL["reference_line"], lw=0.9, ls="--", zorder=0)
        ax.text(0.90, -1.05, "nominal\n0.90", fontsize=6.3, ha="center", va="bottom", color=NEUTRAL["reference_line"])

    ax.set_yticks(list(y_positions))
    ax.set_yticklabels([MODEL_LABELS[m] for m in MODEL_ORDER], fontsize=7.2)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel, fontsize=8)
    ax.set_ylim(len(MODEL_ORDER) - 0.4, -1.35)
    strip_spines(ax, keep=("bottom",))
    ax.tick_params(axis="y", length=0)


def build_figure3():
    test, cv_mean = _load_data()

    with publication_style():
        fig, axes = plt.subplots(2, 2, figsize=(7.0, 5.6), constrained_layout=True)
        for ax, (metric, xlabel, fmt) in zip(axes.flat, PANELS):
            _panel(ax, test, cv_mean, metric, xlabel, fmt)

        fig.legend(
            handles=[
                plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=PALETTE["primary_line"], markersize=7, label="Primary model (final test)"),
                plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=NEUTRAL["contextual_line"], markersize=6, label="Secondary model (final test)"),
                plt.Line2D([0], [0], marker="|", color=NEUTRAL["subtle_grid"], markersize=10, markeredgewidth=1.6, label="CV mean (4 folds)"),
            ],
            loc="outside upper center",
            ncol=3,
            frameon=False,
            fontsize=7.4,
        )

        pdf_path, png_path = save_figure(fig, OUTPUT_STEM)
        plt.close(fig)
    return pdf_path, png_path


def main() -> None:
    pdf_path, png_path = build_figure3()
    print(f"Wrote: {pdf_path}")
    print(f"Wrote: {png_path}")


if __name__ == "__main__":
    main()

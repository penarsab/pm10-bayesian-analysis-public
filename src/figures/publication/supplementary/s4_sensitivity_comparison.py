"""Supplementary Figure S4: M3 sensitivity to prior width and likelihood family.

Analytical source: frozen sensitivity metric and coefficient CSV files under
`data/frozen_results`. No sensitivity model is refit here.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
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

METRICS_PATH = FIGURE_SOURCES_DIR / "sensitivity_metrics.csv"
COEFFICIENTS_PATH = FIGURE_SOURCES_DIR / "sensitivity_coefficients.csv"
OUTPUT_STEM = SUPPLEMENTARY_DIR / "s4_sensitivity_comparison"

VARIANT_ORDER = ["M3_baseline", "M3_wide_priors", "M3_dynamic_student_t"]
VARIANT_LABELS = {"M3_baseline": "Baseline", "M3_wide_priors": "Wide priors", "M3_dynamic_student_t": "Student-t"}
VARIANT_COLORS = {"M3_baseline": PALETTE["primary_line"], "M3_wide_priors": PALETTE["secondary_line"], "M3_dynamic_student_t": "#B33B3B"}
VARIANT_MARKERS = {"M3_baseline": "o", "M3_wide_priors": "s", "M3_dynamic_student_t": "^"}
METRICS = ["mae", "rmse", "crps"]
METRIC_LABELS = {"mae": "MAE", "rmse": "RMSE", "crps": "CRPS"}
PREDICTOR_ORDER = ["temperature_lag1_z", "humidity_lag1_z", "wind_speed_lag1_z", "pressure_lag1_z"]
PREDICTOR_LABELS = {"temperature_lag1_z": "Temperature", "humidity_lag1_z": "Humidity", "wind_speed_lag1_z": "Wind speed", "pressure_lag1_z": "Pressure"}


def build_s4():
    metrics = pd.read_csv(METRICS_PATH).set_index("model").loc[VARIANT_ORDER]
    coefficients = pd.read_csv(COEFFICIENTS_PATH)

    with publication_style():
        fig = plt.figure(figsize=(7.0, 3.4), constrained_layout=True)
        grid = fig.add_gridspec(3, 2, width_ratios=(1.05, 1.55), wspace=0.24, hspace=0.16)
        metric_axes = [fig.add_subplot(grid[row, 0]) for row in range(3)]
        ax_coef = fig.add_subplot(grid[:, 1])

        y_positions = list(range(len(VARIANT_ORDER)))
        for ax_metric, metric in zip(metric_axes, METRICS):
            values = metrics.loc[VARIANT_ORDER, metric].to_numpy(dtype=float)
            axis_max = float(values.max()) * 1.25
            label_pad = axis_max * 0.015

            for y, variant, value in zip(y_positions, VARIANT_ORDER, values):
                color = VARIANT_COLORS[variant]
                ax_metric.hlines(y, 0.0, value, color=color, lw=1.5)
                ax_metric.scatter(
                    [value],
                    [y],
                    color=color,
                    marker=VARIANT_MARKERS[variant],
                    s=25,
                    zorder=3,
                    edgecolor="white",
                    linewidth=0.35,
                )
                ax_metric.text(value + label_pad, y, f"{value:.3f}", va="center", fontsize=6.4)

            ax_metric.set_xlim(0.0, axis_max)
            ax_metric.set_ylim(len(VARIANT_ORDER) - 0.5, -0.5)
            ax_metric.set_yticks(y_positions)
            ax_metric.set_yticklabels([VARIANT_LABELS[variant] for variant in VARIANT_ORDER], fontsize=6.6)
            ax_metric.set_title(METRIC_LABELS[metric], loc="left", pad=1.5)
            ax_metric.xaxis.set_major_locator(MaxNLocator(nbins=3))
            ax_metric.tick_params(axis="y", length=0)
            strip_spines(ax_metric, keep=("bottom",))

        metric_axes[-1].set_xlabel("µg/m³")

        y_positions = range(len(PREDICTOR_ORDER))
        offsets = {"M3_baseline": -0.22, "M3_wide_priors": 0.0, "M3_dynamic_student_t": 0.22}
        for row_idx, predictor in enumerate(PREDICTOR_ORDER):
            for variant in VARIANT_ORDER:
                record = coefficients[(coefficients["model"] == variant) & (coefficients["predictor"] == predictor)].iloc[0]
                y = row_idx + offsets[variant]
                ax_coef.plot([record["q05"], record["q95"]], [y, y], color=VARIANT_COLORS[variant], lw=1.4, solid_capstyle="round")
                ax_coef.scatter(
                    [record["median"]],
                    [y],
                    color=VARIANT_COLORS[variant],
                    marker=VARIANT_MARKERS[variant],
                    s=24,
                    zorder=3,
                    edgecolor="white",
                    linewidth=0.3,
                )

        ax_coef.axvline(0, color=NEUTRAL["reference_line"], lw=0.8, ls="--")
        ax_coef.set_yticks(list(y_positions))
        ax_coef.set_yticklabels([PREDICTOR_LABELS[p] for p in PREDICTOR_ORDER])
        ax_coef.invert_yaxis()
        ax_coef.set_xlabel(r"Standardized coefficient (log-PM$_{10}$ scale)")
        ax_coef.set_ylim(len(PREDICTOR_ORDER) - 0.4, -0.6)
        strip_spines(ax_coef, keep=("bottom",))
        ax_coef.tick_params(axis="y", length=0)
        legend_handles = [
            Line2D(
                [],
                [],
                color=VARIANT_COLORS[variant],
                marker=VARIANT_MARKERS[variant],
                lw=1.4,
                markersize=4.5,
                label=VARIANT_LABELS[variant],
            )
            for variant in VARIANT_ORDER
        ]
        ax_coef.legend(
            handles=legend_handles,
            frameon=False,
            ncol=3,
            loc="lower center",
            bbox_to_anchor=(0.5, 1.0),
            fontsize=6.6,
            handlelength=1.8,
            columnspacing=1.1,
        )

        pdf_path, png_path = save_figure(fig, OUTPUT_STEM)
        plt.close(fig)
    return pdf_path, png_path


def main() -> None:
    pdf_path, png_path = build_s4()
    print(f"Wrote: {pdf_path}")
    print(f"Wrote: {png_path}")


if __name__ == "__main__":
    main()

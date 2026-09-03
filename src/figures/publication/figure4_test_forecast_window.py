"""Figure 4: three forecast-window zooms for the final test period.

This public generator preserves the accepted revision layout: one calm week,
one winter-smog episode, and one transition-season rapid-increase week.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import FIGURE_SOURCES_DIR
from src.figures.publication.common import (
    FIGURES_DIR,
    NEUTRAL,
    PALETTE,
    publication_style,
    save_figure,
    strip_spines,
)

PREDICTIONS_PATH = FIGURE_SOURCES_DIR / "test_predictions.csv"
HIGH_POLLUTION_METRICS_PATH = FIGURE_SOURCES_DIR / "high_pollution_metrics.csv"
OUTPUT_STEM = FIGURES_DIR / "figure4_test_forecast_windows"

WINDOW_HOURS = 24 * 7
MIN_WINDOW_ROWS = 24 * 6
REQUIRED_MODELS = ("M3_dynamic_regression", "B1_persistence")


@dataclass(frozen=True)
class WindowChoice:
    key: str
    title: str
    start: pd.Timestamp
    end: pd.Timestamp
    rationale: str


def _high_pollution_threshold() -> float:
    if not HIGH_POLLUTION_METRICS_PATH.exists():
        raise FileNotFoundError(
            "Figure 4 high-pollution metrics file is missing: "
            f"{HIGH_POLLUTION_METRICS_PATH}"
        )

    metrics = pd.read_csv(HIGH_POLLUTION_METRICS_PATH)
    threshold_column = "threshold_q90_train"
    if threshold_column not in metrics.columns:
        raise KeyError(
            f"Missing required column {threshold_column!r} in "
            f"{HIGH_POLLUTION_METRICS_PATH}"
        )

    selector_columns = {"dataset", "model"}
    missing_selectors = selector_columns.difference(metrics.columns)
    if missing_selectors:
        raise ValueError(
            "Cannot identify the final-test M3 threshold row because "
            f"{HIGH_POLLUTION_METRICS_PATH} is missing selector column(s): "
            f"{', '.join(sorted(missing_selectors))}"
        )

    matching_rows = metrics.loc[
        (metrics["dataset"] == "test")
        & (metrics["model"] == "M3_dynamic_regression")
    ]
    if len(matching_rows) != 1:
        raise ValueError(
            "Expected exactly one final-test M3 threshold row in "
            f"{HIGH_POLLUTION_METRICS_PATH}, found {len(matching_rows)}"
        )

    try:
        threshold = float(matching_rows.iloc[0][threshold_column])
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid {threshold_column!r} value in the final-test M3 row of "
            f"{HIGH_POLLUTION_METRICS_PATH}"
        ) from exc
    if not math.isfinite(threshold) or threshold <= 0:
        raise ValueError(
            f"Expected a finite, positive {threshold_column!r} value in the "
            f"final-test M3 row of {HIGH_POLLUTION_METRICS_PATH}; got {threshold!r}"
        )
    return threshold


def _model_frame(predictions: pd.DataFrame, model: str, columns: dict[str, str]) -> pd.DataFrame:
    frame = predictions.loc[predictions["model"] == model, ["datetime", *columns]].copy()
    if frame.empty:
        raise ValueError(f"Missing model {model} in {PREDICTIONS_PATH}.")
    return frame.rename(columns=columns).sort_values("datetime").reset_index(drop=True)


def load_forecast_data() -> pd.DataFrame:
    predictions = pd.read_csv(PREDICTIONS_PATH, parse_dates=["datetime"])
    available = set(predictions["model"].astype(str).unique())
    missing = [model for model in REQUIRED_MODELS if model not in available]
    if missing:
        raise ValueError(f"Missing required models in {PREDICTIONS_PATH}: {missing}")

    m3 = _model_frame(
        predictions,
        "M3_dynamic_regression",
        {
            "observed_pm10": "observed_pm10",
            "point_median": "m3_median",
            "q05": "m3_q05",
            "q95": "m3_q95",
        },
    )
    b1 = _model_frame(predictions, "B1_persistence", {"point_median": "persistence"})
    data = m3.merge(b1, on="datetime", how="inner", validate="one_to_one")

    if "B2_arx" in available:
        arx = _model_frame(predictions, "B2_arx", {"point_median": "arx_median"})
        data = data.merge(arx, on="datetime", how="inner", validate="one_to_one")

    expected_rows = predictions.loc[
        predictions["model"] == "M3_dynamic_regression", "datetime"
    ].nunique()
    if len(data) != expected_rows:
        raise ValueError("Merged forecast data does not retain every M3 final-test timestamp.")
    return data.sort_values("datetime").reset_index(drop=True)


def _candidate_starts(data: pd.DataFrame) -> list[pd.Timestamp]:
    starts: list[pd.Timestamp] = []
    max_start = data["datetime"].max() - pd.Timedelta(days=7) + pd.Timedelta(hours=1)
    for timestamp in data.loc[data["datetime"].dt.hour == 0, "datetime"]:
        if timestamp <= max_start:
            starts.append(pd.Timestamp(timestamp))
    return starts


def _window_stats(data: pd.DataFrame, start: pd.Timestamp, threshold: float) -> dict[str, object]:
    end = start + pd.Timedelta(days=7) - pd.Timedelta(hours=1)
    window = data.loc[(data["datetime"] >= start) & (data["datetime"] <= end)].copy()
    if len(window) < MIN_WINDOW_ROWS:
        raise ValueError(f"Window starting {start} has only {len(window)} rows.")

    observed = window["observed_pm10"].to_numpy(dtype=float)
    current = window[["datetime", "observed_pm10"]].rename(
        columns={"observed_pm10": "current_pm10"}
    )
    lagged = current.rename(columns={"current_pm10": "pm10_24h_before"}).copy()
    lagged["datetime"] = lagged["datetime"] + pd.Timedelta(hours=24)
    diff24 = current.merge(lagged, on="datetime", how="left")
    increase_24h = diff24["current_pm10"] - diff24["pm10_24h_before"]
    return {
        "start": start,
        "end": end,
        "n": int(len(window)),
        "mean": float(np.mean(observed)),
        "std": float(np.std(observed, ddof=0)),
        "max": float(np.max(observed)),
        "min": float(np.min(observed)),
        "range": float(np.max(observed) - np.min(observed)),
        "high_hours": int(np.sum(observed > threshold)),
        "max_24h_increase": float(increase_24h.max(skipna=True)),
    }


def _anchored_week_stats(
    data: pd.DataFrame,
    peak_time: pd.Timestamp,
    days_before_peak: int,
    threshold: float,
) -> dict[str, object]:
    start = pd.Timestamp(peak_time).normalize() - pd.Timedelta(days=days_before_peak)
    min_start = data["datetime"].min().ceil("D")
    max_start = data["datetime"].max() - pd.Timedelta(days=7) + pd.Timedelta(hours=1)
    start = max(start, min_start)
    start = min(start, max_start.normalize())
    return _window_stats(data, start, threshold)


def choose_windows(data: pd.DataFrame, threshold: float) -> list[WindowChoice]:
    records = []
    for start in _candidate_starts(data):
        try:
            records.append(_window_stats(data, start, threshold))
        except ValueError:
            continue
    stats = pd.DataFrame(records)
    if stats.empty:
        raise ValueError("No complete 7-day windows found in final-test predictions.")

    calm_pool = stats.loc[(stats["high_hours"] == 0) & (stats["max"] < threshold)].copy()
    if calm_pool.empty:
        calm_pool = stats.loc[stats["high_hours"] == stats["high_hours"].min()].copy()
    calm = calm_pool.sort_values(["std", "mean", "max"]).iloc[0]

    winter_rows = data.loc[data["datetime"].dt.month.isin([1, 2, 12])]
    if winter_rows.empty:
        winter_rows = data
    winter_peak_time = winter_rows.loc[winter_rows["observed_pm10"].idxmax(), "datetime"]
    winter = pd.Series(
        _anchored_week_stats(data, winter_peak_time, days_before_peak=5, threshold=threshold)
    )

    transition_rows = data.loc[data["datetime"].dt.month.isin([3, 4, 5, 9, 10, 11])]
    if transition_rows.empty:
        transition_rows = data
    transition_peak_time = transition_rows.loc[
        transition_rows["observed_pm10"].idxmax(), "datetime"
    ]
    transition = pd.Series(
        _anchored_week_stats(
            data, transition_peak_time, days_before_peak=3, threshold=threshold
        )
    )

    return [
        WindowChoice(
            key="calm",
            title="A. Calm week without high-PM10 episode",
            start=pd.Timestamp(calm["start"]),
            end=pd.Timestamp(calm["end"]),
            rationale=(
                f"low variability, max {calm['max']:.1f} ug/m3 and "
                f"{int(calm['high_hours'])} hours above train Q90"
            ),
        ),
        WindowChoice(
            key="winter_smog",
            title="B. Winter smog episode",
            start=pd.Timestamp(winter["start"]),
            end=pd.Timestamp(winter["end"]),
            rationale=(
                f"{int(winter['high_hours'])} hours above train Q90, "
                f"peak {winter['max']:.1f} ug/m3"
            ),
        ),
        WindowChoice(
            key="rapid_increase",
            title="C. Transitional rapid-increase week",
            start=pd.Timestamp(transition["start"]),
            end=pd.Timestamp(transition["end"]),
            rationale=(
                f"largest transition-season 24h increase "
                f"{transition['max_24h_increase']:.1f} ug/m3, "
                f"peak {transition['max']:.1f} ug/m3"
            ),
        ),
    ]


def _window_slice(data: pd.DataFrame, choice: WindowChoice) -> pd.DataFrame:
    return data.loc[(data["datetime"] >= choice.start) & (data["datetime"] <= choice.end)].copy()


def draw_forecast_windows(
    data: pd.DataFrame,
    choices: list[WindowChoice],
    threshold: float,
    output_stem=OUTPUT_STEM,
) -> tuple[plt.Figure, list[plt.Axes]]:
    has_arx = "arx_median" in data.columns

    with publication_style():
        fig, axes = plt.subplots(len(choices), 1, figsize=(8.2, 7.2), sharey=False)
        if len(choices) == 1:
            axes = [axes]

        for ax, choice in zip(axes, choices, strict=True):
            window = _window_slice(data, choice)
            if len(window) < MIN_WINDOW_ROWS:
                raise ValueError(
                    f"{choice.key} window has {len(window)} rows, "
                    f"expected at least {MIN_WINDOW_ROWS}."
                )

            ax.fill_between(
                window["datetime"],
                window["m3_q05"],
                window["m3_q95"],
                color=PALETTE["outer_interval_fill"],
                alpha=0.50,
                linewidth=0,
                label="M3 90% interval",
            )
            ax.plot(
                window["datetime"],
                window["m3_median"],
                color=PALETTE["primary_line"],
                linewidth=1.25,
                label="M3 median",
            )
            ax.plot(
                window["datetime"],
                window["persistence"],
                color=NEUTRAL["contextual_line"],
                linewidth=0.95,
                linestyle="--",
                label="Persistence",
            )
            if has_arx:
                ax.plot(
                    window["datetime"],
                    window["arx_median"],
                    color="#2CA25F",
                    linewidth=0.95,
                    linestyle="-.",
                    label="ARX(1)",
                )
            ax.plot(
                window["datetime"],
                window["observed_pm10"],
                color=NEUTRAL["general_text"],
                linewidth=1.15,
                label="Observed",
            )
            ax.axhline(
                threshold,
                color=NEUTRAL["reference_line"],
                linestyle=":",
                linewidth=0.75,
            )
            ax.set_title(
                f"{choice.title}: {choice.start:%Y-%m-%d} to {choice.end:%Y-%m-%d}",
                loc="left",
                fontsize=9.2,
                fontweight="bold",
            )
            ax.text(
                0.01,
                0.92,
                choice.rationale,
                transform=ax.transAxes,
                ha="left",
                va="top",
                fontsize=7.0,
                color=NEUTRAL["axes_and_spines"],
            )
            ax.set_ylabel("PM10 [ug/m3]")
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
            ax.grid(
                True,
                axis="y",
                color=NEUTRAL["subtle_grid"],
                linewidth=0.6,
                alpha=0.7,
            )
            strip_spines(ax)

        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(
            handles,
            labels,
            loc="upper center",
            bbox_to_anchor=(0.5, 0.955),
            ncol=5,
            frameon=False,
        )
        fig.suptitle(
            "Weekly forecast-window zooms for the final test period",
            fontsize=12.5,
            fontweight="bold",
            y=0.995,
        )
        fig.text(
            0.5,
            0.918,
            "M3 uncertainty is the 90% predictive interval; dotted horizontal line "
            f"is final-train PM10 Q90 = {threshold:.2f} ug/m3.",
            ha="center",
            va="center",
            fontsize=8.0,
            color=NEUTRAL["general_text"],
        )
        fig.subplots_adjust(top=0.85, bottom=0.08, left=0.08, right=0.99, hspace=0.42)
    return fig, list(axes)


def build_figure4():
    threshold = _high_pollution_threshold()
    data = load_forecast_data()
    choices = choose_windows(data, threshold)
    fig, _ = draw_forecast_windows(data, choices, threshold)
    pdf_path, png_path = save_figure(fig, OUTPUT_STEM)
    plt.close(fig)
    return pdf_path, png_path


def main() -> None:
    pdf_path, png_path = build_figure4()
    print(f"Wrote: {pdf_path}")
    print(f"Wrote: {png_path}")


if __name__ == "__main__":
    main()

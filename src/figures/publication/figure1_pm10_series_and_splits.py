"""Figure 1: full PM10 series with the rolling-origin CV and final test split structure.

Analytical source: frozen CSV/JSON inputs under `data/frozen_results`. No
filtering, aggregation, or transformation is applied beyond parsing datetimes
for plotting.
"""

from __future__ import annotations

import json

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from src.config import FIGURE_SOURCES_DIR, MODEL_METADATA_DIR
from src.figures.publication.common import (
    FIGURES_DIR,
    NEUTRAL,
    PALETTE,
    publication_style,
    save_figure,
    strip_spines,
)

DATA_PATH = FIGURE_SOURCES_DIR / "pm10_series.csv"
SPLITS_PATH = MODEL_METADATA_DIR / "splits.json"
OUTPUT_STEM = FIGURES_DIR / "figure1_pm10_series_and_splits"

TEST_COLOR = PALETTE["primary_emphasis"]
CV_COLOR = PALETTE["primary_line"]
TRAIN_COLOR = NEUTRAL["contextual_line"]

BAR_Y = 0.5
BAR_HEIGHT = 0.6


def _load_series() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["datetime"])
    return df.sort_values("datetime")


def _load_splits() -> dict:
    with SPLITS_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def _span_days(start: pd.Timestamp, end: pd.Timestamp) -> float:
    return mdates.date2num(end) - mdates.date2num(start)


def _draw_split_timeline(ax, dataset_start, cv_folds, test_start, test_end) -> None:
    ax.barh(
        BAR_Y,
        _span_days(dataset_start, cv_folds[0][0]),
        left=mdates.date2num(dataset_start),
        height=BAR_HEIGHT,
        color=TRAIN_COLOR,
        edgecolor="none",
        label="Training window (expanding across folds)",
    )
    ax.text(
        mdates.date2num(dataset_start) + _span_days(dataset_start, cv_folds[0][0]) / 2,
        BAR_Y,
        "initial\ntraining",
        ha="center",
        va="center",
        fontsize=6.3,
        color="white",
    )

    for start, end, name in cv_folds:
        ax.barh(
            BAR_Y,
            _span_days(start, end),
            left=mdates.date2num(start),
            height=BAR_HEIGHT,
            color=CV_COLOR,
            edgecolor="white",
            linewidth=0.6,
            hatch="///",
            label="Rolling-origin CV validation window" if name == cv_folds[0][2] else None,
        )
        ax.text(
            mdates.date2num(start) + _span_days(start, end) / 2,
            BAR_Y,
            name.replace("_", " "),
            ha="center",
            va="center",
            fontsize=6.0,
            color="white",
            rotation=90,
        )

    ax.barh(
        BAR_Y,
        _span_days(test_start, test_end),
        left=mdates.date2num(test_start),
        height=BAR_HEIGHT,
        color=TEST_COLOR,
        edgecolor="none",
        label="Final held-out test window",
    )
    ax.text(
        mdates.date2num(test_start) + _span_days(test_start, test_end) / 2,
        BAR_Y,
        "final test\n(held out)",
        ha="center",
        va="center",
        fontsize=6.3,
        color="white",
    )

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.55),
        ncol=3,
        frameon=False,
        fontsize=7,
        handlelength=1.4,
    )


def build_figure1() -> tuple:
    series = _load_series()
    splits = _load_splits()

    dataset_start = pd.Timestamp(splits["datetime_start"])
    cv_folds = [
        (pd.Timestamp(fold["prediction_start"]), pd.Timestamp(fold["prediction_end"]), fold["name"])
        for fold in splits["cv"]
    ]
    test_start = pd.Timestamp(splits["test"]["prediction_start"])
    test_end = pd.Timestamp(splits["test"]["prediction_end"])

    with publication_style():
        fig, (ax_series, ax_splits) = plt.subplots(
            2,
            1,
            figsize=(7.0, 4.6),
            sharex=True,
            gridspec_kw={"height_ratios": [3.4, 1.0], "hspace": 0.08},
            constrained_layout=True,
        )

        ax_series.plot(
            series["datetime"],
            series["PM10"],
            color=NEUTRAL["axes_and_spines"],
            lw=0.35,
            alpha=0.9,
        )
        ax_series.set_ylabel("PM10 [µg/m³]")
        ax_series.axvspan(cv_folds[0][0], test_start, color=CV_COLOR, alpha=0.07, lw=0)
        ax_series.axvspan(test_start, test_end, color=TEST_COLOR, alpha=0.10, lw=0)
        strip_spines(ax_series)

        _draw_split_timeline(ax_splits, dataset_start, cv_folds, test_start, test_end)
        ax_splits.set_yticks([])
        ax_splits.set_ylim(0, 1)
        strip_spines(ax_splits, keep=("bottom",))
        ax_splits.xaxis.set_major_locator(mdates.YearLocator())
        ax_splits.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        fig.supxlabel("Date", fontsize=9)

        pdf_path, png_path = save_figure(fig, OUTPUT_STEM)
        plt.close(fig)
    return pdf_path, png_path


def main() -> None:
    pdf_path, png_path = build_figure1()
    print(f"Wrote: {pdf_path}")
    print(f"Wrote: {png_path}")


if __name__ == "__main__":
    main()

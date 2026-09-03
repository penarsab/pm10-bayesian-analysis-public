"""Supplementary Figure S5: high-pollution persistence safeguard."""

from __future__ import annotations

import os
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_MPLCONFIGDIR = Path(__file__).resolve().parents[2] / "tmp" / "matplotlib"
_MPLCONFIGDIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_MPLCONFIGDIR))

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt

from src.config import FIGURE_SOURCES_DIR, MODEL_METADATA_DIR, PROJECT_ROOT, config_section
from src.figures.publication.common import NEUTRAL, PALETTE, publication_style


TEST_PREDICTIONS_PATH = FIGURE_SOURCES_DIR / "test_predictions.csv"
MODELING_TABLE_PATH = FIGURE_SOURCES_DIR / "modeling_table.csv"
SPLITS_PATH = MODEL_METADATA_DIR / "splits.json"
FIGURE_PATH = PROJECT_ROOT / "figures" / "generated" / "supplementary" / "s5_high_pollution_safeguard.pdf"

SAFEGUARD_QUANTILES = (0.80, 0.90, 0.95)
HIGH_POLLUTION_QUANTILE = 0.90
MODEL_ORDER = (
    "M3_dynamic_regression",
    "B1_persistence",
    "M3_safeguard_q80",
    "M3_safeguard_q90",
    "M3_safeguard_q95",
)
MODEL_LABELS = {
    "M3_dynamic_regression": "M3",
    "B1_persistence": "Persistence",
    "M3_safeguard_q80": "Safeguard Q80",
    "M3_safeguard_q90": "Safeguard Q90",
    "M3_safeguard_q95": "Safeguard Q95",
}
LAG_COLUMNS = {
    "temp": "temp_lag1",
    "humidity": "humidity_lag1",
    "windspeed": "windspeed_lag1",
    "surface_pressure": "pressure_lag1",
}


@dataclass(frozen=True)
class FinalSplitData:
    train: pd.DataFrame
    test: pd.DataFrame


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def _load_final_split_data() -> FinalSplitData:
    raw = pd.read_csv(MODELING_TABLE_PATH, parse_dates=["datetime"])
    raw = raw.sort_values("datetime").reset_index(drop=True)
    grid = pd.DataFrame({"datetime": pd.date_range(raw["datetime"].min(), raw["datetime"].max(), freq="h")})
    data = grid.merge(raw, on="datetime", how="left")

    max_forward_fill_steps = int(config_section("data")["max_forward_fill_steps"])
    meteo_columns = ["temp", "humidity", "windspeed", "surface_pressure"]
    data[meteo_columns] = data[meteo_columns].ffill(limit=max_forward_fill_steps)
    data["PM10"] = pd.to_numeric(data["PM10"], errors="coerce")
    data["z"] = np.log(data["PM10"])
    for source_col, lag_col in LAG_COLUMNS.items():
        data[lag_col] = data[source_col].shift(1)
    data["pm10_prev"] = data["PM10"].shift(1)
    data["log_pm10_prev"] = np.log(data["pm10_prev"])
    data = data.dropna(subset=["PM10", "z", "pm10_prev", "log_pm10_prev", *LAG_COLUMNS.values()]).reset_index(drop=True)

    with SPLITS_PATH.open(encoding="utf-8") as handle:
        split = json.load(handle)["test"]

    train = data.iloc[split["train_start_idx"] : split["train_end_idx"] + 1].copy().reset_index(drop=True)
    test = data.iloc[split["prediction_start_idx"] : split["prediction_end_idx"] + 1].copy().reset_index(drop=True)
    return FinalSplitData(train=train, test=test)

def _prediction_frame(predictions: pd.DataFrame, model: str) -> pd.DataFrame:
    frame = predictions.loc[predictions["model"] == model].copy()
    if frame.empty:
        raise ValueError(f"Missing {model} in {TEST_PREDICTIONS_PATH}.")
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    return frame.sort_values("datetime").reset_index(drop=True)


def _assert_final_test_alignment(prepared_test: pd.DataFrame, m3: pd.DataFrame, persistence: pd.DataFrame) -> None:
    expected_timestamps = pd.to_datetime(prepared_test["datetime"]).reset_index(drop=True)
    for model_name, frame in {"M3_dynamic_regression": m3, "B1_persistence": persistence}.items():
        if not frame["datetime"].reset_index(drop=True).equals(expected_timestamps):
            raise ValueError(f"{model_name} timestamps do not match the authoritative final-test split.")
        if not np.allclose(frame["observed_pm10"].to_numpy(dtype=float), prepared_test["PM10"].to_numpy(dtype=float)):
            raise ValueError(f"{model_name} observed PM10 values do not match the final-test split.")

    pm10_prev = prepared_test["pm10_prev"].to_numpy(dtype=float)
    if not np.allclose(persistence["point_median"].to_numpy(dtype=float), pm10_prev):
        raise ValueError("B1 persistence point_median is not identical to final-test pm10_prev.")
    if not np.allclose(persistence["point_mean"].to_numpy(dtype=float), pm10_prev):
        raise ValueError("B1 persistence point_mean is not identical to final-test pm10_prev.")


def _metrics_row(
    *,
    model: str,
    frame: pd.DataFrame,
    threshold_quantile: float | None,
    threshold_value: float | None,
    train_high_threshold: float,
) -> dict[str, Any]:
    observed = frame["observed_pm10"].to_numpy(dtype=float)
    point_median = frame["point_median"].to_numpy(dtype=float)
    point_mean = frame["point_mean"].to_numpy(dtype=float)
    high_mask = observed > train_high_threshold
    activated = frame["safeguard_activated"].to_numpy(dtype=bool)
    high_observed = observed[high_mask]
    high_median = point_median[high_mask]
    high_mean = point_mean[high_mask]
    return {
        "dataset": "final_test",
        "model": model,
        "model_label": MODEL_LABELS[model],
        "forecast_rule": (
            "Use previous-hour PM10 when previous-hour PM10 exceeds the listed training quantile; otherwise use M3."
            if model.startswith("M3_safeguard")
            else "Existing final-test prediction."
        ),
        "n": int(len(observed)),
        "mae": mae(observed, point_median),
        "rmse": rmse(observed, point_mean),
        "high_pollution_threshold_q90_train": train_high_threshold,
        "n_high": int(high_mask.sum()),
        "mae_high": mae(high_observed, high_median),
        "rmse_high": rmse(high_observed, high_mean),
        "safeguard_threshold_quantile": threshold_quantile,
        "safeguard_threshold_value": threshold_value,
        "safeguard_activated_hours": int(activated.sum()),
        "safeguard_activated_share": float(activated.mean()),
        "safeguard_activated_high_pollution_hours": int((activated & high_mask).sum()),
        "safeguard_activated_high_pollution_share": float((activated & high_mask).sum() / max(1, high_mask.sum())),
        "mae_point_column": "point_median",
        "rmse_point_column": "point_mean",
    }


def build_safeguard_predictions() -> tuple[pd.DataFrame, dict[float, pd.DataFrame], float]:
    prepared = _load_final_split_data()
    predictions = pd.read_csv(TEST_PREDICTIONS_PATH, parse_dates=["datetime"])
    m3 = _prediction_frame(predictions, "M3_dynamic_regression")
    persistence = _prediction_frame(predictions, "B1_persistence")
    _assert_final_test_alignment(prepared.test, m3, persistence)

    observed = prepared.test["PM10"].to_numpy(dtype=float)
    pm10_prev = prepared.test["pm10_prev"].to_numpy(dtype=float)
    m3_median = m3["point_median"].to_numpy(dtype=float)
    m3_mean = m3["point_mean"].to_numpy(dtype=float)
    persistence_point = persistence["point_median"].to_numpy(dtype=float)

    thresholds = {
        quantile: float(prepared.train["PM10"].quantile(quantile))
        for quantile in (*SAFEGUARD_QUANTILES, HIGH_POLLUTION_QUANTILE)
    }
    high_threshold = thresholds[HIGH_POLLUTION_QUANTILE]
    base_columns = {
        "datetime": pd.to_datetime(prepared.test["datetime"]),
        "observed_pm10": observed,
        "pm10_prev": pm10_prev,
    }
    never_activated = np.zeros(len(observed), dtype=bool)

    metric_frames = [
        pd.DataFrame(
            {
                **base_columns,
                "model": "M3_dynamic_regression",
                "point_mean": m3_mean,
                "point_median": m3_median,
                "safeguard_threshold_quantile": np.nan,
                "safeguard_threshold_value": np.nan,
                "safeguard_activated": never_activated,
                "forecast_source": "M3",
            }
        ),
        pd.DataFrame(
            {
                **base_columns,
                "model": "B1_persistence",
                "point_mean": persistence_point,
                "point_median": persistence_point,
                "safeguard_threshold_quantile": np.nan,
                "safeguard_threshold_value": np.nan,
                "safeguard_activated": never_activated,
                "forecast_source": "persistence",
            }
        ),
    ]
    output_frames: dict[float, pd.DataFrame] = {}

    for quantile in SAFEGUARD_QUANTILES:
        threshold = thresholds[quantile]
        activated = pm10_prev > threshold
        suffix = int(round(quantile * 100))
        model = f"M3_safeguard_q{suffix}"
        hybrid_point_median = np.where(activated, pm10_prev, m3_median)
        hybrid_point_mean = np.where(activated, pm10_prev, m3_mean)
        safeguard_frame = pd.DataFrame(
                {
                    **base_columns,
                    "model": model,
                    "point_mean": hybrid_point_mean,
                    "point_median": hybrid_point_median,
                "safeguard_threshold_quantile": quantile,
                "safeguard_threshold_value": threshold,
                "safeguard_activated": activated,
                "forecast_source": np.where(activated, "persistence", "M3"),
            }
        )
        output_frames[quantile] = safeguard_frame.sort_values("datetime").reset_index(drop=True)
        metric_frames.append(safeguard_frame)

    metric_predictions = pd.concat(metric_frames, ignore_index=True)
    metric_predictions["model"] = pd.Categorical(
        metric_predictions["model"],
        categories=list(MODEL_ORDER),
        ordered=True,
    )
    return metric_predictions.sort_values(["model", "datetime"]).reset_index(drop=True), output_frames, high_threshold


def build_safeguard_metrics(safeguard_predictions: pd.DataFrame, high_threshold: float) -> pd.DataFrame:
    rows = []
    for model in MODEL_ORDER:
        group = safeguard_predictions.loc[safeguard_predictions["model"].astype(str) == model].copy()
        threshold_quantile = group["safeguard_threshold_quantile"].dropna()
        threshold_value = group["safeguard_threshold_value"].dropna()
        rows.append(
            _metrics_row(
                model=model,
                frame=group,
                threshold_quantile=float(threshold_quantile.iloc[0]) if len(threshold_quantile) else None,
                threshold_value=float(threshold_value.iloc[0]) if len(threshold_value) else None,
                train_high_threshold=high_threshold,
            )
        )

    metrics = pd.DataFrame(rows)
    metrics["model"] = pd.Categorical(metrics["model"], categories=list(MODEL_ORDER), ordered=True)
    return metrics.sort_values("model").reset_index(drop=True)


def draw_safeguard_figure(metrics: pd.DataFrame, output_path: Path = FIGURE_PATH) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame = metrics.copy()
    frame["model"] = frame["model"].astype(str)
    ordered = frame.set_index("model").loc[list(MODEL_ORDER)]
    labels = [MODEL_LABELS[model] for model in MODEL_ORDER]
    x = np.arange(len(MODEL_ORDER))
    bar_width = 0.68
    grouped_width = 0.34
    mae_color = PALETTE["primary_line"]
    rmse_color = "#D95F02"
    activation_all_color = NEUTRAL["contextual_line"]

    with publication_style():
        fig, axes = plt.subplot_mosaic(
            [["A", "B", "C"], ["D", "E", "C"]],
            figsize=(10.8, 5.9),
            gridspec_kw={"width_ratios": [1.0, 1.0, 1.05]},
        )

        absolute_panels = [
            ("A", "mae_high", "A. High-pollution MAE", "MAE [ug/m3]", mae_color),
            ("B", "rmse_high", "B. High-pollution RMSE", "RMSE [ug/m3]", rmse_color),
        ]
        for key, column, title, ylabel, color in absolute_panels:
            ax = axes[key]
            ax.bar(x, ordered[column].to_numpy(dtype=float), width=bar_width, color=color)
            ax.set_title(title, loc="left", fontsize=9, fontweight="bold")
            ax.set_ylabel(ylabel)
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=28, ha="right")
            ax.grid(True, axis="y", color=NEUTRAL["subtle_grid"], linewidth=0.6, alpha=0.7)

        delta_panels = [
            ("D", "mae", "D. Full-test MAE difference vs M3", "Difference [ug/m3]", mae_color),
            ("E", "rmse", "E. Full-test RMSE difference vs M3", "Difference [ug/m3]", rmse_color),
        ]
        for key, column, title, ylabel, color in delta_panels:
            ax = axes[key]
            delta = ordered[column].to_numpy(dtype=float) - float(ordered.loc["M3_dynamic_regression", column])
            ax.bar(x, delta, width=bar_width, color=color)
            ax.axhline(0.0, color=NEUTRAL["reference_line"], linewidth=0.9)
            ax.set_title(title, loc="left", fontsize=9, fontweight="bold")
            ax.set_ylabel(ylabel)
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=28, ha="right")
            ax.grid(True, axis="y", color=NEUTRAL["subtle_grid"], linewidth=0.6, alpha=0.7)
            limit = max(0.04, float(np.nanmax(np.abs(delta))) * 1.25)
            ax.set_ylim(-limit, limit)
            ax.text(
                0.02,
                0.96,
                "negative = better than M3",
                transform=ax.transAxes,
                ha="left",
                va="top",
                fontsize=7.0,
                color=NEUTRAL["axes_and_spines"],
            )

        activation_models = ["M3_safeguard_q80", "M3_safeguard_q90", "M3_safeguard_q95"]
        activation_labels = [MODEL_LABELS[model].replace("Safeguard ", "") for model in activation_models]
        activation_x = np.arange(len(activation_models))
        activation = ordered.loc[activation_models, "safeguard_activated_hours"].to_numpy(dtype=float)
        total_hours = int(ordered.loc["M3_dynamic_regression", "n"])
        axes["C"].bar(
            activation_x,
            activation,
            width=bar_width,
            color=activation_all_color,
        )
        axes["C"].set_title(f"C. Activations (of {total_hours:,} test hours)", loc="left", fontsize=9, fontweight="bold")
        axes["C"].set_ylabel("Hours")
        axes["C"].set_xticks(activation_x)
        axes["C"].set_xticklabels(activation_labels, rotation=0, ha="center")
        for xpos, value in zip(activation_x, activation, strict=True):
            axes["C"].text(
                xpos,
                value,
                f"{int(value):,}\n({value / total_hours * 100:.1f}%)",
                ha="center",
                va="bottom",
                fontsize=7.2,
                color=NEUTRAL["general_text"],
            )
        axes["C"].set_ylim(0, float(np.nanmax(activation)) * 1.18)
        axes["C"].grid(True, axis="y", color=NEUTRAL["subtle_grid"], linewidth=0.6, alpha=0.7)

        q90 = float(ordered["high_pollution_threshold_q90_train"].iloc[0])
        n_high = int(ordered["n_high"].iloc[0])
        fig.suptitle("Persistence safeguard reduces high-pollution point error", fontsize=12.5, fontweight="bold", y=0.985)
        fig.text(
            0.5,
            0.915,
            f"High-pollution errors use the fixed final-train Q90 subset: PM10 > {q90:.2f} ug/m3 (n={n_high}); full-test panels show differences relative to M3.",
            ha="center",
            va="center",
            fontsize=8.0,
            color=NEUTRAL["general_text"],
        )
        fig.subplots_adjust(top=0.86, bottom=0.16, left=0.075, right=0.99, hspace=0.64, wspace=0.38)
        fig.savefig(output_path, transparent=False, pad_inches=0.05)
        plt.close(fig)
    return output_path


def main() -> None:
    metric_predictions, _, high_threshold = build_safeguard_predictions()
    metrics = build_safeguard_metrics(metric_predictions, high_threshold)
    draw_safeguard_figure(metrics)
    print(metrics.to_string(index=False))
    print(f"Wrote: {FIGURE_PATH}")


if __name__ == "__main__":
    main()

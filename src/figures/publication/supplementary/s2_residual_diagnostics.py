"""Supplementary Figure S2: residual diagnostics for M0-M3 on the final test set.

Analytical source: frozen final-test prediction summaries under
`data/frozen_results/figure_sources/test_predictions.csv`.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import acf

from src.config import FIGURE_SOURCES_DIR
from src.figures.publication.common import (
    NEUTRAL,
    SUPPLEMENTARY_DIR,
    publication_style,
    save_figure,
    strip_spines,
)

OUTPUT_STEM = SUPPLEMENTARY_DIR / "s2_residual_diagnostics"
PREDICTIONS_PATH = FIGURE_SOURCES_DIR / "test_predictions.csv"
MODEL_ORDER = [
    "M0_dynamic_only",
    "M1_meteorological",
    "M2_fourier_seasonality",
    "M3_dynamic_regression",
]
MODEL_SHORT = {
    "M0_dynamic_only": "M0",
    "M1_meteorological": "M1",
    "M2_fourier_seasonality": "M2",
    "M3_dynamic_regression": "M3",
}
MODEL_COLORS = {
    "M0_dynamic_only": "#8C8C8C",
    "M1_meteorological": "#3490CC",
    "M2_fourier_seasonality": "#67C3FF",
    "M3_dynamic_regression": "#015D99",
}
ACF_LAGS = 72


def _load_residuals() -> dict[str, np.ndarray]:
    predictions = pd.read_csv(PREDICTIONS_PATH)
    residuals: dict[str, np.ndarray] = {}
    median_column = "q50" if "q50" in predictions.columns else "point_median"
    for model in MODEL_ORDER:
        frame = predictions[predictions["model"] == model].sort_values("datetime")
        if frame.empty:
            raise ValueError(f"Missing {model} rows in {PREDICTIONS_PATH}.")
        observed = frame["observed_pm10"].to_numpy(dtype=float)
        median = frame[median_column].to_numpy(dtype=float)
        residuals[model] = observed - median
    return residuals


def build_s2():
    residuals = _load_residuals()

    with publication_style():
        fig, (ax_hist, ax_acf) = plt.subplots(1, 2, figsize=(7.0, 2.9), constrained_layout=True)

        for model in MODEL_ORDER:
            ax_hist.hist(
                residuals[model],
                bins=60,
                density=True,
                histtype="step",
                lw=1.2,
                color=MODEL_COLORS[model],
                label=MODEL_SHORT[model],
            )
        ax_hist.axvline(0, color=NEUTRAL["reference_line"], lw=0.8, ls="--")
        ax_hist.set_xlabel("Observed - predictive median [µg/m³]")
        ax_hist.set_ylabel("Density")
        strip_spines(ax_hist)
        ax_hist.legend(frameon=False, fontsize=7, loc="upper right")

        for model in MODEL_ORDER:
            values = acf(residuals[model], nlags=ACF_LAGS, fft=True)
            ax_acf.plot(
                range(len(values)),
                values,
                color=MODEL_COLORS[model],
                lw=1.1,
                label=MODEL_SHORT[model],
            )
        ax_acf.axhline(0, color=NEUTRAL["reference_line"], lw=0.8, ls="--")
        n = len(residuals[MODEL_ORDER[0]])
        conf = 1.96 / np.sqrt(n)
        ax_acf.axhspan(-conf, conf, color=NEUTRAL["subtle_background"], zorder=0)
        ax_acf.set_xlabel("Lag [hours]")
        ax_acf.set_ylabel("Residual autocorrelation")
        strip_spines(ax_acf)

        pdf_path, png_path = save_figure(fig, OUTPUT_STEM)
        plt.close(fig)
    return pdf_path, png_path


def main() -> None:
    pdf_path, png_path = build_s2()
    print(f"Wrote: {pdf_path}")
    print(f"Wrote: {png_path}")


if __name__ == "__main__":
    main()

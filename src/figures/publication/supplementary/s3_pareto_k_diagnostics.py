"""Supplementary Figure S3: PSIS-LOO elpd comparison and Pareto-k diagnostics.

Analytical source: frozen LOO/WAIC CSV under `data/frozen_results`. Same
underlying table as the existing diagnostic figure, restyled to publication
conventions and extended with the elpd-difference-from-best panel.
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

LOO_PATH = FIGURE_SOURCES_DIR / "loo_waic_comparison.csv"
OUTPUT_STEM = SUPPLEMENTARY_DIR / "s3_pareto_k_diagnostics"

MODEL_SHORT = {
    "M0_dynamic_only": "M0",
    "M1_meteorological": "M1",
    "M2_fourier_seasonality": "M2",
    "M3_dynamic_regression": "M3",
}
MODEL_ORDER = ["M3_dynamic_regression", "M0_dynamic_only", "M2_fourier_seasonality", "M1_meteorological"]


def build_s3():
    df = pd.read_csv(LOO_PATH).set_index("model").loc[MODEL_ORDER]

    with publication_style():
        fig, (ax_elpd, ax_k) = plt.subplots(1, 2, figsize=(7.0, 2.8), constrained_layout=True)
        y_positions = range(len(MODEL_ORDER))

        for y, model in zip(y_positions, MODEL_ORDER):
            diff = df.loc[model, "elpd_diff_from_best"]
            se = df.loc[model, "se_diff"]
            color = PALETTE["primary_line"] if diff == 0 else NEUTRAL["contextual_line"]
            ax_elpd.plot([diff - se, diff + se], [y, y], color=color, lw=1.6, solid_capstyle="round")
            ax_elpd.scatter([diff], [y], color=color, s=28, zorder=3, edgecolor="white", linewidth=0.4)
        ax_elpd.axvline(0, color=NEUTRAL["reference_line"], lw=0.8, ls="--")
        ax_elpd.set_yticks(list(y_positions))
        ax_elpd.set_yticklabels([MODEL_SHORT[m] for m in MODEL_ORDER])
        ax_elpd.invert_yaxis()
        ax_elpd.set_xlabel("elpd_loo difference from best (±1 se)")
        ax_elpd.set_ylim(len(MODEL_ORDER) - 0.4, -0.6)
        strip_spines(ax_elpd, keep=("bottom",))
        ax_elpd.tick_params(axis="y", length=0)

        max_k = max(0.75, float(df["pareto_k_max"].max()) * 1.15)
        for y, model in zip(y_positions, MODEL_ORDER):
            k_value = df.loc[model, "pareto_k_max"]
            n_bad = int(df.loc[model, "pareto_k_gt_0_7"])
            color = "#B33B3B" if k_value > 0.7 else PALETTE["primary_line"]
            ax_k.barh([y], [k_value], color=color, height=0.55)
            ax_k.text(k_value + max_k * 0.02, y, f"{k_value:.2f}", fontsize=6.6, va="center", color=color)
        ax_k.axvline(0.7, color=NEUTRAL["reference_line"], lw=0.9, ls="--")
        ax_k.text(0.7, -0.75, "k = 0.7", fontsize=6.3, ha="center", color=NEUTRAL["reference_line"])
        ax_k.set_yticks(list(y_positions))
        ax_k.set_yticklabels([MODEL_SHORT[m] for m in MODEL_ORDER])
        ax_k.invert_yaxis()
        ax_k.set_xlim(0, max_k)
        ax_k.set_xlabel("Maximum Pareto k")
        ax_k.set_ylim(len(MODEL_ORDER) - 0.4, -1.1)
        strip_spines(ax_k, keep=("bottom",))
        ax_k.tick_params(axis="y", length=0)

        pdf_path, png_path = save_figure(fig, OUTPUT_STEM)
        plt.close(fig)
    return pdf_path, png_path


def main() -> None:
    pdf_path, png_path = build_s3()
    print(f"Wrote: {pdf_path}")
    print(f"Wrote: {png_path}")


if __name__ == "__main__":
    main()

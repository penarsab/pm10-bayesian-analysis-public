"""Figure 5: posterior multiplicative-effect comparison, M1 vs. M3.

Analytical source: frozen posterior-effect CSV under `data/frozen_results`. No
effect is recomputed here.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
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

EFFECTS_PATH = FIGURE_SOURCES_DIR / "multiplicative_effects.csv"
OUTPUT_STEM = FIGURES_DIR / "figure5_coefficient_comparison"

PREDICTOR_ORDER = [
    "Temperature lag 1 h",
    "Humidity lag 1 h",
    "Wind speed lag 1 h",
    "Pressure lag 1 h",
]

MODELS = [
    ("M1_meteorological", "M1 (no lag)", NEUTRAL["contextual_line"], -0.14),
    ("M3_dynamic_regression", "M3 (+ lag)", PALETTE["primary_line"], 0.14),
]


def _load() -> pd.DataFrame:
    df = pd.read_csv(EFFECTS_PATH)
    return df[df["model"].isin([m for m, *_ in MODELS])]


def build_figure5():
    df = _load()

    with publication_style():
        fig, ax = plt.subplots(figsize=(7.0, 3.2), constrained_layout=True)

        for row_idx, predictor in enumerate(PREDICTOR_ORDER):
            for model, label, color, dy in MODELS:
                record = df[(df["model"] == model) & (df["predictor"] == predictor)].iloc[0]
                y = row_idx + dy
                ax.plot(
                    [record["effect_q05_percent"], record["effect_q95_percent"]],
                    [y, y],
                    color=color,
                    lw=1.6,
                    solid_capstyle="round",
                )
                ax.scatter([record["effect_median_percent"]], [y], color=color, s=26, zorder=3, edgecolor="white", linewidth=0.4)
                if row_idx == 0:
                    ax.text(
                        record["effect_median_percent"],
                        y + 0.20,
                        label,
                        color=color,
                        fontsize=6.6,
                        ha="center",
                        va="bottom",
                    )

        ax.axvline(0, color=NEUTRAL["reference_line"], lw=0.8, ls="--", zorder=0)
        ax.set_yticks(range(len(PREDICTOR_ORDER)))
        ax.set_yticklabels([p.replace(" lag 1 h", "") for p in PREDICTOR_ORDER])
        ax.invert_yaxis()
        ax.set_xlabel("Effect on PM10 per +1 SD change [%]")
        ax.set_ylim(len(PREDICTOR_ORDER) - 0.5, -0.7)
        strip_spines(ax, keep=("bottom",))
        ax.tick_params(axis="y", length=0)

        pdf_path, png_path = save_figure(fig, OUTPUT_STEM)
        plt.close(fig)
    return pdf_path, png_path


def main() -> None:
    pdf_path, png_path = build_figure5()
    print(f"Wrote: {pdf_path}")
    print(f"Wrote: {png_path}")


if __name__ == "__main__":
    main()

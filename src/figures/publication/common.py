"""Shared helpers for manuscript publication-profile figures.

Implements the `publication` profile from the project's `scientific-figures`
skill: fixed physical dimensions, vector PDF + 300 DPI PNG output, the
`blue_ribbon_v1` / `neutral_v1` palettes, no default grid or figure titles,
and direct labelling preferred over legends.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

_MPLCONFIGDIR = Path(__file__).resolve().parents[3] / "tmp" / "matplotlib"
_MPLCONFIGDIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_MPLCONFIGDIR))

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt

from src.config import CONFIGS_DIR, PROJECT_ROOT, load_yaml

FIGURES_DIR = PROJECT_ROOT / "figures" / "generated" / "main"
SUPPLEMENTARY_DIR = PROJECT_ROOT / "figures" / "generated" / "supplementary"
CAPTIONS_DIR = PROJECT_ROOT / "captions"
PALETTE_CONFIG = load_yaml(CONFIGS_DIR / "palette.yaml")
EXPORT_CONFIG = load_yaml(CONFIGS_DIR / "export-profiles.yaml")
PUBLICATION_STYLE_PATH = CONFIGS_DIR / "publication.mplstyle"


def _semantic_palette(palette_name: str) -> dict[str, str]:
    palette = PALETTE_CONFIG["palettes"][palette_name]
    colors = palette["colors"]
    return {role: colors[color_name] for role, color_name in palette["semantic_roles"].items()}


PALETTE = _semantic_palette(PALETTE_CONFIG["defaults"]["sequential_palette"])
NEUTRAL = _semantic_palette(PALETTE_CONFIG["defaults"]["neutral_palette"])

DIMENSIONS_IN = {
    profile["layout_class"]: (profile["dimensions"]["width_in"], profile["dimensions"]["height_in"])
    for profile in EXPORT_CONFIG["profiles"].values()
    if profile["profile"] == "publication"
}
PNG_DPI = int(EXPORT_CONFIG["profiles"]["publication-double-column"]["png"]["dpi"])
PAD_INCHES = float(EXPORT_CONFIG["defaults"]["pad_inches"])


def mm_to_in(width_mm: float, height_mm: float) -> tuple[float, float]:
    return width_mm / 25.4, height_mm / 25.4


@contextmanager
def publication_style():
    """Local rcParams context implementing the publication profile defaults."""
    rc = {
        "axes.edgecolor": NEUTRAL["axes_and_spines"],
        "axes.labelcolor": NEUTRAL["general_text"],
        "text.color": NEUTRAL["general_text"],
        "xtick.color": NEUTRAL["axes_and_spines"],
        "ytick.color": NEUTRAL["axes_and_spines"],
        "figure.facecolor": NEUTRAL["figure_background"],
        "axes.facecolor": NEUTRAL["figure_background"],
        "savefig.facecolor": NEUTRAL["figure_background"],
    }
    with plt.style.context(str(PUBLICATION_STYLE_PATH)), plt.rc_context(rc):
        yield


def save_figure(fig, stem: Path) -> tuple[Path, Path]:
    """Save `fig` as both vector PDF and 300 DPI PNG at the given path stem."""
    stem.parent.mkdir(parents=True, exist_ok=True)
    pdf_path = stem.with_suffix(".pdf")
    png_path = stem.with_suffix(".png")
    fig.savefig(pdf_path, transparent=False, pad_inches=PAD_INCHES)
    fig.savefig(png_path, dpi=PNG_DPI, transparent=False, pad_inches=PAD_INCHES)
    return pdf_path, png_path


def strip_spines(ax, keep=("left", "bottom")) -> None:
    for side, spine in ax.spines.items():
        spine.set_visible(side in keep)


MODEL_ORDER = [
    "B0_historical_median",
    "B1_persistence",
    "B2_arx",
    "M0_dynamic_only",
    "M1_meteorological",
    "M2_fourier_seasonality",
    "M3_dynamic_regression",
]

MODEL_LABELS = {
    "B0_historical_median": "B0 historical median",
    "B1_persistence": "B1 persistence",
    "B2_arx": "B2 ARX(1)",
    "M0_dynamic_only": "M0 (lag only)",
    "M1_meteorological": "M1 (meteorology)",
    "M2_fourier_seasonality": "M2 (+ seasonality)",
    "M3_dynamic_regression": "M3 (+ lag)",
}

PRIMARY_MODELS = {"B1_persistence", "B2_arx", "M0_dynamic_only", "M3_dynamic_regression"}

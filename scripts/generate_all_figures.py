"""Generate the public manuscript figure set.

The plotting functions imported from ``src.figures.publication`` are the
accepted manuscript builders. This wrapper only maps their outputs to the final
file names used in the submitted manuscript package.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

GENERATED_MAIN = ROOT / "figures" / "generated" / "main"
GENERATED_SUPPLEMENTARY = ROOT / "figures" / "generated" / "supplementary"


def _copy(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_pair(src_stem: Path, dst_stem: Path) -> None:
    for suffix in (".pdf", ".png"):
        source = src_stem.with_suffix(suffix)
        if source.exists():
            _copy(source, dst_stem.with_suffix(suffix))


def main() -> None:
    GENERATED_MAIN.mkdir(parents=True, exist_ok=True)
    GENERATED_SUPPLEMENTARY.mkdir(parents=True, exist_ok=True)

    from src.figures.publication.figure1_pm10_series_and_splits import build_figure1
    from src.figures.publication.figure3_model_comparison import build_figure3
    from src.figures.publication.figure4_test_forecast_window import build_figure4
    from src.figures.publication.figure5_coefficient_comparison import build_figure5
    from src.figures.publication.figure6_high_pollution_comparison import build_figure6
    from src.figures.publication.model_dag import build_model_dag
    from src.figures.publication.supplementary.s1_prior_predictive_checks import build_s1
    from src.figures.publication.supplementary.s2_residual_diagnostics import build_s2
    from src.figures.publication.supplementary.s3_pareto_k_diagnostics import build_s3
    from src.figures.publication.supplementary.s4_sensitivity_comparison import build_s4
    from src.figures.publication.supplementary.s5_high_pollution_safeguard import (
        build_safeguard_metrics,
        build_safeguard_predictions,
        draw_safeguard_figure,
    )

    build_figure1()
    build_model_dag()
    build_figure3()
    build_figure4()
    build_figure5()
    build_figure6()
    build_s1()
    build_s2()
    build_s3()
    build_s4()

    metric_predictions, _, high_threshold = build_safeguard_predictions()
    safeguard_metrics = build_safeguard_metrics(metric_predictions, high_threshold)
    draw_safeguard_figure(safeguard_metrics, GENERATED_SUPPLEMENTARY / "s5_high_pollution_safeguard.pdf")

    _copy_pair(GENERATED_SUPPLEMENTARY / "s3_pareto_k_diagnostics", GENERATED_MAIN / "figure6_loo_pareto_diagnostics")

    generated = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "figures" / "generated").rglob("*") if p.is_file())
    print("\n".join(generated))


if __name__ == "__main__":
    main()

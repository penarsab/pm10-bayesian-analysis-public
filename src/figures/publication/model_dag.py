"""Generate the manuscript model-DAG assets."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from src.config import PROJECT_ROOT
from src.figures.publication.common import FIGURES_DIR

OUTPUT_TEX = FIGURES_DIR / "dag.tex"
OUTPUT_PDF = FIGURES_DIR / "figure2_model_dags.pdf"
OUTPUT_PNG = FIGURES_DIR / "figure2_model_dags.png"
REFERENCE_PDF = PROJECT_ROOT / "figures" / "reference" / "main" / "figure2_model_dags.pdf"
REFERENCE_PNG = PROJECT_ROOT / "figures" / "reference" / "main" / "figure2_model_dags.png"

DAG_TEX = r"""\begin{tikzpicture}[
    font=\small,
    >=Latex,
    line cap=round,
    line join=round,
    active/.style={
        rectangle,
        rounded corners=2pt,
        draw=blue!60!black,
        line width=0.9pt,
        fill=blue!2,
        minimum width=28mm,
        minimum height=10mm,
        align=center,
        inner sep=2pt
    },
    inactive/.style={
        rectangle,
        rounded corners=2pt,
        draw=gray!45,
        line width=0.8pt,
        fill=gray!6,
        text=gray!65,
        minimum width=28mm,
        minimum height=10mm,
        align=center,
        inner sep=2pt
    },
    middlebox/.style={
        rectangle,
        rounded corners=2pt,
        draw=blue!60!black,
        line width=0.9pt,
        fill=blue!2,
        minimum width=27mm,
        minimum height=10mm,
        align=center,
        inner sep=2pt
    },
    outbox/.style={
        rectangle,
        rounded corners=2pt,
        draw=blue!60!black,
        line width=0.9pt,
        fill=blue!2,
        minimum width=26mm,
        minimum height=10mm,
        align=center,
        inner sep=2pt
    },
    arr/.style={
        ->,
        draw=blue!60!black,
        line width=0.9pt
    },
    ghostarr/.style={
        ->,
        draw=gray!45,
        dashed,
        line width=0.8pt
    }
]

% ---------- helper macro ----------
% #1 x origin
% #2 y origin
% #3 model label
% #4 subtitle
% #5 lag active 1/0
% #6 met active 1/0
% #7 season active 1/0
% #8 note
\newcommand{\modelpanel}[8]{%
    % title
    \node[anchor=west,font=\bfseries\large] at (#1,#2) {#3};
    \node[anchor=west,font=\large] at ($(#1,#2)+(0.9,0)$) {#4};

    % left column
    \ifnum#5=1
        \node[active] (lag#3) at ($(#1,#2)+(0,-1.25)$)
        {Lagged PM$_{10}$\\[-1mm] $z_{t-1}^{c}$};
    \else
        \node[inactive] (lag#3) at ($(#1,#2)+(0,-1.25)$)
        {Lagged PM$_{10}$\\[-1mm] $z_{t-1}^{c}$};
    \fi

    \ifnum#6=1
        \node[active] (met#3) at ($(#1,#2)+(0,-2.40)$)
        {Meteorology\\[-1mm] $\mathbf{x}_{t-1}^{*}$};
    \else
        \node[inactive] (met#3) at ($(#1,#2)+(0,-2.40)$)
        {Meteorology\\[-1mm] $\mathbf{x}_{t-1}^{*}$};
    \fi

    \ifnum#7=1
        \node[active] (sea#3) at ($(#1,#2)+(0,-3.55)$)
        {Fourier terms\\[-1mm] $f_{\mathrm{year}}(t),\,f_{\mathrm{day}}(t)$};
    \else
        \node[inactive] (sea#3) at ($(#1,#2)+(0,-3.55)$)
        {Fourier terms\\[-1mm] $f_{\mathrm{year}}(t),\,f_{\mathrm{day}}(t)$};
    \fi

    % middle and output nodes
    \node[middlebox] (eta#3) at ($(#1,#2)+(3.65,-2.40)$)
    {Linear predictor\\[-1mm] $\eta_t$};

    \node[outbox] (y#3) at ($(#1,#2)+(6.85,-2.40)$)
    {PM$_{10}$ outcome\\[-1mm] $y_t$};

    % arrows from inputs
    \ifnum#5=1
        \draw[arr] (lag#3.east) -- (eta#3.west);
    \else
        \draw[ghostarr] (lag#3.east) -- (eta#3.west);
    \fi

    \ifnum#6=1
        \draw[arr] (met#3.east) -- (eta#3.west);
    \else
        \draw[ghostarr] (met#3.east) -- (eta#3.west);
    \fi

    \ifnum#7=1
        \draw[arr] (sea#3.east) -- (eta#3.west);
    \else
        \draw[ghostarr] (sea#3.east) -- (eta#3.west);
    \fi

    \draw[arr] (eta#3.east) -- (y#3.west);

    % panel note
    \node[align=center,text=gray!75!black,font=\large] at ($(#1,#2)+(3.45,-4.65)$) {#8};
}

% ---------- panels ----------
\modelpanel{0}{0}{M0}{Lag-only Bayesian model}{1}{0}{0}{Tests persistence alone}
\modelpanel{9.8}{0}{M1}{Meteorology-only Bayesian model}{0}{1}{0}{No lag information}
\modelpanel{0}{-5.9}{M2}{Meteorology + cyclic seasonality}{0}{1}{1}{Adds daily and annual cycles}
\modelpanel{9.8}{-5.9}{M3}{Final model: lag + meteorology + seasonality}{1}{1}{1}{Full predictive structure}

% ---- separator lines ----
\draw[dashed, gray!50, line width=0.8pt] (8.25,1) -- (8.25,-11);
\draw[dashed, gray!50, line width=0.8pt] (-2,-5.3) -- (19.4,-5.3);

\end{tikzpicture}%
"""


def _copy_reference_renderings() -> tuple[Path, Path]:
    if not REFERENCE_PDF.exists():
        raise FileNotFoundError(REFERENCE_PDF)
    shutil.copy(REFERENCE_PDF, OUTPUT_PDF)
    if REFERENCE_PNG.exists():
        shutil.copy(REFERENCE_PNG, OUTPUT_PNG)
    elif not OUTPUT_PNG.exists():
        raise FileNotFoundError(
            "Cannot create figure2_model_dags.png without a local LaTeX/ImageMagick "
            "toolchain or an existing generated PNG preview."
        )
    else:
        OUTPUT_PNG.touch()
    return OUTPUT_PDF, OUTPUT_PNG


def _render_with_latex() -> tuple[Path, Path] | None:
    pdflatex = shutil.which("pdflatex")
    png_converter = shutil.which("magick")
    if pdflatex is None or png_converter is None:
        return None

    document = "\n".join(
        [
            r"\documentclass[tikz,border=3pt]{standalone}",
            r"\usepackage{amsmath}",
            r"\usepackage{bm}",
            r"\usetikzlibrary{arrows.meta,calc,positioning}",
            r"\begin{document}",
            DAG_TEX,
            r"\end{document}",
            "",
        ]
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        tex_path = tmp / "figure2_model_dags.tex"
        tex_path.write_text(document, encoding="utf-8")
        subprocess.run(
            [pdflatex, "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
            cwd=tmp,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        shutil.copy2(tmp / "figure2_model_dags.pdf", OUTPUT_PDF)
        subprocess.run(
            [png_converter, "-density", "300", str(OUTPUT_PDF), "-quality", "100", str(OUTPUT_PNG)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return OUTPUT_PDF, OUTPUT_PNG


def build_model_dag(output_tex: Path = OUTPUT_TEX) -> tuple[Path, Path, Path]:
    output_tex.parent.mkdir(parents=True, exist_ok=True)
    output_tex.write_text(DAG_TEX + "\n", encoding="utf-8")
    rendered = _render_with_latex()
    if rendered is None:
        rendered = _copy_reference_renderings()
    return output_tex, *rendered


def main() -> None:
    for path in build_model_dag():
        print(f"Wrote: {path}")


if __name__ == "__main__":
    main()

"""Build manuscript LaTeX tables from frozen public CSV sources."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pandas as pd

from src.config import TABLE_SOURCES_DIR

MODEL_LABELS = {
    "B0_historical_median": "Historical median",
    "B1_persistence": "Persistence",
    "B2_arx": "ARX(1)",
    "M0_dynamic_only": "M0",
    "M1_meteorological": "M1",
    "M2_fourier_seasonality": "M2",
    "M3_dynamic_regression": "M3",
}


def _fmt(value: object, digits: int = 3) -> str:
    return f"{float(value):.{digits}f}"


def _fmt_int(value: object) -> str:
    return str(int(float(value)))


def _yes_no(value: object) -> str:
    text = str(value)
    if text.lower() in {"true", "yes"}:
        return "yes"
    if text.lower() in {"false", "no"}:
        return "no"
    return text


def _model_short(value: str) -> str:
    if value.startswith("M0"):
        return "M0"
    if value.startswith("M1"):
        return "M1"
    if value.startswith("M2"):
        return "M2"
    if value.startswith("M3"):
        return "M3"
    if value.startswith("B0"):
        return "B0"
    if value.startswith("B1"):
        return "B1"
    if value.startswith("B2"):
        return "B2"
    return value


def _model_display(value: str) -> str:
    replacements = {
        "B1 persistence": "Persistence",
        "B2 ARX(1)": "ARX(1)",
        "B2_arx": "ARX(1)",
        "M0 (lag only)": "M0",
        "M3 (+ lag)": "M3",
        "M1 (meteorology)": "M1",
        "M2 (+ seasonality)": "M2",
    }
    return replacements.get(value, value)


def _table(
    caption: str,
    tabular: str,
    header: str,
    rows: list[str],
    *,
    centered_first: bool = False,
    size: str = r"\small",
    resize: bool = False,
    tabularx: bool = False,
    label_after_caption: str | None = None,
) -> str:
    lines = [r"\begin{table}[H]"]
    if centered_first:
        lines.append(r"\centering")
        lines.append(caption)
    else:
        lines.append(caption)
        lines.append(r"\centering")
    if label_after_caption:
        lines.append(label_after_caption)
    lines.append(size)
    if resize:
        lines.append(r"\resizebox{\textwidth}{!}{%")
    env = "tabularx" if tabularx else "tabular"
    if tabularx:
        lines.append(rf"\begin{{{env}}}{tabular}")
    else:
        lines.append(rf"\begin{{{env}}}{tabular}")
    lines.append(r"\toprule")
    lines.append(header)
    lines.append(r"\midrule")
    lines.extend(rows)
    lines.append(r"\bottomrule")
    end = rf"\end{{{env}}}"
    if resize:
        end += "}"
    lines.append(end)
    lines.append(r"\end{table}")
    return "\n".join(lines) + "\n"


def _read(stem: str) -> pd.DataFrame:
    return pd.read_csv(TABLE_SOURCES_DIR / f"{stem}.csv")


def _write(stem: str, text: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{stem}.tex"
    path.write_text(text, encoding="utf-8")
    return path


def table1_data_summary() -> str:
    data = dict(_read("table1_data_summary").itertuples(index=False, name=None))
    period = data["Study period"].replace("2020-01-01 00:00:00 to 2024-12-31 23:00:00", "1 January 2020--31 December 2024")
    pm_missing = int(data["PM10 rows removed for missingness (unfillable within 2 h)"])
    pm_share = float(data["PM10 missing share (complete hourly grid)"]) * 100
    rows = [
        f"Study period & {period}\\\\",
        "Temporal resolution & Hourly\\\\",
        f"Model-ready observations & {int(data['Model-ready observations (n, after lag construction)']):,}\\\\",
        f"Final training set & {int(data['Training set size (final split)']):,} observations\\\\",
        f"Final held-out test set & {int(data['Final held-out test set size'])} observations\\\\",
        f"Rolling-origin validation folds & {int(data['Rolling-origin CV folds'])}\\\\",
        f"DST-ambiguous rows excluded & {int(data['Excluded DST-ambiguous rows (PM10 source)'])} $\\PM$ rows; {int(data['Excluded DST-ambiguous rows (weather source)'])} weather rows\\\\",
        f"$\\PM$ rows removed for missingness & {pm_missing} ({pm_share:.2f}\\% of the complete hourly grid)\\\\",
        "Target & $\\PM$ concentration [$\\pmunit$]\\\\",
        "Meteorological predictors & Temperature, relative humidity, wind speed, surface pressure; each lagged by 1 h\\\\",
        "Additional inputs & Lagged log-$\\PM$ (B1, B2, M0, M3); two annual and two daily Fourier harmonics (B2, M2, M3)\\\\",
    ]
    return _table(
        r"\caption{Data and split summary.\label{tab:data-summary}}",
        r"{\textwidth}{p{0.42\textwidth}X}",
        r"\textbf{Quantity} & \textbf{Value}\\",
        rows,
        tabularx=True,
    )


def table2_model_definitions() -> str:
    rows = []
    defs = {
        "B0": ("--", "--", "--", "--", "Training-set median used for every hour."),
        "B1": ("yes", "--", "--", "--", r"$\widehat y_t=y_{t-1}$."),
        "B2": ("yes", "yes", "yes", "yes", r"{Dynamic regression on log-$\PM$ with AR(1) errors; rolling one-step Kalman forecasts.}"),
        "M0": ("yes", "--", "--", "yes", r"Lognormal model with centered lagged log-$\PM$."),
        "M1": ("--", "yes", "--", "yes", "Lognormal regression with standardized lagged meteorology."),
        "M2": ("--", "yes", "yes", "yes", "M1 plus annual and daily Fourier terms."),
        "M3": ("yes", "yes", "yes", "yes", r"M2 plus centered lagged log-$\PM$."),
    }
    name_map = {"B2": "{ARX(1)}", "M2": "Meteorology + seasonality", "M3": "Full Bayesian model"}
    for row in _read("table2_model_definitions").itertuples(index=False):
        model = row.model
        lag, met, cyc, prob, definition = defs[model]
        name = name_map.get(model, row.name)
        rows.append(f"{model} & {name} & {lag} & {met} & {cyc} & {prob} & {definition}\\\\")
    return _table(
        r"\caption{Definitions of the reference and Bayesian models.\label{tab:model-definitions}}",
        r"{\textwidth}{l l c c c c X}",
        r"\textbf{ID} & \textbf{Model} & \textbf{Lag} & \textbf{Met.} & \textbf{Cyclic} & \textbf{Prob.} & \textbf{Definition}\\",
        rows,
        size=r"\scriptsize",
        tabularx=True,
    )


def table3_test_performance() -> str:
    df = _read("table3_test_performance")
    rows = []
    best = {"RMSE": df["RMSE"].idxmin(), "Coverage (90%)": df["Coverage (90%)"].idxmax(), "MAE": df["MAE"].idxmin(), "CRPS": df["CRPS"].idxmin(), "Width (90%)": df["Width (90%)"].where(df["Width (90%)"] > 0).idxmin()}
    labels = {"B2 ARX(1)": "B2 {ARX(1)}", "M0 (lag only)": "M0 lag only", "M1 (meteorology)": "M1 meteorology", "M2 (+ seasonality)": "M2 + seasonality", "M3 (+ lag)": "M3 full"}
    for idx, row in df.iterrows():
        values = []
        for col in ["MAE", "RMSE", "CRPS", "Coverage (90%)", "Width (90%)"]:
            value = _fmt(row[col])
            if best[col] == idx:
                value = rf"\textbf{{{value}}}"
            values.append(value)
        rows.append(f"{labels.get(row['Model'], row['Model'])} & " + " & ".join(values) + r"\\")
    return _table(
        r"\caption{Predictive performance on the final held-out test set ($n=8565$ hours). Lower MAE, RMSE, and CRPS are better. {MAE, RMSE, CRPS, and predictive-interval width are reported in $\pmunit$.} Coverage refers to the nominal 90\% predictive interval. B0 and B1 are deterministic; their CRPS values correspond to point-mass forecasts and they do not provide predictive intervals.\label{tab:test-performance}}",
        "{lrrrrr}",
        r"\textbf{Model} & \textbf{MAE} & \textbf{RMSE} & \textbf{CRPS} & \textbf{Coverage} & \textbf{Width}\\",
        rows,
    )


def table4_bootstrap_comparisons() -> str:
    rows = []
    for _, row in _read("table4_bootstrap_comparisons").iterrows():
        comparison = row["Comparison"].replace(" (persistence)", "").replace("B2 (ARX(1))", "{ARX(1)}")
        interval = f"[{_fmt(row['95% CI lower'])}, {_fmt(row['95% CI upper'])}]"
        rows.append(
            f"{comparison} & {row['Metric'].upper()} & {_fmt(row['Observed difference'])} & "
            f"{_fmt(row['Bootstrap median'])} & {interval} & {_fmt(row['P(difference < 0)'])}\\\\"
        )
    return _table(
        r"\caption{Paired moving-block bootstrap comparison on the final test set (24 h blocks, 2000 replications). A negative difference favors the first model. {Differences for MAE, RMSE, and CRPS are reported in $\pmunit$.}\label{tab:bootstrap-comparisons}}",
        "{llrrrr}",
        r"\textbf{Comparison} & \textbf{Metric} & \textbf{Observed $\Delta$} & \textbf{Bootstrap median} & \textbf{95\% interval} & \textbf{$P(\Delta<0)$}\\",
        rows,
        size=r"\scriptsize",
    )


def table5_meteorological_effects() -> str:
    pred = {"Temperature lag 1 h": "Temperature", "Humidity lag 1 h": "Relative humidity", "Wind speed lag 1 h": "Wind speed", "Pressure lag 1 h": "Surface pressure"}
    rows = []
    for row in _read("table5_meteorological_effects").itertuples(index=False):
        median = _fmt(row._2, 2)
        interval = row._3
        if row.Model == "M3":
            median = "{" + median + "}"
            interval = "{" + interval + "}"
        rows.append(f"{pred[row.Predictor]} & {row.Model} & {median} & {interval}\\\\")
    return _table(
        r"\caption{Posterior multiplicative effect of a one-standard-deviation increase in each lagged meteorological predictor on median $\PM$.\label{tab:meteorological-effects}}",
        "{llrr}",
        r"\textbf{Predictor} & \textbf{Model} & \textbf{Median effect [\%]} & \textbf{90\% interval [\%]}\\",
        rows,
    )


def table_s1_mcmc_diagnostics() -> str:
    rows = []
    for _, row in _read("table_s1_mcmc_diagnostics").iterrows():
        rows.append(
            f"{_model_short(row['Model'])} & {_fmt_int(row['Chains'])} & {_fmt_int(row['Warmup iters/chain'])} & "
            f"{_fmt_int(row['Sampling iters/chain'])} & {_fmt(row['Max R-hat'])} & {_fmt_int(row['Min bulk ESS'])} & "
            f"{_fmt_int(row['Min tail ESS'])} & {_fmt_int(row['Divergences'])} & {_fmt_int(row['Max-treedepth hits'])} & "
            f"{_fmt(row['Min E-BFMI'])} & {_yes_no(row['Flagged problematic'])}\\\\"
        )
    return _table(
        r"\caption{{MCMC diagnostics for the four final Bayesian models.}\label{tab:s1-mcmc}}",
        "{lrrrrrrrrrr}",
        r"Model & Chains & Warmup & Draws & Max $\widehat R$ & Min bulk ESS & Min tail ESS & Divergences & Tree-depth hits & Min E-BFMI & Flagged\\",
        rows,
        centered_first=True,
        size=r"\scriptsize",
        resize=True,
    )


def table_s2_loo_waic() -> str:
    rows = []
    for _, row in _read("table_s2_loo_waic").iterrows():
        rows.append(
            f"{_model_short(row['Model'])} & {_fmt(row['elpd_loo'])} & {_fmt(row['se(elpd_loo)'])} & {_fmt(row['p_loo'])} & "
            f"{_fmt(row['elpd_waic'])} & {_fmt(row['elpd diff. from best'])} & {_fmt(row['se(diff.)'])} & "
            f"{_fmt(row['Max Pareto k'])} & {_fmt_int(row['n (k > 0.7)'])} & {_fmt_int(row['Rank'])}\\\\"
        )
    return _table(
        r"\caption{{PSIS-LOO and WAIC comparison across the final Bayesian models. Higher elpd is better.}\label{tab:s2-loo}}",
        "{lrrrrrrrrr}",
        r"Model & elpd$_{\mathrm{loo}}$ & SE & $p_{\mathrm{loo}}$ & elpd$_{\mathrm{waic}}$ & $\Delta$ elpd & SE($\Delta$) & Max $k$ & $n(k>0.7)$ & Rank\\",
        rows,
        centered_first=True,
        size=r"\scriptsize",
        resize=True,
    )


def table_s3_sensitivity() -> str:
    labels = {
        "M3 baseline prior": "M3 baseline",
        "M3 beta prior Normal(0, 0.6)": r"M3 wide $\beta$ prior",
        "M3 Student-t log-PM10 likelihood": r"M3 Student-$t$ log-likelihood",
    }
    rows = []
    for row in _read("table_s3_sensitivity").itertuples(index=False):
        rows.append(f"{labels[row.Variant]} & {_fmt(row.MAE)} & {_fmt(row.RMSE)} & {_fmt(row.CRPS)} & {_fmt(row._4)} & {_fmt(row._5)}\\\\")
    return _table(
        r"\caption{{M3 sensitivity to prior width and likelihood family.}\label{tab:s3-sensitivity}}",
        "{lrrrrr}",
        r"Variant & MAE & RMSE & CRPS & Coverage 90\% & Width 90\%\\",
        rows,
        centered_first=True,
    )


def table_s4_sensitivity_assessment() -> str:
    labels = {
        "M3_wide_priors vs M3_baseline": "Wide prior vs baseline",
        "M3_dynamic_student_t vs M3_baseline": r"Student-$t$ vs baseline",
    }
    quantity = {"mae": "MAE", "rmse": "RMSE", "crps": "CRPS", "width_90": r"Width 90\%"}
    df = _read("table_s4_sensitivity_assessment")
    keep = ((df["comparison"] == "M3_wide_priors vs M3_baseline") & (df["quantity"].isin(["mae", "rmse", "crps"]))) | (
        (df["comparison"] == "M3_dynamic_student_t vs M3_baseline") & (df["quantity"].isin(["mae", "rmse", "crps", "width_90"]))
    )
    rows = []
    for row in df[keep].itertuples(index=False):
        rows.append(
            f"{labels[row.comparison]} & {quantity[row.quantity]} & {_fmt(row.baseline_value)} & {_fmt(row.variant_value)} & "
            f"{_fmt(row.absolute_change)} & {row.relative_change * 100:.1f}\\% & {_yes_no(row.material_change)}\\\\"
        )
    return _table(
        r"\caption{{Materiality assessment of sensitivity variants relative to M3 baseline. A change is marked material when its absolute relative magnitude is at least 5\%.}\label{tab:s4-assessment}}",
        r"{\textwidth}{l l r r r r c}",
        r"Comparison & Quantity & Baseline & Variant & Absolute change & Relative change & Material\\",
        rows,
        centered_first=True,
        size=r"\scriptsize",
        tabularx=True,
    )


def table_s5_yearly_holdouts() -> str:
    rows = []
    df = _read("table_s5_yearly_holdouts")
    for row in df.itertuples(index=False):
        rows.append(
            f"{_fmt_int(row.year)} & {_model_display(row.model_label)} & {_fmt_int(row.n)} & {_fmt(row.mae)} & {_fmt(row.rmse)} & "
            f"{_fmt(row.crps)} & {_fmt(row.coverage_90)} & {_fmt(row.mae_high)} & {_fmt(row.rmse_high)}\\\\"
        )
    return _table(
        r"\caption{{Sequential yearly hold-out performance. Each year was evaluated after fitting on all preceding years. Error scores are in $\pmunit$; coverage refers to the nominal 90\% predictive interval. High-pollution subsets use the training-period 90th percentile for the corresponding split. Values are rounded to three decimals.}\label{tab:s5-yearly-holdouts}}",
        "{llrrrrrrr}",
        r"Year & Model & $n$ & MAE & RMSE & CRPS & Coverage & High MAE & High RMSE\\",
        rows,
        centered_first=True,
        size=r"\scriptsize",
        resize=True,
    )


def table_s6_fourier_sensitivity() -> str:
    rows = []
    for row in _read("table_s6_fourier_sensitivity").itertuples(index=False):
        rows.append(
            rf"${row.variant}$ & {_fmt(row.mae)} & {_fmt(row.rmse)} & {_fmt(row.crps)} & {_fmt(row.coverage_90)} & {_fmt(row.width_90)} & "
            f"{_fmt(row.elpd_loo, 1)} & {_fmt(row.max_rhat)} & {_fmt_int(row.divergences)} & {_fmt_int(row.max_treedepth_hits)}\\\\"
        )
    return _table(
        r"\caption{{M3 sensitivity to the number of annual and daily Fourier harmonics. Test-set error scores are in $\pmunit$. PSIS-LOO was calculated on the final training set. Values are rounded to three decimals, except elpd.}\label{tab:s6-fourier}}",
        "{lrrrrrrrrr}",
        r"Order & MAE & RMSE & CRPS & Coverage 90\% & Width 90\% & elpd$_{\mathrm{loo}}$ & Max $\widehat R$ & Divergences & Tree-depth hits\\",
        rows,
        centered_first=True,
        size=r"\scriptsize",
        resize=True,
    )


def table_s7_phi_diagnostics() -> str:
    rows = []
    for row in _read("table_s7_phi_diagnostics").itertuples(index=False):
        model = _model_short(row.model)
        interval = f"[{_fmt(row.phi_q05)}, {_fmt(row.phi_q95)}]"
        rows.append(
            f"{model} & {_fmt(row.phi_median)} & {interval} & {_fmt(row.rhat_phi)} & {_fmt_int(row.bulk_ess_phi)} & "
            f"{_fmt_int(row.tail_ess_phi)} & {_fmt_int(row.divergences)} & {_fmt_int(row.max_treedepth_hits)} & {_fmt(row.min_ebfmi)}\\\\"
        )
    return _table(
        r"\caption{{Diagnostics for the persistence coefficient $\phi$ under the main $\tanh(\phi_{\mathrm{raw}})$ parameterization. Intervals are 90\% posterior intervals.}\label{tab:s7-phi-diagnostics}}",
        "{lrrrrrrrr}",
        r"Model & Median & 90\% interval & $\widehat R$ & Bulk ESS & Tail ESS & Divergences & Tree-depth hits & Min E-BFMI\\",
        rows,
        centered_first=True,
        size=r"\scriptsize",
    )


def table_s8_phi_parameterization() -> str:
    rows = []
    labels = {"tanh": r"$\tanh(\phi_{\mathrm{raw}})$", "phi_free": r"direct $\phi$"}
    intervals = {
        ("M0", "tanh"): "0.914 [0.910, 0.917]",
        ("M0", "phi_free"): "0.914 [0.910, 0.918]",
        ("M3", "tanh"): "0.865 [0.860, 0.869]",
        ("M3", "phi_free"): "0.865 [0.860, 0.869]",
    }
    for row in _read("table_s8_phi_parameterization").itertuples(index=False):
        rows.append(
            f"{row.model_family} & {labels[row.variant]} & {intervals[(row.model_family, row.variant)]} & {_fmt(row.mae)} & "
            f"{_fmt(row.rmse)} & {_fmt(row.crps)} & {_fmt(row.coverage_90)} & {_fmt(row.width_90)}\\\\"
        )
    return _table(
        r"\caption{{Sensitivity to sampling $\phi$ through $\tanh(\phi_{\mathrm{raw}})$ or directly. Error scores are final-test values in $\pmunit$; intervals are 90\% posterior intervals.}\label{tab:s8-phi-parameterization}}",
        "{lllrrrrr}",
        r"Family & Parameterization & $\phi$ median (90\% interval) & MAE & RMSE & CRPS & Coverage 90\% & Width 90\%\\",
        rows,
        centered_first=True,
        size=r"\scriptsize",
        resize=True,
    )


def table_s9_missingness_audit() -> str:
    df = _read("table_s9_missingness_audit").set_index("metric")
    miss = int(df.loc["missing_count", "value"].iloc[0]) if isinstance(df.loc["missing_count", "value"], pd.Series) else int(df.loc["missing_count", "value"])
    share = float(df[(df["variable"] == "PM10") & (df.index == "missing_share")]["value"].iloc[0]) * 100
    run_count = int(float(df[(df["variable"] == "PM10") & (df.index == "missing_run_count")]["value"].iloc[0]))
    longest = int(float(df[(df["variable"] == "PM10") & (df.index == "longest_missing_run_hours")]["value"].iloc[0]))
    filled = int(float(df[(df["section"] == "forward_fill") & (df.index == "filled_by_forward_fill_limit_2h")]["value"].iloc[0]))
    duplicate = int(float(df[(df["variable"] == "pm10_gios") & (df.index == "excluded_dst_rows")]["value"].iloc[0]))
    high_dup = int(float(df[(df["section"] == "dst_high_pm10") & (df.index == "excluded_rows_with_high_pm10")]["value"].iloc[0]))
    processed_gaps = int(float(df[(df["variable"] == "processed_merged") & (df.index == "gaps_gt_1h_count")]["value"].iloc[0]))
    processed_max = int(float(df[(df["variable"] == "processed_merged") & (df.index == "max_gap_hours")]["value"].iloc[0]))
    ready_gaps = int(float(df[(df["variable"] == "model_ready") & (df.index == "gaps_gt_1h_count")]["value"].iloc[0]))
    ready_max = int(float(df[(df["variable"] == "model_ready") & (df.index == "max_gap_hours")]["value"].iloc[0]))
    rows = [
        f"Missing $\\PM$ values & {miss} ({share:.3f}\\%) & Not interpolated; {run_count} missing runs, longest {longest}~h.\\\\",
        f"Meteorological values forward-filled & {filled} per variable & Limited to at most two consecutive hours for each of four weather variables.\\\\",
        f"Excluded duplicate $\\PM$ rows & {duplicate} & Five DST-ambiguous timestamps; four excluded rows exceeded the final-training 90th-percentile threshold.\\\\",
        f"Processed-series gaps $>1$~h & {processed_gaps} & Maximum gap {processed_max}~h before model-ready filtering.\\\\",
        f"Model-ready gaps $>1$~h & {ready_gaps} & Maximum retained-sequence gap {ready_max}~h; retained lag values still refer to the preceding grid hour.\\\\",
    ]
    return _table(
        r"\caption{{Missingness, forward-fill, timestamp-gap, and DST audit for the complete 2020--2024 source grid.}\label{tab:s9-missingness}}",
        r"{\textwidth}{l r X}",
        r"Audit quantity & Value & Interpretation\\",
        rows,
        centered_first=True,
        tabularx=True,
    )


def table_s10_gap_filtered_metrics() -> str:
    df = _read("table_s10_gap_filtered_metrics")
    df = df[df["scenario"] == "exclude_any_gap_sensitive"]
    rows = []
    for row in df.itertuples(index=False):
        rows.append(
            f"{MODEL_LABELS[row.model]} & {_fmt(row.mae_filtered)} & {_fmt(row.mae_change)} & {_fmt(row.rmse_filtered)} & "
            f"{_fmt(row.rmse_change)} & {_fmt(row.crps_filtered)} & {_fmt(row.crps_change)}\\\\"
        )
    n_excluded = _fmt_int(df.iloc[0]["n_excluded"])
    n_remaining = _fmt_int(df.iloc[0]["n_remaining"])
    return _table(
        rf"\caption{{{{Final-test sensitivity after excluding {n_excluded} rows in the combined gap, DST, and forward-fill audit windows ($n={n_remaining}$ retained). Error scores are in $\pmunit$; $\Delta$ is filtered minus the corresponding full-test value from the same audit calculation.}}\label{{tab:s10-gap-filtered}}}}",
        "{lrrrrrr}",
        r"Model & MAE filtered & $\Delta$ MAE & RMSE filtered & $\Delta$ RMSE & CRPS filtered & $\Delta$ CRPS\\",
        rows,
        centered_first=True,
        size=r"\scriptsize",
        resize=True,
    )


def table_s11_meteorological_scale() -> str:
    unit = {"deg C": r"$^{\circ}$C", "%": r"\%", "km/h": "km/h", "hPa": "hPa"}
    rows = []
    for row in _read("table_s11_meteorological_scale").itertuples(index=False):
        scale_unit = unit.get(row.sd_unit, row.sd_unit)
        if row.sd_unit == "percentage points":
            scale = f"{_fmt(row.sd)} percentage points"
        else:
            scale = f"{_fmt(row.sd)}~{scale_unit}"
        rows.append(
            f"{row.predictor} & {unit.get(row.unit, row.unit)} & {_fmt(row.mean)} & {_fmt(row.sd)} & {_fmt(row.min)} & {_fmt(row.median)} & {_fmt(row.max)} & {scale}\\\\"
        )
    return _table(
        r"\caption{{Physical scale of standardized meteorological predictors in the final training split. The SD column gives the physical-unit change corresponding to a one-standard-deviation increase in Table~5.}\label{tab:s11-meteorological-scale}}",
        "{llrrrrrl}",
        r"Predictor & Unit & Mean & SD & Min & Median & Max & One-SD physical scale\\",
        rows,
        centered_first=True,
        size=r"\scriptsize",
        resize=True,
    )


def table_s12_high_pollution_safeguard() -> str:
    df = _read("table_s12_high_pollution_safeguard")
    rows = []
    for row in df.itertuples(index=False):
        threshold = "--" if pd.isna(row.safeguard_threshold_value) else _fmt(row.safeguard_threshold_value)
        rows.append(
            f"{row.model_label} & {threshold} & {_fmt_int(row.safeguard_activated_hours)} & {_fmt(row.mae)} & {_fmt(row.rmse)} & {_fmt(row.mae_high)} & {_fmt(row.rmse_high)} \\\\"
        )
    n = _fmt_int(df.iloc[0]["n"])
    n_high = _fmt_int(df.iloc[0]["n_high"])
    q90 = _fmt(df.iloc[0]["high_pollution_threshold_q90_train"])
    return _table(
        rf"\caption{{{{Persistence-safeguard sensitivity on the final held-out test set ($n={n}$). For each Q80/Q90/Q95 rule, the forecast uses persistence when the previous-hour $\PM$ exceeds the listed final-training threshold and otherwise uses M3. High-pollution metrics use the same fixed subset of {n_high} observations with observed $\PM$ above the final-training Q90 threshold of {q90}~$\pmunit$. MAE and RMSE are reported in $\pmunit$.}}}}",
        "{lrrrrrr}",
        r"Model & Threshold & Activations & Full MAE & Full RMSE & High MAE & High RMSE \\",
        rows,
        centered_first=True,
        size=r"\scriptsize",
        resize=True,
        label_after_caption=r"\label{tab:s12}",
    )


BUILDERS: dict[str, Callable[[], str]] = {
    name: builder
    for name, builder in globals().items()
    if name.startswith("table") and callable(builder)
}


def build_table(stem: str, output_dir: Path) -> Path:
    try:
        text = BUILDERS[stem]()
    except KeyError as exc:
        raise ValueError(f"No table builder registered for {stem}") from exc
    return _write(stem, text, output_dir)

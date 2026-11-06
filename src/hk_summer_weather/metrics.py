"""Calculate annual, monthly, and period summer weather metrics."""

from dataclasses import dataclass
from typing import Final

import polars as pl

EARLY_PERIOD: Final = "early_1991_2000"
RECENT_PERIOD: Final = "recent_2016_2025"
HOT_DAY_THRESHOLD_C: Final = 33.0
RAINY_DAY_THRESHOLD_MM: Final = 0.1


@dataclass(frozen=True, slots=True)
class PeriodSummaries:
    """Hold annual and monthly early-versus-recent summaries."""

    annual: pl.DataFrame
    monthly: pl.DataFrame


def build_annual_metrics(
    daily: pl.DataFrame,
    quality: pl.DataFrame,
) -> pl.DataFrame:
    """Calculate annual summer metrics for complete years only."""
    valid_years = quality.filter(pl.col("valid_summer")).select("year")
    return (
        daily.join(valid_years, on="year", how="inner", validate="m:1")
        .filter(pl.col("complete_day"))
        .group_by("year")
        .agg(
            pl.col("mean_temp_c").mean().alias("summer_mean_temp_c"),
            pl.col("rainfall_mm").sum().alias("summer_total_rainfall_mm"),
            (pl.col("max_temp_c") >= HOT_DAY_THRESHOLD_C)
            .sum()
            .alias("hot_days_ge_33c"),
            (pl.col("rainfall_mm") >= RAINY_DAY_THRESHOLD_MM)
            .sum()
            .alias("rainy_days_ge_0_1mm"),
            pl.len().alias("valid_days"),
        )
        .sort("year")
    )


def build_monthly_metrics(
    daily: pl.DataFrame,
    quality: pl.DataFrame,
) -> pl.DataFrame:
    """Calculate June-to-August monthly metrics for complete years only."""
    valid_years = quality.filter(pl.col("valid_summer")).select("year")
    return (
        daily.join(valid_years, on="year", how="inner", validate="m:1")
        .filter(pl.col("complete_day"))
        .group_by("year", "month")
        .agg(
            pl.col("mean_temp_c").mean().alias("monthly_mean_temp_c"),
            pl.col("rainfall_mm").sum().alias("monthly_total_rainfall_mm"),
            pl.len().alias("valid_days"),
        )
        .sort("year", "month")
    )


def build_period_summaries(
    annual: pl.DataFrame,
    monthly: pl.DataFrame,
) -> PeriodSummaries:
    """Average annual and monthly metrics within early and recent periods."""
    annual_summary = (
        _with_period(annual)
        .group_by("period")
        .agg(
            pl.len().alias("year_count"),
            pl.col("summer_mean_temp_c").mean().alias("average_summer_mean_temp_c"),
            pl.col("summer_total_rainfall_mm")
            .mean()
            .alias("average_summer_total_rainfall_mm"),
            pl.col("hot_days_ge_33c").mean().alias("average_hot_days_ge_33c"),
            pl.col("rainy_days_ge_0_1mm").mean().alias("average_rainy_days_ge_0_1mm"),
        )
        .sort("period")
    )
    monthly_summary = (
        _with_period(monthly)
        .group_by("period", "month")
        .agg(
            pl.len().alias("year_count"),
            pl.col("monthly_mean_temp_c").mean().alias("average_monthly_mean_temp_c"),
            pl.col("monthly_total_rainfall_mm")
            .mean()
            .alias("average_monthly_total_rainfall_mm"),
        )
        .sort("period", "month")
    )
    return PeriodSummaries(annual=annual_summary, monthly=monthly_summary)


def _with_period(frame: pl.DataFrame) -> pl.DataFrame:
    return frame.with_columns(
        pl.when(pl.col("year").is_between(1991, 2000))
        .then(pl.lit(EARLY_PERIOD))
        .when(pl.col("year").is_between(2016, 2025))
        .then(pl.lit(RECENT_PERIOD))
        .otherwise(None)
        .alias("period")
    ).filter(pl.col("period").is_not_null())

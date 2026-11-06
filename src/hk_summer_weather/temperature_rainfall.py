"""Prepare paired annual summer temperature and rainfall metrics for Figure 5."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, override

import numpy as np

from hk_summer_weather.cleaning import END_YEAR, START_YEAR

if TYPE_CHECKING:
    import polars as pl
    from numpy.typing import NDArray

MINIMUM_YEARS: Final = 3
SUMMER_DAYS: Final = 92
REQUIRED_COLUMNS: Final = (
    "year",
    "summer_total_rainfall_mm",
    "summer_mean_temp_c",
    "valid_days",
)


@dataclass(frozen=True, slots=True)
class TemperatureRainfallPlotData:
    """Hold paired observations and an OLS line over observed rainfall only."""

    years: NDArray[np.int64]
    rainfall_mm: NDArray[np.float64]
    mean_temperature_c: NDArray[np.float64]
    fitted_rainfall_mm: NDArray[np.float64]
    fitted_temperature_c: NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class InvalidAnnualMetricsError(Exception):
    """Explain why annual metrics cannot support a paired scatter plot."""

    detail: str

    @override
    def __str__(self) -> str:
        """Return the input diagnostic."""
        return self.detail


def _prepare_annual_metrics(annual: pl.DataFrame) -> pl.DataFrame:
    """Check the annual-table boundary and retain paired, complete study years."""
    missing = sorted(set(REQUIRED_COLUMNS) - set(annual.columns))
    if missing:
        raise InvalidAnnualMetricsError(detail=f"missing columns: {', '.join(missing)}")
    annual = annual.select(REQUIRED_COLUMNS).sort("year")
    if annual.height < MINIMUM_YEARS:
        raise InvalidAnnualMetricsError(detail="at least three complete years required")
    if annual.null_count().sum_horizontal().item() != 0:
        raise InvalidAnnualMetricsError(detail="annual metrics contain missing values")
    if not all(annual.schema[column].is_numeric() for column in REQUIRED_COLUMNS):
        raise InvalidAnnualMetricsError(detail="annual metric columns must be numeric")
    if not annual.schema["year"].is_integer():
        raise InvalidAnnualMetricsError(detail="years must be integers")
    if annual["year"].n_unique() != annual.height:
        raise InvalidAnnualMetricsError(detail="each year must appear exactly once")
    if not annual["year"].is_between(START_YEAR, END_YEAR).all():
        raise InvalidAnnualMetricsError(detail="years must be within 1991-2025")
    if not (annual["valid_days"] == SUMMER_DAYS).all():
        raise InvalidAnnualMetricsError(detail="each summer must contain 92 valid days")
    return annual


def prepare_temperature_rainfall(annual: pl.DataFrame) -> TemperatureRainfallPlotData:
    """Pair complete summers by year and fit temperature on rainfall.

    The OLS line is descriptive, uses an intercept, and spans observed rainfall
    only. It does not remove time trends or establish a causal relationship.
    """
    annual = _prepare_annual_metrics(annual)

    rainfall: NDArray[np.float64] = (
        annual["summer_total_rainfall_mm"].to_numpy().astype(np.float64)
    )
    temperature: NDArray[np.float64] = (
        annual["summer_mean_temp_c"].to_numpy().astype(np.float64)
    )
    years: NDArray[np.int64] = annual["year"].to_numpy().astype(np.int64)
    if not (np.isfinite(rainfall).all() and np.isfinite(temperature).all()):
        raise InvalidAnnualMetricsError(detail="weather metrics must be finite")
    if (rainfall < 0).any():
        raise InvalidAnnualMetricsError(detail="rainfall must be nonnegative")
    centered_rainfall = rainfall - np.mean(rainfall)
    rainfall_variation = float(np.sum(centered_rainfall**2))
    if rainfall_variation == 0:
        raise InvalidAnnualMetricsError(detail="rainfall must vary to fit a line")
    slope = (
        float(np.sum(centered_rainfall * (temperature - np.mean(temperature))))
        / rainfall_variation
    )
    intercept = float(np.mean(temperature)) - slope * float(np.mean(rainfall))
    fitted_rainfall = np.array([float(np.min(rainfall)), float(np.max(rainfall))])
    return TemperatureRainfallPlotData(
        years=years,
        rainfall_mm=rainfall,
        mean_temperature_c=temperature,
        fitted_rainfall_mm=fitted_rainfall,
        fitted_temperature_c=intercept + slope * fitted_rainfall,
    )

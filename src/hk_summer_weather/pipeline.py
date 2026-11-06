"""Run the reproducible data preparation and metric pipeline."""

from dataclasses import dataclass
from pathlib import Path
from typing import Final, override

from hk_summer_weather.cleaning import (
    MeasurementKind,
    build_daily_table,
    build_quality_table,
    read_measurement,
)
from hk_summer_weather.metrics import (
    build_annual_metrics,
    build_monthly_metrics,
    build_period_summaries,
)

MEAN_TEMPERATURE_FILE: Final = "daily_mean_temperature_hko.csv"
MAXIMUM_TEMPERATURE_FILE: Final = "daily_maximum_temperature_hko.csv"
RAINFALL_FILE: Final = "daily_rainfall_hko.csv"


@dataclass(frozen=True, slots=True)
class PipelinePaths:
    """Locate raw inputs and generated data products."""

    raw: Path
    processed: Path
    metrics: Path


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """Summarize generated data row counts."""

    daily_rows: int
    valid_years: int
    annual_rows: int
    monthly_rows: int


@dataclass(frozen=True, slots=True)
class MissingSourceFileError(Exception):
    """Report a required raw source file that is unavailable."""

    path: Path

    @override
    def __str__(self) -> str:
        """Return the missing-source diagnostic."""
        return f"missing source file: {self.path}"


def run_pipeline(paths: PipelinePaths) -> PipelineResult:
    """Build all first- and second-step project data products."""
    required_sources = (
        paths.raw / MEAN_TEMPERATURE_FILE,
        paths.raw / MAXIMUM_TEMPERATURE_FILE,
        paths.raw / RAINFALL_FILE,
    )
    missing_source = next(
        (source for source in required_sources if not source.is_file()),
        None,
    )
    if missing_source is not None:
        raise MissingSourceFileError(path=missing_source)

    mean_temperature = read_measurement(
        required_sources[0],
        MeasurementKind.MEAN_TEMPERATURE,
    )
    maximum_temperature = read_measurement(
        required_sources[1],
        MeasurementKind.MAXIMUM_TEMPERATURE,
    )
    rainfall = read_measurement(
        required_sources[2],
        MeasurementKind.RAINFALL,
    )
    daily = build_daily_table(mean_temperature, maximum_temperature, rainfall)
    quality = build_quality_table(daily)
    annual = build_annual_metrics(daily, quality)
    monthly = build_monthly_metrics(daily, quality)
    periods = build_period_summaries(annual, monthly)

    paths.processed.mkdir(parents=True, exist_ok=True)
    paths.metrics.mkdir(parents=True, exist_ok=True)
    daily.write_csv(paths.processed / "daily_summer_weather_1991_2025.csv")
    quality.write_csv(paths.processed / "summer_data_quality_by_year.csv")
    annual.write_csv(paths.metrics / "annual_summer_metrics.csv")
    monthly.write_csv(paths.metrics / "monthly_summer_metrics.csv")
    periods.annual.write_csv(paths.metrics / "period_annual_summary.csv")
    periods.monthly.write_csv(paths.metrics / "period_monthly_summary.csv")

    return PipelineResult(
        daily_rows=daily.height,
        valid_years=quality.filter("valid_summer").height,
        annual_rows=annual.height,
        monthly_rows=monthly.height,
    )

import numpy as np
import polars as pl
import pytest

from hk_summer_weather.temperature_rainfall import (
    InvalidAnnualMetricsError,
    prepare_temperature_rainfall,
)


def _annual_metrics() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "year": [1993, 1991, 1992],
            "summer_total_rainfall_mm": [1200.0, 800.0, 1000.0],
            "summer_mean_temp_c": [28.0, 30.0, 29.0],
            "valid_days": [92, 92, 92],
        }
    )


def test_scatter_pairs_the_same_year_and_fits_temperature_on_rainfall() -> None:
    # Given
    annual = _annual_metrics()

    # When
    points = prepare_temperature_rainfall(annual)

    # Then
    np.testing.assert_array_equal(points.years, [1991, 1992, 1993])
    np.testing.assert_allclose(
        np.column_stack((points.rainfall_mm, points.mean_temperature_c)),
        [[800.0, 30.0], [1000.0, 29.0], [1200.0, 28.0]],
    )
    np.testing.assert_allclose(points.fitted_rainfall_mm, [800.0, 1200.0])
    np.testing.assert_allclose(points.fitted_temperature_c, [30.0, 28.0])


@pytest.mark.parametrize(
    "annual",
    [
        _annual_metrics().head(1),
        _annual_metrics().drop("summer_mean_temp_c"),
        _annual_metrics().with_columns(pl.lit(1991).alias("year")),
        _annual_metrics().with_columns(pl.lit(91).alias("valid_days")),
        _annual_metrics().with_columns(
            pl.lit(1000.0).alias("summer_total_rainfall_mm")
        ),
        _annual_metrics().with_columns(pl.lit(-1.0).alias("summer_total_rainfall_mm")),
        _annual_metrics().with_columns(
            pl.lit(float("nan")).alias("summer_mean_temp_c")
        ),
        _annual_metrics().with_columns(
            pl.lit(None, dtype=pl.Float64).alias("summer_mean_temp_c")
        ),
    ],
    ids=[
        "insufficient-years",
        "missing-column",
        "duplicate-years",
        "incomplete-summer",
        "constant-rainfall",
        "negative-rainfall",
        "nonfinite-temperature",
        "missing-temperature",
    ],
)
def test_scatter_rejects_metrics_that_cannot_support_the_figure(
    annual: pl.DataFrame,
) -> None:
    # Given / When / Then
    with pytest.raises(InvalidAnnualMetricsError):
        _ = prepare_temperature_rainfall(annual)

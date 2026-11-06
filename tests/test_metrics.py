import polars as pl

from hk_summer_weather.metrics import (
    build_annual_metrics,
    build_monthly_metrics,
    build_period_summaries,
)


def test_build_annual_metrics_applies_thresholds_to_complete_years() -> None:
    # Given
    daily = pl.DataFrame(
        {
            "year": [1991, 1991, 1991, 1991, 1992],
            "month": [6, 6, 7, 8, 6],
            "mean_temp_c": [28.0, 29.0, 30.0, 31.0, 99.0],
            "max_temp_c": [32.9, 33.0, 34.0, 31.0, 99.0],
            "rainfall_mm": [0.0, 0.05, 0.1, 2.0, 99.0],
            "complete_day": [True, True, True, True, False],
        }
    )
    quality = pl.DataFrame({"year": [1991, 1992], "valid_summer": [True, False]})

    # When
    result = build_annual_metrics(daily, quality)

    # Then
    assert result.to_dicts() == [
        {
            "year": 1991,
            "summer_mean_temp_c": 29.5,
            "summer_total_rainfall_mm": 2.15,
            "hot_days_ge_33c": 2,
            "rainy_days_ge_0_1mm": 2,
            "valid_days": 4,
        }
    ]


def test_build_monthly_metrics_uses_month_totals_not_period_totals() -> None:
    # Given
    daily = pl.DataFrame(
        {
            "year": [1991, 1991, 1991],
            "month": [6, 6, 7],
            "mean_temp_c": [28.0, 30.0, 31.0],
            "rainfall_mm": [1.0, 2.0, 4.0],
            "complete_day": [True, True, True],
        }
    )
    quality = pl.DataFrame({"year": [1991], "valid_summer": [True]})

    # When
    result = build_monthly_metrics(daily, quality)

    # Then
    assert result.to_dicts() == [
        {
            "year": 1991,
            "month": 6,
            "monthly_mean_temp_c": 29.0,
            "monthly_total_rainfall_mm": 3.0,
            "valid_days": 2,
        },
        {
            "year": 1991,
            "month": 7,
            "monthly_mean_temp_c": 31.0,
            "monthly_total_rainfall_mm": 4.0,
            "valid_days": 1,
        },
    ]


def test_build_period_summaries_compares_early_and_recent_years() -> None:
    # Given
    annual = pl.DataFrame(
        {
            "year": [1991, 2000, 2010, 2016, 2025],
            "summer_mean_temp_c": [28.0, 30.0, 99.0, 30.0, 32.0],
            "summer_total_rainfall_mm": [400.0, 600.0, 99.0, 500.0, 700.0],
            "hot_days_ge_33c": [1, 3, 99, 4, 6],
            "rainy_days_ge_0_1mm": [30, 40, 99, 35, 45],
            "valid_days": [92, 92, 92, 92, 92],
        }
    )
    monthly = pl.DataFrame(
        {
            "year": [1991, 2000, 2016, 2025],
            "month": [6, 6, 6, 6],
            "monthly_mean_temp_c": [27.0, 29.0, 29.0, 31.0],
            "monthly_total_rainfall_mm": [100.0, 200.0, 150.0, 250.0],
            "valid_days": [30, 30, 30, 30],
        }
    )

    # When
    result = build_period_summaries(annual, monthly)

    # Then
    assert result.annual["period"].to_list() == [
        "early_1991_2000",
        "recent_2016_2025",
    ]
    assert result.annual["average_summer_mean_temp_c"].to_list() == [29.0, 31.0]
    assert result.monthly["average_monthly_total_rainfall_mm"].to_list() == [
        150.0,
        200.0,
    ]

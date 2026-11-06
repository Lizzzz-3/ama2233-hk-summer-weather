from pathlib import Path

import polars as pl
import pytest

from hk_summer_weather.cleaning import (
    DuplicateDateError,
    MeasurementKind,
    build_daily_table,
    build_quality_table,
    read_measurement,
)


def _write_source(path: Path, rows: list[str]) -> Path:
    source = path / "source.csv"
    content = "\n".join(
        [
            "Daily weather at the Hong Kong Observatory",
            "Downloaded test fixture",
            "年/Year,月/Month,日/Day,數值/Value,數據完整性/data Completeness",
            *rows,
            "*** 沒有數據/unavailable",
            "# 數據不完整/data incomplete",
        ]
    )
    _ = source.write_text(content, encoding="utf-8-sig")
    return source


def test_read_measurement_parses_trace_when_rainfall_is_complete(
    tmp_path: Path,
) -> None:
    # Given
    source = _write_source(
        tmp_path,
        ["1991,6,1,Trace,C", "1991,6,2,***,"],
    )

    # When
    result = read_measurement(source, MeasurementKind.RAINFALL)

    # Then
    assert result.to_dicts() == [
        {
            "date": result["date"][0],
            "rainfall_mm": 0.0,
            "rainfall_trace": True,
            "rainfall_complete": True,
        },
        {
            "date": result["date"][1],
            "rainfall_mm": None,
            "rainfall_trace": False,
            "rainfall_complete": False,
        },
    ]


def test_read_measurement_keeps_only_study_summers(tmp_path: Path) -> None:
    # Given
    source = _write_source(
        tmp_path,
        [
            "1990,6,1,27.1,C",
            "1991,5,31,27.2,C",
            "1991,6,1,27.3,C",
            "2025,8,31,29.4,C",
            "2026,6,1,29.5,C",
        ],
    )

    # When
    result = read_measurement(source, MeasurementKind.MEAN_TEMPERATURE)

    # Then
    assert result["mean_temp_c"].to_list() == [27.3, 29.4]


def test_read_measurement_rejects_duplicate_dates(tmp_path: Path) -> None:
    # Given
    source = _write_source(
        tmp_path,
        ["1991,6,1,27.3,C", "1991,6,1,27.4,C"],
    )

    # When
    with pytest.raises(DuplicateDateError) as caught:
        _ = read_measurement(source, MeasurementKind.MEAN_TEMPERATURE)

    # Then
    assert caught.value.duplicate_rows == 1


def test_build_quality_table_marks_only_full_summers_valid() -> None:
    # Given
    dates = pl.date_range(
        pl.date(1991, 6, 1),
        pl.date(1991, 8, 31),
        interval="1d",
        eager=True,
    )
    mean_temperature = pl.DataFrame(
        {
            "date": dates,
            "mean_temp_c": [28.0] * len(dates),
            "mean_temp_complete": [True] * len(dates),
        }
    )
    maximum_temperature = pl.DataFrame(
        {
            "date": dates,
            "max_temp_c": [32.0] * len(dates),
            "max_temp_complete": [True] * len(dates),
        }
    )
    rainfall = pl.DataFrame(
        {
            "date": dates,
            "rainfall_mm": [0.0] * len(dates),
            "rainfall_trace": [False] * len(dates),
            "rainfall_complete": [True] * len(dates),
        }
    )

    # When
    quality = build_quality_table(
        build_daily_table(mean_temperature, maximum_temperature, rainfall)
    )

    # Then
    year_1991 = quality.filter(pl.col("year") == 1991).row(0, named=True)
    year_1992 = quality.filter(pl.col("year") == 1992).row(0, named=True)
    assert year_1991["complete_days"] == 92
    assert year_1991["valid_summer"] is True
    assert year_1992["complete_days"] == 0
    assert year_1992["valid_summer"] is False

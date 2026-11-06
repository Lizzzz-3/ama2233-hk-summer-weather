import subprocess
import sys
from pathlib import Path

import polars as pl


def test_cli_builds_all_data_products_from_official_raw_files(
    tmp_path: Path,
) -> None:
    # Given
    project_root = Path(__file__).parents[1]
    processed = tmp_path / "processed"
    metrics = tmp_path / "metrics"

    # When
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "hk_summer_weather.cli",
            "build",
            "--raw-dir",
            str(project_root / "data/raw"),
            "--processed-dir",
            str(processed),
            "--metrics-dir",
            str(metrics),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    # Then
    assert completed.returncode == 0, completed.stderr
    assert "daily_rows=3220 valid_years=35" in completed.stdout
    assert pl.read_csv(processed / "daily_summer_weather_1991_2025.csv").height == 3220
    assert pl.read_csv(metrics / "annual_summer_metrics.csv").height == 35
    assert pl.read_csv(metrics / "monthly_summer_metrics.csv").height == 105
    assert pl.read_csv(metrics / "period_annual_summary.csv").height == 2
    assert pl.read_csv(metrics / "period_monthly_summary.csv").height == 6


def test_cli_reports_missing_raw_files_without_traceback(tmp_path: Path) -> None:
    # Given
    missing_raw = tmp_path / "missing-raw"

    # When
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "hk_summer_weather.cli",
            "build",
            "--raw-dir",
            str(missing_raw),
            "--processed-dir",
            str(tmp_path / "processed"),
            "--metrics-dir",
            str(tmp_path / "metrics"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    # Then
    assert completed.returncode == 2
    assert "missing source file" in completed.stderr
    assert "Traceback" not in completed.stderr

"""Command-line interface for the weather data pipeline."""

from pathlib import Path
from typing import Annotated, Final

import typer

from hk_summer_weather.pipeline import (
    MissingSourceFileError,
    PipelinePaths,
    run_pipeline,
)

app = typer.Typer(no_args_is_help=True)
DEFAULT_RAW_DIR: Final = Path("data/raw")
DEFAULT_PROCESSED_DIR: Final = Path("data/processed")
DEFAULT_METRICS_DIR: Final = Path("data/metrics")


@app.callback()
def root() -> None:
    """Prepare Hong Kong summer weather project data."""


@app.command()
def build(
    raw_dir: Annotated[Path, typer.Option()] = DEFAULT_RAW_DIR,
    processed_dir: Annotated[Path, typer.Option()] = DEFAULT_PROCESSED_DIR,
    metrics_dir: Annotated[Path, typer.Option()] = DEFAULT_METRICS_DIR,
) -> None:
    """Generate cleaned daily data and annual and monthly metrics."""
    try:
        result = run_pipeline(
            PipelinePaths(raw=raw_dir, processed=processed_dir, metrics=metrics_dir)
        )
    except MissingSourceFileError as error:
        message = str(error)
        raise typer.BadParameter(message, param_hint="--raw-dir") from error
    summary_fields = [
        f"daily_rows={result.daily_rows}",
        f"valid_years={result.valid_years}",
        f"annual_rows={result.annual_rows}",
        f"monthly_rows={result.monthly_rows}",
    ]
    typer.echo(" ".join(summary_fields))


def main() -> None:
    """Run the command-line application."""
    app()


if __name__ == "__main__":
    main()

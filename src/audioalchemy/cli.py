"""CLI entrypoint for AudioAlchemy.

Defines the Typer application and all subcommands. Business logic is delegated
entirely to the service layer — the CLI is responsible only for argument
parsing, validation, and user-facing output.

Entry point registered in ``pyproject.toml``::

    [project.scripts]
    audioalchemy = "audioalchemy.cli:app"
"""

from pathlib import Path

import typer
from rich.console import Console

from audioalchemy.config.settings import get_settings
from audioalchemy.services.pipeline import ConversionPipeline
from audioalchemy.utils.album_meta import ALBUM_MD_FILENAME, ALBUM_MD_TEMPLATE
from audioalchemy.utils.logging import configure_logging

app = typer.Typer(
    name="audioalchemy",
    help="Batch audio conversion and metadata management.",
    add_completion=False,
)

console = Console()

_SUPPORTED_FORMATS = ["mp3", "wav", "flac", "ogg", "aac"]


@app.callback()
def main() -> None:
    """AudioAlchemy — transform your audio library at scale."""
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def convert(
    input_dir: Path = typer.Argument(
        ...,
        help="Directory containing source audio files.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
    output_dir: Path = typer.Argument(
        ...,
        help="Destination directory for converted files.",
        resolve_path=True,
    ),
    format: str = typer.Option(  # noqa: A002
        None,
        "--format",
        "-f",
        help=f"Output audio format. Supported: {', '.join(_SUPPORTED_FORMATS)}.",
    ),
) -> None:
    """Convert all audio files in INPUT_DIR to the target format.

    Files are written to OUTPUT_DIR preserving the relative directory structure
    of INPUT_DIR. The output directory is created if it does not exist.

    Example::

        audioalchemy convert ./music ./converted --format mp3
    """
    settings = get_settings()
    output_format = format or settings.default_format

    if output_format not in _SUPPORTED_FORMATS:
        console.print(
            f"[bold red]Error:[/bold red] Unsupported format '{output_format}'. "
            f"Choose from: {', '.join(_SUPPORTED_FORMATS)}."
        )
        raise typer.Exit(code=1)

    console.print(
        f"[bold green]AudioAlchemy[/bold green] · converting "
        f"[cyan]{input_dir}[/cyan] → [cyan]{output_dir}[/cyan] "
        f"([bold]{output_format}[/bold])"
    )

    pipeline = ConversionPipeline(settings=settings, output_format=output_format)
    pipeline.run(input_dir=input_dir, output_dir=output_dir)

    console.print("[bold green]Done.[/bold green]")


@app.command("init-album")
def init_album(
    directory: Path = typer.Argument(
        ...,
        help="Directory where the album metadata template will be created.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help=f"Overwrite an existing {ALBUM_MD_FILENAME}.",
    ),
) -> None:
    """Generate an album metadata template (_album.md) in DIRECTORY.

    Edit the generated file to fill in shared album tags (title, year,
    artist, genre, etc.). These values are merged into every track's
    metadata during conversion.

    Example::

        audioalchemy init-album ./music
    """
    target = directory / ALBUM_MD_FILENAME

    if target.exists() and not force:
        console.print(
            f"[yellow]{target}[/yellow] already exists. "
            "Use [bold]--force[/bold] to overwrite."
        )
        raise typer.Exit(code=1)

    target.write_text(ALBUM_MD_TEMPLATE, encoding="utf-8")
    console.print(f"[bold green]Created[/bold green] [cyan]{target}[/cyan]")

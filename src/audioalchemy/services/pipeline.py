"""Conversion pipeline — orchestrates the full batch conversion workflow.

The pipeline is the single point of coordination between filesystem scanning,
audio conversion, and metadata management. The CLI delegates entirely to this
layer and should contain no business logic of its own.

TODO: Wire up concrete ``AudioConverter`` and ``MetadataManager`` implementations
      once they exist.
"""

from pathlib import Path

from audioalchemy.config.settings import Settings
from audioalchemy.utils.album_meta import load_album_meta
from audioalchemy.utils.filename import parse_filename
from audioalchemy.utils.filesystem import scan_directory
from audioalchemy.utils.logging import get_logger

logger = get_logger(__name__)


class ConversionPipeline:
    """Orchestrates batch audio conversion from an input directory to an output directory.

    Responsibilities:
    - Discover source files via :func:`~audioalchemy.utils.filesystem.scan_directory`.
    - Parse per-track metadata from filenames via :func:`~audioalchemy.utils.filename.parse_filename`.
    - Load shared album metadata from ``_album.md`` via :func:`~audioalchemy.utils.album_meta.load_album_meta`.
    - Delegate each file to an ``AudioConverter`` (not yet wired).
    - Optionally copy/rewrite metadata via a ``MetadataManager`` (not yet wired).
    - Report progress to the logger.

    Args:
        settings: Application configuration resolved from the environment.
        output_format: Target audio format for this run (e.g. ``"mp3"``).
    """

    def __init__(self, settings: Settings, output_format: str) -> None:
        self._settings = settings
        self._output_format = output_format
        # TODO: Inject AudioConverter and MetadataManager once implemented.

    def run(self, input_dir: Path, output_dir: Path) -> None:
        """Execute the full batch conversion pipeline.

        Scans *input_dir* for supported audio files, parses filename metadata,
        merges album-level metadata from ``_album.md`` (if present), and
        converts each file to *output_format* under *output_dir* preserving
        the relative directory structure and the original filename stem.

        Args:
            input_dir: Directory containing source audio files.
            output_dir: Directory where converted files will be written.

        TODO: Replace placeholder log statements with real conversion calls.
        """
        logger.info(
            "Starting conversion pipeline — input=%s output=%s format=%s",
            input_dir,
            output_dir,
            self._output_format,
        )

        album_meta = load_album_meta(input_dir)
        if album_meta is not None:
            logger.info("Loaded album metadata from _album.md: album=%r", album_meta.album)
        else:
            logger.debug("No _album.md found in %s — album fields will be empty.", input_dir)

        source_files = scan_directory(input_dir)

        if not source_files:
            logger.warning("No audio files found in %s", input_dir)
            return

        output_dir.mkdir(parents=True, exist_ok=True)

        for source in source_files:
            # Preserve relative structure and original filename stem.
            relative = source.relative_to(input_dir)
            destination = output_dir / relative.with_suffix(f".{self._output_format}")

            # Parse per-track metadata from the filename.
            track_info = parse_filename(source.stem)

            # Build merged metadata: album fields first, track fields override.
            metadata: dict[str, str | list[str]] = {}
            if album_meta is not None:
                metadata.update(album_meta.to_metadata_record())

            if track_info.track_number is not None:
                metadata["tracknumber"] = str(track_info.track_number)
            metadata["title"] = track_info.title
            if track_info.artists:
                metadata["artist"] = track_info.artists  # type: ignore[assignment]

            logger.info(
                "[stub] %s → %s | track=%s title=%r artists=%s",
                source.name,
                destination.name,
                track_info.track_number,
                track_info.title,
                track_info.artists,
            )
            # TODO: destination.parent.mkdir(parents=True, exist_ok=True)
            # TODO: converter.convert(source, destination, self._output_format)
            # TODO: metadata_manager.write(destination, metadata)

        logger.info("Pipeline complete. %d file(s) processed (stub).", len(source_files))

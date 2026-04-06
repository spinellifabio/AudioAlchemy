"""Conversion pipeline — orchestrates the full batch conversion workflow.

The pipeline is the single point of coordination between filesystem scanning,
audio conversion, and metadata management. The CLI delegates entirely to this
layer and should contain no business logic of its own.

TODO: Wire up concrete ``AudioConverter`` and ``MetadataManager`` implementations
      once they exist.
"""

from pathlib import Path

from audioalchemy.config.settings import Settings
from audioalchemy.utils.filesystem import scan_directory
from audioalchemy.utils.logging import get_logger

logger = get_logger(__name__)


class ConversionPipeline:
    """Orchestrates batch audio conversion from an input directory to an output directory.

    Responsibilities:
    - Discover source files via :func:`~audioalchemy.utils.filesystem.scan_directory`.
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

        Scans *input_dir* for supported audio files, converts each one to
        *output_format*, and writes the result under *output_dir* preserving
        the relative directory structure.

        Args:
            input_dir: Directory containing source audio files.
            output_dir: Directory where converted files will be written.

        TODO: Replace placeholder log statements with real conversion calls.
        """
        logger.info(
            "Starting conversion pipeline",
            extra={
                "input_dir": str(input_dir),
                "output_dir": str(output_dir),
                "format": self._output_format,
            },
        )

        source_files = scan_directory(input_dir)

        if not source_files:
            logger.warning("No audio files found in %s", input_dir)
            return

        output_dir.mkdir(parents=True, exist_ok=True)

        for source in source_files:
            relative = source.relative_to(input_dir)
            destination = output_dir / relative.with_suffix(f".{self._output_format}")

            logger.info("[stub] Would convert %s → %s", source, destination)
            # TODO: converter.convert(source, destination, self._output_format)
            # TODO: metadata = metadata_manager.read(source)
            # TODO: metadata_manager.write(destination, metadata)

        logger.info("Pipeline complete. %d file(s) processed (stub).", len(source_files))

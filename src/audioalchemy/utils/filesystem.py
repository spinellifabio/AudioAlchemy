"""Filesystem utilities for discovering audio files.

Provides helpers for recursively scanning directories and filtering results
by audio file extension. No audio parsing is performed here — this module
deals only with the filesystem.
"""

from pathlib import Path

# File extensions recognised as audio. Extend this set as new formats are supported.
AUDIO_EXTENSIONS: frozenset[str] = frozenset(
    {".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a", ".wma", ".opus"}
)


def scan_directory(directory: Path, recursive: bool = True) -> list[Path]:
    """Return all audio files found under *directory*.

    Args:
        directory: Root directory to scan.
        recursive: When ``True`` (default) the scan descends into sub-directories.

    Returns:
        A sorted list of :class:`~pathlib.Path` objects pointing to audio files.
        Returns an empty list if *directory* contains no recognised audio files.

    Raises:
        NotADirectoryError: If *directory* exists but is not a directory.
        FileNotFoundError: If *directory* does not exist.
    """
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")

    glob_pattern = "**/*" if recursive else "*"
    candidates = directory.glob(glob_pattern)

    return sorted(
        path
        for path in candidates
        if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS
    )

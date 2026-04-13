"""Album-level metadata loader.

Reads a ``_album.md`` file placed alongside audio files. The file uses YAML
frontmatter (between ``---`` delimiters) to store shared, album-wide tags that
are merged with per-track metadata during conversion.

File format::

    ---
    album: "Wind Ensemble Classics"
    year: "2024"
    album_artist: "Tokyo Wind Ensemble"
    genre: "Classical"
    comment: "Recorded live at Suntory Hall"
    ---

    # Album Notes

    Freeform notes here — this section is ignored during extraction.

Only the frontmatter block is parsed; everything after the closing ``---`` is
treated as freeform markdown and ignored.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ALBUM_MD_FILENAME = "_album.md"

# Matches the YAML frontmatter block at the start of the file.
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


@dataclass
class AlbumMeta:
    """Album-level metadata shared across all tracks in a directory.

    All fields are optional strings; unset fields are empty strings.

    Attributes:
        album: Album title.
        year: Release year (stored as string to preserve formatting).
        album_artist: Primary artist credited to the album as a whole.
        genre: Musical genre.
        comment: Freeform comment written to the comment tag of every track.
    """

    album: str = ""
    year: str = ""
    album_artist: str = ""
    genre: str = ""
    comment: str = ""
    extra: dict[str, str] = field(default_factory=dict)

    def to_metadata_record(self) -> dict[str, str]:
        """Return a flat dict suitable for merging into a ``MetadataRecord``.

        Only non-empty standard fields are included. Unknown keys from
        *extra* are also included.
        """
        record: dict[str, str] = {}
        for key in ("album", "year", "album_artist", "genre", "comment"):
            value = getattr(self, key)
            if value:
                record[key] = value
        record.update({k: v for k, v in self.extra.items() if v})
        return record


def load_album_meta(directory: Path) -> AlbumMeta | None:
    """Load album metadata from ``_album.md`` in *directory*.

    Args:
        directory: Directory that may contain a ``_album.md`` file.

    Returns:
        An :class:`AlbumMeta` instance if the file exists and contains valid
        frontmatter, or ``None`` if no ``_album.md`` is found.

    Raises:
        ValueError: If the frontmatter block exists but cannot be parsed as YAML.
    """
    md_path = directory / ALBUM_MD_FILENAME
    if not md_path.exists():
        return None

    text = md_path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        # File exists but has no frontmatter — return empty AlbumMeta.
        return AlbumMeta()

    try:
        data: dict = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML frontmatter in {md_path}: {exc}") from exc

    known = {"album", "year", "album_artist", "genre", "comment"}
    extra = {k: str(v) for k, v in data.items() if k not in known and v is not None}

    return AlbumMeta(
        album=str(data.get("album") or ""),
        year=str(data.get("year") or ""),
        album_artist=str(data.get("album_artist") or ""),
        genre=str(data.get("genre") or ""),
        comment=str(data.get("comment") or ""),
        extra=extra,
    )


ALBUM_MD_TEMPLATE = """\
---
album: ""
year: ""
album_artist: ""
genre: ""
comment: ""
---

# Album Notes

Add any freeform notes here. This section is ignored during metadata extraction.
"""

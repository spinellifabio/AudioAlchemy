"""Audio filename parser.

Parses the structured filename convention used by AudioAlchemy:

    ``{NN} {Title} - {Artist1}, {Artist2} - arr. {Artist3}``

Rules:
- The filename stem (no extension) is split on `` - `` separators.
- The first segment contains the optional zero-padded track number followed
  by the track title.
- Every subsequent segment is a comma-separated list of artist names.
  The ``arr.`` prefix is preserved as part of the artist name so that the
  role (arranger) is retained in the metadata.

Example::

    >>> info = parse_filename(
    ...     "05 Beauty and the Beast Medley - Howard Ashman, Alan Menken - arr. Toshio Mashima"
    ... )
    >>> info.track_number
    5
    >>> info.title
    'Beauty and the Beast Medley'
    >>> info.artists
    ['Howard Ashman', 'Alan Menken', 'arr. Toshio Mashima']
"""

import re
from dataclasses import dataclass, field

# Matches an optional leading track number: one or more digits followed by a space.
_TRACK_NUMBER_RE = re.compile(r"^(\d+)\s+(.+)$")

# Matches arranger credit embedded directly in the title after a comma, e.g.
# "ABBA GOLD, Arr. Ron Sebregts" — used when there is no ' - ' separator.
_EMBEDDED_ARR_RE = re.compile(r",\s+([Aa]rr\..+)$")

# Matches a trailing performance qualifier in the last artist field, e.g. " (bis)".
# Requires a space before the opening paren so it does not match identifiers like
# "Arr. Bittmar(01)" where the paren is part of the name.
_TRAILING_QUALIFIER_RE = re.compile(r"\s+\([^)]+\)$")


@dataclass
class TrackInfo:
    """Structured metadata extracted from an audio filename stem.

    Attributes:
        track_number: Numeric position of the track, or ``None`` if the
            filename does not start with a digit sequence.
        title: Track title extracted from the first filename segment.
        artists: Ordered list of artist names found across all non-title
            segments. The ``arr.`` prefix is kept as part of the name.
    """

    title: str
    artists: list[str] = field(default_factory=list)
    track_number: int | None = None


def parse_filename(stem: str) -> TrackInfo:
    """Parse an audio filename stem into structured metadata.

    Args:
        stem: The filename without its extension, e.g.
            ``"05 Beauty and the Beast Medley - Howard Ashman, Alan Menken - arr. Toshio Mashima"``.

    Returns:
        A :class:`TrackInfo` with *track_number*, *title*, and *artists* populated.
    """
    segments = [s.strip() for s in stem.split(" - ")]

    # --- Parse title segment (first) ---
    title_segment = segments[0]
    track_number: int | None = None

    match = _TRACK_NUMBER_RE.match(title_segment)
    if match:
        track_number = int(match.group(1))
        title = match.group(2).strip()
    else:
        title = title_segment.strip()

    # --- Parse artist segments (remainder) ---
    # The arr. prefix is preserved so the arranger role is visible in metadata.
    artists: list[str] = []
    for segment in segments[1:]:
        for raw_name in segment.split(","):
            name = raw_name.strip()
            if name:
                artists.append(name)

    # Fallback: arranger credit embedded in the title without a ' - ' separator,
    # e.g. "ABBA GOLD, Arr. Ron Sebregts". Split at the first ', Arr.' occurrence.
    if not artists:
        arr_match = _EMBEDDED_ARR_RE.search(title)
        if arr_match:
            title = title[: arr_match.start()].strip()
            for raw_name in arr_match.group(1).split(","):
                name = raw_name.strip()
                if name:
                    artists.append(name)

    # A trailing " (qualifier)" on the last artist (e.g. " (bis)") belongs to the
    # track title, not the artist name. Move it back to the title.
    if artists:
        q_match = _TRAILING_QUALIFIER_RE.search(artists[-1])
        if q_match:
            artists[-1] = artists[-1][: q_match.start()]
            title = title + q_match.group(0)

    return TrackInfo(title=title, artists=artists, track_number=track_number)

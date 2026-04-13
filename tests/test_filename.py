"""Unit tests for audioalchemy.utils.filename."""

import pytest

from audioalchemy.utils.filename import TrackInfo, parse_filename


class TestParseFilename:
    def test_full_pattern(self) -> None:
        """Canonical example: track number, title, multiple artists, arr. prefix preserved."""
        info = parse_filename(
            "05 Beauty and the Beast Medley - Howard Ashman, Alan Menken - arr. Toshio Mashima"
        )
        assert info.track_number == 5
        assert info.title == "Beauty and the Beast Medley"
        assert info.artists == ["Howard Ashman", "Alan Menken", "arr. Toshio Mashima"]

    def test_single_artist(self) -> None:
        info = parse_filename("01 Overture - John Williams")
        assert info.track_number == 1
        assert info.title == "Overture"
        assert info.artists == ["John Williams"]

    def test_no_track_number(self) -> None:
        info = parse_filename("Theme - Hans Zimmer")
        assert info.track_number is None
        assert info.title == "Theme"
        assert info.artists == ["Hans Zimmer"]

    def test_no_artists(self) -> None:
        info = parse_filename("03 Interlude")
        assert info.track_number == 3
        assert info.title == "Interlude"
        assert info.artists == []

    def test_arr_prefix_preserved(self) -> None:
        """arr. prefix is kept as part of the artist name."""
        info = parse_filename("02 Song - arr. Toshio Mashima")
        assert info.artists == ["arr. Toshio Mashima"]

    def test_multiple_artist_segments(self) -> None:
        """Multiple ' - ' segments each contribute artists."""
        info = parse_filename("10 Finale - Composer A, Composer B - arr. Arranger C")
        assert info.artists == ["Composer A", "Composer B", "arr. Arranger C"]

    def test_zero_padded_track_number(self) -> None:
        info = parse_filename("09 Waltz - Chopin")
        assert info.track_number == 9

    def test_large_track_number(self) -> None:
        info = parse_filename("42 Epic Track - Artist")
        assert info.track_number == 42

    def test_title_with_hyphen_inside(self) -> None:
        """Hyphens inside a title (not surrounded by spaces) must be preserved."""
        info = parse_filename("07 A-B-C Song - Artist")
        assert info.title == "A-B-C Song"

    def test_returns_track_info_type(self) -> None:
        assert isinstance(parse_filename("01 Test - Artist"), TrackInfo)

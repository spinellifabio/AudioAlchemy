"""Unit tests for audioalchemy.utils.album_meta."""

import pytest

from audioalchemy.utils.album_meta import (
    ALBUM_MD_FILENAME,
    ALBUM_MD_TEMPLATE,
    AlbumMeta,
    load_album_meta,
)


class TestLoadAlbumMeta:
    def test_returns_none_when_missing(self, tmp_path):
        assert load_album_meta(tmp_path) is None

    def test_reads_standard_fields(self, tmp_path):
        (tmp_path / ALBUM_MD_FILENAME).write_text(
            "---\n"
            "album: Wind Ensemble Classics\n"
            "date: '2024-04-11'\n"
            "album_artist: Tokyo Wind Ensemble\n"
            "genre: Classical\n"
            "comment: Recorded live\n"
            "---\n",
            encoding="utf-8",
        )
        meta = load_album_meta(tmp_path)
        assert meta is not None
        assert meta.album == "Wind Ensemble Classics"
        assert meta.date == "2024-04-11"
        assert meta.album_artist == "Tokyo Wind Ensemble"
        assert meta.genre == "Classical"
        assert meta.comment == "Recorded live"

    def test_year_accepted_as_date_fallback(self, tmp_path):
        (tmp_path / ALBUM_MD_FILENAME).write_text(
            "---\nalbum: Test\nyear: '2024'\n---\n", encoding="utf-8"
        )
        meta = load_album_meta(tmp_path)
        assert meta is not None
        assert meta.date == "2024"
        assert "year" not in meta.extra

    def test_date_takes_precedence_over_year(self, tmp_path):
        (tmp_path / ALBUM_MD_FILENAME).write_text(
            "---\nalbum: Test\ndate: '2026-04-11'\nyear: '2024'\n---\n", encoding="utf-8"
        )
        meta = load_album_meta(tmp_path)
        assert meta is not None
        assert meta.date == "2026-04-11"

    def test_extra_fields_captured(self, tmp_path):
        (tmp_path / ALBUM_MD_FILENAME).write_text(
            "---\nalbum: Test\nconductor: Seiji Ozawa\n---\n",
            encoding="utf-8",
        )
        meta = load_album_meta(tmp_path)
        assert meta is not None
        assert meta.extra.get("conductor") == "Seiji Ozawa"

    def test_missing_fields_default_to_empty_string(self, tmp_path):
        (tmp_path / ALBUM_MD_FILENAME).write_text(
            "---\nalbum: Only Album\n---\n", encoding="utf-8"
        )
        meta = load_album_meta(tmp_path)
        assert meta is not None
        assert meta.date == ""
        assert meta.genre == ""

    def test_file_without_frontmatter_returns_empty_meta(self, tmp_path):
        (tmp_path / ALBUM_MD_FILENAME).write_text(
            "# Just notes\nNo frontmatter here.\n", encoding="utf-8"
        )
        meta = load_album_meta(tmp_path)
        assert isinstance(meta, AlbumMeta)
        assert meta.album == ""

    def test_invalid_yaml_raises_value_error(self, tmp_path):
        (tmp_path / ALBUM_MD_FILENAME).write_text(
            "---\n: bad: yaml: [\n---\n", encoding="utf-8"
        )
        with pytest.raises(ValueError, match="Invalid YAML"):
            load_album_meta(tmp_path)

    def test_notes_section_ignored(self, tmp_path):
        (tmp_path / ALBUM_MD_FILENAME).write_text(
            "---\nalbum: Test\n---\n\n# Notes\nSome freeform text.\n",
            encoding="utf-8",
        )
        meta = load_album_meta(tmp_path)
        assert meta is not None
        assert meta.album == "Test"


class TestAlbumMetaToMetadataRecord:
    def test_empty_fields_excluded(self):
        meta = AlbumMeta(album="Test", date="", genre="")
        record = meta.to_metadata_record()
        assert "album" in record
        assert "date" not in record
        assert "genre" not in record

    def test_all_fields_included_when_set(self):
        meta = AlbumMeta(
            album="A", date="2020-06-15", album_artist="B", genre="Jazz", comment="C"
        )
        record = meta.to_metadata_record()
        assert record == {
            "album": "A",
            "date": "2020-06-15",
            "album_artist": "B",
            "genre": "Jazz",
            "comment": "C",
        }

    def test_extra_fields_included(self):
        meta = AlbumMeta(extra={"conductor": "Ozawa"})
        record = meta.to_metadata_record()
        assert record["conductor"] == "Ozawa"


class TestAlbumMdTemplate:
    def test_template_has_required_keys(self):
        for key in ("album", "date", "album_artist", "genre", "comment"):
            assert key in ALBUM_MD_TEMPLATE

    def test_template_has_frontmatter_delimiters(self):
        assert ALBUM_MD_TEMPLATE.startswith("---")
        assert "---" in ALBUM_MD_TEMPLATE[3:]

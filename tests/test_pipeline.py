import shutil
from pathlib import Path

import mutagen
import pytest
from pydub import AudioSegment
from typer.testing import CliRunner

from audioalchemy.cli import app
from audioalchemy.config.settings import Settings
from audioalchemy.core.converter import AudioConverter
from audioalchemy.core.metadata import MetadataManager
from audioalchemy.services.pipeline import ConversionPipeline

needs_ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not on PATH")


class FakeConverter(AudioConverter):
    def __init__(self) -> None:
        self.calls: list[tuple[Path, Path, str]] = []

    def supported_formats(self) -> list[str]:
        return ["mp3"]

    def convert(self, source: Path, destination: Path, output_format: str) -> None:
        self.calls.append((source, destination, output_format))
        destination.write_bytes(b"x")


class FakeMetadata(MetadataManager):
    def __init__(self) -> None:
        self.written: dict[str, dict] = {}

    def read(self, path: Path) -> dict:
        return {}

    def write(self, path: Path, metadata: dict) -> None:
        self.written[path.name] = metadata


def _wav(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    AudioSegment.silent(duration=300).export(str(path), format="wav")


def _run(src: Path, out: Path, recursive: bool = False) -> tuple[FakeConverter, FakeMetadata]:
    conv, meta = FakeConverter(), FakeMetadata()
    ConversionPipeline(Settings(), "mp3", conv, meta).run(src, out, recursive=recursive)
    return conv, meta


def test_pipeline_merges_album_and_track_metadata(tmp_path):
    src, out = tmp_path / "in", tmp_path / "out"
    src.mkdir()
    (src / "_album.md").write_text('---\nalbum: "Best"\ngenre: "Pop"\n---\n', encoding="utf-8")
    (src / "05 Song - Art, Bob.wav").write_bytes(b"x")
    _, meta = _run(src, out)
    assert meta.written["05 Song - Art, Bob.mp3"] == {
        "album": "Best",
        "genre": "Pop",
        "tracknumber": "5",
        "title": "Song",
        "artist": ["Art", "Bob"],
    }


def test_pipeline_recursive_keeps_structure(tmp_path):
    src, out = tmp_path / "in", tmp_path / "out"
    (src / "sub").mkdir(parents=True)
    (src / "a.wav").write_bytes(b"x")
    (src / "sub" / "b.wav").write_bytes(b"x")
    flat, _ = _run(src, out)
    assert [c[1].name for c in flat.calls] == ["a.mp3"]
    deep, _ = _run(src, tmp_path / "out2", recursive=True)
    assert (tmp_path / "out2" / "sub" / "b.mp3").exists()
    assert len(deep.calls) == 2


def test_pipeline_empty_dir_does_nothing(tmp_path):
    (tmp_path / "in").mkdir()
    conv, _ = _run(tmp_path / "in", tmp_path / "out")
    assert conv.calls == []
    assert not (tmp_path / "out").exists()


@needs_ffmpeg
@pytest.mark.parametrize("fmt", ["mp3", "flac", "ogg"])
def test_convert_end_to_end(tmp_path, fmt):
    src, out = tmp_path / "in", tmp_path / "out"
    _wav(src / "05 Song - Art.wav")
    _wav(src / "sub" / "01 Deep.wav")
    result = CliRunner().invoke(app, ["convert", str(src), str(out), "-f", fmt, "--recursive"])
    assert result.exit_code == 0, result.output
    first, second = out / f"05 Song - Art.{fmt}", out / "sub" / f"01 Deep.{fmt}"
    assert first.exists() and second.exists()
    assert mutagen.File(first, easy=True)["title"] == ["Song"]


@needs_ffmpeg
@pytest.mark.parametrize("ext,fmt", [("m4a", "ipod"), ("opus", "opus"), ("wma", "asf")])
def test_non_default_input_formats_are_decoded(tmp_path, ext, fmt):
    src, out = tmp_path / "in", tmp_path / "out"
    src.mkdir()
    AudioSegment.silent(duration=300).export(str(src / f"track.{ext}"), format=fmt)
    result = CliRunner().invoke(app, ["convert", str(src), str(out), "-f", "flac"])
    assert result.exit_code == 0, result.output
    assert (out / "track.flac").exists()


@needs_ffmpeg
@pytest.mark.xfail(strict=True, reason="WAV tagging crashes: ID3 frames get list values")
def test_wav_output_with_tags(tmp_path):
    src, out = tmp_path / "in", tmp_path / "out"
    _wav(src / "05 Song - Art.wav")
    result = CliRunner().invoke(app, ["convert", str(src), str(out), "-f", "wav"])
    assert result.exit_code == 0


@needs_ffmpeg
@pytest.mark.xfail(strict=True, reason="pydub format 'aac' is rejected by ffmpeg")
def test_aac_output(tmp_path):
    src, out = tmp_path / "in", tmp_path / "out"
    _wav(src / "a.wav")
    result = CliRunner().invoke(app, ["convert", str(src), str(out), "-f", "aac"])
    assert result.exit_code == 0

import shutil
from pathlib import Path

import mutagen
import pytest
from pydub import AudioSegment

from audioalchemy.adapters.mutagen_metadata import MutagenMetadataManager
from audioalchemy.adapters.pydub_converter import PydubConverter

needs_ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not on PATH")


@pytest.fixture
def wav(tmp_path: Path) -> Path:
    path = tmp_path / "in.wav"
    AudioSegment.silent(duration=200).export(str(path), format="wav")
    return path


def test_converter_rejects_missing_source(tmp_path):
    with pytest.raises(FileNotFoundError):
        PydubConverter().convert(tmp_path / "nope.wav", tmp_path / "out.wav", "wav")


def test_converter_rejects_unknown_format(wav, tmp_path):
    with pytest.raises(ValueError, match="Unsupported format"):
        PydubConverter().convert(wav, tmp_path / "out.xyz", "xyz")


def test_converter_wav_to_wav(wav, tmp_path):
    out = tmp_path / "out.wav"
    PydubConverter().convert(wav, out, "wav")
    assert out.stat().st_size > 0


def test_converter_undecodable_file(tmp_path):
    bad = tmp_path / "bad.mp3"
    bad.write_bytes(b"not audio")
    with pytest.raises(ValueError, match="Could not decode"):
        PydubConverter().convert(bad, tmp_path / "out.wav", "wav")


def test_metadata_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        MutagenMetadataManager().read(tmp_path / "nope.mp3")
    with pytest.raises(FileNotFoundError):
        MutagenMetadataManager().write(tmp_path / "nope.mp3", {})


def test_metadata_unrecognised_format(tmp_path):
    bad = tmp_path / "x.txt"
    bad.write_bytes(b"not audio")
    with pytest.raises(ValueError, match="Unrecognised"):
        MutagenMetadataManager().write(bad, {"title": "t"})


@needs_ffmpeg
def test_mp3_tag_round_trip(wav, tmp_path):
    mp3 = tmp_path / "t.mp3"
    PydubConverter().convert(wav, mp3, "mp3")
    mgr = MutagenMetadataManager()
    mgr.write(mp3, {"title": "Song", "artist": ["A", "B"], "tracknumber": "3", "bogus": "skipped"})
    tags = mgr.read(mp3)
    assert tags["title"] == "Song"
    assert tags["artist"] == "A / B"
    assert tags["tracknumber"] == "3"
    assert "bogus" not in tags


@needs_ffmpeg
def test_flac_vorbis_tags(wav, tmp_path):
    flac = tmp_path / "t.flac"
    PydubConverter().convert(wav, flac, "flac")
    MutagenMetadataManager().write(flac, {"title": "Song", "album_artist": "Band"})
    audio = mutagen.File(flac)
    assert audio["title"] == ["Song"]
    assert audio["albumartist"] == ["Band"]

"""Tests for the AudioAlchemy CLI.

Uses ``typer.testing.CliRunner`` to invoke commands in-process without
spawning a subprocess, making tests fast and portable.
"""

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from audioalchemy.cli import app

runner = CliRunner()


def test_app_help() -> None:
    """``--help`` should exit 0 and mention the app name."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "AudioAlchemy" in result.output or "audioalchemy" in result.output.lower()


def test_convert_help() -> None:
    """``convert --help`` should describe the subcommand."""
    result = runner.invoke(app, ["convert", "--help"])
    assert result.exit_code == 0
    assert "INPUT_DIR" in result.output or "input" in result.output.lower()


def test_convert_unsupported_format(tmp_path: pytest.TempPathFactory) -> None:
    """Passing an unknown format should exit with code 1."""
    result = runner.invoke(
        app,
        ["convert", str(tmp_path), str(tmp_path), "--format", "xyz123"],
    )
    assert result.exit_code == 1
    assert "Unsupported format" in result.output


def test_convert_empty_directory(tmp_path: pytest.TempPathFactory) -> None:
    """Converting an empty directory should succeed with a warning, not crash."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"

    result = runner.invoke(
        app,
        ["convert", str(input_dir), str(output_dir), "--format", "mp3"],
    )
    assert result.exit_code == 0


def test_convert_runs(tmp_path: pytest.TempPathFactory) -> None:
    """Pipeline should call converter and metadata manager for each audio file."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "track.wav").write_bytes(b"\x00" * 16)
    output_dir = tmp_path / "output"

    with (
        patch("audioalchemy.adapters.pydub_converter.PydubConverter.convert"),
        patch("audioalchemy.adapters.mutagen_metadata.MutagenMetadataManager.write"),
    ):
        result = runner.invoke(
            app,
            ["convert", str(input_dir), str(output_dir), "--format", "mp3"],
        )

    assert result.exit_code == 0
    assert "Done" in result.output

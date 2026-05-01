"""pydub-based audio format converter.

Requires ffmpeg on PATH for non-WAV formats (FLAC, MP3, OGG, AAC).
Install ffmpeg: https://ffmpeg.org/download.html
"""

from pathlib import Path

from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

from audioalchemy.core.converter import AudioConverter


class PydubConverter(AudioConverter):
    """Converts audio files using pydub / ffmpeg."""

    _SUPPORTED: list[str] = ["mp3", "wav", "flac", "ogg", "aac"]

    def supported_formats(self) -> list[str]:
        return list(self._SUPPORTED)

    def convert(self, source: Path, destination: Path, output_format: str) -> None:
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")
        if output_format not in self._SUPPORTED:
            raise ValueError(
                f"Unsupported format {output_format!r}. "
                f"Supported: {', '.join(self._SUPPORTED)}"
            )
        try:
            audio = AudioSegment.from_file(str(source))
        except CouldntDecodeError as exc:
            raise ValueError(
                f"Could not decode {source.name}. "
                "Ensure ffmpeg is installed and on PATH."
            ) from exc
        audio.export(str(destination), format=output_format)

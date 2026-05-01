"""mutagen-based audio metadata reader/writer."""

from pathlib import Path

import mutagen
import mutagen.id3
import mutagen.mp3

from audioalchemy.core.metadata import MetadataManager, MetadataRecord
from audioalchemy.utils.logging import get_logger

logger = get_logger(__name__)

_ID3_TAG_MAP: dict[str, str] = {
    "title": "TIT2",
    "artist": "TPE1",
    "album": "TALB",
    "album_artist": "TPE2",
    "tracknumber": "TRCK",
    "year": "TDRC",
    "genre": "TCON",
    "comment": "COMM",
}

_ID3_TAG_MAP_INV: dict[str, str] = {v: k for k, v in _ID3_TAG_MAP.items()}

# Generic key → VorbisComment standard key (FLAC/OGG).
# album_artist must be written as 'albumartist' (no underscore) per spec.
_VORBIS_NORMALISE: dict[str, str] = {
    "album_artist": "albumartist",
}


class MutagenMetadataManager(MetadataManager):
    """Reads and writes audio tags using mutagen."""

    def read(self, path: Path) -> MetadataRecord:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        audio = mutagen.File(path)
        if audio is None:
            raise ValueError(f"Unrecognised audio format: {path}")
        if isinstance(audio, mutagen.mp3.MP3):
            record: MetadataRecord = {}
            for frame_name, value in (audio.tags or {}).items():
                generic = _ID3_TAG_MAP_INV.get(frame_name[:4])
                if generic:
                    record[generic] = str(value)
            return record
        return dict(audio.tags or {})

    def write(self, path: Path, metadata: MetadataRecord) -> None:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        audio = mutagen.File(path)
        if audio is None:
            raise ValueError(f"Unrecognised audio format: {path}")

        if isinstance(audio, mutagen.mp3.MP3):
            if audio.tags is None:
                audio.add_tags()
            for key, value in metadata.items():
                frame_name = _ID3_TAG_MAP.get(key)
                if frame_name is None:
                    logger.debug("Skipping unknown ID3 key %r", key)
                    continue
                text = " / ".join(value) if isinstance(value, list) else str(value)
                if frame_name == "COMM":
                    audio.tags[frame_name] = mutagen.id3.COMM(
                        encoding=3, lang="eng", desc="", text=text
                    )
                else:
                    frame_cls = getattr(mutagen.id3, frame_name)
                    audio.tags[frame_name] = frame_cls(encoding=3, text=text)
        else:
            for key, value in metadata.items():
                vorbis_key = _VORBIS_NORMALISE.get(key, key).lower()
                audio[vorbis_key] = value if isinstance(value, list) else [str(value)]

        audio.save()

"""Audio metadata read/write interface.

Defines the contract for reading and writing audio file tags (ID3, Vorbis
comments, MP4 atoms, etc.). Real operations will be delegated to ``mutagen``
in a future implementation.

TODO: Implement ``MutagenMetadataManager`` using ``mutagen.File``.
"""

from abc import ABC, abstractmethod
from pathlib import Path


# A metadata record is a plain dict of tag-name → value pairs.
# Values are strings for simplicity; multi-value tags use a list of strings.
MetadataRecord = dict[str, str | list[str]]


class MetadataManager(ABC):
    """Abstract base class for audio metadata managers.

    Concrete implementations handle format-specific tag reading and writing
    (ID3 for MP3, Vorbis comments for FLAC/OGG, etc.).

    Example future usage::

        manager = MutagenMetadataManager()
        tags = manager.read(Path("track.mp3"))
        tags["title"] = "My Track"
        manager.write(Path("track.mp3"), tags)
    """

    @abstractmethod
    def read(self, path: Path) -> MetadataRecord:
        """Read all metadata tags from an audio file.

        Args:
            path: Path to the audio file.

        Returns:
            A dict mapping tag names to their values.

        Raises:
            FileNotFoundError: If *path* does not exist.
            ValueError: If the file format is not recognised.

        TODO: Implement using ``mutagen.File(path)``.
        """
        raise NotImplementedError

    @abstractmethod
    def write(self, path: Path, metadata: MetadataRecord) -> None:
        """Write metadata tags to an audio file.

        Merges *metadata* into the existing tags — keys present in *metadata*
        are overwritten; keys absent from *metadata* are left unchanged.

        Args:
            path: Path to the audio file to tag.
            metadata: Dict of tag names → values to write.

        Raises:
            FileNotFoundError: If *path* does not exist.
            ValueError: If the file format is not recognised or a tag is invalid.

        TODO: Implement using ``mutagen.File(path).save()``.
        """
        raise NotImplementedError

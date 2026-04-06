"""Audio conversion interface.

Defines the contract that all concrete converter implementations must satisfy.
Real conversion will be delegated to ``pydub`` in a future implementation.

TODO: Implement ``PydubConverter`` as a concrete subclass using ``pydub.AudioSegment``.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class AudioConverter(ABC):
    """Abstract base class for audio format converters.

    Concrete implementations are responsible for reading a source audio file
    and writing the result to a destination path in the requested format.

    Example future usage::

        converter = PydubConverter()
        converter.convert(Path("input/track.wav"), Path("output/track.mp3"), "mp3")
    """

    @abstractmethod
    def convert(
        self,
        source: Path,
        destination: Path,
        output_format: str,
    ) -> None:
        """Convert a single audio file to the target format.

        Args:
            source: Absolute or relative path to the source audio file.
            destination: Absolute or relative path for the output file.
            output_format: Target format identifier (e.g. ``"mp3"``, ``"wav"``).

        Raises:
            FileNotFoundError: If *source* does not exist.
            ValueError: If *output_format* is not supported.

        TODO: Implement using ``pydub.AudioSegment.from_file`` and
              ``AudioSegment.export``.
        """
        raise NotImplementedError

    @abstractmethod
    def supported_formats(self) -> list[str]:
        """Return the list of output formats this converter supports.

        Returns:
            A list of lowercase format identifiers, e.g. ``["mp3", "wav", "flac"]``.

        TODO: Derive from pydub's supported codec list.
        """
        raise NotImplementedError

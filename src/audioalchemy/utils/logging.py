"""Structured logging setup for AudioAlchemy.

Configures the standard :mod:`logging` library with a ``rich`` handler for
colourised, structured console output. Import :func:`get_logger` in any module
that needs to emit log records.

Usage::

    from audioalchemy.utils.logging import get_logger

    logger = get_logger(__name__)
    logger.info("Hello from %s", __name__)
"""

import logging

from rich.logging import RichHandler

_LOGGING_CONFIGURED = False


def configure_logging(level: str = "INFO") -> None:
    """Configure root logger with a Rich console handler.

    This function is idempotent — calling it multiple times has no effect
    after the first successful call.

    Args:
        level: Logging level string (``"DEBUG"``, ``"INFO"``, etc.).
    """
    global _LOGGING_CONFIGURED  # noqa: PLW0603
    if _LOGGING_CONFIGURED:
        return

    logging.basicConfig(
        level=level.upper(),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                show_path=False,
                markup=True,
            )
        ],
    )
    _LOGGING_CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger.

    Callers should pass ``__name__`` so log records carry the correct module
    path, e.g. ``audioalchemy.services.pipeline``.

    Args:
        name: Logger name, conventionally the module's ``__name__``.

    Returns:
        A :class:`logging.Logger` instance.
    """
    return logging.getLogger(name)

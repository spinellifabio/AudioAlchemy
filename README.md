# AudioAlchemy

A production-ready CLI tool for batch audio conversion and metadata management.

> **Note:** This project is currently in scaffolding phase. Audio processing is not yet implemented.

---

## Features (Planned)

- Batch convert audio files between formats (MP3, WAV, FLAC, OGG, AAC)
- Read and write audio file metadata (ID3 tags, Vorbis comments, etc.)
- Environment-based configuration
- Structured logging with rich output

## Installation

Requires Python 3.11+.

```bash
# Clone the repository
git clone <repo-url>
cd AudioAlchemy

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in editable mode (includes dev dependencies)
pip install -e ".[dev]"

# Copy environment config
cp .env.example .env
```

## Usage

```bash
# Show help
audioalchemy --help

# Convert all audio files in a directory
audioalchemy convert ./input ./output --format mp3
```

## Configuration

Edit `.env` to configure defaults:

| Variable | Default | Description |
|---|---|---|
| `AUDIOALCHEMY_DEFAULT_FORMAT` | `mp3` | Default output format |
| `AUDIOALCHEMY_LOG_LEVEL` | `INFO` | Logging verbosity |

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=audioalchemy
```

## Project Structure

```
src/audioalchemy/
    cli.py          # Typer CLI entrypoint
    core/           # Conversion and metadata interfaces
    config/         # Pydantic-based settings
    services/       # Orchestration pipeline
    utils/          # Filesystem and logging helpers
tests/              # Test suite
```

## License

MIT

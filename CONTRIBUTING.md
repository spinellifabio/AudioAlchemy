# AudioAlchemy

Python 3.11+ CLI for batch audio conversion and metadata tagging (pydub/ffmpeg + mutagen). Pre-alpha
`0.1.0`; `convert` and `init-album` work end to end. Features, usage, limitations: `README.md`.

## Read first
- `README.md` is the source of truth for behavior and limitations. Keep it in line with the code;
  document only what is implemented and verified.
- Some docstrings in `core/` and `services/pipeline.py` still say "TODO / not yet wired" but the
  implementations exist. Trust the code, fix the docstring when touching the file.

## Architecture
- Layers: `cli.py` (Typer, args and output only) → `services/pipeline.py` (`ConversionPipeline`) →
  `core/` abstract interfaces (`AudioConverter`, `MetadataManager`) ← `adapters/` (pydub, mutagen).
- `utils/`: `filesystem` (scan), `filename` (track parser), `album_meta` (`_album.md` loader),
  `logging`. `config/settings.py`: Pydantic settings, env prefix `AUDIOALCHEMY_`.
- No business logic in the CLI. New backends implement the `core/` interfaces.
- Filename convention and `_album.md` format are user-facing contracts: change them together with
  `README.md` and tests.

## Commands
```
python -m venv .venv && .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```
Conversion needs `ffmpeg` on PATH. Tests cover CLI, `_album.md` loader and filename parser only;
adapters and pipeline have none yet.

## Conventions
- Match the surrounding style: type hints, short docstrings, `get_logger(__name__)` for logging.
- Comments minimal, only for the why, in a plain human voice.
- Commits: Conventional Commits; ask before committing.

# AudioAlchemy

A CLI tool for batch audio conversion and metadata management.

---

## Features

- Batch audio file discovery (MP3, WAV, FLAC, OGG, AAC, M4A, WMA, OPUS)
- Album-level metadata via `_album.md` YAML frontmatter
- Per-track metadata extraction from structured filenames
- Pipeline orchestration with metadata merging
- Audio format conversion via pydub / ffmpeg
- Metadata tag writing (ID3 for MP3, VorbisComment for FLAC/OGG)
- `init-album` command to scaffold album metadata templates
- Structured logging with Rich output
- Environment-based configuration via Pydantic settings

---

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

---

## Usage

### Convert audio files

```bash
audioalchemy convert INPUT_DIR OUTPUT_DIR [--format FORMAT] [--recursive]
```

| Argument | Description |
|---|---|
| `INPUT_DIR` | Source directory containing audio files |
| `OUTPUT_DIR` | Destination directory (created if missing) |
| `--format, -f` | Output format: `mp3`, `wav`, `flac`, `ogg`, `aac` (default: `mp3`) |
| `--recursive` | Also convert files in sub-directories (default: off) |
| `--no-recursive` | Explicitly limit to top-level directory only |

```bash
# Convert all audio files in a single directory to FLAC
audioalchemy convert ./input ./output --format flac

# Include sub-directories
audioalchemy convert ./input ./output --format flac --recursive

# Use the default format from .env
audioalchemy convert ./input ./output
```

### Initialize album metadata

```bash
audioalchemy init-album DIRECTORY [--force]
```

Creates a `_album.md` template in the given directory for defining album-level metadata.

| Argument | Description |
|---|---|
| `DIRECTORY` | Target directory where `_album.md` will be created |
| `--force` | Overwrite an existing `_album.md` |

```bash
audioalchemy init-album ./music
audioalchemy init-album ./music --force
```

---

## Album Metadata (`_album.md`)

Place a `_album.md` file in any audio directory to define shared album-level metadata. The pipeline automatically loads it and merges the fields into every track in that directory.

**Format:** YAML frontmatter between `---` delimiters, followed by optional freeform notes (ignored).

```markdown
---
album: "Wind Ensemble Classics"
year: "2024"
album_artist: "Tokyo Wind Ensemble"
genre: "Classical"
comment: "Recorded live at Suntory Hall"
---

# Optional notes
Any freeform text here is ignored by the parser.
```

**Fields:**

| Field | Description |
|---|---|
| `album` | Album title |
| `year` | Release year |
| `album_artist` | Album-level artist (e.g. ensemble or band name) |
| `genre` | Genre |
| `comment` | Free-form comment |

Any extra keys are captured and passed through as additional metadata fields.

Use `audioalchemy init-album <dir>` to generate a blank template.

---

## Filename Convention

The pipeline parses structured filenames to extract per-track metadata automatically.

**Pattern:**
```
{NN} {Title} - {Artist1}, {Artist2}, Arr. {Arranger}
```

- `{NN}` — optional zero-padded track number followed by a space
- `{Title}` — track title (hyphens within the title are preserved)
- ` - ` — segment separator (space-hyphen-space); may be omitted when the only credit is an arranger
- Remaining segments — comma-separated artist/arranger names; `Arr.` prefix is preserved
- A trailing ` (qualifier)` such as ` (bis)` is treated as part of the title, not the arranger name

**Examples:**

| Filename stem | Track # | Title | Artists |
|---|---|---|---|
| `05 Beauty and the Beast - Howard Ashman, Alan Menken - Arr. Toshio Mashima` | 5 | Beauty and the Beast | Howard Ashman, Alan Menken, Arr. Toshio Mashima |
| `08 ABBA GOLD, Arr. Ron Sebregts` | 8 | ABBA GOLD | Arr. Ron Sebregts |
| `11 West Side Story - Leonard Bernstein, Arr. Naohiro Iwai (bis)` | 11 | West Side Story (bis) | Leonard Bernstein, Arr. Naohiro Iwai |
| `Theme - Hans Zimmer` | — | Theme | Hans Zimmer |
| `03 Interlude` | 3 | Interlude | — |

---

## Configuration

Copy `.env.example` to `.env` and edit as needed:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `AUDIOALCHEMY_DEFAULT_FORMAT` | `mp3` | Default output format when `--format` is not specified |
| `AUDIOALCHEMY_LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## Project Structure

```
src/audioalchemy/
    cli.py              # Typer CLI entrypoint (convert, init-album)
    core/
        converter.py    # AudioConverter abstract base class
        metadata.py     # MetadataManager abstract base class
    adapters/
        pydub_converter.py      # PydubConverter — audio conversion via ffmpeg
        mutagen_metadata.py     # MutagenMetadataManager — tag reading/writing
    config/
        settings.py     # Pydantic-based settings loaded from env / .env
    services/
        pipeline.py     # ConversionPipeline orchestration
    utils/
        filesystem.py   # Audio file discovery (scan_directory)
        logging.py      # Rich logging setup
        album_meta.py   # _album.md loader and AlbumMeta dataclass
        filename.py     # Filename parser and TrackInfo dataclass
tests/
    test_cli.py
    test_album_meta.py
    test_filename.py
```

---

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=audioalchemy
```

---

## Requirements

Audio conversion requires **ffmpeg** installed and on PATH.

- Windows: `winget install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html)
- macOS: `brew install ffmpeg`
- Linux: `apt install ffmpeg` / `dnf install ffmpeg`

---

## License

MIT

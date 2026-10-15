# AudioAlchemy

![GitHub Repo stars](https://img.shields.io/github/stars/spinellifabio/AudioAlchemy)
![Last Commit](https://img.shields.io/github/last-commit/spinellifabio/AudioAlchemy)
![Issues](https://img.shields.io/github/issues/spinellifabio/AudioAlchemy)

![Python](https://img.shields.io/badge/language-Python%203.11%2B-3776AB.svg)
![CLI](https://img.shields.io/badge/type-CLI-555.svg)
![ffmpeg](https://img.shields.io/badge/requires-ffmpeg-007808.svg)
![coverage](https://img.shields.io/badge/coverage-77%25-yellow)
![version](https://img.shields.io/github/v/tag/spinellifabio/AudioAlchemy)

A CLI tool for batch audio conversion and metadata management.

---

## Features

- Batch audio file discovery (input: MP3, WAV, FLAC, OGG, AAC, M4A, WMA, OPUS)
- Album-level metadata via `_album.md` YAML frontmatter
- Per-track metadata extraction from structured filenames
- Pipeline orchestration with metadata merging
- Audio format conversion via pydub / ffmpeg (output: MP3, WAV, FLAC, OGG, AAC)
- Metadata tag writing: ID3 for MP3, Vorbis-style tags for other formats (see [Limitations](#limitations))
- `init-album` command to scaffold album metadata templates
- Structured logging with Rich output
- Environment-based configuration via Pydantic settings

**Status:** pre-alpha (`0.1.0`). Both CLI commands are implemented end to end.

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

Place a `_album.md` file in the **root of `INPUT_DIR`** to define shared album-level metadata. The pipeline loads it once per run and merges the fields into every converted track (including tracks in sub-directories when `--recursive` is used). `_album.md` files inside sub-directories are not read.

**Format:** YAML frontmatter between `---` delimiters, followed by optional freeform notes (ignored).

```markdown
---
album: "Wind Ensemble Classics"
date: "2026-04-11"
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
| `date` | Recording/release date — any ISO format accepted (`2026`, `2026-04`, `2026-04-11`) |
| `album_artist` | Album-level artist (e.g. ensemble or band name) |
| `genre` | Genre |
| `comment` | Free-form comment |

`year` is accepted as a legacy alias for `date` (used only when `date` is absent).

Any extra keys are captured and passed to the tag writer. For MP3 output only the standard fields above (plus title, artist and track number from the filename) are written; unknown keys are skipped. For other formats they are written as tags with the lower-cased key name.

Track-level values from the filename (`title`, `artist`, `tracknumber`) override album-level values. Multiple artists are joined with ` / ` in ID3 tags and stored as multiple values in Vorbis-style tags.

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

Current tests cover the CLI (`test_cli.py`), the `_album.md` loader (`test_album_meta.py`) and the filename parser (`test_filename.py`). There are no dedicated tests for `PydubConverter`, `MutagenMetadataManager` or `ConversionPipeline`.

---

## Limitations

- Tag writing is implemented for MP3 (ID3) and generic Vorbis-style tags. Tagging of WAV and AAC output is not specifically handled or tested.
- Input files in M4A, WMA and OPUS are discovered and decoded through ffmpeg, but they cannot be chosen as output formats.
- The pipeline has no per-file error handling: an unreadable or undecodable file raises and aborts the run.
- Conversion settings such as bitrate or sample rate are not configurable; pydub/ffmpeg defaults are used.
- Only `AUDIOALCHEMY_DEFAULT_FORMAT` and `AUDIOALCHEMY_LOG_LEVEL` are configurable.

---

## Requirements

Audio conversion requires **ffmpeg** installed and on PATH.

- Windows: `winget install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html)
- macOS: `brew install ffmpeg`
- Linux: `apt install ffmpeg` / `dnf install ffmpeg`

---

## Credits

```text
  ______                   __  __             ______   __            __
 ╱      ╲                 ╱  │╱  │           ╱      ╲ ╱  │          ╱  │
╱$$$$$$  │ __    __   ____$$ │$$╱   ______  ╱$$$$$$  │$$ │  _______ $$ │____    ______   _____  ____   __    __
$$ │__$$ │╱  │  ╱  │ ╱    $$ │╱  │ ╱      ╲ $$ │__$$ │$$ │ ╱       │$$      ╲  ╱      ╲ ╱     ╲╱    ╲ ╱  │  ╱  │
$$    $$ │$$ │  $$ │╱$$$$$$$ │$$ │╱$$$$$$  │$$    $$ │$$ │╱$$$$$$$╱ $$$$$$$  │╱$$$$$$  │$$$$$$ $$$$  │$$ │  $$ │
$$$$$$$$ │$$ │  $$ │$$ │  $$ │$$ │$$ │  $$ │$$$$$$$$ │$$ │$$ │      $$ │  $$ │$$    $$ │$$ │ $$ │ $$ │$$ │  $$ │
$$ │  $$ │$$ ╲__$$ │$$ ╲__$$ │$$ │$$ ╲__$$ │$$ │  $$ │$$ │$$ ╲_____ $$ │  $$ │$$$$$$$$╱ $$ │ $$ │ $$ │$$ ╲__$$ │
$$ │  $$ │$$    $$╱ $$    $$ │$$ │$$    $$╱ $$ │  $$ │$$ │$$       │$$ │  $$ │$$       │$$ │ $$ │ $$ │$$    $$ │
$$╱   $$╱  $$$$$$╱   $$$$$$$╱ $$╱  $$$$$$╱  $$╱   $$╱ $$╱  $$$$$$$╱ $$╱   $$╱  $$$$$$$╱ $$╱  $$╱  $$╱  $$$$$$$ │
                                                                                                      ╱  ╲__$$ │
                                                                                                      $$    $$╱
                                                                                                       $$$$$$╱

                                                                  v1.0.0 - Code assembled in spare time by Fabio
```

# Contributing to AudioAlchemy

Thanks for helping out. Bug reports and pull requests are welcome.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Conversion needs [ffmpeg](https://ffmpeg.org/) on PATH.

## Checks

```bash
ruff check src tests
pytest
```

CI runs both on Python 3.11, 3.12 and 3.13.

## Code layout

`cli.py` (Typer, args and output only) calls `services/pipeline.py`, which uses the abstract
interfaces in `core/` implemented by `adapters/` (pydub, mutagen). Keep business logic out of the CLI;
new backends implement the `core/` interfaces. See the Project Structure section of `README.md`.

The filename convention and the `_album.md` format are user-facing contracts: change them together
with `README.md` and tests.

## Workflow

- Git Flow: branch from `develop` as `feature/<name>`, open the PR against `develop`.
  Hotfixes branch from `main`.
- Commits follow [Conventional Commits](https://www.conventionalcommits.org) (`feat`, `fix`,
  `refactor`, `docs`, `perf`, `chore`). Subjects feed the changelog.
- The changelog is generated with [git-cliff](https://git-cliff.org) from `cliff.toml`:
  `git cliff -o CHANGELOG.md`. Commits scoped `changelog` are excluded.
- Update `README.md` when behavior changes, and document only what is implemented and verified.

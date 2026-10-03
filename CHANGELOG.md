# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Nothing yet.

## [1.0.0] - 2026-10-03

First public release.

### Packaging

- Published to PyPI as **`dataclean-csv`** — `pip install dataclean-csv`.
  The distribution name is `dataclean-csv` (the plain name `dataclean` was already
  taken on PyPI by an unrelated project); the import package and the console
  command remain `dataclean`.
- Added PEP 621 `pyproject.toml` metadata (setuptools backend), a `MANIFEST.in`,
  and a `dataclean` console-script entry point.
- Both an sdist and a pure-Python wheel are built and published.

### Added

- `dataclean clean` — reads a CSV, normalizes it, and writes a cleaned CSV plus a JSON
  data-quality report.
- `dataclean profile` — reports per-column type, missing count, and unique count without
  modifying the input. `--json` emits a single JSON object instead of a table.
- **Header normalization** — lowercased, stripped, non-alphanumeric runs collapsed to `_`,
  edge underscores removed (`E-Mail` → `e_mail`, ` First Name ` → `first_name`). Collisions
  get `_2`, `_3`, … suffixes.
- **Missing-value detection** — empty cells and case-insensitive `na`, `n/a`, `null`, `none`,
  `-`, `?` are all treated as missing.
- **Duplicate removal** — runs after normalization, keeps the first occurrence, and runs
  *before* filling so `--fill` cannot mask a duplicate.
- **Type inference** — per column, in order: `integer` → `float` → `boolean` → `date` →
  `string`; an all-missing column is `empty`.
- **Flags** — `--out`, `--report`, `--fill COL=VAL` (repeatable), `--keep-duplicates`,
  `--strict`, `--version`.
- **Exit codes** — `0` success, `1` data/I-O error, `2` usage error, `3` strict-mode warnings
  after successful writes. Safe to use as a CI data-quality gate.
- **Deterministic output** — identical input, flags, and input path produce byte-identical
  output.
- **Zero dependencies** — standard library only, Python 3.11+.
- 16 unit tests covering the cleaner and the CLI.

### Known limitations

- All rows are held in memory; there is no streaming. Not suitable for multi-GB files.
- Standard comma-separated RFC4180 dialect only — no delimiter or encoding auto-detection.
- Writes are not transactional; an I/O failure mid-write can leave a truncated CSV.
- Existing output files are overwritten without confirmation.
- No formula sanitization — untrusted values may execute as formulas in a spreadsheet.

[Unreleased]: https://github.com/omniforgelabs-dev/csv-cleaner/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/omniforgelabs-dev/csv-cleaner/releases/tag/v1.0.0

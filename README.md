# csv-cleaner (`dataclean`)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests: 16 passing](https://img.shields.io/badge/tests-16%20passing-brightgreen.svg)](#tests)
[![Dependencies: none](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](#install)
[![PyPI](https://img.shields.io/badge/pypi-dataclean--csv-blue.svg)](https://pypi.org/project/dataclean-csv/)

**A dependency-free Python CLI that turns a messy CSV into a clean CSV plus a machine-readable JSON data-quality report.**

No dependencies, no network, no credentials, no config files. Standard library only, Python 3.11+.

```sh
pip install dataclean-csv
dataclean clean messy.csv --out clean.csv --report report.json
# clean: 5 rows in, 4 rows out, 1 duplicate(s) removed, 4 missing value(s), 0 filled
```

**What it fixes:** inconsistent header casing, stray whitespace, `N/A` / `null` / `-` standing in for blanks, duplicated rows — and it tells you exactly how many values were missing, per column, in JSON you can log or diff.

---

## Why

Spreadsheet exports are messy: inconsistent header casing, stray whitespace, `N/A` and `-` standing in for blanks, duplicated rows, and no idea how many values are missing. `dataclean` fixes that in one command and hands you a JSON report you can diff, log, or feed into a pipeline.

## Install

### From PyPI (recommended)

```sh
pip install dataclean-csv
dataclean --version
```

The distribution is named `dataclean-csv`; the import package and the console command are both `dataclean`.

### From source (zero install)

Nothing to install. Clone the repo and run it from the repository root:

```sh
git clone https://github.com/omniforgelabs-dev/csv-cleaner.git
cd csv-cleaner
python3 --version   # must be 3.11 or newer
```

Optionally install the `dataclean` console script from the checkout:

```sh
pip install -e .
dataclean --version
```

The zero-setup invocation `python -m dataclean` works without any install step.

## Usage

### Clean a CSV

```sh
python -m dataclean clean fixtures/sample.csv --out out/clean.csv --report out/report.json
```

Real output:

```text
clean: 5 rows in, 4 rows out, 1 duplicate(s) removed, 4 missing value(s), 0 filled
```

`out/clean.csv` (headers normalized, duplicate row dropped):

```csv
id,first_name,e_mail,age,notes
1,Alice,alice@example.com,30,ok
2,Bob,bob@example.com,,
3,Carol,carol@example.com,25,
4,Dave,dave@example.com,40,
```

`out/report.json` (excerpt):

```json
{
  "input_file": "fixtures/sample.csv",
  "input_rows": 5,
  "output_rows": 4,
  "duplicates_removed": 1,
  "missing_values": 4,
  "filled_cells": 0,
  "columns": [
    { "name": "id",         "inferred_type": "integer", "missing": 0, "unique": 4 },
    { "name": "first_name", "inferred_type": "string",  "missing": 0, "unique": 4 },
    { "name": "e_mail",     "inferred_type": "string",  "missing": 0, "unique": 4 },
    { "name": "age",        "inferred_type": "integer", "missing": 1, "unique": 3 },
    { "name": "notes",      "inferred_type": "string",  "missing": 3, "unique": 1 }
  ]
}
```

### Fill missing values

```sh
python -m dataclean clean fixtures/sample.csv --out out/filled.csv --report out/filled.json --fill notes=unknown
```

```text
clean: 5 rows in, 4 rows out, 1 duplicate(s) removed, 1 missing value(s), 3 filled
```

### Profile a CSV without modifying it

```sh
python -m dataclean profile fixtures/sample.csv
```

```text
id      integer 0       4
first_name      string  0       4
e_mail  string  0       4
age     integer 2       3
notes   string  4       1
```

Add `--json` for a single JSON object instead.

### Other flags

| Flag | Effect |
| --- | --- |
| `--keep-duplicates` | Keep every normalized row instead of dropping repeats |
| `--fill COL=VAL` | Replace empty cells in `COL` with the literal `VAL` (repeatable) |
| `--strict` | Write both files, then exit `3` if duplicates were removed or missing values remain |
| `--version` | Print `dataclean 1.0.0` and exit |
| `-h`, `--help` | Argparse help (option abbreviations are disabled) |

## Exit codes

| Exit | Meaning |
| --- | --- |
| `0` | Success |
| `1` | Data or I/O error (missing/empty input, ragged row, unknown `--fill` column) |
| `2` | Argument usage error |
| `3` | Strict-mode warnings after successful writes |

Exit codes make the tool safe to use in shell pipelines and CI:

```sh
python -m dataclean clean data.csv --out clean.csv --report report.json --strict || echo "data quality gate failed"
```

## What it does to your data

- **Headers** are lowercased, stripped, non-alphanumeric runs collapsed to `_`, and edge underscores removed (`E-Mail` → `e_mail`, ` First Name ` → `first_name`). Collisions get `_2`, `_3`, … suffixes.
- **Cells** are stripped. Empty cells and case-insensitive `na`, `n/a`, `null`, `none`, `-`, `?` all become missing.
- **Duplicates** are removed after normalization, keeping the first occurrence. Deduplication runs *before* filling.
- **Types** are inferred per column in order: `integer` → `float` → `boolean` → `date` → `string`; an all-missing column is `empty`.
- **Deterministic**: identical input, flags and input path produce byte-identical output.

## Tests

```sh
python -m unittest discover -s tests -t . -v
```

```text
Ran 16 tests in 0.025s

OK
```

## Limitations

- **Not for huge files.** All rows are held in memory; there is no streaming. Fine for typical spreadsheet exports, not for multi-GB dumps.
- **Standard CSV dialect only.** Comma-separated, RFC4180 quoting, strict parsing. No delimiter auto-detection, no exotic quoting, no schema configuration.
- **Writes are not transactional.** An I/O failure mid-write can leave a truncated CSV and a partial report. Existing output files are overwritten without confirmation — back them up.
- **No spreadsheet UI.** This is a CLI for scripts and pipelines, not a replacement for Excel/Google Sheets or a visual data-cleaning tool.
- **No formula sanitization.** Untrusted values may execute as formulas when opened in a spreadsheet application.
- **Portability caveat.** Application code is portable, but the acceptance commands use POSIX shell utilities and need adaptation for native Windows shells.
- **Not hardened for sensitive data.** Cleaned CSVs and reports can expose sensitive values; filesystem permissions are inherited, not tightened.

## License

MIT — see `LICENSE`.

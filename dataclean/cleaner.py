"""Normalization, stable deduplication, literal filling and CSV output."""
import csv
from pathlib import Path
import re

MISSING = {"", "na", "n/a", "null", "none", "-", "?"}


def normalize_headers(header):
    names, used = [], set()
    for cell in header:
        base = re.sub(r"[^a-z0-9]+", "_", cell.lower().strip()).strip("_")
        base = base or "column"
        name, suffix = base, 2
        while name in used:
            name = f"{base}_{suffix}"
            suffix += 1
        used.add(name)
        names.append(name)
    return names


def normalize_rows(rows):
    result = []
    for row in rows:
        cells = [cell.strip() for cell in row]
        result.append(["" if cell.lower() in MISSING else cell for cell in cells])
    return result


def deduplicate(rows):
    seen, result = set(), []
    for row in rows:
        key = tuple(row)
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result, len(rows) - len(result)


def fill_rows(header, rows, fills):
    indices = {}
    for name, value in fills:
        if name not in header:
            raise ValueError(f"unknown column in --fill: {name}")
        indices[header.index(name)] = value
    result, filled = [], 0
    for row in rows:
        row = row.copy()
        for index, value in indices.items():
            if row[index] == "":
                row[index] = value
                filled += 1
        result.append(row)
    return result, filled


def write_csv(path, header, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        # Include CR in quoting decisions, then emit LF record terminators.
        class LFWriter:
            def write(self, text):
                return stream.write(text[:-2] + "\n")
        writer = csv.writer(LFWriter(), lineterminator="\r\n")
        writer.writerow(header)
        writer.writerows(rows)

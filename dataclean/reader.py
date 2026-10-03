"""Read and validate the entire input before any outputs are opened."""
import csv
from pathlib import Path


def read_csv(path):
    try:
        stream = Path(path).open("r", encoding="utf-8-sig", newline="")
    except FileNotFoundError:
        raise ValueError(f"input file not found: {path}") from None
    with stream:
        reader = csv.reader(stream, strict=True)
        try:
            header = next(reader, None)
            if header is None:
                raise ValueError(f"input file is empty: {path}")
            if not header:
                raise ValueError("header has no fields")
            rows = []
            while True:
                line = reader.line_num + 1
                row = next(reader, None)
                if row is None:
                    break
                if len(row) != len(header):
                    raise ValueError(
                        f"line {line} has {len(row)} field(s), expected {len(header)}"
                    )
                rows.append(row)
        except csv.Error as error:
            raise ValueError(
                f"invalid CSV at line {reader.line_num}: {error}"
            ) from None
    return header, rows

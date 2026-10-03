"""Deterministic type inference and report construction."""
from datetime import date
import re


def parses(value, converter):
    try:
        converter(value)
        return True
    except (ValueError, OverflowError):
        return False


def infer_type(values):
    values = [value for value in values if value != ""]
    if not values:
        return "empty"
    if all(parses(value, int) for value in values):
        return "integer"
    if all(parses(value, float) for value in values):
        return "float"
    if all(value.lower() in {"true", "false", "yes", "no"} for value in values):
        return "boolean"
    if all(re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value)
           and parses(value, date.fromisoformat) for value in values):
        return "date"
    return "string"


def profile_columns(header, rows):
    columns = []
    for index, name in enumerate(header):
        values = [row[index] for row in rows]
        columns.append({
            "name": name,
            "inferred_type": infer_type(values),
            "missing": values.count(""),
            "unique": len({value for value in values if value != ""}),
        })
    return columns


def build_report(input_file, input_rows, header, rows, removed, filled):
    columns = profile_columns(header, rows)
    return {
        "input_file": input_file,
        "input_rows": input_rows,
        "output_rows": len(rows),
        "duplicates_removed": removed,
        "missing_values": sum(column["missing"] for column in columns),
        "filled_cells": filled,
        "columns": columns,
    }

"""Command-line interface. main returns the documented process exit code."""
import argparse
import json
from pathlib import Path
import sys

from . import __version__
from .cleaner import deduplicate, fill_rows, normalize_headers, normalize_rows, write_csv
from .profiler import build_report, profile_columns
from .reader import read_csv


def fill_argument(text):
    if "=" not in text:
        raise argparse.ArgumentTypeError("--fill must be COL=VAL")
    return tuple(text.split("=", 1))


def parser():
    root = argparse.ArgumentParser(prog="dataclean")
    root.add_argument("--version", action="version", version=f"dataclean {__version__}")
    commands = root.add_subparsers(dest="command", required=True)
    clean = commands.add_parser("clean", allow_abbrev=False)
    clean.add_argument("input")
    clean.add_argument("--out", required=True)
    clean.add_argument("--report", required=True)
    clean.add_argument("--keep-duplicates", action="store_true")
    clean.add_argument("--fill", type=fill_argument, action="append", default=[])
    clean.add_argument("--strict", action="store_true")
    profile = commands.add_parser("profile", allow_abbrev=False)
    profile.add_argument("input")
    profile.add_argument("--json", action="store_true")
    root.allow_abbrev = False
    return root


def same_path(first, second):
    first, second = Path(first), Path(second)
    return (first.resolve() == second.resolve()
            or (first.exists() and second.exists() and first.samefile(second)))


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        header, rows = read_csv(args.input)
        header = normalize_headers(header)
        rows = normalize_rows(rows)
        if args.command == "profile":
            columns = profile_columns(header, rows)
            if args.json:
                print(json.dumps({"input_file": args.input, "rows": len(rows),
                                  "columns": columns}))
            else:
                for column in columns:
                    print("\t".join(str(column[key]) for key in
                                    ("name", "inferred_type", "missing", "unique")))
            return 0
        input_rows = len(rows)
        removed = 0
        if not args.keep_duplicates:
            rows, removed = deduplicate(rows)
        rows, filled = fill_rows(header, rows, args.fill)
        if same_path(args.out, args.report):
            raise ValueError("--out and --report must refer to different files")
        if same_path(args.input, args.out) or same_path(args.input, args.report):
            raise ValueError("output paths must not refer to the input file")
        report = build_report(args.input, input_rows, header, rows, removed, filled)
        write_csv(args.out, header, rows)
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(report, indent=2) + "\n")
        missing = report["missing_values"]
        print(f"clean: {input_rows} rows in, {len(rows)} rows out, "
              f"{removed} duplicate(s) removed, {missing} missing value(s), {filled} filled")
        if args.strict and (removed or missing):
            print(f"dataclean: strict: {removed} duplicate(s) removed, "
                  f"{missing} missing value(s) remaining", file=sys.stderr)
            return 3
        return 0
    except (OSError, UnicodeError, ValueError) as error:
        print(f"dataclean: error: {error}", file=sys.stderr)
        return 1

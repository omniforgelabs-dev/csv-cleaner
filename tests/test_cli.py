import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from dataclean.cli import main
from dataclean.reader import read_csv


class CLITests(unittest.TestCase):
    def setUp(self):
        self.root = Path("out/unit") / self._testMethodName
        self.root.mkdir(parents=True, exist_ok=True)
        self.output = self.root / "clean.csv"
        self.report = self.root / "report.json"
        for path in (self.output, self.report):
            if path.exists():
                path.unlink()

    def invoke(self, args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch("sys.stdout", stdout), patch("sys.stderr", stderr):
            try:
                code = main(args)
            except SystemExit as error:
                code = error.code
        return code, stdout.getvalue(), stderr.getvalue()

    def clean(self, source="fixtures/sample.csv", extra=()):
        return self.invoke(["clean", source, "--out", str(self.output),
                            "--report", str(self.report), *extra])

    def source(self, content):
        path = self.root / "input.csv"
        path.write_bytes(content)
        return str(path)

    def test_usage(self):
        self.assertEqual(self.invoke(["--version"]), (0, "dataclean 1.0.0\n", ""))
        for args in (["clean", "fixtures/sample.csv"],
                     ["profile", "fixtures/sample.csv", "--unknown"]):
            code, stdout, stderr = self.invoke(args)
            self.assertEqual((code, stdout), (2, ""))
            self.assertTrue(stderr.startswith("usage: dataclean"))
        self.assertEqual(self.clean(extra=["--fill", "NOTES"])[0], 2)

    def test_input_errors(self):
        cases = [("fixtures/nope.csv", "input file not found: fixtures/nope.csv"),
                 ("fixtures/bad.csv", "line 3 has 1 field(s), expected 2"),
                 (self.source(b""), f"input file is empty: {self.root / 'input.csv'}")]
        for source, message in cases:
            self.assertEqual(self.clean(source), (1, "", f"dataclean: error: {message}\n"))
            self.assertFalse(self.output.exists())
            self.assertFalse(self.report.exists())

    def test_clean_exact_and_deterministic(self):
        self.assertEqual(self.clean(), (0, "clean: 5 rows in, 4 rows out, 1 duplicate(s) removed, 4 missing value(s), 0 filled\n", ""))
        expected = ("id,first_name,e_mail,age,notes\n"
                    "1,Alice,alice@example.com,30,ok\n"
                    "2,Bob,bob@example.com,,\n"
                    "3,Carol,carol@example.com,25,\n"
                    "4,Dave,dave@example.com,40,\n")
        self.assertEqual(self.output.read_bytes(), expected.encode())
        data = json.loads(self.report.read_text())
        columns = [("id", "integer", 0, 4), ("first_name", "string", 0, 4),
                   ("e_mail", "string", 0, 4), ("age", "integer", 1, 3),
                   ("notes", "string", 3, 1)]
        self.assertEqual(data, {
            "input_file": "fixtures/sample.csv", "input_rows": 5, "output_rows": 4,
            "duplicates_removed": 1, "missing_values": 4, "filled_cells": 0,
            "columns": [dict(zip(("name", "inferred_type", "missing", "unique"), c))
                        for c in columns],
        })
        before = (self.output.read_bytes(), self.report.read_bytes())
        self.assertEqual(self.clean()[0], 0)
        self.assertEqual(before, (self.output.read_bytes(), self.report.read_bytes()))

    def test_fill_and_unknown(self):
        self.assertEqual(self.clean(extra=["--fill", "missing=x"]),
                         (1, "", "dataclean: error: unknown column in --fill: missing\n"))
        self.assertFalse(self.output.exists())
        self.assertFalse(self.report.exists())
        self.assertEqual(self.clean(extra=["--fill", "notes=unknown"])[0], 0)
        data = json.loads(self.report.read_text())
        self.assertEqual((data["filled_cells"], data["missing_values"]), (3, 1))

    def test_keep(self):
        self.assertEqual(self.clean(extra=["--keep-duplicates"])[0], 0)
        data = json.loads(self.report.read_text())
        self.assertEqual((data["output_rows"], data["duplicates_removed"], data["missing_values"]),
                         (5, 0, 6))

    def test_strict(self):
        code, stdout, stderr = self.clean(extra=["--strict"])
        self.assertEqual(code, 3)
        self.assertEqual(stderr, "dataclean: strict: 1 duplicate(s) removed, 4 missing value(s) remaining\n")
        self.assertTrue(self.output.exists() and self.report.exists())
        self.assertEqual(self.clean(self.source(b"a\n1\n"), ["--strict"]),
                         (0, "clean: 1 rows in, 1 rows out, 0 duplicate(s) removed, 0 missing value(s), 0 filled\n", ""))

    def test_profile(self):
        before = sorted(str(p) for p in Path(".").rglob("*"))
        code, stdout, stderr = self.invoke(["profile", "fixtures/sample.csv", "--json"])
        self.assertEqual((code, stderr), (0, ""))
        data = json.loads(stdout)
        self.assertEqual(set(data), {"input_file", "rows", "columns"})
        self.assertEqual(data["rows"], 5)
        self.assertEqual([c["missing"] for c in data["columns"]], [0, 0, 0, 2, 4])
        self.assertEqual(self.invoke(["profile", "fixtures/sample.csv"]),
                         (0, "id\tinteger\t0\t4\nfirst_name\tstring\t0\t4\ne_mail\tstring\t0\t4\nage\tinteger\t2\t3\nnotes\tstring\t4\t1\n", ""))
        self.assertEqual(before, sorted(str(p) for p in Path(".").rglob("*")))

    def test_header_only(self):
        self.assertEqual(self.clean(self.source(b" A ,A,\n"))[0], 0)
        data = json.loads(self.report.read_text())
        self.assertEqual(data["output_rows"], 0)
        self.assertEqual([c["name"] for c in data["columns"]], ["a", "a_2", "column"])
        self.assertTrue(all(c["inferred_type"] == "empty" for c in data["columns"]))

    def test_csv_edges(self):
        source = self.source(b'\xef\xbb\xbfa,b\n1,"x\ny\rz"\n')
        self.assertEqual(self.clean(source)[0], 0)
        self.assertEqual(read_csv(source), read_csv(self.output))
        self.assertEqual(self.output.read_bytes(), b'a,b\n1,"x\ny\rz"\n')
        self.assertEqual(self.clean(self.source(b'a,b\n1,"unfinished\n'))[0], 1)
        self.assertEqual(self.clean(self.source(b'a,b\n1,"x\ny"\n3\n')),
                         (1, "", "dataclean: error: line 4 has 1 field(s), expected 2\n"))
        self.assertEqual(self.clean(self.source(b'a\n\xff\n'))[0], 1)

    def test_path_errors(self):
        self.assertEqual(self.invoke(["clean", "fixtures/sample.csv", "--out", str(self.output),
                                      "--report", str(self.output)])[0], 1)
        source = self.source(b"a\n1\n")
        self.assertEqual(self.invoke(["clean", source, "--out", source,
                                      "--report", str(self.report)])[0], 1)
        blocked = self.root / "blocked"
        blocked.write_text("not a directory")
        self.assertEqual(self.invoke(["clean", source, "--out", str(blocked / "x.csv"),
                                      "--report", str(self.report)])[0], 1)

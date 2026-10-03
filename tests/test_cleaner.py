import unittest

from dataclean.cleaner import deduplicate, fill_rows, normalize_headers, normalize_rows
from dataclean.profiler import infer_type, profile_columns


class CleanerTests(unittest.TestCase):
    def test_headers(self):
        self.assertEqual(normalize_headers(["ID", " First Name ", "E-Mail"]),
                         ["id", "first_name", "e_mail"])
        self.assertEqual(normalize_headers(["A", "A", "A_2", "", "?"]),
                         ["a", "a_2", "a_2_2", "column", "column_2"])

    def test_cells(self):
        self.assertEqual(normalize_rows([[" NA ", "n/A", "NULL", "None", "-", "?", " ", " x "]]),
                         [["", "", "", "", "", "", "", "x"]])

    def test_deduplication(self):
        self.assertEqual(deduplicate([["2"], ["1"], ["2"]]), ([["2"], ["1"]], 1))

    def test_fill(self):
        self.assertEqual(fill_rows(["a"], [[""], ["x"]], [("a", "old"), ("a", " NA ")]),
                         ([[" NA "], ["x"]], 1))
        self.assertEqual(fill_rows(["a"], [["x"]], [("a", "y")]), ([["x"]], 0))
        self.assertEqual(fill_rows(["a"], [[""]], [("a", "")]), ([[""]], 1))
        with self.assertRaisesRegex(ValueError, "unknown column in --fill: b"):
            fill_rows(["a"], [], [("b", "x")])

    def test_inference(self):
        for values, expected in [(["", "-2", "+3"], "integer"),
                                 (["2", "1.5"], "float"),
                                 (["YES", "false"], "boolean"),
                                 (["2024-02-29"], "date"),
                                 (["2023-02-29"], "string"),
                                 (["2024-2-01"], "string"),
                                 (["x", "2"], "string"), ([""], "empty")]:
            with self.subTest(values=values):
                self.assertEqual(infer_type(values), expected)

    def test_profile(self):
        self.assertEqual(profile_columns(["a"], [[""], ["1"], ["1"]]),
                         [{"name": "a", "inferred_type": "integer", "missing": 1, "unique": 1}])

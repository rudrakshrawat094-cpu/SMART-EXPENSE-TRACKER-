import tempfile
import unittest
from pathlib import Path

import _bootstrap  # noqa: F401
from base import DBTestCase
from expense_tracker.exceptions import ValidationError
from expense_tracker.exporter import export_csv, import_csv
from expense_tracker.expenses import ExpenseService


class ExporterTests(DBTestCase):
    def setUp(self):
        super().setUp()
        self.svc = ExpenseService(self.db)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_round_trip(self):
        self.svc.add(self.user.id, 55.5, "Food", "lunch, with comma", "2024-01-01")
        path = Path(self.tmp.name) / "out.csv"
        self.assertEqual(export_csv(self.svc.list(self.user.id), path), 1)
        other = ExpenseService(self.db)
        n, errors = import_csv(other, self.user.id, path)
        self.assertEqual((n, errors), (1, []))
        self.assertEqual(len(self.svc.list(self.user.id)), 2)

    def test_import_skips_bad_rows(self):
        path = Path(self.tmp.name) / "in.csv"
        path.write_text("date,amount,category,description\n"
                        "2024-01-01,10,Food,ok\n"
                        "2024-01-02,abc,Food,bad amount\n"
                        "2024-01-03,10,Nope,bad category\n", encoding="utf-8")
        n, errors = import_csv(self.svc, self.user.id, path)
        self.assertEqual(n, 1)
        self.assertEqual(len(errors), 2)

    def test_missing_file_and_bad_header(self):
        with self.assertRaises(ValidationError):
            import_csv(self.svc, self.user.id, Path(self.tmp.name) / "nope.csv")
        bad = Path(self.tmp.name) / "bad.csv"
        bad.write_text("foo,bar\n1,2\n", encoding="utf-8")
        with self.assertRaises(ValidationError):
            import_csv(self.svc, self.user.id, bad)


if __name__ == "__main__":
    unittest.main()

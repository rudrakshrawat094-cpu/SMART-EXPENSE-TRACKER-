import unittest

import _bootstrap  # noqa: F401
from expense_tracker import validators as v
from expense_tracker.exceptions import ValidationError


class ValidatorTests(unittest.TestCase):
    def test_amount_valid(self):
        self.assertEqual(v.validate_amount("1,250.456"), 1250.46)

    def test_amount_invalid(self):
        for bad in ["abc", "-5", "0", "nan", "inf", "99999999999", None]:
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                v.validate_amount(bad)

    def test_date(self):
        self.assertEqual(v.validate_date("2024-02-29"), "2024-02-29")
        for bad in ["2023-02-29", "12-01-2024", "2999-01-01", ""]:
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                v.validate_date(bad)

    def test_month(self):
        self.assertEqual(v.validate_month("2024-03"), "2024-03")
        with self.assertRaises(ValidationError):
            v.validate_month("2024-13")

    def test_category_normalised(self):
        self.assertEqual(v.validate_category("  food "), "Food")
        with self.assertRaises(ValidationError):
            v.validate_category("gambling")

    def test_username_and_password(self):
        self.assertEqual(v.validate_username(" bob_1 "), "bob_1")
        for bad in ["ab", "has space", "x" * 21, "a;drop"]:
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                v.validate_username(bad)
        for bad in ["abc1", "allletters", "12345678"]:
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                v.validate_password(bad)

    def test_description_length(self):
        with self.assertRaises(ValidationError):
            v.validate_description("x" * 101)


if __name__ == "__main__":
    unittest.main()

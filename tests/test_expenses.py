import unittest

import _bootstrap  # noqa: F401
from base import DBTestCase
from expense_tracker.auth import AuthService
from expense_tracker.exceptions import NotFoundError, ValidationError
from expense_tracker.expenses import ExpenseService


class ExpenseTests(DBTestCase):
    def setUp(self):
        super().setUp()
        self.svc = ExpenseService(self.db)
        self.uid = self.user.id

    def test_add_and_get(self):
        e = self.svc.add(self.uid, "120.5", "food", "lunch", "2024-01-10")
        self.assertEqual(self.svc.get(self.uid, e.id).amount, 120.5)

    def test_list_filters_and_sorting(self):
        self.svc.add(self.uid, 100, "Food", "pizza", "2024-01-05")
        self.svc.add(self.uid, 300, "Rent", "room", "2024-01-01")
        self.svc.add(self.uid, 50, "Food", "tea", "2024-02-02")
        self.assertEqual(len(self.svc.list(self.uid, category="Food")), 2)
        self.assertEqual(len(self.svc.list(self.uid, month="2024-01")), 2)
        self.assertEqual(len(self.svc.list(self.uid, keyword="pizz")), 1)
        amounts = [e.amount for e in self.svc.list(self.uid, sort_by="amount", descending=False)]
        self.assertEqual(amounts, sorted(amounts))

    def test_invalid_sort_field(self):
        with self.assertRaises(ValidationError):
            self.svc.list(self.uid, sort_by="id; DROP TABLE expenses")

    def test_update(self):
        e = self.svc.add(self.uid, 10, "Food", "x", "2024-01-01")
        updated = self.svc.update(self.uid, e.id, amount="99", category="health")
        self.assertEqual((updated.amount, updated.category), (99.0, "Health"))
        with self.assertRaises(ValidationError):
            self.svc.update(self.uid, e.id, created_at="2000-01-01")
        with self.assertRaises(ValidationError):
            self.svc.update(self.uid, e.id, amount="-1")

    def test_delete(self):
        e = self.svc.add(self.uid, 10, "Food")
        self.svc.delete(self.uid, e.id)
        with self.assertRaises(NotFoundError):
            self.svc.get(self.uid, e.id)

    def test_users_cannot_touch_each_others_data(self):
        e = self.svc.add(self.uid, 10, "Food")
        other = AuthService(self.db).register("mallory", "hacker123")
        with self.assertRaises(NotFoundError):
            self.svc.get(other.id, e.id)
        with self.assertRaises(NotFoundError):
            self.svc.delete(other.id, e.id)
        self.assertEqual(self.svc.list(other.id), [])


if __name__ == "__main__":
    unittest.main()

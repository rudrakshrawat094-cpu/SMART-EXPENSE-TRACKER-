import unittest

import _bootstrap  # noqa: F401
from base import DBTestCase
from expense_tracker.budget import BudgetService
from expense_tracker.expenses import ExpenseService


class BudgetTests(DBTestCase):
    def setUp(self):
        super().setUp()
        self.exp = ExpenseService(self.db)
        self.bud = BudgetService(self.db)
        self.uid = self.user.id

    def test_status_calculation(self):
        self.bud.set_limit(self.uid, "Food", "2024-01", 1000)
        self.exp.add(self.uid, 250, "Food", "", "2024-01-03")
        self.exp.add(self.uid, 250, "Food", "", "2024-02-03")  # other month ignored
        st = self.bud.status(self.uid, "2024-01")[0]
        self.assertEqual((st.spent, st.remaining, st.percent), (250.0, 750.0, 25.0))

    def test_set_limit_twice_updates(self):
        self.bud.set_limit(self.uid, "Food", "2024-01", 1000)
        self.bud.set_limit(self.uid, "Food", "2024-01", 2000)
        self.assertEqual(len(self.bud.status(self.uid, "2024-01")), 1)
        self.assertEqual(self.bud.status(self.uid, "2024-01")[0].limit, 2000)

    def test_alert_levels(self):
        self.bud.set_limit(self.uid, "Food", "2024-01", 1000)
        self.exp.add(self.uid, 500, "Food", "", "2024-01-03")
        self.assertIsNone(self.bud.check_alert(self.uid, "Food", "2024-01-03"))
        self.exp.add(self.uid, 350, "Food", "", "2024-01-04")
        self.assertIn("Warning", self.bud.check_alert(self.uid, "Food", "2024-01-04"))
        self.exp.add(self.uid, 200, "Food", "", "2024-01-05")
        self.assertIn("EXCEEDED", self.bud.check_alert(self.uid, "Food", "2024-01-05"))

    def test_no_budget_no_alert(self):
        self.assertIsNone(self.bud.check_alert(self.uid, "Rent", "2024-01-05"))


if __name__ == "__main__":
    unittest.main()

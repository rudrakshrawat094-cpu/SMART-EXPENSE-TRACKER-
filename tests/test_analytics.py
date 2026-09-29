import unittest

import _bootstrap  # noqa: F401
from base import DBTestCase
from expense_tracker.analytics import AnalyticsService, shift_month
from expense_tracker.expenses import ExpenseService


class AnalyticsTests(DBTestCase):
    def setUp(self):
        super().setUp()
        e = ExpenseService(self.db)
        uid = self.user.id
        e.add(uid, 600, "Rent", "room", "2024-03-01")
        e.add(uid, 200, "Food", "groceries", "2024-03-05")
        e.add(uid, 200, "Food", "dinner", "2024-03-05")
        e.add(uid, 300, "Food", "misc", "2024-02-10")
        e.add(uid, 900, "Rent", "room", "2024-01-01")
        self.uid, self.an = uid, AnalyticsService(self.db)

    def test_shift_month_wraps_years(self):
        self.assertEqual(shift_month("2024-01", -1), "2023-12")
        self.assertEqual(shift_month("2023-12", 1), "2024-01")
        self.assertEqual(shift_month("2024-03", -14), "2023-01")

    def test_month_total_and_breakdown(self):
        self.assertEqual(self.an.month_total(self.uid, "2024-03"), 1000.0)
        breakdown = self.an.category_breakdown(self.uid, "2024-03")
        self.assertEqual(breakdown[0], ("Rent", 600.0, 60.0))
        self.assertAlmostEqual(sum(p for _, _, p in breakdown), 100.0)

    def test_trend_and_forecast(self):
        trend = self.an.monthly_trend(self.uid, "2024-03", 3)
        self.assertEqual(trend, [("2024-01", 900.0), ("2024-02", 300.0), ("2024-03", 1000.0)])
        self.assertEqual(self.an.forecast_next_month(self.uid, "2024-03"), 733.33)

    def test_forecast_none_without_data(self):
        self.assertIsNone(self.an.forecast_next_month(self.uid, "2020-01"))

    def test_daily_average(self):
        self.assertEqual(self.an.daily_average(self.uid, "2024-03"), 500.0)  # 2 distinct days

    def test_report_and_chart(self):
        report = self.an.monthly_report(self.uid, "2024-03")
        self.assertIn("Total spent", report)
        self.assertIn("Forecast", report)
        self.assertEqual(self.an.monthly_report(self.uid, "2020-01"), "No expenses recorded for 2020-01.")
        self.assertEqual(AnalyticsService.bar_chart([]), "(no data)")


if __name__ == "__main__":
    unittest.main()

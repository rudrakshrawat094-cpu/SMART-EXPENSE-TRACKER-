"""Reporting & analytics: summaries, category breakdown, trends, forecast and ASCII charts."""
from typing import List, Optional, Tuple

from .database import Database
from .validators import validate_month


def shift_month(month: str, delta: int) -> str:
    """Return the 'YYYY-MM' string `delta` months away from `month` (negative = past)."""
    year, mon = int(month[:4]), int(month[5:7])
    index = year * 12 + (mon - 1) + delta
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


class AnalyticsService:
    def __init__(self, db: Database):
        self.db = db

    def month_total(self, user_id: int, month: str) -> float:
        month = validate_month(month)
        row = self.db.query_one(
            "SELECT COALESCE(SUM(amount), 0) AS t FROM expenses WHERE user_id = ? AND substr(date,1,7) = ?",
            (user_id, month))
        return round(row["t"], 2)

    def category_breakdown(self, user_id: int, month: str) -> List[Tuple[str, float, float]]:
        """Return [(category, total, percent)] sorted by total descending."""
        month = validate_month(month)
        rows = self.db.query(
            "SELECT category, SUM(amount) AS t FROM expenses "
            "WHERE user_id = ? AND substr(date,1,7) = ? GROUP BY category ORDER BY t DESC",
            (user_id, month))
        grand = sum(r["t"] for r in rows)
        return [(r["category"], round(r["t"], 2), round(r["t"] / grand * 100, 1)) for r in rows] if grand else []

    def top_expenses(self, user_id: int, month: str, n: int = 3):
        month = validate_month(month)
        return self.db.query(
            "SELECT * FROM expenses WHERE user_id = ? AND substr(date,1,7) = ? "
            "ORDER BY amount DESC LIMIT ?", (user_id, month, n))

    def monthly_trend(self, user_id: int, end_month: str, months: int = 6) -> List[Tuple[str, float]]:
        end_month = validate_month(end_month)
        return [(m, self.month_total(user_id, m))
                for m in (shift_month(end_month, -i) for i in range(months - 1, -1, -1))]

    def forecast_next_month(self, user_id: int, current_month: str, window: int = 3) -> Optional[float]:
        """Simple moving-average forecast over the last `window` months (None if no data)."""
        totals = [t for _, t in self.monthly_trend(user_id, current_month, window)]
        if not any(totals):
            return None
        return round(sum(totals) / len(totals), 2)

    def daily_average(self, user_id: int, month: str) -> float:
        total = self.month_total(user_id, month)
        row = self.db.query_one(
            "SELECT COUNT(DISTINCT date) AS d FROM expenses WHERE user_id = ? AND substr(date,1,7) = ?",
            (user_id, validate_month(month)))
        return round(total / row["d"], 2) if row["d"] else 0.0

    @staticmethod
    def bar_chart(data: List[Tuple[str, float]], width: int = 30) -> str:
        if not data:
            return "(no data)"
        peak = max(v for _, v in data) or 1
        label_w = max(len(str(k)) for k, _ in data)
        lines = []
        for label, value in data:
            bar = "#" * int(round(value / peak * width))
            lines.append(f"{str(label):<{label_w}} | {bar:<{width}} {value:,.2f}")
        return "\n".join(lines)

    def monthly_report(self, user_id: int, month: str) -> str:
        month = validate_month(month)
        total = self.month_total(user_id, month)
        if total == 0:
            return f"No expenses recorded for {month}."
        breakdown = self.category_breakdown(user_id, month)
        out = [f"=== Report for {month} ===",
               f"Total spent   : {total:,.2f}",
               f"Daily average : {self.daily_average(user_id, month):,.2f}",
               "", "Spending by category:",
               self.bar_chart([(f"{c} ({p}%)", t) for c, t, p in breakdown]),
               "", "Top expenses:"]
        for r in self.top_expenses(user_id, month):
            out.append(f"  {r['date']}  {r['amount']:>10,.2f}  {r['category']:<13} {r['description']}")
        forecast = self.forecast_next_month(user_id, month)
        if forecast is not None:
            out += ["", f"Forecast for next month (3-month moving average): {forecast:,.2f}"]
        return "\n".join(out)

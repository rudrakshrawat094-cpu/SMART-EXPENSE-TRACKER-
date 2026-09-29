"""Budget module: monthly per-category limits with warning / exceeded alerts."""
from typing import List, Optional

from .config import BUDGET_WARNING_THRESHOLD
from .database import Database
from .logger import get_logger
from .models import BudgetStatus
from .validators import validate_amount, validate_category, validate_month

log = get_logger("budget")


class BudgetService:
    def __init__(self, db: Database):
        self.db = db

    def set_limit(self, user_id: int, category: str, month: str, limit) -> BudgetStatus:
        category, month, limit = validate_category(category), validate_month(month), validate_amount(limit)
        self.db.execute(
            """INSERT INTO budgets (user_id, category, month, limit_amount) VALUES (?,?,?,?)
               ON CONFLICT (user_id, category, month) DO UPDATE SET limit_amount = excluded.limit_amount""",
            (user_id, category, month, limit))
        log.info("User %s set %s budget for %s = %.2f", user_id, category, month, limit)
        return self._status(user_id, category, month, limit)

    def _spent(self, user_id: int, category: str, month: str) -> float:
        row = self.db.query_one(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses "
            "WHERE user_id = ? AND category = ? AND substr(date, 1, 7) = ?",
            (user_id, category, month))
        return round(row["total"], 2)

    def _status(self, user_id, category, month, limit) -> BudgetStatus:
        return BudgetStatus(category, month, limit, self._spent(user_id, category, month))

    def status(self, user_id: int, month: str) -> List[BudgetStatus]:
        month = validate_month(month)
        rows = self.db.query(
            "SELECT category, limit_amount FROM budgets WHERE user_id = ? AND month = ? ORDER BY category",
            (user_id, month))
        return [self._status(user_id, r["category"], month, r["limit_amount"]) for r in rows]

    def check_alert(self, user_id: int, category: str, expense_date: str) -> Optional[str]:
        """Return a warning message if the given expense pushed a budget over the threshold."""
        month = expense_date[:7]
        row = self.db.query_one(
            "SELECT limit_amount FROM budgets WHERE user_id = ? AND category = ? AND month = ?",
            (user_id, category, month))
        if row is None:
            return None
        st = self._status(user_id, category, month, row["limit_amount"])
        if st.percent >= 100:
            return f"BUDGET EXCEEDED for {category} ({month}): spent {st.spent:.2f} of {st.limit:.2f}."
        if st.percent >= BUDGET_WARNING_THRESHOLD:
            return f"Warning: {st.percent:.0f}% of your {category} budget for {month} is used."
        return None

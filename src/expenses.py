"""Expense management: full CRUD plus filtering, searching and sorting."""
from datetime import date
from typing import List, Optional

from .config import DATE_FORMAT
from .database import Database
from .exceptions import NotFoundError, ValidationError
from .logger import get_logger
from .models import Expense
from .validators import (validate_amount, validate_category, validate_date,
                         validate_description, validate_month)

log = get_logger("expenses")

_SORTABLE = {"date": "date", "amount": "amount", "category": "category"}
_UPDATABLE = {
    "amount": validate_amount,
    "category": validate_category,
    "description": validate_description,
    "date": validate_date,
}


class ExpenseService:
    def __init__(self, db: Database):
        self.db = db

    # ---- Create -------------------------------------------------------
    def add(self, user_id: int, amount, category: str, description: str = "",
            when: Optional[str] = None) -> Expense:
        amount = validate_amount(amount)
        category = validate_category(category)
        description = validate_description(description)
        when = validate_date(when) if when else date.today().strftime(DATE_FORMAT)
        cur = self.db.execute(
            "INSERT INTO expenses (user_id, amount, category, description, date) VALUES (?,?,?,?,?)",
            (user_id, amount, category, description, when))
        log.info("User %s added expense %s (%.2f %s)", user_id, cur.lastrowid, amount, category)
        return Expense(cur.lastrowid, user_id, amount, category, description, when)

    # ---- Read ---------------------------------------------------------
    def get(self, user_id: int, expense_id: int) -> Expense:
        row = self.db.query_one("SELECT * FROM expenses WHERE id = ? AND user_id = ?",
                                (expense_id, user_id))
        if row is None:
            raise NotFoundError(f"Expense #{expense_id} not found.")
        return Expense.from_row(row)

    def list(self, user_id: int, category: Optional[str] = None, month: Optional[str] = None,
             keyword: Optional[str] = None, sort_by: str = "date",
             descending: bool = True) -> List[Expense]:
        if sort_by not in _SORTABLE:
            raise ValidationError(f"Sort field must be one of: {', '.join(_SORTABLE)}.")
        sql, params = "SELECT * FROM expenses WHERE user_id = ?", [user_id]
        if category:
            sql += " AND category = ?"
            params.append(validate_category(category))
        if month:
            sql += " AND substr(date, 1, 7) = ?"
            params.append(validate_month(month))
        if keyword:
            sql += " AND description LIKE ?"
            params.append(f"%{keyword.strip()}%")
        sql += f" ORDER BY {_SORTABLE[sort_by]} {'DESC' if descending else 'ASC'}, id DESC"
        return [Expense.from_row(r) for r in self.db.query(sql, params)]

    # ---- Update -------------------------------------------------------
    def update(self, user_id: int, expense_id: int, **fields) -> Expense:
        self.get(user_id, expense_id)  # ownership + existence check
        unknown = set(fields) - set(_UPDATABLE)
        if unknown:
            raise ValidationError(f"Cannot update field(s): {', '.join(sorted(unknown))}.")
        if not fields:
            raise ValidationError("Nothing to update.")
        cleaned = {k: _UPDATABLE[k](v) for k, v in fields.items()}
        assignments = ", ".join(f"{k} = ?" for k in cleaned)  # keys come from the whitelist
        self.db.execute(f"UPDATE expenses SET {assignments} WHERE id = ? AND user_id = ?",
                        (*cleaned.values(), expense_id, user_id))
        log.info("User %s updated expense %s", user_id, expense_id)
        return self.get(user_id, expense_id)

    # ---- Delete -------------------------------------------------------
    def delete(self, user_id: int, expense_id: int) -> None:
        self.get(user_id, expense_id)
        self.db.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id))
        log.info("User %s deleted expense %s", user_id, expense_id)

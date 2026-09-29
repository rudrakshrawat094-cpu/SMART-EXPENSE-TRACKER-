"""Plain data classes shared between layers."""
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    username: str


@dataclass(frozen=True)
class Expense:
    id: int
    user_id: int
    amount: float
    category: str
    description: str
    date: str

    @classmethod
    def from_row(cls, row) -> "Expense":
        return cls(row["id"], row["user_id"], row["amount"], row["category"],
                   row["description"], row["date"])


@dataclass(frozen=True)
class BudgetStatus:
    category: str
    month: str
    limit: float
    spent: float

    @property
    def remaining(self) -> float:
        return round(self.limit - self.spent, 2)

    @property
    def percent(self) -> float:
        return round(self.spent / self.limit * 100, 1) if self.limit else 0.0

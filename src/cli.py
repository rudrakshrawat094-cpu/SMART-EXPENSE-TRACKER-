"""Command-line interface: menu loop that wires all services together."""
from datetime import date
from getpass import getpass

from .analytics import AnalyticsService
from .auth import AuthService
from .budget import BudgetService
from .config import CATEGORIES, EXPORT_DIR, MONTH_FORMAT
from .database import Database
from .exceptions import ExpenseTrackerError
from .exporter import export_csv, import_csv
from .expenses import ExpenseService
from .logger import get_logger

log = get_logger("cli")

MAIN_MENU = "\n--- Smart Expense Tracker ---\n1. Register\n2. Login\n0. Exit"
USER_MENU = """
--- Menu ({user}) ---
1. Add expense          7. Monthly report
2. View / search        8. Trend & forecast
3. Edit expense         9. Export CSV
4. Delete expense      10. Import CSV
5. Set budget          11. Logout
6. Budget status
"""


def _current_month() -> str:
    return date.today().strftime(MONTH_FORMAT)


def _ask_month() -> str:
    return input(f"Month YYYY-MM [{_current_month()}]: ").strip() or _current_month()


def _print_expenses(expenses) -> None:
    if not expenses:
        print("No expenses found.")
        return
    print(f"{'ID':>4}  {'Date':<10}  {'Amount':>10}  {'Category':<13} Description")
    for e in expenses:
        print(f"{e.id:>4}  {e.date:<10}  {e.amount:>10,.2f}  {e.category:<13} {e.description}")
    print(f"Total: {sum(e.amount for e in expenses):,.2f}  ({len(expenses)} records)")


class App:
    def __init__(self, db: Database):
        self.auth = AuthService(db)
        self.expenses = ExpenseService(db)
        self.budgets = BudgetService(db)
        self.analytics = AnalyticsService(db)
        self.user = None

    def run(self) -> None:
        while True:
            try:
                if self.user is None:
                    print(MAIN_MENU)
                    if not self._guest_action(input("Choose: ").strip()):
                        print("Goodbye!")
                        return
                else:
                    print(USER_MENU.format(user=self.user.username))
                    self._user_action(input("Choose: ").strip())
            except ExpenseTrackerError as exc:
                print(f"Error: {exc}")
            except ValueError:
                print("Error: please enter a valid number.")
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                return
            except Exception:  # last-resort safety net; details go to the log file
                log.exception("Unexpected error")
                print("Something went wrong. Details were written to logs/app.log.")

    def _guest_action(self, choice: str) -> bool:
        if choice == "1":
            user = self.auth.register(input("Username: "), getpass("Password: "))
            print(f"Account created. Welcome, {user.username}! Please log in.")
        elif choice == "2":
            self.user = self.auth.login(input("Username: "), getpass("Password: "))
            print(f"Logged in as {self.user.username}.")
        elif choice == "0":
            return False
        else:
            print("Invalid choice.")
        return True

    def _user_action(self, choice: str) -> None:
        uid = self.user.id
        if choice == "1":
            print(f"Categories: {', '.join(CATEGORIES)}")
            e = self.expenses.add(uid, input("Amount: "), input("Category: "),
                                  input("Description: "),
                                  input("Date YYYY-MM-DD (blank = today): ").strip() or None)
            print(f"Saved expense #{e.id}.")
            alert = self.budgets.check_alert(uid, e.category, e.date)
            if alert:
                print(alert)
        elif choice == "2":
            _print_expenses(self.expenses.list(
                uid, category=input("Category filter (blank = all): ").strip() or None,
                month=input("Month YYYY-MM (blank = all): ").strip() or None,
                keyword=input("Keyword (blank = none): ").strip() or None,
                sort_by=input("Sort by date/amount/category [date]: ").strip() or "date"))
        elif choice == "3":
            eid = int(input("Expense ID: "))
            current = self.expenses.get(uid, eid)
            print("Leave a field blank to keep the current value.")
            changes = {}
            for field in ("amount", "category", "description", "date"):
                val = input(f"{field} [{getattr(current, field)}]: ").strip()
                if val:
                    changes[field] = val
            self.expenses.update(uid, eid, **changes)
            print("Updated.")
        elif choice == "4":
            eid = int(input("Expense ID: "))
            if input("Type YES to confirm delete: ").strip() == "YES":
                self.expenses.delete(uid, eid)
                print("Deleted.")
            else:
                print("Cancelled.")
        elif choice == "5":
            st = self.budgets.set_limit(uid, input("Category: "), _ask_month(), input("Limit: "))
            print(f"Budget set. Used so far: {st.percent}%")
        elif choice == "6":
            statuses = self.budgets.status(uid, _ask_month())
            if not statuses:
                print("No budgets set for that month.")
            for s in statuses:
                print(f"{s.category:<13} spent {s.spent:>10,.2f} / {s.limit:>10,.2f}  ({s.percent}%)  "
                      f"left {s.remaining:,.2f}")
        elif choice == "7":
            print(self.analytics.monthly_report(uid, _ask_month()))
        elif choice == "8":
            month = _current_month()
            print(self.analytics.bar_chart(self.analytics.monthly_trend(uid, month, 6)))
            fc = self.analytics.forecast_next_month(uid, month)
            print(f"Forecast next month: {fc:,.2f}" if fc is not None else "Not enough data to forecast.")
        elif choice == "9":
            path = EXPORT_DIR / f"expenses_{self.user.username}_{date.today()}.csv"
            print(f"Exported {export_csv(self.expenses.list(uid), path)} records to {path}")
        elif choice == "10":
            n, errors = import_csv(self.expenses, uid, input("CSV file path: ").strip())
            print(f"Imported {n} rows.")
            for err in errors[:10]:
                print("  skipped -", err)
        elif choice == "11":
            self.user = None
            print("Logged out.")
        else:
            print("Invalid choice.")

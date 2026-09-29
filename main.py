"""Entry point:  python main.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from expense_tracker.cli import App                   # noqa: E402
from expense_tracker.database import Database         # noqa: E402
from expense_tracker.exceptions import DatabaseError  # noqa: E402


def main() -> int:
    try:
        db = Database()
    except DatabaseError as exc:
        print(f"Fatal: {exc}")
        return 1
    try:
        App(db).run()
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

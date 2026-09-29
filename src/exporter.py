"""CSV export / import so users can back up data or bring in bank statements."""
import csv
from pathlib import Path
from typing import Iterable, List, Tuple

from .exceptions import ExpenseTrackerError, ValidationError
from .expenses import ExpenseService
from .logger import get_logger
from .models import Expense

log = get_logger("exporter")
FIELDS = ["date", "amount", "category", "description"]


def export_csv(expenses: Iterable[Expense], path) -> int:
    path = Path(path)
    count = 0
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS)
            writer.writeheader()
            for e in expenses:
                writer.writerow({"date": e.date, "amount": e.amount,
                                 "category": e.category, "description": e.description})
                count += 1
    except OSError as exc:
        log.exception("CSV export failed")
        raise ExpenseTrackerError(f"Could not write file: {exc}") from exc
    log.info("Exported %d expenses to %s", count, path)
    return count


def import_csv(service: ExpenseService, user_id: int, path) -> Tuple[int, List[str]]:
    """Import rows; invalid rows are skipped and reported instead of aborting the whole import."""
    path = Path(path)
    if not path.is_file():
        raise ValidationError(f"File not found: {path}")
    imported, errors = 0, []
    try:
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if not reader.fieldnames or not {"date", "amount", "category"} <= set(reader.fieldnames):
                raise ValidationError("CSV must have columns: date, amount, category[, description].")
            for line_no, row in enumerate(reader, start=2):
                try:
                    service.add(user_id, row["amount"], row["category"],
                                row.get("description") or "", row["date"])
                    imported += 1
                except ExpenseTrackerError as exc:
                    errors.append(f"Line {line_no}: {exc}")
    except (OSError, UnicodeDecodeError) as exc:
        raise ExpenseTrackerError(f"Could not read file: {exc}") from exc
    log.info("Imported %d rows (%d errors) from %s", imported, len(errors), path)
    return imported, errors

"""Central configuration: paths, constants and limits."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "expenses.db"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"
EXPORT_DIR = BASE_DIR / "exports"

CATEGORIES = [
    "Food", "Transport", "Rent", "Utilities", "Education",
    "Entertainment", "Health", "Shopping", "Savings", "Other",
]

MAX_AMOUNT = 10_000_000
MAX_DESCRIPTION_LEN = 100
MIN_PASSWORD_LEN = 6
PBKDF2_ITERATIONS = 100_000
BUDGET_WARNING_THRESHOLD = 80.0  # percent of the limit at which a warning is shown
DATE_FORMAT = "%Y-%m-%d"
MONTH_FORMAT = "%Y-%m"

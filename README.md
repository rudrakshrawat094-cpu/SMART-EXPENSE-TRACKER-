# SMART-EXPENSE-TRACKER

A modular, command-line personal finance manager written in **Python** with **SQLite** storage.
It lets students and individuals record expenses, set monthly budgets, get alerts, and view
analytics such as category breakdowns, monthly trends and a spending forecast.

> Built for the **VITyarthi – Build Your Own Project** evaluation.

## Overview
Most people do not know where their money goes until the month is over. This tool makes tracking
quick (one menu, a few prompts), warns you *before* a budget is broken, and turns raw records into
simple reports and a next-month forecast.

## Features
| Module | What it does |
|---|---|
| **User management** (`auth.py`) | Register / login, salted PBKDF2-SHA256 password hashing, per-user data isolation |
| **Expense management** (`expenses.py`) | Full CRUD, filter by category / month / keyword, sort by date / amount / category |
| **Budgeting** (`budget.py`) | Monthly per-category limits, live status, warning at 80 % and alert when exceeded |
| **Analytics** (`analytics.py`) | Monthly report, category percentages, top expenses, daily average, 6-month trend chart, moving-average forecast |
| **Import / Export** (`exporter.py`) | Back up to CSV and import CSV (bad rows are skipped and reported) |
| **Logging & error handling** | Rotating log file (`logs/app.log`), custom exception hierarchy, friendly CLI messages |

## Technologies
- Python 3.9+ (standard library only: `sqlite3`, `hashlib`, `csv`, `logging`, `unittest`, `dataclasses`)
- SQLite 3 for storage
- Git & GitHub for version control

## Project structure
```
smart-expense-tracker/
├── main.py                     # entry point
├── src/expense_tracker/
│   ├── config.py               # constants & paths
│   ├── exceptions.py           # custom exception hierarchy
│   ├── logger.py               # rotating file logging
│   ├── validators.py           # input validation
│   ├── models.py               # dataclasses (User, Expense, BudgetStatus)
│   ├── database.py             # SQLite wrapper + schema
│   ├── auth.py                 # register / login
│   ├── expenses.py             # CRUD + search
│   ├── budget.py               # budgets & alerts
│   ├── analytics.py            # reports, trend, forecast
│   ├── exporter.py             # CSV import/export
│   └── cli.py                  # menu-driven interface
├── tests/                      # 31 unit tests
├── data/sample_expenses.csv    # demo data you can import
└── docs/                       # design diagrams, report guide, git guide
```

## Install & run
```bash
git clone https://github.com/<your-username>/smart-expense-tracker.git
cd smart-expense-tracker
python main.py            # no dependencies to install
```
1. Choose **1. Register**, then **2. Login**.
2. Try **10. Import CSV** with `data/sample_expenses.csv` to load demo data.
3. Open **7. Monthly report** and enter `2025-01`.

## Testing
```bash
python -m unittest discover -s tests -v
```
Tests use an in-memory SQLite database, so they never touch your real data.
They cover validation, authentication, CRUD, cross-user isolation, SQL-injection attempts on sort fields,
budget alerts, analytics maths (incl. year-boundary month arithmetic) and CSV round-trips.

## Screenshots
Add screenshots of the menu, monthly report and budget alert in a `docs/screenshots/` folder and link them here.

## Author
*Your Name – RUDRAKSH RAWAT 
*Reg. No. – 26MIB10026

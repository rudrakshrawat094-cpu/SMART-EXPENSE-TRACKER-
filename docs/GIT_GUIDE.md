# Git & GitHub guide (10 % of marks are for repository + version control)

Make **many small commits** with clear messages - graders look at the history.

```bash
cd smart-expense-tracker
git init
git branch -M main

git add .gitignore requirements.txt && git commit -m "chore: add gitignore and requirements"
git add README.md statement.md       && git commit -m "docs: add README and problem statement"
git add src/expense_tracker/config.py src/expense_tracker/exceptions.py src/expense_tracker/logger.py src/expense_tracker/__init__.py \
                                     && git commit -m "feat: add config, exceptions and logging"
git add src/expense_tracker/validators.py src/expense_tracker/models.py \
                                     && git commit -m "feat: add input validation and data models"
git add src/expense_tracker/database.py && git commit -m "feat: add SQLite storage layer and schema"
git add src/expense_tracker/auth.py  && git commit -m "feat: add user registration and login"
git add src/expense_tracker/expenses.py && git commit -m "feat: add expense CRUD, search and sort"
git add src/expense_tracker/budget.py   && git commit -m "feat: add budgets and alerts"
git add src/expense_tracker/analytics.py && git commit -m "feat: add reports, trend and forecast"
git add src/expense_tracker/exporter.py  && git commit -m "feat: add CSV import/export"
git add src/expense_tracker/cli.py main.py data/ && git commit -m "feat: add CLI and sample data"
git add tests/                          && git commit -m "test: add unit tests"
git add docs/                           && git commit -m "docs: add design diagrams and guides"
```

Create an **empty** repository on github.com (no README), then:
```bash
git remote add origin https://github.com/<your-username>/smart-expense-tracker.git
git push -u origin main
```

Later changes: `git checkout -b feature/xyz` → edit → commit → merge/PR.

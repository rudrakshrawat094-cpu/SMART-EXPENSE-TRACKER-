# Project Statement

## Problem statement
Students and young professionals often lose track of their spending because records are scattered
across notes, chat messages and bank apps. Without a single, organised view they cannot tell which
categories consume most of their money, they overshoot budgets without noticing, and they cannot
predict next month's expenses.

## Scope of the project
**In scope**
- Multi-user, offline, command-line application with secure login
- Recording, editing, deleting, searching and sorting expenses
- Monthly per-category budgets with warning / exceeded alerts
- Reports: totals, category breakdown, top expenses, daily average, 6-month trend, simple forecast
- CSV import and export; logging; input validation; automated tests

**Out of scope**
- Graphical / web interface, bank-account syncing, multi-currency support, cloud storage

## Target users
- College students managing a monthly allowance
- Young professionals who want a lightweight, private budgeting tool
- Learners who want a reference example of a layered, tested Python application

## High-level features
1. User registration and login with hashed passwords
2. Expense CRUD with filtering, keyword search and sorting
3. Budget limits with automatic alerts
4. Analytics report with ASCII bar charts and moving-average forecast
5. CSV import / export
6. Central logging and robust error handling

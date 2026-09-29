# Design Documentation

GitHub renders the Mermaid diagrams below automatically. To put them in your PDF report, open this file on
GitHub (or paste each block into <https://mermaid.live>) and export as PNG/SVG.

## 1. Problem statement & objectives
See `statement.md`. **Objectives:** (1) capture expenses quickly and safely, (2) prevent budget overruns,
(3) give insight through analytics and a forecast, (4) keep the code modular, tested and documented.

## 2. Functional requirements
| ID | Requirement |
|----|-------------|
| FR1 | User can register and log in; each user sees only their own data |
| FR2 | User can add, view, edit and delete expenses |
| FR3 | User can filter by category/month, search by keyword and sort |
| FR4 | User can set a monthly budget per category and see used/remaining amounts |
| FR5 | System warns at ≥80 % and alerts at ≥100 % of a budget when an expense is added |
| FR6 | System produces a monthly report, 6-month trend and next-month forecast |
| FR7 | User can export expenses to CSV and import from CSV |

## 3. Non-functional requirements
| ID | Category | Requirement | How it is met |
|----|----------|-------------|---------------|
| NFR1 | Security | Passwords never stored in plain text; no SQL injection | PBKDF2-SHA256 + random salt, `hmac.compare_digest`, parameterised queries, whitelist for sort/update fields |
| NFR2 | Reliability | Bad input or bad files must not crash the app | Central validators, custom exceptions, CLI catch-all, per-row CSV error reporting |
| NFR3 | Usability | Clear menus, defaults, confirmation before delete | Blank = default prompts, `YES` confirmation, readable tables |
| NFR4 | Maintainability | Small single-purpose modules, documented, tested | Layered architecture, docstrings, 31 unit tests |
| NFR5 | Logging | Important events are auditable | Rotating log file with timestamps and levels |
| NFR6 | Performance | Reports on thousands of rows respond instantly | Indexed `(user_id, date)` and SQL aggregation |
| NFR7 | Portability | Runs anywhere Python 3.9+ runs | Standard library only |

## 4. System architecture
```mermaid
flowchart TB
    U([User]) --> CLI[cli.py<br/>Presentation layer]
    subgraph Services [Business logic layer]
        AUTH[auth.py]
        EXP[expenses.py]
        BUD[budget.py]
        ANA[analytics.py]
        EXPT[exporter.py]
    end
    CLI --> AUTH & EXP & BUD & ANA & EXPT
    EXPT --> EXP
    subgraph Support [Cross-cutting]
        VAL[validators.py]
        LOG[logger.py]
        CFG[config.py]
        ERR[exceptions.py]
    end
    Services --> VAL
    Services --> LOG
    AUTH & EXP & BUD & ANA --> DB[(database.py<br/>SQLite)]
    EXPT --> CSV[(CSV files)]
    LOG --> LF[(logs/app.log)]
```

## 5. Workflow diagram
```mermaid
flowchart TD
    A([Start]) --> B{Registered?}
    B -- No --> C[Register] --> D[Login]
    B -- Yes --> D
    D --> E{Valid credentials?}
    E -- No --> D
    E -- Yes --> F[Main menu]
    F --> G[Add / Edit / Delete expense]
    F --> H[Set budget]
    F --> I[Reports & forecast]
    F --> J[Import / Export CSV]
    G --> K{Input valid?}
    K -- No --> L[Show error] --> F
    K -- Yes --> M[Save to database] --> N{Budget >= 80%?}
    N -- Yes --> O[Show alert] --> F
    N -- No --> F
    H --> F
    I --> F
    J --> F
    F --> P([Logout / Exit])
```

## 6. Use case diagram
```mermaid
flowchart LR
    User((User))
    subgraph System [Smart Expense Tracker]
        UC1([Register / Login])
        UC2([Manage expenses - CRUD])
        UC3([Search & sort expenses])
        UC4([Set budget])
        UC5([View budget status & alerts])
        UC6([View monthly report])
        UC7([View trend & forecast])
        UC8([Import / Export CSV])
    end
    User --- UC1 & UC2 & UC3 & UC4 & UC5 & UC6 & UC7 & UC8
```

## 7. Sequence diagram - adding an expense
```mermaid
sequenceDiagram
    actor U as User
    participant C as CLI
    participant V as Validators
    participant E as ExpenseService
    participant D as Database
    participant B as BudgetService
    U->>C: choose "Add expense", enter data
    C->>E: add(user_id, amount, category, desc, date)
    E->>V: validate amount / category / description / date
    alt invalid
        V-->>C: ValidationError
        C-->>U: "Error: ..."
    else valid
        E->>D: INSERT INTO expenses
        D-->>E: new id
        E-->>C: Expense
        C->>B: check_alert(user_id, category, date)
        B->>D: SELECT budget + SUM(spent)
        B-->>C: alert message or None
        C-->>U: "Saved expense #id" (+ alert)
    end
```

## 8. Class / component diagram
```mermaid
classDiagram
    class Database { +execute() +query() +query_one() +close() }
    class AuthService { +register() +login() }
    class ExpenseService { +add() +get() +list() +update() +delete() }
    class BudgetService { +set_limit() +status() +check_alert() }
    class AnalyticsService { +month_total() +category_breakdown() +top_expenses() +monthly_trend() +forecast_next_month() +daily_average() +bar_chart() +monthly_report() }
    class App { +run() }
    class User { +id +username }
    class Expense { +id +user_id +amount +category +description +date }
    class BudgetStatus { +category +month +limit +spent +remaining +percent }
    App --> AuthService
    App --> ExpenseService
    App --> BudgetService
    App --> AnalyticsService
    AuthService --> Database
    ExpenseService --> Database
    BudgetService --> Database
    AnalyticsService --> Database
    AuthService ..> User
    ExpenseService ..> Expense
    BudgetService ..> BudgetStatus
```

## 9. ER diagram & schema
```mermaid
erDiagram
    USERS ||--o{ EXPENSES : records
    USERS ||--o{ BUDGETS : sets
    USERS {
        int id PK
        text username UK
        text password_hash
        text salt
        text created_at
    }
    EXPENSES {
        int id PK
        int user_id FK
        real amount
        text category
        text description
        text date
        text created_at
    }
    BUDGETS {
        int id PK
        int user_id FK
        text category
        text month
        real limit_amount
    }
```
Constraints: `amount > 0`, `limit_amount > 0`, `UNIQUE(user_id, category, month)`, foreign keys with `ON DELETE CASCADE`,
index on `expenses(user_id, date)`. Full DDL is in `src/expense_tracker/database.py`.

## 10. Design decisions & rationale
| Decision | Rationale |
|----------|-----------|
| Layered architecture (CLI → services → DB) | Business rules can be tested without the UI; UI can later be swapped for Tkinter/Flask |
| SQLite | Zero-setup, transactional, supports SQL aggregation for reports |
| Standard library only | Easy to run/grade, no dependency issues |
| Service classes receive `Database` (dependency injection) | Tests use `:memory:` database |
| Custom exception hierarchy | UI catches one base class and shows friendly messages |
| Amounts rounded to 2 decimals in validators | Prevents floating-point clutter in reports |
| Moving-average forecast | Simple, explainable, good enough for small personal datasets |
| Same error for unknown user and wrong password | Prevents username enumeration |

## 11. Algorithms / concepts used
Hashing with salt (PBKDF2), SQL aggregation & grouping, sorting with whitelisted keys, moving average,
month arithmetic across year boundaries, normalisation of percentages, exception handling, file I/O (CSV),
OOP (classes, dataclasses, composition), modules/packages, logging and unit testing.

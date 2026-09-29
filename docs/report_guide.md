# How to turn this project into the required PDF report

The portal wants a PDF with 15 sections. Here is where to get the content for each one.

| # | Section | Source / what to write |
|---|---------|------------------------|
| 1 | Cover page | Title, your name, register no., course, faculty, date |
| 2 | Introduction | README "Overview" - add 1-2 paragraphs on why expense tracking matters |
| 3 | Problem statement | `statement.md` |
| 4 | Functional requirements | `docs/design.md` §2 |
| 5 | Non-functional requirements | `docs/design.md` §3 |
| 6 | System architecture | `docs/design.md` §4 (export diagram as image) |
| 7 | Design diagrams | §5 workflow, §6 use case, §7 sequence, §8 class, §9 ER |
| 8 | Design decisions & rationale | `docs/design.md` §10 |
| 9 | Implementation details | One paragraph per module + short code snippets (e.g. password hashing, alert logic, forecast) |
| 10 | Screenshots / results | Run the app and capture menu, add-expense with alert, monthly report, test output |
| 11 | Testing approach | Describe unit tests, in-memory DB, edge cases; paste `unittest` output |
| 12 | Challenges faced | e.g. SQL injection safety for dynamic sort/update, month arithmetic across years, CSV bad rows, floating-point money |
| 13 | Learnings & takeaways | Layered design, testing, validation, Git workflow |
| 14 | Future enhancements | GUI/web front-end, charts (matplotlib), recurring expenses, multi-currency, encrypted DB, ML-based forecasting |
| 15 | References | Python docs (sqlite3, hashlib, unittest, logging), OWASP password storage cheat sheet, course material |

Tip: write it in Word/Google Docs, insert the diagram images, and export to PDF.

# FinTrack API

A learning-oriented personal finance backend built with **Python, FastAPI, SQLAlchemy, and SQLite**. It demonstrates REST API design, relational persistence, request validation, filtering, pagination, and summary calculations.

## Features implemented
- Create, list, retrieve, update, and delete transactions.
- Validate transaction amounts, fields, and transaction type.
- Filter transactions by type and category.
- Paginate list responses with `limit` and `offset`.
- Calculate total income, total expenses, and balance.
- Automatically generate interactive API docs.
- Basic automated tests for health and input validation.

## Run locally
Python 3.11+ recommended.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Example request
`POST /transactions`
```json
{
  "title": "Part-time income",
  "amount": 2500,
  "category": "Income",
  "kind": "income",
  "transaction_date": "2026-10-20"
}
```

## Run tests
```bash
pytest
```

## Suggested next improvements
- Add user accounts and authorization before supporting multiple users.
- Add a dedicated test database and more CRUD/summary tests.
- Replace SQLite with PostgreSQL and configure `DATABASE_URL`.
- Add structured logging and stronger error handling.
- Add budgets and monthly reports.
- Do not describe this starter version as production-ready.

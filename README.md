# Expense Tracker API

GitHub Repository: https://github.com/kevalpatel5011/expense-tracker-api

A Flask-based REST API for managing expenses with JSON file persistence.

## Features

- Add, view, update, and delete expenses
- Filter expenses by category, amount range, and date range
- Sort expenses by amount, date, title, or category
- Paginate expense results with limit and offset
- Generate summary, monthly, yearly, and category reports
- Save expenses to a JSON file
- Includes unit tests for core logic and API routes

## Project Structure

```text
expense tracker/
├── app.py
├── config.py
├── expense_utils.py
├── Expense_Tracker_System.py
├── expenses.json
└── tests/
    ├── test_app.py
    └── test_expense_tracker.py
```

## Run The App

```bash
cd "/Users/kevalpatel/Learning/expense tracker"
"$PWD/.venv/bin/python3" app.py
```

## Run Tests

```bash
cd "/Users/kevalpatel/Learning/expense tracker"
PYTHONPATH="$PWD" "$PWD/.venv/bin/python3" -m unittest discover -s tests
```

## Example API Requests

```bash
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/expenses
curl "http://127.0.0.1:5000/expenses?category=housing"
curl "http://127.0.0.1:5000/expenses?min_amount=100&max_amount=2000"
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check if API is running |
| GET | `/health` | Health check route |
| GET | `/expenses` | Get all expenses, with optional filters |
| POST | `/expenses` | Create a new expense |
| GET | `/expenses/<expense_id>` | Get one expense by ID |
| PUT | `/expenses/<expense_id>` | Replace an existing expense |
| PATCH | `/expenses/<expense_id>` | Update selected expense fields |
| DELETE | `/expenses/<expense_id>` | Delete an expense |
| GET | `/expenses/summary` | Get expense summary |
| GET | `/expenses/category/<category>` | Get expenses by category |
| GET | `/expenses/date/<date>` | Get expenses by date |
| GET | `/reports/monthly/<year>/<month>` | Get monthly expense report |
| GET | `/reports/yearly/<year>` | Get yearly expense report |
| GET | `/reports/categories` | Get category summary report |
| GET | `/reports/categories/<year>` | Get yearly category report |
| GET | `/reports/categories/<year>/<month>` | Get monthly category report |
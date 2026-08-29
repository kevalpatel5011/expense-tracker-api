# Expense Tracker API

GitHub Repository: https://github.com/kevalpatel5011/expense-tracker-api

A Flask REST API for managing expenses with SQLite database persistence.

## Portfolio Summary

This project demonstrates backend API development using Python, Flask, and SQLite. It includes RESTful routes, JSON request handling, input validation, filtering, sorting, pagination, report generation, database transactions, data migration, automated testing, and Git/GitHub version control.

## Features

* Add, view, update, and delete expenses
* Store expense data in SQLite
* Filter expenses by category, amount range, and date range
* Sort expenses by amount, date, title, or category
* Paginate expense results using limit and offset
* Generate summary, monthly, yearly, and category reports
* Use parameterized SQL queries for safer database operations
* Use commit, rollback, and connection cleanup for database transactions
* Migrate existing expense data from JSON to SQLite
* Automatically initialize the SQLite table when the application starts
* Includes automated tests for core logic, API routes, repository operations, and data migration

## Project Structure

```text
expense-tracker-api/
├── .gitignore
├── app.py
├── config.py
├── database.py
├── expense_repository.py
├── expense_utils.py
├── Expense_Tracker_System.py
├── expenses.json
├── migrate_json_to_sqlite.py
├── requirements.txt
├── README.md
└── tests/
    ├── test_app.py
    ├── test_expense_repository.py
    ├── test_expense_tracker.py
    └── test_migration.py
```

The `expenses.db` file is generated locally and ignored by Git. The `expenses.json` file is retained as the original data source for the optional migration script.

## Technologies Used

* Python
* Flask
* SQLite
* SQL
* Python `unittest`
* Git and GitHub

## Setup

Clone the repository and enter the project directory:

```bash
git clone https://github.com/kevalpatel5011/expense-tracker-api.git
cd expense-tracker-api
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required packages:

```bash
python3 -m pip install -r requirements.txt
```

## Run the Application

```bash
python3 app.py
```

The application automatically creates the SQLite database table if it does not already exist.

The API runs locally at:

```text
http://127.0.0.1:5000
```

## Migrate Existing JSON Data

To import existing records from `expenses.json` into SQLite, run:

```bash
python3 migrate_json_to_sqlite.py
```

The migration script reports how many expenses were inserted and how many were skipped. Existing primary-key IDs are not overwritten, so duplicate IDs are skipped safely.

## Run Tests

Run the complete test suite from the project root:

```bash
python3 -m unittest discover -s tests
```

## Example API Requests

```bash
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/expenses
curl "http://127.0.0.1:5000/expenses?category=housing"
curl "http://127.0.0.1:5000/expenses?min_amount=100&max_amount=2000"
```

## API Endpoints

| Method | Endpoint                             | Description                                                   |
| ------ | ------------------------------------ | ------------------------------------------------------------- |
| GET    | `/`                                  | Check whether the API is running                              |
| GET    | `/health`                            | Get the API health status                                     |
| GET    | `/expenses`                          | Get expenses with optional filtering, sorting, and pagination |
| POST   | `/expenses`                          | Create an expense                                             |
| GET    | `/expenses/<expense_id>`             | Get one expense by ID                                         |
| PUT    | `/expenses/<expense_id>`             | Replace an existing expense                                   |
| PATCH  | `/expenses/<expense_id>`             | Update selected expense fields                                |
| DELETE | `/expenses/<expense_id>`             | Delete an expense                                             |
| GET    | `/expenses/summary`                  | Get an expense summary                                        |
| GET    | `/expenses/category/<category>`      | Get expenses by category                                      |
| GET    | `/expenses/date/<date>`              | Get expenses by date                                          |
| GET    | `/reports/monthly/<year>/<month>`    | Get a monthly expense report                                  |
| GET    | `/reports/yearly/<year>`             | Get a yearly expense report                                   |
| GET    | `/reports/categories`                | Get a category summary report                                 |
| GET    | `/reports/categories/<year>`         | Get a yearly category report                                  |
| GET    | `/reports/categories/<year>/<month>` | Get a monthly category report                                 |

## Example Create Expense Request

```bash
curl -X POST http://127.0.0.1:5000/expenses \
  -H "Content-Type: application/json" \
  -d '{"expense_id":120,"title":"internet","amount":80,"category":"utility","date":"2026-06-22"}'
```

Example response:

```json
{
  "amount": 80,
  "category": "utility",
  "date": "2026-06-22",
  "expense_id": 120,
  "title": "internet"
}
```

## Test Status

The project includes automated tests for:

* Core expense tracker logic
* Flask API routes
* SQLite repository CRUD operations
* JSON-to-SQLite data migration
* Database isolation and duplicate handling

Current test result:

```text
Ran 92 tests

OK
```

## Future Improvements

* Upgrade from SQLite to PostgreSQL
* Move more filtering and report calculations into SQL
* Add user authentication and authorization
* Add Swagger/OpenAPI documentation
* Add Docker support
* Add continuous integration
* Add production deployment configuration

# Expense Tracker API

GitHub Repository: https://github.com/kevalpatel5011/expense-tracker-api

A Flask REST API for managing expenses with PostgreSQL persistence and Alembic database migrations.

## Portfolio Summary

This project demonstrates backend API development using Python, Flask, PostgreSQL, Psycopg, and Alembic. It includes RESTful routes, JSON request handling, input validation, filtering, sorting, pagination, reporting, parameterized SQL queries, database transactions, version-controlled schema migrations, automated testing, code-quality checks, and continuous integration with GitHub Actions.

## Features

* Add, view, update, and delete expenses
* Store expense data in PostgreSQL
* Manage database schema changes with Alembic
* Filter expenses by category, amount range, and date range
* Sort expenses by amount, date, title, or category
* Paginate results using limit and offset
* Generate summary, monthly, yearly, and category reports
* Use parameterized SQL queries through Psycopg
* Store monetary values using PostgreSQL `NUMERIC`
* Store dates using PostgreSQL `DATE`
* Reject duplicate expense IDs with a primary-key constraint
* Reject negative amounts with a database check constraint
* Use automatic commit, rollback, and connection cleanup
* Run isolated PostgreSQL integration tests
* Apply migrations and run quality checks through GitHub Actions
* Reuse PostgreSQL connections through a connection pool
* Package and run the API with Docker
* Run Flask, Alembic, and PostgreSQL with Docker Compose
* Serve Flask through the production Gunicorn WSGI server
* Run containers with a non-root user
* Verify Docker configuration and image builds in CI
* Document the API contract with OpenAPI 3.2

## Project Structure

```text
expense-tracker-api/
├── .github/
│   └── workflows/
│       └── tests.yml
├── migrations/
│   ├── versions/
│   │   └── 781b81c21abf_create_expenses_table.py
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── .gitignore
├── alembic.ini
├── .dockerignore
├── .env.example
├── Dockerfile
├── compose.yaml
├── app.py
├── config.py
├── database.py
├── expense_repository.py
├── postgres_database.py
├── postgres_expense_repository.py
├── expense_utils.py
├── Expense_Tracker_System.py
├── expenses.json
├── migrate_json_to_sqlite.py
├── openapi.yaml
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── tests/
    ├── test_app.py
    ├── test_expense_repository.py
    ├── test_expense_tracker.py
    ├── test_migration.py
    ├── test_postgres_database.py
    └── test_postgres_expense_repository.py
```

The Flask application uses PostgreSQL as its active database. Alembic migration files are the single source of truth for the PostgreSQL schema.

The SQLite repository and JSON-to-SQLite migration files are retained as previous implementation examples and for comparison with PostgreSQL. The generated `expenses.db` file is ignored by Git.

## Technologies Used

* Python
* Flask
* PostgreSQL 18
* Psycopg 3
* Psycopg connection pooling
* Alembic
* SQLAlchemy migration operations
* SQL
* Ruff
* Python `unittest`
* GitHub Actions
* Git and GitHub
* Docker
* Docker Compose
* Gunicorn
* OpenAPI 3.2 and openapi-spec-validator

## Database Design

The PostgreSQL `expenses` table contains:

| Column       | Type                     | Purpose                   |
| ------------ | ------------------------ | ------------------------- |
| `expense_id` | `INTEGER PRIMARY KEY`    | Unique expense identifier |
| `title`      | `TEXT NOT NULL`          | Expense title             |
| `amount`     | `NUMERIC(12,2) NOT NULL` | Accurate monetary value   |
| `category`   | `TEXT NOT NULL`          | Expense category          |
| `date`       | `DATE NOT NULL`          | Expense date              |

The database also enforces:

```sql
CHECK (amount >= 0)
```

This prevents negative expense amounts from being stored.

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

Install the application and development dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
```

## PostgreSQL Setup

Install PostgreSQL 18 and start the PostgreSQL server.

Create a restricted application role:

```bash
createuser \
  --login \
  --pwprompt \
  --no-superuser \
  --no-createdb \
  --no-createrole \
  expense_app
```

Create the development database:

```bash
createdb --owner=expense_app expense_tracker
```

Create the isolated test database:

```bash
createdb --owner=expense_app expense_tracker_test
```

## PostgreSQL Configuration

The application and Alembic read PostgreSQL connection settings from environment variables:

```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DATABASE=expense_tracker
export POSTGRES_USER=expense_app
read -s POSTGRES_PASSWORD
export POSTGRES_PASSWORD
```

Never commit a real database password to GitHub.

The default non-secret configuration is:

| Variable            | Default           |
| ------------------- | ----------------- |
| `POSTGRES_HOST`     | `localhost`       |
| `POSTGRES_PORT`     | `5432`            |
| `POSTGRES_DATABASE` | `expense_tracker` |
| `POSTGRES_USER`     | `expense_app`     |

`POSTGRES_PASSWORD` does not have a default and must be supplied through the environment.

## Database Migrations

Apply every missing migration before starting the application:

```bash
python3 -m alembic upgrade head
```

View the database’s current revision:

```bash
python3 -m alembic current
```

View the complete migration history:

```bash
python3 -m alembic history
```

Create a migration for a future schema change:

```bash
python3 -m alembic revision -m "describe the schema change"
```

After creating a revision, implement its `upgrade()` and `downgrade()` functions and test both directions on a disposable database.

The initial revision creates the PostgreSQL `expenses` table. Existing databases that already matched this schema were stamped once during Alembic adoption. New databases must use `alembic upgrade head`; they should not use `stamp` to skip unapplied migrations.

## Run the Application

Apply migrations first:

```bash
python3 -m alembic upgrade head
```

Start the Flask development server:

```bash
python3 app.py
```

The API runs at:

```text
http://127.0.0.1:5000
```

Stop the development server with `Control + C`.

When finished, remove the password from the current shell:

```bash
unset POSTGRES_PASSWORD
```

## Run with Docker

Create the local environment file:

```bash
cp .env.example .env
```

## Run Tests

Make sure PostgreSQL is running and `expense_tracker_test` exists.

Enter the PostgreSQL password and run the complete suite:

```bash
read -s POSTGRES_PASSWORD
export POSTGRES_PASSWORD
python3 -m unittest discover -s tests
unset POSTGRES_PASSWORD
```

The PostgreSQL tests temporarily switch to `expense_tracker_test`, apply the current Alembic migrations, and clear the `expenses` table before and after every test.

Never use a development or production database for automated tests.

## Run Code-Quality Checks

Run Ruff:

```bash
python3 -m ruff check .
```

Check for whitespace errors:

```bash
git diff --check
```

## Continuous Integration

GitHub Actions runs automatically on pushes to `main` and pull requests targeting `main`.

The workflow:

* Starts a temporary PostgreSQL 18 service
* Creates an isolated test database
* Installs application and development dependencies
* Validates the OpenAPI specification
* Applies all Alembic migrations
* Runs Ruff
* Runs the complete automated test suite
* Reports a successful or failed status check on the pull request
* Validates the Docker Compose configuration
* Builds the Docker image

The `main` branch requires the GitHub Actions test check to pass before merging.

## OpenAPI Documentation
* [`openapi.yaml`](openapi.yaml) contains the OpenAPI 3.2 API contract.
* It documents endpoints, parameters, request bodies, response bodies, and reusable schemas.
* Developers can validate it with:
```bash
python3 -m openapi_spec_validator openapi.yaml
```

## Example API Requests

Check API health:

```bash
curl http://127.0.0.1:5000/health
```

Get all expenses:

```bash
curl http://127.0.0.1:5000/expenses
```

Filter by category:

```bash
curl "http://127.0.0.1:5000/expenses?category=housing"
```

Filter by amount range:

```bash
curl "http://127.0.0.1:5000/expenses?min_amount=100&max_amount=2000"
```

## API Endpoints

| Method | Endpoint                             | Description                                                 |
| ------ | ------------------------------------ | ----------------------------------------------------------- |
| GET    | `/`                                  | Check whether the API is running                            |
| GET    | `/health`                            | Get the API health status                                   |
| GET    | `/expenses`                          | Get expenses with optional filters, sorting, and pagination |
| POST   | `/expenses`                          | Create an expense                                           |
| GET    | `/expenses/{expense_id}`             | Get an expense by ID                                        |
| PUT    | `/expenses/{expense_id}`             | Replace an existing expense                                 |
| PATCH  | `/expenses/{expense_id}`             | Update selected expense fields                              |
| DELETE | `/expenses/{expense_id}`             | Delete an expense                                           |
| GET    | `/expenses/summary`                  | Get an expense summary                                      |
| GET    | `/expenses/category/{category}`      | Get expenses by category                                    |
| GET    | `/expenses/date/{date}`              | Get expenses by date                                        |
| GET    | `/reports/monthly/{year}/{month}`    | Get a monthly expense report                                |
| GET    | `/reports/yearly/{year}`             | Get a yearly expense report                                 |
| GET    | `/reports/categories`                | Get a category summary                                      |
| GET    | `/reports/categories/{year}`         | Get a yearly category report                                |
| GET    | `/reports/categories/{year}/{month}` | Get a monthly category report                               |

## Create an Expense

```bash
curl -X POST http://127.0.0.1:5000/expenses \
  -H "Content-Type: application/json" \
  -d '{"expense_id":120,"title":"internet","amount":80,"category":"utility","date":"2026-06-22"}'
```

Example response:

```json
{
  "amount": 80.0,
  "category": "utility",
  "date": "2026-06-22",
  "expense_id": 120,
  "title": "internet"
}
```

## Update an Expense

```bash
curl -X PATCH http://127.0.0.1:5000/expenses/120 \
  -H "Content-Type: application/json" \
  -d '{"amount":85}'
```

## Delete an Expense

```bash
curl -X DELETE http://127.0.0.1:5000/expenses/120
```

## Test Status

The automated test suite covers:

* Core expense tracker logic
* Flask API routes
* SQLite repository behavior
* PostgreSQL repository CRUD operations
* PostgreSQL database constraints
* Alembic schema migration setup
* PostgreSQL connection-pool creation, borrowing, and cleanup
* Duplicate-ID rollback behavior
* Test database isolation
* JSON-to-SQLite migration behavior

Current local test result:

```text
Ran 105 tests

OK
```

## Future Improvements

* Move filtering, sorting, pagination, and reports into SQL queries
* Add user authentication and authorization
* Add an interactive Swagger UI for browsing and testing the API
* Add migration rollback tests to continuous integration
* Deploy the Dockerized API to a production hosting platform

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
EXPENSE_FILE = os.environ.get("EXPENSE_FILE", str(BASE_DIR / "expenses.json"))

DATABASE_FILE = os.environ.get("DATABASE_FILE", str(BASE_DIR / "expenses.db"))

POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", "5432"))
POSTGRES_DATABASE = os.environ.get("POSTGRES_DATABASE", "expense_tracker")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "expense_app")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
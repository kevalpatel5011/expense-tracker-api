import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
EXPENSE_FILE = os.environ.get("EXPENSE_FILE", str(BASE_DIR / "expenses.json"))

DATABASE_FILE = os.environ.get("DATABASE_FILE", str(BASE_DIR / "expenses.db"))

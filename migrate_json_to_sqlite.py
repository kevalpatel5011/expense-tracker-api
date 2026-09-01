import json
import sqlite3

from config import EXPENSE_FILE
from database import init_db
from expense_repository import insert_expense


def load_json_expenses():
    with open(EXPENSE_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise TypeError("JSON data must be a list")
    return data


def migrate_expenses():
    init_db()
    all_expenses = load_json_expenses()
    inserted_expenses = 0
    skipped_expenses = 0
    for expense in all_expenses:
        try:
            insert_expense(expense)
            inserted_expenses += 1
        except sqlite3.IntegrityError:
            skipped_expenses += 1
    return (inserted_expenses, skipped_expenses)


if __name__ == "__main__":
    inserted, skipped = migrate_expenses()
    print("inserted count:", inserted)
    print("skipped count:", skipped)

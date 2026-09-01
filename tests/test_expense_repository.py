import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from database import init_db
from expense_repository import (
    delete_expense_by_id,
    get_all_expenses,
    get_expense_by_id,
    insert_expense,
    update_expense_by_id,
)


class TestExpenseRepository(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db_path = str(Path(self.temp_dir.name) / "test_expenses.db")
        self.db_patcher = patch("database.DATABASE_FILE", self.test_db_path)
        self.db_patcher.start()
        init_db()

    def tearDown(self):
        self.db_patcher.stop()
        self.temp_dir.cleanup()

    def test_database_starts_empty(self):
        result = get_all_expenses()
        self.assertEqual(result, [])

    def test_insert_and_get_expense(self):
        expense = {
            "expense_id": 1100,
            "title": "rent",
            "amount": 1000.0,
            "category": "housing",
            "date": "2026-08-20"
            }
        insert_expense(expense)
        result = get_expense_by_id(expense["expense_id"])
        self.assertEqual(result, expense)

    def test_get_expense_by_id_returns_none_when_missing(self):
        result = get_expense_by_id(2000)
        self.assertIsNone(result)

    def test_get_all_expenses_orders_by_expense_id(self):
        expense_1 = {
            "expense_id": 2400,
            "title": "uber",
            "amount": 26.0,
            "category": "travel",
            "date": "2026-08-20"
            }
        expense_2 = {
            "expense_id": 2200,
            "title": "hospital fees",
            "amount": 240.0,
            "category": "medical",
            "date": "2026-08-21"
            }
        insert_expense(expense_1)
        insert_expense(expense_2)
        result = get_all_expenses()
        self.assertEqual(result, [expense_2, expense_1])

    def test_update_existing_expense(self):
        original_expense = {
            "expense_id": 2200,
            "title": "hospital fees",
            "amount": 240.0,
            "category": "medical",
            "date": "2026-08-21"
            }
        insert_expense(original_expense)
        update_data = {
            "title": "uber",
            "amount": 26.0,
            "category": "travel",
            "date": "2026-08-20"
            }
        update_result = update_expense_by_id(original_expense["expense_id"], update_data)
        stored_expense = get_expense_by_id(original_expense["expense_id"])
        expected_expense = {
            "expense_id": 2200,
            "title": "uber",
            "amount": 26.0,
            "category": "travel",
            "date": "2026-08-20"
            }
        self.assertTrue(update_result)
        self.assertEqual(stored_expense, expected_expense)

    def test_update_missing_expense_returns_false(self):
        update_data = {
            "title": "uber",
            "amount": 26.0,
            "category": "travel",
            "date": "2026-08-20"
            }
        update_result = update_expense_by_id(2300, update_data)
        found = get_expense_by_id(2300)
        self.assertFalse(update_result)
        self.assertIsNone(found)

    def test_delete_existing_expense(self):
        expense = {
            "expense_id": 2200,
            "title": "hospital fees",
            "amount": 240.0,
            "category": "medical",
            "date": "2026-08-21"
            }
        insert_expense(expense)
        delete_result = delete_expense_by_id(expense["expense_id"])
        stored_expense = get_expense_by_id(expense["expense_id"])
        self.assertTrue(delete_result)
        self.assertIsNone(stored_expense)

    def test_delete_missing_expense_preserves_existing_data(self):
        expense = {
            "expense_id": 2200,
            "title": "hospital fees",
            "amount": 240.0,
            "category": "medical",
            "date": "2026-08-21"
            }
        insert_expense(expense)
        delete_result = delete_expense_by_id(2000)
        stored_expense = get_expense_by_id(expense["expense_id"])
        self.assertFalse(delete_result)
        self.assertEqual(stored_expense, expense)

    def test_insert_duplicate_id_raises_integrity_error(self):
        expense = {
            "expense_id": 2200,
            "title": "hospital fees",
            "amount": 240.0,
            "category": "medical",
            "date": "2026-08-21"
            }
        insert_expense(expense)
        with self.assertRaises(sqlite3.IntegrityError):
            insert_expense(expense)
        result = get_expense_by_id(expense["expense_id"])
        self.assertEqual(result, expense)


if __name__ == "__main__":
    unittest.main()

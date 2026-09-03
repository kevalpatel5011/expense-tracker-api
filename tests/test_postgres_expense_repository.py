import unittest
from unittest.mock import patch

import psycopg

from postgres_database import get_postgres_connection, init_postgres_db
from postgres_expense_repository import (
    delete_expense_by_id,
    get_all_expenses,
    get_expense_by_id,
    insert_expense,
    update_expense_by_id,
)


class TestPostgresExpenseRepository(unittest.TestCase):
    def setUp(self):
        self.database_patcher = patch(
            "postgres_database.POSTGRES_DATABASE",
            "expense_tracker_test",
        )
        self.database_patcher.start()

        init_postgres_db()

        with get_postgres_connection() as connection:
            connection.execute("TRUNCATE TABLE expenses")

    def tearDown(self):
        with get_postgres_connection() as connection:
            connection.execute("TRUNCATE TABLE expenses")

        self.database_patcher.stop()

    def test_database_starts_empty(self):
        result = get_all_expenses()
        self.assertEqual(result, [])

    def test_insert_and_get_expense(self):
        expense = {
            "expense_id": 2200,
            "title": "hospital fees",
            "amount": 240.0,
            "category": "medical",
            "date": "2026-08-21"
        }
        insert_expense(expense)
        result = get_expense_by_id(expense["expense_id"])
        self.assertEqual(result, expense)

    def test_get_expense_by_id_returns_none_when_missing(self):
        result = get_expense_by_id(20)
        self.assertIsNone(result)

    def test_get_all_expenses_orders_by_expense_id(self):
        expense_1 = {
            "expense_id": 2400,
            "title": "bills",
            "amount": 100,
            "category": "utility",
            "date": "2026-06-10"
        }
        expense_2 = {
            "expense_id": 2200,
            "title": "hospital fees",
            "amount": 240,
            "category": "medical",
            "date": "2026-08-21"
        }
        insert_expense(expense_1)
        insert_expense(expense_2)
        result = get_all_expenses()
        self.assertEqual(result[0], expense_2)
        self.assertEqual(result[1], expense_1)

    def test_update_existing_expense(self):
        expense = {
            "expense_id": 2400,
            "title": "bills",
            "amount": 100,
            "category": "utility",
            "date": "2026-06-10"
        }
        insert_expense(expense)
        updated_expense = {
            "title": "hospital fees",
            "amount": 240,
            "category": "medical",
            "date": "2026-08-21"
        }
        update = update_expense_by_id(expense["expense_id"], updated_expense)
        self.assertTrue(update)
        result = get_expense_by_id(expense["expense_id"])
        self.assertEqual(result["title"], updated_expense["title"])
        self.assertEqual(result["amount"], updated_expense["amount"])
        self.assertEqual(result["date"], updated_expense["date"])
        self.assertEqual(result["category"], updated_expense["category"])

    def test_update_missing_expense_returns_false(self):
        update_expense = {
            "title": "hospital fees",
            "amount": 240,
            "category": "medical",
            "date": "2026-08-21"
        }
        update = update_expense_by_id(200, update_expense)
        self.assertFalse(update)
        self.assertIsNone(get_expense_by_id(200))

    def test_delete_existing_expense(self):
        expense = {
            "expense_id": 200,
            "title": "bills",
            "amount": 100,
            "category": "utility",
            "date": "2026-06-10"
        }
        insert_expense(expense)
        delete = delete_expense_by_id(expense["expense_id"])
        self.assertTrue(delete)
        result = get_expense_by_id(expense["expense_id"])
        self.assertIsNone(result)

    def test_delete_missing_expense_preserves_existing_data(self):
        expense = {
            "expense_id": 400,
            "title": "bills",
            "amount": 100,
            "category": "utility",
            "date": "2026-06-10"
        }
        insert_expense(expense)
        delete = delete_expense_by_id(500)
        self.assertFalse(delete)
        result = get_expense_by_id(expense["expense_id"])
        self.assertEqual(result, expense)

    def test_insert_duplicate_id_raises_integrity_error(self):
        expense = {
            "expense_id": 2200,
            "title": "hospital fees",
            "amount": 240.0,
            "category": "medical",
            "date": "2026-08-21",
        }

        insert_expense(expense)

        with self.assertRaises(psycopg.IntegrityError):
            insert_expense(expense)

        result = get_expense_by_id(expense["expense_id"])
        self.assertEqual(result, expense)

    def test_insert_negative_amount_raises_integrity_error(self):
        expense = {
            "expense_id": 2300,
            "title": "invalid expense",
            "amount": -10.0,
            "category": "testing",
            "date": "2026-09-03",
        }

        with self.assertRaises(psycopg.IntegrityError):
            insert_expense(expense)

        result = get_expense_by_id(expense["expense_id"])
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
import unittest
from unittest.mock import patch

import psycopg
from alembic import command
from alembic.config import Config

from postgres_database import get_postgres_connection
from postgres_expense_repository import (
    delete_expense_by_id,
    get_all_expenses,
    get_expense_by_id,
    insert_expense,
    search_expenses,
    update_expense_by_id,
)


class TestPostgresExpenseRepository(unittest.TestCase):
    def setUp(self):
        self.database_patcher = patch(
            "postgres_database.POSTGRES_DATABASE",
            "expense_tracker_test",
        )
        self.config_database_patcher = patch(
            "config.POSTGRES_DATABASE",
            "expense_tracker_test",
        )
        self.database_patcher.start()
        self.config_database_patcher.start()

        alembic_config = Config("alembic.ini")
        command.upgrade(alembic_config, "head")

        with get_postgres_connection() as connection:
            connection.execute("TRUNCATE TABLE expenses")

    def tearDown(self):
        with get_postgres_connection() as connection:
            connection.execute("TRUNCATE TABLE expenses")

        self.config_database_patcher.stop()
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

    def test_search_expenses_filters_by_category_case_insensitively(self):
        expense_1 = {
            "expense_id": 100,
            "title": "rent",
            "amount": 2200.0,
            "category": "housing",
            "date": "2026-09-03",
        }
        expense_2 = {
            "expense_id": 101,
            "title": "bill",
            "amount": 200.0,
            "category": "utility",
            "date": "2026-09-03",
        }
        expense_3 = {
            "expense_id": 110,
            "title": "tax",
            "amount": 100.0,
            "category": "housing",
            "date": "2026-09-03",
        }
        insert_expense(expense_1)
        insert_expense(expense_2)
        insert_expense(expense_3)
        result = search_expenses(category="HOUSING")

        self.assertEqual([expense["expense_id"] for expense in result],[100, 110])

    def test_search_expenses_filters_by_inclusive_amount_range(self):
        expense_1 = {
            "expense_id": 100,
            "title": "uber",
            "amount": 50.0,
            "category": "transport",
            "date": "2026-09-03",
        }
        expense_2 = {
            "expense_id": 101,
            "title": "bill",
            "amount": 100.0,
            "category": "utility",
            "date": "2026-09-05",
        }
        expense_3 = {
            "expense_id": 102,
            "title": "tax",
            "amount": 200.0,
            "category": "housing",
            "date": "2026-09-08",
        }
        expense_4 = {
            "expense_id": 103,
            "title": "water",
            "amount": 250.0,
            "category": "utility",
            "date": "2026-09-13",
        }
        insert_expense(expense_1)
        insert_expense(expense_2)
        insert_expense(expense_3)
        insert_expense(expense_4)
        result = search_expenses(min_amount=100, max_amount=200)

        self.assertEqual([expense["expense_id"] for expense in result],[101, 102])

    def test_search_expenses_filters_by_inclusive_date_range(self):
        expense_1 = {
            "expense_id": 100,
            "title": "uber",
            "amount": 50.0,
            "category": "transport",
            "date": "2026-05-31",
        }
        expense_2 = {
            "expense_id": 101,
            "title": "bill",
            "amount": 100.0,
            "category": "utility",
            "date": "2026-06-01",
        }
        expense_3 = {
            "expense_id": 102,
            "title": "tax",
            "amount": 200.0,
            "category": "housing",
            "date": "2026-06-30",
        }
        expense_4 = {
            "expense_id": 103,
            "title": "water",
            "amount": 250.0,
            "category": "utility",
            "date": "2026-07-01",
        }
        insert_expense(expense_1)
        insert_expense(expense_2)
        insert_expense(expense_3)
        insert_expense(expense_4)
        result = search_expenses(
            start_date="2026-06-01",
            end_date="2026-06-30",
        )

        self.assertEqual([expense["expense_id"] for expense in result],[101, 102])

    def test_search_expenses_combines_filters(self):
        expense_1 = {
            "expense_id": 100,
            "title": "uber",
            "amount": 150.0,
            "category": "housing",
            "date": "2026-06-15",
        }
        expense_2 = {
            "expense_id": 101,
            "title": "bill",
            "amount": 250.0,
            "category": "housing",
            "date": "2026-06-15",
        }
        expense_3 = {
            "expense_id": 102,
            "title": "tax",
            "amount": 150.0,
            "category": "utility",
            "date": "2026-06-15",
        }
        expense_4 = {
            "expense_id": 103,
            "title": "water",
            "amount": 150.0,
            "category": "housing",
            "date": "2026-07-01",
        }
        insert_expense(expense_1)
        insert_expense(expense_2)
        insert_expense(expense_3)
        insert_expense(expense_4)
        result = search_expenses(
            category="HOUSING",
            min_amount=100,
            max_amount=200,
            start_date="2026-06-01",
            end_date="2026-06-30",
        )

        self.assertEqual([expense["expense_id"] for expense in result],[100])

    def test_search_expenses_sorts_by_amount_descending(self):
        expense_1 = {
            "expense_id": 100,
            "title": "uber",
            "amount": 50.0,
            "category": "housing",
            "date": "2026-06-15",
        }
        expense_2 = {
            "expense_id": 101,
            "title": "bill",
            "amount": 300.0,
            "category": "housing",
            "date": "2026-06-15",
        }
        expense_3 = {
            "expense_id": 102,
            "title": "tax",
            "amount": 150.0,
            "category": "utility",
            "date": "2026-06-15",
        }
        insert_expense(expense_1)
        insert_expense(expense_2)
        insert_expense(expense_3)
        result = search_expenses(sort_by="amount", order="desc")

        self.assertEqual([expense["expense_id"] for expense in result],[101, 102, 100])

    def test_search_expenses_rejects_invalid_sort_field(self):
        with self.assertRaises(ValueError):
            search_expenses(sort_by="amount; DROP TABLE expenses")

    def test_search_expenses_rejects_invalid_sort_order(self):
        with self.assertRaises(ValueError):
            search_expenses(order="sideways")

    def test_search_expenses_applies_limit_and_offset(self):
        expense_1 = {
            "expense_id": 100,
            "title": "uber",
            "amount": 50.0,
            "category": "transport",
            "date": "2026-09-03",
        }
        expense_2 = {
            "expense_id": 101,
            "title": "bill",
            "amount": 100.0,
            "category": "utility",
            "date": "2026-09-05",
        }
        expense_3 = {
            "expense_id": 102,
            "title": "tax",
            "amount": 200.0,
            "category": "housing",
            "date": "2026-09-08",
        }
        expense_4 = {
            "expense_id": 103,
            "title": "water",
            "amount": 250.0,
            "category": "utility",
            "date": "2026-09-13",
        }
        insert_expense(expense_1)
        insert_expense(expense_2)
        insert_expense(expense_3)
        insert_expense(expense_4)
        result = search_expenses(limit=2, offset=1)

        self.assertEqual([expense["expense_id"] for expense in result],[101, 102])

    def test_search_expenses_rejects_nonpositive_limit(self):
        with self.assertRaises(ValueError):
            search_expenses(limit=0)

    def test_search_expenses_rejects_negative_offset(self):
        with self.assertRaises(ValueError):
            search_expenses(offset=-1)

    def test_search_expenses_applies_offset_without_limit(self):
        expense_1 = {
            "expense_id": 100,
            "title": "uber",
            "amount": 50.0,
            "category": "transport",
            "date": "2026-09-03",
        }
        expense_2 = {
            "expense_id": 101,
            "title": "bill",
            "amount": 100.0,
            "category": "utility",
            "date": "2026-09-05",
        }
        expense_3 = {
            "expense_id": 102,
            "title": "tax",
            "amount": 200.0,
            "category": "housing",
            "date": "2026-09-08",
        }
        expense_4 = {
            "expense_id": 103,
            "title": "water",
            "amount": 250.0,
            "category": "utility",
            "date": "2026-09-13",
        }
        insert_expense(expense_1)
        insert_expense(expense_2)
        insert_expense(expense_3)
        insert_expense(expense_4)
        result = search_expenses(offset=2)

        self.assertEqual([expense["expense_id"] for expense in result],[102, 103])

if __name__ == "__main__":
    unittest.main()
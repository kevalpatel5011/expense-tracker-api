import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from expense_repository import get_all_expenses
from migrate_json_to_sqlite import migrate_expenses


class TestMigration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "test_expenses.db")
        self.json_path = str(Path(self.temp_dir.name) / "test_expenses.json")
        self.sample_data = [
            {
                "expense_id": 100,
                "title": "rent",
                "amount": 1900,
                "category": "housing",
                "date": "2026-07-01"
            },
            {
                "expense_id": 101,
                "title": "bills",
                "amount": 100,
                "category": "utility",
                "date": "2026-06-10"
            }
        ]
        with open(self.json_path, "w", encoding="utf-8") as file:
            json.dump(self.sample_data, file)
        self.db_patcher = patch("database.DATABASE_FILE", self.db_path)
        self.json_patcher = patch("migrate_json_to_sqlite.EXPENSE_FILE", self.json_path)
        self.db_patcher.start()
        self.json_patcher.start()

    def tearDown(self):
        self.json_patcher.stop()
        self.db_patcher.stop()
        self.temp_dir.cleanup()

    def test_migration_inserts_json_expenses(self):
        inserted, skipped = migrate_expenses()
        result = get_all_expenses()
        self.assertEqual(inserted, 2)
        self.assertEqual(skipped, 0)
        self.assertEqual(result, self.sample_data)

    def test_repeated_migration_skips_duplicates(self):
        migrate_expenses()
        inserted, skipped = migrate_expenses()
        result = get_all_expenses()
        self.assertEqual(inserted, 0)
        self.assertEqual(skipped, 2)
        self.assertEqual(result, self.sample_data)

    def test_migration_rejects_non_list_json(self):
        invalid_data = {
            "expense_id": 100,
            "title": "rent",
            "amount": 1900,
            "category": "housing",
            "date": "2026-07-01"
        }
        with open(self.json_path, "w", encoding="utf-8") as file:
            json.dump(invalid_data, file)
        with self.assertRaisesRegex(ValueError, "JSON data must be a list"):
            migrate_expenses()
        self.assertEqual(get_all_expenses(), [])
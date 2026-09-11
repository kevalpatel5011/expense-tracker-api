import unittest
from unittest.mock import patch

from alembic import command
from alembic.config import Config

from postgres_database import get_postgres_connection

EXPENSE_QUERY_INDEXES = {
    "ix_expenses_date",
    "ix_expenses_amount",
    "ix_expenses_normalized_category",
}

class TestPostgresMigration(unittest.TestCase):
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

        self.alembic_config = Config("alembic.ini")
        command.upgrade(self.alembic_config, "head")

    def tearDown(self):
        command.upgrade(self.alembic_config, "head")

        self.config_database_patcher.stop()
        self.database_patcher.stop()

    def get_expense_index_names(self):
        query = """
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'expenses'
        """

        with get_postgres_connection() as connection:
            rows = connection.execute(query).fetchall()

        return {row["indexname"] for row in rows}

    def test_expense_query_indexes_are_created(self):
        index_names = self.get_expense_index_names()

        self.assertTrue(EXPENSE_QUERY_INDEXES.issubset(index_names))

    def test_expense_query_indexes_are_removed_by_downgrade(self):
        command.downgrade(self.alembic_config, "781b81c21abf")

        index_names = self.get_expense_index_names()

        self.assertTrue(EXPENSE_QUERY_INDEXES.isdisjoint(index_names))
        self.assertIn("expenses_pkey", index_names)

if __name__ == "__main__":
    unittest.main()
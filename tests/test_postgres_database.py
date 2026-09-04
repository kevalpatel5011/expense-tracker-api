import unittest
from unittest.mock import patch

from postgres_database import (
    close_postgres_pool,
    get_postgres_connection,
    get_postgres_pool,
)


class TestPostgresDatabase(unittest.TestCase):
    @patch("postgres_database.ConnectionPool")
    def test_get_postgres_pool_creates_only_one_pool(self, pool_class):
        expected_pool = pool_class.return_value

        with patch("postgres_database._postgres_pool", None):
            first_result = get_postgres_pool()
            second_result = get_postgres_pool()

        self.assertIs(first_result, expected_pool)
        self.assertIs(second_result, expected_pool)
        pool_class.assert_called_once()

    @patch("postgres_database.get_postgres_pool")
    def test_get_postgres_connection_borrows_from_pool(self, get_pool):
        expected_connection_context = object()
        pool = get_pool.return_value
        pool.connection.return_value = expected_connection_context

        result = get_postgres_connection()

        self.assertIs(result, expected_connection_context)
        pool.connection.assert_called_once_with()

    @patch("postgres_database._postgres_pool")
    def test_close_postgres_pool_closes_pool(self, pool):
        close_postgres_pool()

        pool.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
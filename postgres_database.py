import psycopg
from psycopg.rows import dict_row

from config import (
    POSTGRES_DATABASE,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)


def get_postgres_connection():
    return psycopg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DATABASE,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        row_factory=dict_row,
    )


def init_postgres_db():
    query = """
        CREATE TABLE IF NOT EXISTS expenses (
            expense_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            amount NUMERIC(12, 2) NOT NULL CHECK (amount >= 0),
            category TEXT NOT NULL,
            date DATE NOT NULL
        )
    """

    with get_postgres_connection() as connection:
        connection.execute(query)
import atexit

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from config import (
    POSTGRES_DATABASE,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)

_postgres_pool = None


def get_postgres_pool():
    global _postgres_pool

    if _postgres_pool is None:
        _postgres_pool = ConnectionPool(
            kwargs={
                "host": POSTGRES_HOST,
                "port": POSTGRES_PORT,
                "dbname": POSTGRES_DATABASE,
                "user": POSTGRES_USER,
                "password": POSTGRES_PASSWORD,
                "row_factory": dict_row,
            },
            min_size=1,
            max_size=5,
            timeout=10,
            open=True,
        )

    return _postgres_pool


def get_postgres_connection():
    return get_postgres_pool().connection()


def close_postgres_pool():
    if _postgres_pool is not None:
        _postgres_pool.close()


atexit.register(close_postgres_pool)
from datetime import date
from decimal import Decimal

from postgres_database import get_postgres_connection


def insert_expense(expense):
    query = """
        INSERT INTO expenses (expense_id, title, amount, category, date)
        VALUES (%s, %s, %s, %s, %s)
    """

    parameters = (
        expense["expense_id"],
        expense["title"],
        Decimal(str(expense["amount"])),
        expense["category"],
        date.fromisoformat(expense["date"]),
    )

    with get_postgres_connection() as connection:
        connection.execute(query, parameters)


def _serialize_expense(row):
    if row is None:
        return None
    row_dict = dict(row)

    if "amount" in row_dict and row_dict["amount"] is not None:
        row_dict["amount"] = float(row_dict["amount"])

    if "date" in row_dict and row_dict["date"] is not None:
        row_dict["date"] = row_dict["date"].isoformat()

    return row_dict


def get_expense_by_id(expense_id):
    query = """
    SELECT expense_id, title, amount, category, date
    FROM expenses
    WHERE expense_id = %s
    """
    parameters = (expense_id,)

    with get_postgres_connection() as connection:
        result = connection.execute(query, parameters).fetchone()
    return _serialize_expense(result)


def get_all_expenses():
    query = """
    SELECT expense_id, title, amount, category, date
    FROM expenses
    ORDER BY expense_id
    """

    with get_postgres_connection() as connection:
        rows = connection.execute(query).fetchall()
        expenses = [_serialize_expense(row) for row in rows]
    return expenses


def delete_expense_by_id(expense_id):
    query = """
    DELETE FROM expenses
    WHERE expense_id = %s
    """
    parameters = (expense_id,)

    with get_postgres_connection() as connection:
        cursor = connection.execute(query, parameters)
        deleted = cursor.rowcount == 1
    return deleted


def update_expense_by_id(expense_id, expense):
    query = """
    UPDATE expenses
    SET title = %s, amount = %s, category = %s, date = %s
    WHERE expense_id = %s
    """
    parameters = (
        expense["title"],
        Decimal(str(expense["amount"])),
        expense["category"],
        date.fromisoformat(expense["date"]),
        expense_id,
    )
    with get_postgres_connection() as connection:
        cursor = connection.execute(query, parameters)
        updated = cursor.rowcount == 1
    return updated

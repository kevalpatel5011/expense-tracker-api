from datetime import date
from decimal import Decimal

from psycopg import sql

from postgres_database import get_postgres_connection

SEARCH_SORT_FIELDS = {
    "expense_id",
    "title",
    "amount",
    "category",
    "date",
}

SEARCH_SORT_ORDERS = {"asc", "desc"}


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


def search_expenses(
        category=None,
        min_amount=None,
        max_amount=None,
        start_date=None,
        end_date=None,
        sort_by="expense_id",
        order="asc",
        limit=None,
        offset=0,
    ):
    query = """
    SELECT expense_id, title, amount, category, date
    FROM expenses
    """
    conditions = []
    parameters = []
    if category is not None:
        conditions.append("LOWER(category) = LOWER(%s)")
        parameters.append(category)
    if min_amount is not None and max_amount is not None:
        conditions.append("amount BETWEEN %s AND %s")
        parameters.extend([
            Decimal(str(min_amount)),
            Decimal(str(max_amount)),
        ])
    if start_date is not None and end_date is not None:
        conditions.append("date BETWEEN %s AND %s")
        parameters.extend([
            date.fromisoformat(start_date),
            date.fromisoformat(end_date),
        ])
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if sort_by not in SEARCH_SORT_FIELDS:
        raise ValueError("Invalid sort field")
    if order not in SEARCH_SORT_ORDERS:
        raise ValueError("Invalid sort order")
    if limit is not None and limit <= 0:
        raise ValueError("Invalid limit")
    if offset < 0:
        raise ValueError("Invalid offset")

    query = sql.SQL(query) + sql.SQL(" ORDER BY {} {}").format(
        sql.Identifier(sort_by),
        sql.SQL(order.upper()),
    )
    if limit is not None:
        query += sql.SQL(" LIMIT %s")
        parameters.append(limit)

    if offset > 0:
        query += sql.SQL(" OFFSET %s")
        parameters.append(offset)

    with get_postgres_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()
        expenses = [_serialize_expense(row) for row in rows]
    return expenses

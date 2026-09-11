from calendar import monthrange
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


def get_expense_summary():
    aggregate_query = """
    SELECT
        COUNT(*) AS count,
        COALESCE(SUM(amount), 0) AS total_amount,
        COALESCE(AVG(amount), 0) AS average_amount
    FROM expenses
    """

    highest_query = """
    SELECT expense_id, title, amount, category, date
    FROM expenses
    ORDER BY amount DESC, expense_id ASC
    LIMIT 1
    """

    lowest_query = """
    SELECT expense_id, title, amount, category, date
    FROM expenses
    ORDER BY amount ASC, expense_id ASC
    LIMIT 1
    """

    with get_postgres_connection() as connection:
        aggregate_row = connection.execute(aggregate_query).fetchone()
        highest_row = connection.execute(highest_query).fetchone()
        lowest_row = connection.execute(lowest_query).fetchone()

    summary = dict(aggregate_row)

    summary["total_amount"] = float(summary["total_amount"])
    summary["average_amount"] = float(summary["average_amount"])
    summary["highest_expense"] = _serialize_expense(highest_row)
    summary["lowest_expense"] = _serialize_expense(lowest_row)

    return summary

def get_category_summary():
    query = """
    SELECT
        LOWER(TRIM(category)) AS category,
        COUNT(*) AS count,
        SUM(amount) AS total_amount
    FROM expenses
    GROUP BY LOWER(TRIM(category))
    ORDER BY category
    """

    with get_postgres_connection() as connection:
        rows = connection.execute(query).fetchall()

    summary = {}

    for row in rows:
        row_dict = dict(row)
        summary[row_dict["category"]] = {
            "count": row_dict["count"],
            "total_amount": float(row_dict["total_amount"]),
        }

    return summary


def get_expense_report(start_date, end_date):
    parameters = []
    parameters.extend([
        date.fromisoformat(start_date),
        date.fromisoformat(end_date),
    ])
    query = """
    SELECT
        expense_id, title, amount, category, date,
        COUNT(*) OVER () AS report_count,
        SUM(amount) OVER () AS report_total
    FROM expenses
    WHERE date BETWEEN %s AND %s
    ORDER BY expense_id
    """

    with get_postgres_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()

    if not rows:
        return {}

    report = {
        "count": rows[0]["report_count"],
        "total_amount": float(rows[0]["report_total"]),
        "expenses": [],
    }

    for row in rows:
        row_dict = dict(row)
        row_dict.pop("report_count")
        row_dict.pop("report_total")
        report["expenses"].append(_serialize_expense(row_dict))

    return report


def get_monthly_report(year, month):
    if not isinstance(year, int) or not 1000 <= year <= 9999:
        return {}
    if not isinstance(month, int) or not 1 <= month <= 12:
        return {}
    first_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    last_date = date(year, month, last_day)

    return get_expense_report(
        first_date.isoformat(),
        last_date.isoformat(),
    )


def get_yearly_report(year):
    if not isinstance(year, int) or not 1000 <= year <= 9999:
        return {}
    first_date = date(year, 1, 1).isoformat()
    last_date = date(year, 12, 31).isoformat()

    return get_expense_report(first_date, last_date)


def get_category_report(start_date, end_date):
    parameters = []
    parameters.extend([
        date.fromisoformat(start_date),
        date.fromisoformat(end_date),
    ])
    query = """
    SELECT
        expense_id, title, amount, category, date,
        LOWER(TRIM(category)) AS normalized_category,
        COUNT(*) OVER (PARTITION BY LOWER(TRIM(category))) AS report_count,
        SUM(amount) OVER (PARTITION BY LOWER(TRIM(category))) AS report_total
    FROM expenses
    WHERE date BETWEEN %s AND %s
    ORDER BY expense_id
    """

    with get_postgres_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()

    if not rows:
        return {}

    report = {}

    for row in rows:
        row_dict = dict(row)
        category = row_dict.pop("normalized_category")
        count = row_dict.pop("report_count")
        total = float(row_dict.pop("report_total"))
        if category not in report:
            report[category] = {
                "count": count,
                "total_amount": total,
                "expenses": [],
            }
        report[category]["expenses"].append(_serialize_expense(row_dict))

    return report


def get_monthly_category_report(year, month):
    if not isinstance(year, int) or not 1000 <= year <= 9999:
        return {}
    if not isinstance(month, int) or not 1 <= month <= 12:
        return {}
    first_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    last_date = date(year, month, last_day)

    return get_category_report(
        first_date.isoformat(),
        last_date.isoformat(),
    )


def get_yearly_category_report(year):
    if not isinstance(year, int) or not 1000 <= year <= 9999:
        return {}
    first_date = date(year, 1, 1).isoformat()
    last_date = date(year, 12, 31).isoformat()

    return get_category_report(first_date, last_date)


def get_expenses_by_category(category):
    query = """
    SELECT expense_id, title, amount, category, date
    FROM expenses
    WHERE LOWER(TRIM(category)) = LOWER(TRIM(%s))
    ORDER BY expense_id
    """
    parameter = (category,)
    with get_postgres_connection() as connection:
        rows = connection.execute(query, parameter).fetchall()

    return [_serialize_expense(row) for row in rows]


def get_expenses_by_date(expense_date):
    query = """
    SELECT expense_id, title, amount, category, date
    FROM expenses
    WHERE date = %s
    ORDER BY expense_id
    """
    parameter = (date.fromisoformat(expense_date),)
    with get_postgres_connection() as connection:
        rows = connection.execute(query, parameter).fetchall()

    return [_serialize_expense(row) for row in rows]
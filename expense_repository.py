import sqlite3

from database import get_db_connection


def insert_expense(expense):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            '''
            INSERT INTO expenses (expense_id, title, amount, category, date)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                expense["expense_id"],
                expense["title"],
                expense["amount"],
                expense["category"],
                expense["date"],
            ),
        )
        connection.commit()
    except sqlite3.Error:
        connection.rollback()
        raise
    finally:
        connection.close()

def get_all_expenses():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        query = """
        SELECT expense_id, title, amount, category, date
        FROM expenses
        ORDER BY expense_id;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        expenses_list = [dict(row) for row in results]
        return expenses_list
    finally:
        connection.close()

def get_expense_by_id(expense_id):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        query = """
        SELECT expense_id, title, amount, category, date
        FROM expenses
        WHERE expense_id = ?
        """
        parameters = (expense_id,)
        cursor.execute(query, parameters)
        result = cursor.fetchone()
        if result is None:
            return None
        match = dict(result)
        return match
    finally:
        connection.close()

def delete_expense_by_id(expense_id):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        query = """
        DELETE FROM expenses
        WHERE expense_id = ?
        """
        parameters = (expense_id,)
        cursor.execute(query, parameters)
        result = cursor.rowcount
        connection.commit()
        return result == 1
    except sqlite3.Error:
        connection.rollback()
        raise
    finally:
        connection.close()

def update_expense_by_id(expense_id, expense):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        query = """
        UPDATE expenses
        SET title = ?, amount = ?, category = ?, date = ?
        WHERE expense_id = ?
        """
        parameters = (
            expense["title"],
            expense["amount"],
            expense["category"],
            expense["date"],
            expense_id,
            )
        cursor.execute(query, parameters)
        result = cursor.rowcount
        connection.commit()
        return result == 1
    except sqlite3.Error:
        connection.rollback()
        raise
    finally:
        connection.close()


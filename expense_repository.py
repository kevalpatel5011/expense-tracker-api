from database import get_db_connection


def insert_expense(expense):
    connection = get_db_connection()
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
    connection.close()

def get_all_expenses():
    connection = get_db_connection()
    cursor = connection.cursor()
    query = """
    SELECT expense_id, title, amount, category, date  
    FROM expenses 
    ORDER BY expense_id;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    expenses_list = [dict(row) for row in results]
    connection.close()
    return expenses_list

def get_expense_by_id(expense_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = """
    SELECT expense_id, title, amount, category, date  
    FROM expenses 
    WHERE expense_id = ?
    """
    parameters = (expense_id,)
    cursor.execute(query, parameters)
    result = cursor.fetchone()
    connection.close()
    if result is None:
        return None
    match = dict(result)
    return match

def delete_expense_by_id(expense_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = """
    DELETE FROM expenses
    WHERE expense_id = ?
    """
    parameters = (expense_id,)
    cursor.execute(query, parameters)
    result = cursor.rowcount
    connection.commit()
    connection.close()
    return result == 1

def update_expense_by_id(expense_id, expense):
    connection = get_db_connection()
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
    connection.close()
    return result == 1


from datetime import datetime

from Expense_Tracker_System import Expense


def validate_required_fields(data, required_fields):
    for field in required_fields:
        if field not in data:
            return field
    return None


def validate_allowed_fields(data, allowed_fields):
    for field in data:
        if field not in allowed_fields:
            return field
    return None


def apply_expense_updates(expense, data):
    if "title" in data:
        expense.title = data["title"]
    if "amount" in data:
        expense.amount = data["amount"]
    if "category" in data:
        expense.category = data["category"]
    if "date" in data:
        expense.date = data["date"]


def create_expense_from_data(data):
    return Expense(
        data["expense_id"],
        data["title"],
        data["amount"],
        data["category"],
        data["date"]
    )


def is_valid_date_format(date_value):
    try:
        datetime.strptime(date_value, "%Y-%m-%d") # noqa: DTZ007
        return True
    except ValueError:
        return False


REQUIRED_EXPENSE_FIELDS = ["expense_id", "title", "amount", "category", "date"]
REQUIRED_UPDATE_FIELDS = ["title", "amount", "category", "date"]
ALLOWED_UPDATE_FIELDS = ["title", "amount", "category", "date"]
ALLOWED_SORT_FIELDS = ["expense_id", "amount", "date", "title", "category"]
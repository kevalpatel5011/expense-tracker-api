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


def backup_expense(expense):
    return {
        "title": expense.title,
        "amount": expense.amount,
        "category": expense.category,
        "date": expense.date,
    }


def restore_expense(expense, backup):
    expense.title = backup["title"]
    expense.amount = backup["amount"]
    expense.category = backup["category"]
    expense.date = backup["date"]


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


def filter_by_category(expenses, category):
    filtered = []
    for expense in expenses:
        if expense["category"].lower() == category.lower():
            filtered.append(expense)
    return filtered


def filter_by_amount_range(expenses, min_amount, max_amount):
    filtered = []
    for expense in expenses:
        if min_amount <= expense["amount"] <= max_amount:
            filtered.append(expense)
    return filtered


def filter_by_date_range(expenses, start_date, end_date):
    filtered = []
    for expense in expenses:
        if start_date <= expense["date"] <= end_date:
            filtered.append(expense)
    return filtered


def sort_expenses(expenses, sort_by, order):
    if order == "asc":
        expenses.sort(key=lambda expense: expense[sort_by])
    else:
        expenses.sort(reverse=True, key=lambda expense: expense[sort_by])


def apply_pagination(expenses, offset, limit):
    if limit is not None:
        expenses = expenses[offset:offset + limit]
    return expenses


def build_category_summary(expenses):
    summary = {}
    for expense in expenses:
        category = expense["category"].strip().lower()
        if category not in summary:
            summary[category] = {
                "count": 0,
                "total_amount": 0,
            }
        summary[category]["count"] += 1
        summary[category]["total_amount"] += expense["amount"]
    return summary


def is_valid_date_format(date_value):
    try:
        datetime.strptime(date_value, "%Y-%m-%d") # noqa: DTZ007
        return True
    except ValueError:
        return False


REQUIRED_EXPENSE_FIELDS = ["expense_id", "title", "amount", "category", "date"]
REQUIRED_UPDATE_FIELDS = ["title", "amount", "category", "date"]
ALLOWED_UPDATE_FIELDS = ["title", "amount", "category", "date"]
ALLOWED_SORT_FIELDS = ["amount", "date", "title", "category"]
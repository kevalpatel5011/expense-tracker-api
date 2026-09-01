import sqlite3

from flask import Flask, jsonify, request

from database import init_db
from expense_repository import (
    delete_expense_by_id as delete_expense_by_id_from_db,
)
from expense_repository import (
    get_all_expenses,
    insert_expense,
)
from expense_repository import (
    get_expense_by_id as get_expense_by_id_from_db,
)
from expense_repository import (
    update_expense_by_id as update_expense_by_id_in_db,
)
from Expense_Tracker_System import ExpenseTracker
from expense_utils import (
    ALLOWED_SORT_FIELDS,
    ALLOWED_UPDATE_FIELDS,
    REQUIRED_EXPENSE_FIELDS,
    REQUIRED_UPDATE_FIELDS,
    apply_expense_updates,
    apply_pagination,
    build_category_summary,
    create_expense_from_data,
    filter_by_amount_range,
    filter_by_category,
    filter_by_date_range,
    is_valid_date_format,
    sort_expenses,
    validate_allowed_fields,
    validate_required_fields,
)

app = Flask(__name__)


# Helper functions
def error_response(message, status_code):
    return jsonify({
        "error": message
    }), status_code


def get_json_body():
    data = request.get_json(silent=True)
    if data is None:
        return None, error_response("JSON body is required", 400)
    return data, None


def parse_amount(value):
    try:
        return float(value), None
    except ValueError:
        return None, error_response("min_amount and max_amount must be numbers", 400)


def build_tracker_from_database():
    manager = ExpenseTracker()
    all_expenses = get_all_expenses()
    for expense in all_expenses:
        expense_obj = create_expense_from_data(expense)
        manager.add_expense(expense_obj)
    return manager


# Basic routes
@app.route("/")
def home():
    return "Expense Tracker API is running"


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "Expense Tracker API is running",
})


# Expense routes
@app.route("/expenses", methods=["GET", "POST"])
def expenses():
    if request.method == "GET":
        result = get_all_expenses()

        category = request.args.get("category")
        min_amount = request.args.get("min_amount")
        max_amount = request.args.get("max_amount")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        limit = request.args.get("limit")
        offset = request.args.get("offset")
        sort_by = request.args.get("sort_by")
        order = request.args.get("order")
        
        if category:
            result = filter_by_category(result, category)

        if (min_amount is None) != (max_amount is None):
            return error_response("Both min_amount and max_amount are required", 400)
        if min_amount and max_amount:
            min_amount, error = parse_amount(min_amount)
            if error:
                return error
            max_amount, error = parse_amount(max_amount)
            if error:
                return error
            result = filter_by_amount_range(result, min_amount, max_amount)

        if (start_date is None) != (end_date is None):
            return error_response("Both start_date and end_date are required", 400)
        if start_date and end_date:
            if not is_valid_date_format(start_date):
                return error_response("Date must be in YYYY-MM-DD format", 400)
            if not is_valid_date_format(end_date):
                return error_response("Date must be in YYYY-MM-DD format", 400)
            
            if start_date > end_date:
                return error_response("start_date must be before or equal to end_date", 400)
            result = filter_by_date_range(result, start_date, end_date)

        if order and not sort_by:
            return error_response("sort_by is required when order is provided", 400)
        if sort_by:
            if sort_by not in ALLOWED_SORT_FIELDS:
                return error_response("sort_by must be amount, date, title, or category", 400)
            if order is None:
                order = "asc"
            if order not in ["asc", "desc"]:
                return error_response("order must be asc or desc", 400)
            sort_expenses(result, sort_by, order)
        
        if limit is not None:
            try:
                limit = int(limit)
            except ValueError:
                return error_response("limit must be a number", 400)
            if limit <= 0:
                return error_response("limit must be greater than 0", 400)
        if offset is not None:
            try:
                offset = int(offset)
            except ValueError:
                return error_response("offset must be a number", 400)
            if offset < 0:
                return error_response("offset must be non-negative", 400)
        else:
            offset = 0
        result = apply_pagination(result, offset, limit)
        return jsonify(result)

    if request.method == "POST":
        data, error = get_json_body()
        if error:
            return error
        missing_field = validate_required_fields(data, REQUIRED_EXPENSE_FIELDS)
        if missing_field:
            return error_response(f"Missing field: {missing_field}", 400)
        expense = create_expense_from_data(data)
        if not expense.is_valid():
            return error_response("Invalid expense", 400)
        try:
            insert_expense(expense.get_details())
        except sqlite3.IntegrityError:
            return error_response("Invalid expense", 400)
        return jsonify(expense.get_details()), 201


@app.route("/expenses/summary")
def get_expense_summary():
    manager = build_tracker_from_database()
    return jsonify({
        "count": manager.get_expense_count(),
        "total_amount": manager.get_total_expense_amount(),
        "average_amount": manager.get_average_expense_amount(),
        "highest_expense": manager.get_highest_expense(),
        "lowest_expense": manager.get_lowest_expense(),
    })


@app.route("/expenses/<int:expense_id>")
def get_expense_by_id(expense_id):
    result = get_expense_by_id_from_db(expense_id)
    if result is not None:
        return jsonify(result)
    
    return error_response("Expense not found", 404)


@app.route("/expenses/category/<category>")
def expenses_by_category(category):
    manager = build_tracker_from_database()
    result = manager.get_expenses_by_category(category)
    return jsonify(result)


@app.route("/expenses/date/<date>")
def expenses_by_date(date):
    manager = build_tracker_from_database()
    result = manager.get_expenses_by_date(date)
    return jsonify(result)


@app.route("/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    remove = delete_expense_by_id_from_db(expense_id)
    if remove:
        return jsonify({
            "message": "Expense deleted successfully"
        }), 200
    return error_response("Expense not found", 404)


@app.route("/expenses/<int:expense_id>", methods=["PATCH"])
def patch_expense(expense_id):
    stored_expense = get_expense_by_id_from_db(expense_id)
    if stored_expense is None:
        return error_response("Expense not found", 404)
    data, error = get_json_body()
    if error:
        return error
    invalid_field = validate_allowed_fields(data, ALLOWED_UPDATE_FIELDS)
    if invalid_field:
        return error_response(f"Invalid field: {invalid_field}", 400)
    expense = create_expense_from_data(stored_expense)
    apply_expense_updates(expense, data)
    if not expense.is_valid():
        return error_response("Invalid expense", 400)
    updated = update_expense_by_id_in_db(expense_id, expense.get_details())
    if not updated:
        return error_response("Expense not found", 404)
    return jsonify(expense.get_details())


@app.route("/expenses/<int:expense_id>", methods=["PUT"])
def replace_expense(expense_id):
    stored_expense = get_expense_by_id_from_db(expense_id)
    if stored_expense is None:
        return error_response("Expense not found", 404)
    data, error = get_json_body()
    if error:
        return error
    missing_field = validate_required_fields(data, REQUIRED_UPDATE_FIELDS)
    if missing_field:
        return error_response(f"Missing field: {missing_field}", 400)
    expense = create_expense_from_data(stored_expense)
    apply_expense_updates(expense, data)
    if not expense.is_valid():
        return error_response("Invalid expense", 400)
    updated = update_expense_by_id_in_db(expense_id, expense.get_details())
    if not updated:
        return error_response("Expense not found", 404)
    return jsonify(expense.get_details())


# Report routes
@app.route("/reports/categories")
def get_report_by_category():
    all_expenses = get_all_expenses()
    if not all_expenses:
        return jsonify({})
    summary = build_category_summary(all_expenses)
    return jsonify(summary)


@app.route("/reports/categories/<int:year>/<int:month>")
def get_monthly_category_report(year, month):
    manager = build_tracker_from_database()
    return jsonify(manager.get_category_report_by_month(year, month))


@app.route("/reports/categories/<int:year>")
def get_yearly_category_report(year):
    manager = build_tracker_from_database()
    return jsonify(manager.get_category_report_by_year(year))


@app.route("/reports/monthly/<int:year>/<int:month>")
def get_monthly_report(year, month):
    manager = build_tracker_from_database()
    result = manager.get_monthly_report(year, month)
    return jsonify(result)


@app.route("/reports/yearly/<int:year>")
def get_yearly_report(year):
    manager = build_tracker_from_database()
    result = manager.get_yearly_report(year)
    return jsonify(result)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

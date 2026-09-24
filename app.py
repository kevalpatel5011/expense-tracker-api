import hmac
import time
from uuid import uuid4

import psycopg
from flask import Flask, g, jsonify, render_template, request, send_from_directory
from psycopg_pool import PoolTimeout

from config import API_KEY
from expense_utils import (
    ALLOWED_SORT_FIELDS,
    ALLOWED_UPDATE_FIELDS,
    REQUIRED_EXPENSE_FIELDS,
    REQUIRED_UPDATE_FIELDS,
    apply_expense_updates,
    create_expense_from_data,
    is_valid_date_format,
    validate_allowed_fields,
    validate_required_fields,
)
from postgres_database import check_postgres_connection
from postgres_expense_repository import (
    delete_expense_by_id as delete_expense_by_id_from_db,
)
from postgres_expense_repository import (
    get_category_summary,
    insert_expense,
    search_expenses,
)
from postgres_expense_repository import (
    get_expense_by_id as get_expense_by_id_from_db,
)
from postgres_expense_repository import (
    get_expense_summary as get_expense_summary_from_db,
)
from postgres_expense_repository import (
    get_expenses_by_category as get_expenses_by_category_from_db,
)
from postgres_expense_repository import (
    get_expenses_by_date as get_expenses_by_date_from_db,
)
from postgres_expense_repository import (
    get_monthly_category_report as get_monthly_category_report_from_db,
)
from postgres_expense_repository import (
    get_monthly_report as get_monthly_report_from_db,
)
from postgres_expense_repository import (
    get_yearly_category_report as get_yearly_category_report_from_db,
)
from postgres_expense_repository import (
    get_yearly_report as get_yearly_report_from_db,
)
from postgres_expense_repository import (
    update_expense_by_id as update_expense_by_id_in_db,
)

app = Flask(__name__)

app.config["API_KEY"] = API_KEY


@app.before_request
def begin_request_tracking():
    g.request_id = str(uuid4())
    g.request_started_at = time.perf_counter()


@app.after_request
def finish_request_tracking(response):
    duration_ms = (
        time.perf_counter() - g.request_started_at
    ) * 1000
    response.headers["X-Request-ID"] = g.request_id
    app.logger.info(
    (
        "Request completed request_id=%s method=%s "
        "path=%s status=%s duration_ms=%.2f"
    ),
    g.request_id,
    request.method,
    request.path,
    response.status_code,
    duration_ms,
    )
    return response


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


@app.errorhandler(psycopg.Error)
@app.errorhandler(PoolTimeout)
def handle_database_unavailable(error):
    app.logger.error(
        "Database operation failed request_id=%s",
        g.request_id,
        exc_info=(type(error), error, error.__traceback__),
    )
    return error_response("Database temporarily unavailable", 503)


@app.errorhandler(404)
def handle_not_found(_error):
    return error_response("Resource not found", 404)


@app.errorhandler(405)
def handle_method_not_allowed(_error):
    return error_response("Method not allowed", 405)


@app.errorhandler(500)
def handle_internal_server_error(error):
    original_error = getattr(error, "original_exception", error)

    app.logger.error(
        "Unexpected server error request_id=%s",
        g.request_id,
        exc_info=(
            type(original_error),
            original_error,
            original_error.__traceback__,
        ),
    )

    return error_response("Internal server error", 500)


def is_protected_path(path):
    return path in {"/expenses", "/reports"} or path.startswith(
        ("/expenses/", "/reports/")
    )


@app.before_request
def require_api_key():
    if not is_protected_path(request.path):
        return None
    configured_key = app.config.get("API_KEY")
    if not configured_key:
        return error_response("API authentication is not configured", 503)
    provided_key = request.headers.get("X-API-Key")
    if not provided_key or not hmac.compare_digest(provided_key, configured_key):
        return error_response("Invalid or missing API key", 401)
    return None


# Basic routes
@app.route("/")
def home():
    return "Expense Tracker API is running"


@app.route("/openapi.yaml")
def get_openapi_spec():
    return send_from_directory(
        app.root_path,
        "openapi.yaml",
        mimetype="application/yaml",
    )


@app.route("/docs")
def get_swagger_ui():
    return render_template("swagger_ui.html")


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "Expense Tracker API is running",
})


@app.route("/ready")
def readiness():
    try:
        check_postgres_connection()
    except (psycopg.Error, PoolTimeout):
        return jsonify({
            "status": "unavailable",
            "database": "disconnected",
        }), 503

    return jsonify({
        "status": "ready",
        "database": "connected",
    }), 200


# Expense routes
@app.route("/expenses", methods=["GET", "POST"])
def expenses():
    if request.method == "GET":

        category = request.args.get("category")
        min_amount = request.args.get("min_amount")
        max_amount = request.args.get("max_amount")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        limit = request.args.get("limit")
        offset = request.args.get("offset")
        sort_by = request.args.get("sort_by")
        order = request.args.get("order")
        
        if (min_amount is None) != (max_amount is None):
            return error_response("Both min_amount and max_amount are required", 400)
        if min_amount and max_amount:
            min_amount, error = parse_amount(min_amount)
            if error:
                return error
            max_amount, error = parse_amount(max_amount)
            if error:
                return error

        if (start_date is None) != (end_date is None):
            return error_response("Both start_date and end_date are required", 400)
        if start_date and end_date:
            if not is_valid_date_format(start_date):
                return error_response("Date must be in YYYY-MM-DD format", 400)
            if not is_valid_date_format(end_date):
                return error_response("Date must be in YYYY-MM-DD format", 400)
            
            if start_date > end_date:
                return error_response("start_date must be before or equal to end_date", 400)

        if order and not sort_by:
            return error_response("sort_by is required when order is provided", 400)
        if sort_by:
            if sort_by not in ALLOWED_SORT_FIELDS:
                return error_response(
                    "sort_by must be expense_id, amount, date, title, or category",
                    400,
                )
            if order is None:
                order = "asc"
            if order not in ["asc", "desc"]:
                return error_response("order must be asc or desc", 400)
        else:
            sort_by = "expense_id"
            order = "asc"
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

        result = search_expenses(
            category=category or None,
            min_amount=min_amount,
            max_amount=max_amount,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            order=order,
            limit=limit,
            offset=offset,
        )
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
        except psycopg.IntegrityError:
            return error_response("Invalid expense", 400)
        return jsonify(expense.get_details()), 201


@app.route("/expenses/summary")
def get_expense_summary():
    return jsonify(get_expense_summary_from_db())


@app.route("/expenses/<int:expense_id>")
def get_expense_by_id(expense_id):
    result = get_expense_by_id_from_db(expense_id)
    if result is not None:
        return jsonify(result)
    
    return error_response("Expense not found", 404)


@app.route("/expenses/category/<category>")
def expenses_by_category(category):
    return jsonify(get_expenses_by_category_from_db(category))


@app.route("/expenses/date/<date>")
def expenses_by_date(date):
    if not is_valid_date_format(date):
        return error_response("Date must be in YYYY-MM-DD format", 400)

    return jsonify(get_expenses_by_date_from_db(date))


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
    return jsonify(get_category_summary())


@app.route("/reports/categories/<int:year>/<int:month>")
def get_monthly_category_report(year, month):
    return jsonify(get_monthly_category_report_from_db(year, month))


@app.route("/reports/categories/<int:year>")
def get_yearly_category_report(year):
    return jsonify(get_yearly_category_report_from_db(year))


@app.route("/reports/monthly/<int:year>/<int:month>")
def get_monthly_report(year, month):
    return jsonify(get_monthly_report_from_db(year, month))


@app.route("/reports/yearly/<int:year>")
def get_yearly_report(year):
    return jsonify(get_yearly_report_from_db(year))


if __name__ == "__main__":
    app.run(debug=True)

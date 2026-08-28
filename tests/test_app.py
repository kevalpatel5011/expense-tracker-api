import unittest
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEST_EXPENSE_FILE = str(BASE_DIR / "test_expenses.json")

os.environ["EXPENSE_FILE"] = TEST_EXPENSE_FILE
# Set test file before importing app because app reads EXPENSE_FILE at import time.
from app import app, admin


class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        test_data = [
            {
                "expense_id": 100,
                "title": "rent",
                "amount": 1900,
                "category": "housing",
                "date": "2026-07-01"
            },
            {
                "expense_id": 101,
                "title": "bills",
                "amount": 100,
                "category": "utility",
                "date": "2026-06-10"
            },
            {
                "expense_id": 110,
                "title": "insurance",
                "amount": 1000,
                "category": "housing",
                "date": "2026-06-20"
            }
        ]

        with open(TEST_EXPENSE_FILE, "w") as file:
            json.dump(test_data, file, indent=4)
        admin.expenses = []
        admin.load_expenses_from_json(TEST_EXPENSE_FILE)

    def tearDown(self):
        if os.path.exists(TEST_EXPENSE_FILE):
            os.remove(TEST_EXPENSE_FILE)

    def make_expense(self, expense_id, amount=100):
        return {
            "expense_id": expense_id,
            "title": "test expense",
            "amount": amount,
            "category": "test",
            "date": "2026-08-20"
        }

    def create_expense(self, expense_id, amount=100):
        response = self.client.post("/expenses", json=self.make_expense(expense_id, amount))
        self.assertEqual(response.status_code, 201)
        return response

    def test_health(self):
        response = self.client.get("/health")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["message"], "Expense Tracker API is running")

    def test_get_expenses(self):
        response = self.client.get("/expenses")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_get_expense_by_existing_id(self):
        response = self.client.get("/expenses/100")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["expense_id"], 100)

    def test_get_expense_by_missing_id(self):
        response = self.client.get("/expenses/999999")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["error"], "Expense not found")

    def test_expense_summary(self):
        response = self.client.get("/expenses/summary")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], 3)
        self.assertEqual(data["total_amount"], 3000)
        self.assertIn("average_amount", data)
        self.assertIn("highest_expense", data)
        self.assertIn("lowest_expense", data)

    def test_get_expenses_filter_by_category(self):
        response = self.client.get("/expenses?category=housing")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

        for expense in data:
            self.assertEqual(expense["category"], "housing")

    def test_get_expenses_filter_by_missing_category(self):
        response = self.client.get("/expenses?category=food")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, [])

    def test_get_expenses_filter_by_amount_range(self):
        response = self.client.get("/expenses?min_amount=100&max_amount=1000")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 2)

        for expense in data:
            self.assertGreaterEqual(expense["amount"], 100)
            self.assertLessEqual(expense["amount"], 1000)

    def test_get_expenses_amount_filter_missing_max(self):
        response = self.client.get("/expenses?min_amount=100")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Both min_amount and max_amount are required")

    def test_get_expenses_filter_by_date_range(self):
        response = self.client.get("/expenses?start_date=2026-06-01&end_date=2026-06-30")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 2)

        for expense in data:
            self.assertGreaterEqual(expense["date"], "2026-06-01")
            self.assertLessEqual(expense["date"], "2026-06-30")

    def test_get_expenses_filter_invalid_date(self):
        response = self.client.get("/expenses?start_date=abc&end_date=2026-06-30")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Date must be in YYYY-MM-DD format")

    def test_get_expenses_sort_by_amount_asc(self):
        response = self.client.get("/expenses?sort_by=amount")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        amounts = []

        for expense in data:
            amounts.append(expense["amount"])
        self.assertEqual(amounts, sorted(amounts))

    def test_get_expenses_invalid_sort_by(self):
        response = self.client.get("/expenses?sort_by=expense_id")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "sort_by must be amount, date, title, or category"
        )

    def test_get_expenses_pagination_limit(self):
        response = self.client.get("/expenses?limit=2")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 2)

    def test_get_expenses_invalid_limit(self):
        response = self.client.get("/expenses?limit=0")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "limit must be greater than 0")

    def test_create_expense(self):
        self.client.delete("/expenses/9991")
        # Use high IDs so tests do not conflict with normal expenses.
        new_expense = self.make_expense(9991, 25)
        response = self.client.post("/expenses", json=new_expense)
        data = response.get_json()

        try:
            self.assertEqual(response.status_code, 201)
            self.assertEqual(data["expense_id"], 9991)
        finally:
            self.client.delete("/expenses/9991")

    def test_create_expense_missing_json_body(self):
        response = self.client.post("/expenses")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "JSON body is required")

    def test_create_expense_missing_field(self):
        response = self.client.post("/expenses", json={
            "title": "coffee"
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Missing field: expense_id")

    def test_delete_existing_expense(self):
        self.client.delete("/expenses/9992")
        self.create_expense(9992)
        try:
            delete_response = self.client.delete("/expenses/9992")
            data = delete_response.get_json()

            self.assertEqual(delete_response.status_code, 200)
            self.assertEqual(data["message"], "Expense deleted successfully")
        finally:
            self.client.delete("/expenses/9992")

    def test_delete_missing_expense(self):
        response = self.client.delete("/expenses/999999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"], "Expense not found")

    def test_patch_expense_amount(self):
        self.client.delete("/expenses/9993")
        self.create_expense(9993)
        response = self.client.patch("/expenses/9993", json={"amount": 99})
        data = response.get_json()

        try:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["amount"], 99)
        finally:
            self.client.delete("/expenses/9993")

    def test_patch_expense_invalid_field(self):
        self.client.delete("/expenses/9994")
        self.create_expense(9994)
        response = self.client.patch("/expenses/9994", json={"expense_id": 1})
        data = response.get_json()
        try:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data["error"], "Invalid field: expense_id")
        finally:
            self.client.delete("/expenses/9994")

    def test_put_expense_replace_data(self):
        self.client.delete("/expenses/9995")
        self.create_expense(9995)
        update = {
            "title": "updated expense",
            "amount": 120,
            "category": "updated",
            "date": "2026-08-21"
        }
        response = self.client.put("/expenses/9995", json=update)
        data = response.get_json()
        try:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["title"], "updated expense")
            self.assertEqual(data["amount"], 120)
        finally:
            self.client.delete("/expenses/9995")

    def test_put_expense_missing_field(self):
        self.client.delete("/expenses/9996")
        self.create_expense(9996)
        update = {
            "title": "updated expense",
            "amount": 120
        }
        response = self.client.put("/expenses/9996", json=update)
        data = response.get_json()
        try:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data["error"], "Missing field: category")
        finally:
            self.client.delete("/expenses/9996")

    def test_put_expense_invalid_amount(self):
        self.client.delete("/expenses/9997")
        self.create_expense(9997)
        update = {
            "title": "updated expense",
            "amount": -10,
            "category": "updated",
            "date": "2026-08-21"
        }
        response = self.client.put("/expenses/9997", json=update)
        data = response.get_json()
        try:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data["error"], "Invalid expense")
        finally:
            self.client.delete("/expenses/9997")

    def test_patch_expense_invalid_amount(self):
        self.client.delete("/expenses/9998")
        self.create_expense(9998, 25)
        response = self.client.patch("/expenses/9998", json={"amount": -10})
        data = response.get_json()
        try:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data["error"], "Invalid expense")
            get_response = self.client.get("/expenses/9998")
            get_data = get_response.get_json()
            self.assertEqual(get_response.status_code, 200)
            self.assertEqual(get_data["amount"], 25)
        finally:
            self.client.delete("/expenses/9998")

    def test_category_report(self):
        response = self.client.get("/reports/categories")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("housing", data)
        self.assertIn("utility", data)
        self.assertEqual(data["housing"]["count"], 2)

    def test_monthly_category_report(self):
        response = self.client.get("/reports/categories/2026/6")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("housing", data)
        self.assertIn("utility", data)

    def test_yearly_category_report(self):
        response = self.client.get("/reports/categories/2026")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("housing", data)
        self.assertEqual(data["housing"]["total_amount"], 2900)

    def test_patch_missing_expense(self):
        response = self.client.patch("/expenses/999999", json={"amount": 50})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"], "Expense not found")

    def test_put_missing_expense(self):
        response = self.client.put("/expenses/999999", json={
            "title": "missing",
            "amount": 50,
            "category": "test",
            "date": "2026-08-21"
        })
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"], "Expense not found")

    def test_patch_missing_json_body(self):
        response = self.client.patch("/expenses/100")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "JSON body is required")

    def test_put_missing_json_body(self):
        response = self.client.put("/expenses/100")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "JSON body is required")

    def test_create_expense_invalid_amount(self):
        self.client.delete("/expenses/9999")
        new_expense = self.make_expense(9999, -10)
        response = self.client.post("/expenses", json=new_expense)
        data = response.get_json()
        try:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data["error"], "Invalid expense")
        finally:
            self.client.delete("/expenses/9999")

    def test_create_duplicate_expense_id(self):
        new_expense = self.make_expense(100, 1000)
        response = self.client.post("/expenses", json=new_expense)
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "Invalid expense")

    def test_get_expenses_combined_category_and_amount_filter(self):
        response = self.client.get("/expenses?category=housing&min_amount=1000&max_amount=2000")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)
        for expense in data:
            self.assertEqual(expense["category"], "housing")
            self.assertGreaterEqual(expense["amount"], 1000)
            self.assertLessEqual(expense["amount"], 2000)

    def test_get_expenses_combined_category_and_date_filter(self):
        response = self.client.get("/expenses?category=housing&start_date=2026-06-01&end_date=2026-06-30")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        for expense in data:
            self.assertEqual(expense["expense_id"], 110)

    def test_get_expenses_sort_and_limit(self):
        response = self.client.get("/expenses?sort_by=amount&order=desc&limit=1")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["amount"], 1900)

    def test_get_expenses_pagination_offset_and_limit(self):
        response = self.client.get("/expenses?sort_by=amount&offset=1&limit=1")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["amount"], 1000)

    def test_get_expenses_invalid_offset(self):
        response = self.client.get("/expenses?offset=-1&limit=1")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "offset must be non-negative")

    def test_get_expenses_order_without_sort_by(self):
        response = self.client.get("/expenses?order=desc")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"], "sort_by is required when order is provided")

    def test_get_expenses_invalid_sort_order(self):
        response = self.client.get("/expenses?sort_by=amount&order=random")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "order must be asc or desc")

    def test_get_expenses_invalid_amount_query(self):
        response = self.client.get("/expenses?min_amount=abc&max_amount=100")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "min_amount and max_amount must be numbers")

    def test_get_expenses_start_date_after_end_date(self):
        response = self.client.get("/expenses?start_date=2026-07-01&end_date=2026-06-01")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "start_date must be before or equal to end_date")

    def test_get_expenses_invalid_limit_type(self):
        response = self.client.get("/expenses?limit=abc")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "limit must be a number")

    def test_get_expenses_invalid_offset_type(self):
        response = self.client.get("/expenses?offset=abc&limit=1")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "offset must be a number")

    def test_expenses_by_category_route(self):
        response = self.client.get("/expenses/category/housing")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)
        for expense in data:
            self.assertEqual(expense["category"], "housing")

    def test_expenses_by_date_route(self):
        response = self.client.get("/expenses/date/2026-06-10")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["expense_id"], 101)

    def test_monthly_report_route(self):
        response = self.client.get("/reports/monthly/2026/6")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], 2)
        self.assertEqual(data["total_amount"], 1100)

    def test_yearly_report_route(self):
        response = self.client.get("/reports/yearly/2026")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], 3)
        self.assertEqual(data["total_amount"], 3000)

    def test_expenses_by_date_route_no_match(self):
        response = self.client.get("/expenses/date/2026-01-01")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, [])

    def test_expenses_by_category_route_no_match(self):
        response = self.client.get("/expenses/category/food")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, [])

    def test_monthly_report_invalid_month(self):
        response = self.client.get("/reports/monthly/2026/13")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {})

    def test_yearly_report_no_match(self):
        response = self.client.get("/reports/yearly/2025")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {})

    def test_category_report_by_month_no_match(self):
        response = self.client.get("/reports/categories/2025/1")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {})

    def test_category_report_by_year_no_match(self):
        response = self.client.get("/reports/categories/2025")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {})

    def test_create_expense_invalid_title(self):
        post_data = self.make_expense(2000)
        post_data["title"] = " "
        response = self.client.post("/expenses", json=post_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Invalid expense")

    def test_create_expense_invalid_date(self):
        post_data = self.make_expense(2001)
        post_data["date"] = "2026-99-01"
        response = self.client.post("/expenses", json=post_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Invalid expense")

    def test_patch_expense_invalid_date(self):
        self.create_expense(3000)
        response = self.client.patch("/expenses/3000", json={"date": "2026-99-01"})
        try:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()["error"], "Invalid expense")
            get_response = self.client.get("/expenses/3000")
            self.assertEqual(get_response.get_json()["date"], "2026-08-20")
        finally:
            self.client.delete("/expenses/3000")

    def test_put_expense_invalid_date(self):
        self.create_expense(2100)
        update = {
            "title": "updated expense",
            "amount": 120,
            "category": "updated",
            "date": "2026-99-21"
        }
        response = self.client.put("/expenses/2100", json=update)
        try:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()["error"], "Invalid expense")
        finally:
            self.client.delete("/expenses/2100")

    def test_get_expenses_category_case_insensitive(self):
        response = self.client.get("/expenses?category=HOUSING")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)
        for expense in data:
            self.assertEqual(expense["category"], "housing")

    def test_get_expenses_amount_range_no_match(self):
        response = self.client.get("/expenses?min_amount=4000&max_amount=5000")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, [])

    def test_get_expenses_date_range_no_match(self):
        response = self.client.get("/expenses?start_date=2022-06-01&end_date=2022-06-30")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, [])

    def test_get_expenses_sort_by_date_desc(self):
        response = self.client.get("/expenses?sort_by=date&order=desc")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data[0]["date"], "2026-07-01")

    def test_home_route(self):
        response = self.client.get("/")
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, "Expense Tracker API is running")


if __name__ == "__main__":
    unittest.main()
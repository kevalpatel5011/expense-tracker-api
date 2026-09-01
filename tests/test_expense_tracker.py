import os
import tempfile
import unittest

from Expense_Tracker_System import Expense, ExpenseTracker


class TestExpenseTracker(unittest.TestCase):
    def setUp(self):
        self.admin = ExpenseTracker()
        self.expense1 = Expense(11, "water bill", 50, "utilities", "2026-05-23")
        self.expense2 = Expense(13, "electricity bill", 150, "utilities", "2026-06-10")
        self.expense3 = Expense(15, "lunch", 300, "food", "2026-06-20")
        self.expense4 = Expense(17, " ", 150, "utilities", "2026-05-23")
        self.duplicate_expense = Expense(11, "gas bill", 90, "utilities", "2026-06-01")

    def test_add_valid_expense(self):
        result = self.admin.add_expense(self.expense1)

        self.assertTrue(result)
        self.assertEqual(self.admin.get_expense_count(), 1)

    def test_add_invalid_expense(self):
        result = self.admin.add_expense(self.expense4)

        self.assertFalse(result)
        self.assertEqual(self.admin.get_expense_count(), 0)

    def test_add_duplicate_expense_id(self):
        result1 = self.admin.add_expense(self.expense1)
        result2 = self.admin.add_expense(self.duplicate_expense)

        self.assertTrue(result1)
        self.assertFalse(result2)
        self.assertEqual(self.admin.get_expense_count(), 1)

    def test_get_total_expense_amount(self):
        self.admin.add_expense(self.expense1)
        self.admin.add_expense(self.expense2)

        self.assertEqual(self.admin.get_total_expense_amount(), 200)

    def test_get_expenses_by_category(self):
        self.admin.add_expense(self.expense1)
        self.admin.add_expense(self.expense2)
        self.admin.add_expense(self.expense3)
        result = self.admin.get_expenses_by_category("utilities")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["category"], "utilities")   

    def test_remove_expense_by_id(self):
        self.admin.add_expense(self.expense3)

        self.assertTrue(self.admin.remove_expense_by_id(15))
        self.assertEqual(self.admin.get_expense_count(), 0)
        self.assertFalse(self.admin.remove_expense_by_id(15))

    def test_get_highest_and_lowest_expense(self):
        self.admin.add_expense(self.expense1)
        self.admin.add_expense(self.expense2)
        self.admin.add_expense(self.expense3)
        high = self.admin.get_highest_expense()
        low = self.admin.get_lowest_expense()

        self.assertEqual(high["amount"], 300)
        self.assertEqual(low["amount"], 50)

    def test_get_average_expense_amount(self):
        self.admin.add_expense(self.expense1)
        self.admin.add_expense(self.expense2)
        zero = ExpenseTracker()

        average1 = self.admin.get_average_expense_amount()
        average2 = zero.get_average_expense_amount()

        self.assertEqual(average1, 100)
        self.assertEqual(average2, 0)

    def test_get_expenses_between_amounts(self):
        self.admin.add_expense(self.expense1)
        self.admin.add_expense(self.expense2)
        self.admin.add_expense(self.expense3)
        result = self.admin.get_expenses_between_amounts(100, 200)
        invalid = self.admin.get_expenses_between_amounts(300, 100)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["amount"], 150)
        self.assertEqual(invalid, [])

    def test_get_expenses_by_date(self):
        self.admin.add_expense(self.expense1)
        self.admin.add_expense(self.expense2)
        self.admin.add_expense(self.expense3)
        result = self.admin.get_expenses_by_date("2026-06-10")
        invalid = self.admin.get_expenses_by_date(" ")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["date"], "2026-06-10")
        self.assertEqual(invalid, [])
        
    def test_get_total_by_date(self):
        self.admin.add_expense(self.expense1)
        self.admin.add_expense(self.expense2)
        self.admin.add_expense(self.expense3)
        result = self.admin.get_total_by_date("2026-06-10")
        invalid = self.admin.get_total_by_date(" ")

        self.assertEqual(result, 150)
        self.assertEqual(invalid, 0)


    def test_get_expenses_between_dates(self):
        self.admin.add_expense(self.expense1)
        self.admin.add_expense(self.expense2)
        self.admin.add_expense(self.expense3)
        result = self.admin.get_expenses_between_dates("2026-06-01", "2026-06-30")
        invalid = self.admin.get_expenses_between_dates("2026-07-01", "2026-06-01")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["date"], "2026-06-10")
        self.assertEqual(invalid, [])

    def test_get_total_between_dates(self):
        self.admin.add_expense(self.expense1)
        self.admin.add_expense(self.expense2)
        self.admin.add_expense(self.expense3)
        result = self.admin.get_total_between_dates("2026-06-01", "2026-06-30")
        invalid = self.admin.get_total_between_dates("", "")

        self.assertEqual(result, 450)
        self.assertEqual(invalid, 0)

    def test_get_monthly_report(self):
        self.admin.add_expense(self.expense3)
        self.admin.add_expense(self.expense2)
        self.admin.add_expense(self.expense1)

        report = self.admin.get_monthly_report(2026, 6)
        result = self.admin.get_monthly_report(2026, 13)

        self.assertEqual(report["count"], 2)
        self.assertEqual(report["total_amount"], 450)
        self.assertEqual(len(report["expenses"]), 2)
        self.assertEqual(result, {})


    def test_csv_save_and_load(self):
        self.admin.add_expense(self.expense1)
        self.admin.add_expense(self.expense3)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as temp_file:
            filename = temp_file.name
        save = self.admin.save_expenses_to_csv(filename)
        new_admin = ExpenseTracker()
        load = new_admin.load_expenses_from_csv(filename)

        self.assertTrue(save)
        self.assertEqual(load, 2)
        self.assertEqual(new_admin.get_expense_count(), 2)

        os.remove(filename)
        
if __name__ == "__main__":
    unittest.main()
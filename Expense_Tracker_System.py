import json
from datetime import datetime


class Expense:

    def __init__(self, expense_id, title, amount, category, date):
        self.expense_id = expense_id
        self.title = title
        self.amount = amount
        self.category = category
        self.date = date

    def get_details(self) -> dict:
        return {
            "expense_id": self.expense_id,
            "title": self.title,
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
        }

    def is_valid(self) -> bool:
        if not (isinstance(self.expense_id, int) and self.expense_id > 0):
            return False
        if not (isinstance(self.title, str) and self.title.strip() != ""):
            return False
        if not (isinstance(self.amount, (int, float)) and self.amount >= 0):
            return False
        if not (isinstance(self.category, str) and self.category.strip() != ""):
            return False
        if not (isinstance(self.date, str) and self.date.strip() != ""):
            return False
        try:
            datetime.strptime(self.date, "%Y-%m-%d") # noqa: DTZ007
        except ValueError:
            return False
        return True


class ExpenseTracker:

    def __init__(self):
        self.expenses = []

    def add_expense(self, expense) -> bool:
        if not isinstance(expense, Expense):
            return False
        if not expense.is_valid():
            return False
        if self.expense_exists(expense.expense_id):
            return False
        self.expenses.append(expense)
        return True
        
    
    def get_expense_count(self) -> int:
        return len(self.expenses)

    def get_all_expense_details(self) -> list:
        expense_details = []
        for expense in self.expenses:
            expense_details.append(expense.get_details())
        return expense_details

    def find_expense_by_id(self, expense_id) -> Expense | None:
        for expense in self.expenses:
            if expense.expense_id == expense_id:
                return expense
        return None

    def expense_exists(self, expense_id) -> bool:
        found = self.find_expense_by_id(expense_id)
        return found is not None

    def get_expense_details_by_id(self, expense_id) -> dict | None:
        found = self.find_expense_by_id(expense_id)
        if not found:
            return None
        return found.get_details()

    def update_expense_title(self, expense_id, new_title) -> bool:
        found = self.find_expense_by_id(expense_id)
        if not found:
            return False
        if not (isinstance(new_title, str) and new_title.strip() != ""):
            return False
        found.title = new_title
        return True

    def update_expense_amount(self, expense_id, new_amount) -> bool:
        found = self.find_expense_by_id(expense_id)
        if not found:
            return False
        if not (isinstance(new_amount, (int, float)) and new_amount >= 0):
            return False
        found.amount = new_amount
        return True

    def update_expense_category(self, expense_id, new_category) -> bool:
        found = self.find_expense_by_id(expense_id)
        if not found:
            return False
        if not (isinstance(new_category, str) and new_category.strip() != ""):
            return False
        found.category = new_category
        return True

    def remove_expense_by_id(self, expense_id) -> bool:
        found = self.find_expense_by_id(expense_id)
        if not found:
            return False
        self.expenses.remove(found)
        return True

    def get_total_expense_amount(self) -> int | float:
        total = 0
        for expense in self.expenses:
            total += expense.amount
        return total

    def get_expenses_by_category(self, category) -> list:
        found = []
        if not (isinstance(category, str) and category.strip() != ""):
            return []
        for expense in self.expenses:
            if expense.category.strip().lower() == category.strip().lower():
                found.append(expense.get_details())
        return found

    def get_total_by_category(self, category) -> int | float:
        total = 0
        if not (isinstance(category, str) and category.strip() != ""):
            return 0
        for expense in self.expenses:
            if expense.category.strip().lower() == category.strip().lower():
                total += expense.amount
        return total

    def get_count_by_category(self, category) -> int:
        return len(self.get_expenses_by_category(category))

    def get_highest_expense(self) -> dict | None:
        if not self.expenses:
            return None
        highest = self.expenses[0]
        for expense in self.expenses:
            if expense.amount > highest.amount:
                highest = expense
        return highest.get_details()

    def get_lowest_expense(self) -> dict | None:
        if not self.expenses:
            return None
        lowest = self.expenses[0]
        for expense in self.expenses:
            if expense.amount < lowest.amount:
                lowest = expense
        return lowest.get_details()

    def get_expenses_above_amount(self, amount) -> list:
        if not (isinstance(amount, (int, float)) and amount >= 0):
            return []
        found = []
        for expense in self.expenses:
            if expense.amount > amount:
                found.append(expense.get_details())
        return found

    def get_expenses_below_amount(self, amount) -> list:
        if not (isinstance(amount, (int, float)) and amount >= 0):
            return []
        found = []
        for expense in self.expenses:
            if expense.amount < amount:
                found.append(expense.get_details())
        return found

    def get_category_summary(self) -> dict:
        summary = {}
        for expense in self.expenses:
            category = expense.category.strip().lower()
            if category not in summary:
                summary[category] = 0
            summary[category] += expense.amount
        return summary

    def get_all_categories(self) -> list:
        all_categories = []
        for expense in self.expenses:
            if expense.category not in all_categories:
                all_categories.append(expense.category)
        return all_categories

    def has_expenses(self) -> bool:
        return bool(self.expenses)

    def get_average_expense_amount(self) -> int | float:
        if not self.has_expenses():
            return 0
        total = self.get_total_expense_amount() / len(self.expenses)
        return total

    def search_expenses_by_title(self, keyword) -> list:
        result = []
        if not (isinstance(keyword, str) and keyword.strip() != ""):
            return []
        for expense in self.expenses:
            if keyword.strip().lower() in expense.title.lower():
                result.append(expense.get_details())
        return result

    def get_expenses_sorted_high_to_low(self) -> list:
        all_expenses = self.get_all_expense_details().copy()
        all_expenses.sort(reverse = True, key=lambda expense: expense["amount"])
        return all_expenses

    def get_expenses_sorted_low_to_high(self) -> list:
        all_expenses = self.get_all_expense_details().copy()
        all_expenses.sort(key=lambda expense: expense["amount"])
        return all_expenses

    def clear_all_expenses(self) -> bool:
        self.expenses.clear()
        return True

    def get_expenses_between_amounts(self, min_amount, max_amount) -> list:
        result = []
        if not (isinstance(min_amount, (int, float)) and min_amount >= 0):
            return []
        if not (isinstance(max_amount, (int, float)) and max_amount >= 0):
            return []
        if not min_amount <= max_amount:
            return []
        for expense in self.expenses:
            if min_amount <= expense.amount <= max_amount:
                result.append(expense.get_details())
        return result

    def get_expenses_by_exact_amount(self, amount) -> list:
        result = []
        if not (isinstance(amount, (int, float)) and amount >= 0):
            return []
        for expense in self.expenses:
            if expense.amount == amount:
                result.append(expense.get_details())
        return result

    def get_highest_spending_category(self) -> str | None:
        if not self.expenses:
            return None
        summary = self.get_category_summary()
        biggest_category = None
        biggest_amount = 0
        for category, amount in summary.items():
            if biggest_category is None or amount > biggest_amount:
                biggest_category = category
                biggest_amount = amount
        return biggest_category

    def get_lowest_spending_category(self) -> str | None:
        if not self.expenses:
            return None
        summary = self.get_category_summary()
        biggest_category = None
        biggest_amount = 0
        for category, amount in summary.items():
            if biggest_category is None or amount < biggest_amount:
                biggest_category = category
                biggest_amount = amount
        return biggest_category

    def get_expense_report(self) -> dict:
        return {
            "total_expenses": self.get_expense_count(),
            "total_amount": self.get_total_expense_amount(),
            "average_amount": self.get_average_expense_amount(),
            "highest_expense": self.get_highest_expense(),
            "lowest_expense": self.get_lowest_expense(),
            "categories": self.get_all_categories(),
            "category_summary": self.get_category_summary(),
        }

    def get_category_report(self) -> dict:
        if not self.expenses:
            return{}
        summary = {}
        for expense in self.expenses:
            category = expense.category.strip().lower()
            if category not in summary:
                summary[category] = {
                    "count": 0,
                    "total_amount": 0,
                    "expenses": []
                }
            summary[category]["count"] += 1
            summary[category]["total_amount"] += expense.amount
            summary[category]["expenses"].append(expense.get_details())
        return summary

    def remove_expenses_by_category(self, category) -> int:
        if not (isinstance(category, str) and category.strip().lower() != ""):
            return 0
        count = 0
        unmatch = []
        for expense in self.expenses:
            if expense.category.strip().lower() == category.strip().lower():
                count += 1
            else:
                unmatch.append(expense)
        self.expenses = unmatch
        return count

    def save_expenses_to_file(self, filename) -> bool:
        if not (isinstance(filename, str) and filename.strip() != ""):
            return False
        try:
            with open(filename, "w") as file:
                for expense in self.expenses:
                    line = f"{expense.get_details()}"
                    file.write(line + "\n")
            return True
        except OSError:
            return False

    def read_expenses_from_file(self, filename) -> list:
        if not (isinstance(filename, str) and filename.strip() != ""):
            return []
        try:   
            with open(filename, "r") as file:
                lines = file.readlines()
        except OSError:
            return []
        return lines

    def count_expenses_in_file(self, filename) -> int:
        if not (isinstance(filename, str) and filename.strip() != ""):
            return 0
        try:
            with open(filename, "r") as file:
                lines = file.readlines()
                count = 0
                for line in lines:
                    count += 1
            return count
        except OSError:
            return 0

    def is_expense_file_empty(self, filename) -> bool:
        if not (isinstance(filename, str) and filename.strip() != ""):
            return True
        lines = self.count_expenses_in_file(filename)
        return lines == 0

    def append_expense_to_file(self, filename, expense) -> bool:
        if not (isinstance(filename, str) and filename.strip() != ""):
            return False
        if not isinstance(expense, Expense):
            return False
        if not expense.is_valid():
            return False
        line = str(expense.get_details())
        try:
            with open(filename, "a") as file:
                file.write(line + "\n")
                return True
        except OSError:
            return False

    def clear_expense_file(self, filename) -> bool:
        if not (isinstance(filename, str) and filename.strip() != ""):
            return False
        try:
            with open(filename, "w"):
                return True
        except OSError:
            return False

    def save_expenses_to_csv(self, filename) -> bool:
        if not (isinstance(filename, str) and filename.strip() != ""):
            return False
        try:
            with open(filename, "w") as file:
                file.write("expense_id,title,amount,category,date\n")
                for expense in self.expenses:
                    line = f"{expense.expense_id},{expense.title},{expense.amount},{expense.category},{expense.date}\n"
                    file.write(line)
                return True
        except OSError:
            return False

    def load_expenses_from_csv(self, filename) -> int:
        if not (isinstance(filename, str) and filename.strip() != ""):
            return 0
        count = 0
        try:
            with open(filename, "r") as file:
                first_line = file.readline()
                if first_line.strip() != "expense_id,title,amount,category,date":
                    return 0
                for line in file:
                    parts = line.strip().split(",")
                    if len(parts) != 5:
                        continue
                    try:
                        expense = Expense(int(parts[0]), (parts[1]), float(parts[2]), parts[3], parts[4])
                    except ValueError:
                        continue
                    if expense.is_valid() and self.add_expense(expense):
                            count += 1
                return count
        except OSError:
            return 0

    def save_expenses_to_json(self, filename) -> bool:
        if not (isinstance(filename, str) and filename.strip() != ""):
            return False
        try:
            with open(filename, "w") as file:
                final = []
                for expense in self.expenses:
                    final.append(expense.get_details())
                json.dump(final, file, indent=4)
                return True
        except OSError:
            return False 

    def load_expenses_from_json(self, filename) -> int:
        if not (isinstance(filename, str) and filename.strip() != ""):
            return 0
        try:
            with open(filename, "r") as file:
                data = json.load(file)
                if not isinstance(data, list):
                    return 0
                count = 0
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    expense = Expense(item.get("expense_id"), item.get("title"), item.get("amount"), item.get("category"), item.get("date"))
                    if self.add_expense(expense):
                        count += 1
                return count
        except (OSError, json.JSONDecodeError, ValueError, TypeError, KeyError):
            return 0

    def append_expense_to_json(self, filename, expense) -> bool:
        if not (isinstance(filename, str) and filename.strip() != ""):
            return False
        if not isinstance(expense, Expense):
            return False
        if not expense.is_valid():
            return False
        try:
            with open(filename, "r") as file:
                data = json.load(file)
                if not isinstance(data, list):
                    return False
                data.append(expense.get_details())
            with open(filename, "w") as file:
                json.dump(data, file, indent=4)
                return True
        except (OSError, json.JSONDecodeError, TypeError):
            return False

    def clear_expense_json_file(self, filename) -> bool:
        if not (isinstance(filename, str) and filename.strip() != ""):
            return False
        try:
            with open(filename, "w") as file:
                json.dump([], file, indent=4)
                return True
        except OSError:
            return False

    def count_expenses_in_json(self, filename) -> int:
        if not (isinstance(filename, str) and filename.strip() != ""):
            return 0
        try:
            with open(filename, "r") as file:
                data = json.load(file)
                if not isinstance(data, list):
                    return 0
                return len(data)
        except (OSError, json.JSONDecodeError, TypeError):
            return 0

    def get_expenses_by_date(self, date) -> list:
        if not (isinstance(date, str) and date.strip() != ""):
            return []
        result = []
        for expense in self.expenses:
            if expense.date.strip() == date.strip():
                result.append(expense.get_details())
        return result

    def get_total_by_date(self, date) -> int | float:
        if not (isinstance(date, str) and date.strip() != ""):
            return 0
        total = 0
        for expense in self.expenses:
            if expense.date.strip() == date.strip():
                total += expense.amount
        return total

    def get_expenses_between_dates(self, start_date, end_date) -> list:
        if not (isinstance(start_date, str) and start_date.strip() != ""):
            return []
        if not (isinstance(end_date, str) and end_date.strip() != ""):
            return []
        try:
            datetime.strptime(start_date, "%Y-%m-%d") # noqa: DTZ007
            datetime.strptime(end_date, "%Y-%m-%d") # noqa: DTZ007
            if start_date > end_date:
                return []
            result = []
            for expense in self.expenses:
                if start_date <= expense.date <= end_date:
                    result.append(expense.get_details())
            return result
        except ValueError:
            return []

    def get_total_between_dates(self, start_date, end_date) -> int | float:
        result = self.get_expenses_between_dates(start_date, end_date)
        if not result:
            return 0
        total = 0
        for expense in result:
            total += expense["amount"]
        return total

    def get_count_between_dates(self, start_date, end_date) -> int:
        result = self.get_expenses_between_dates(start_date, end_date)
        return len(result)

    def get_expenses_by_month(self, year, month) -> list:
        if not (isinstance(year, int) and len(str(year)) == 4):
            return []
        if not (isinstance(month, int) and 1 <= month <= 12):
            return []
        result = []
        target = f"{year}-{month:02d}"
        for expense in self.expenses:
            if expense.date.startswith(target):
                result.append(expense.get_details())
        return result

    def get_total_by_month(self, year, month) -> int | float:
        result = self.get_expenses_by_month(year, month)
        if not result:
            return 0
        total = 0
        for expense in result:
            total += expense["amount"]
        return total

    def get_count_by_month(self, year, month) -> int:
        result = self.get_expenses_by_month(year, month)
        return len(result)

    def get_monthly_report(self, year, month) -> dict:
        result = self.get_expenses_by_month(year, month)
        if not result:
            return {}
        return{
            "count": self.get_count_by_month(year, month),
            "total_amount": self.get_total_by_month(year, month),
            "expenses": result,
        }

    def get_expenses_by_year(self, year) -> list:
        if not (isinstance(year, int) and len(str(year)) == 4):
            return []
        result = []
        target = str(year)
        for expense in self.expenses:
            if expense.date.startswith(target):
                result.append(expense.get_details())
        return result

    def get_total_by_year(self, year) -> int | float:
        result = self.get_expenses_by_year(year)
        if not result:
            return 0
        total = 0
        for expense in result:
            total += expense["amount"]
        return total

    def get_count_by_year(self, year) -> int:
        return len(self.get_expenses_by_year(year))

    def get_yearly_report(self, year) -> dict:
        result = self.get_expenses_by_year(year)
        if not result:
            return {}
        return{
            "count": self.get_count_by_year(year),
            "total_amount": self.get_total_by_year(year),
            "expenses": result,
        }

    def get_category_summary_by_month(self, year, month) -> dict:
        result = self.get_expenses_by_month(year, month)
        summary = {}
        for expense in result:
            category = expense["category"].strip().lower()
            if category not in summary:
                summary[category] = 0
            summary[category] += expense["amount"]
        return summary

    def get_category_count_by_month(self, year, month) -> dict:
        result = self.get_expenses_by_month(year, month)
        summary = {}
        for expense in result:
            category = expense["category"].strip().lower()
            if category not in summary:
                summary[category] = 0
            summary[category] += 1
        return summary

    def get_category_report_by_month(self, year, month) -> dict:
        result = self.get_expenses_by_month(year, month)
        summary = {}
        for expense in result:
            category = expense["category"].strip().lower()
            if category not in summary:
                summary[category] = {
                    "count": 0,
                    "total_amount": 0,
                    "expenses": []
                }
            summary[category]["count"] += 1
            summary[category]["total_amount"] += expense["amount"]
            summary[category]["expenses"].append(expense)
        return summary

    def get_category_summary_by_year(self, year) -> dict:
        result = self.get_expenses_by_year(year)
        summary = {}
        for expense in result:
            category = expense["category"].strip().lower()
            if category not in summary:
                summary[category] = 0
            summary[category] += expense["amount"]
        return summary
    
    def get_category_count_by_year(self, year) -> dict:
        result = self.get_expenses_by_year(year)
        summary = {}
        for expense in result:
            category = expense["category"].strip().lower()
            if category not in summary:
                summary[category] = 0
            summary[category] += 1
        return summary

    def get_category_report_by_year(self, year) -> dict:
        result = self.get_expenses_by_year(year)
        summary = {}
        for expense in result:
            category = expense["category"].strip().lower()
            if category not in summary:
                summary[category] = {
                    "count": 0,
                    "total_amount": 0,
                    "expenses": []
                }
            summary[category]["count"] += 1
            summary[category]["total_amount"] += expense["amount"]
            summary[category]["expenses"].append(expense)
        return summary
    
    def remove_expenses_by_date(self, date) -> int:
        if not (isinstance(date, str) and date.strip() != ""):
            return 0
        try:
            datetime.strptime(date, "%Y-%m-%d") # noqa: DTZ007
            count = 0
            unmatch = []
            for expense in self.expenses:
                if expense.date.strip() == date.strip():
                    count += 1
                else:
                    unmatch.append(expense)
            self.expenses = unmatch
            return count
        except ValueError:
            return 0

    def remove_expenses_by_month(self, year, month) -> int:
        if not (isinstance(year, int) and len(str(year)) == 4):
            return 0
        if not (isinstance(month, int) and 1 <= month <= 12):
            return 0
        target = f"{year}-{month:02d}"
        count = 0
        unmatch = []
        for expense in self.expenses:
            if expense.date.startswith(target):
                count += 1
            else:
                unmatch.append(expense)
        self.expenses = unmatch
        return count


    def remove_expenses_by_year(self, year) -> int:
        if not (isinstance(year, int) and len(str(year)) == 4):
            return 0
        target = str(year)
        count = 0
        unmatch = []
        for expense in self.expenses:
            if expense.date.startswith(target):
                count += 1
            else:
                unmatch.append(expense)
        self.expenses = unmatch
        return count

    def get_expenses_sorted_by_date_oldest_first(self) -> list:
        all_expenses = self.get_all_expense_details().copy()
        all_expenses.sort(key=lambda expense: expense["date"])
        return all_expenses

    def get_expenses_sorted_by_date_newest_first(self) -> list:
        all_expenses = self.get_all_expense_details().copy()
        all_expenses.sort(reverse=True, key=lambda expense: expense["date"])
        return all_expenses

    def get_expenses_sorted_by_date_then_amount(self) -> list:
        all_expenses = self.get_all_expense_details().copy()
        all_expenses.sort(key=lambda expense: (expense["date"], expense["amount"]))
        return all_expenses


if __name__ == "__main__":
    expense1 = Expense(100, "rent", 1500, "housing", "2026-08-13")
    expense2 = Expense(101, "bills", 100, "utility", "")
    expense3 = Expense(110, "insurance", 1000, "housing", "2026-09-13")
    et = ExpenseTracker()

    print(et.add_expense(expense1))
    print(et.add_expense(expense2))
    print(et.add_expense(expense3))

    print(et.get_expenses_by_date("2026-08-13"))
    print(et.get_total_by_date("2026-08-13"))
    print(et.get_total_between_dates("2026-08-13", "2026-09-10"))
    print(et.get_expenses_sorted_by_date_oldest_first())
    
    
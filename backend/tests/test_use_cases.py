import os
import tempfile

from backend.domain.entities import Expense, Income, Recurrence
from backend.repositories.sqlite.entrada_repo import SQLiteIncomeRepository
from backend.repositories.sqlite.gasto_repo import SQLiteExpenseRepository
from backend.repositories.sqlite.recorrencia_repo import SQLiteRecurrenceRepository
from backend.use_cases.apply_recurrence import apply_recurrence
from backend.use_cases.list_expenses import list_expenses
from backend.use_cases.list_incomes import list_incomes


def test_list_expenses_filters_by_month_and_year():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        repo = SQLiteExpenseRepository(db_path)
        try:
            repo.add(Expense(name="Conta 1", value=10.0, month=1, year=2026))
            repo.add(Expense(name="Conta 2", value=20.0, month=2, year=2026))
            filtered = list_expenses(repo, month=2, year=2026)
            assert len(filtered) == 1
            assert filtered[0].name == "Conta 2"
        finally:
            repo.close()


def test_list_incomes_filters_by_month_and_year():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        repo = SQLiteIncomeRepository(db_path)
        try:
            repo.add(Income(name="Bônus", value=100.0, month=1, year=2026))
            repo.add(Income(name="Salário", value=2000.0, month=2, year=2026))
            filtered = list_incomes(repo, month=2, year=2026)
            assert len(filtered) == 1
            assert filtered[0].name == "Salário"
        finally:
            repo.close()


def test_apply_recurrence_creates_expenses():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        expense_repo = SQLiteExpenseRepository(db_path)
        income_repo = SQLiteIncomeRepository(db_path)
        recurrence_repo = SQLiteRecurrenceRepository(db_path)
        try:
            recurrence = Recurrence(
                kind="expense",
                name="Assinatura",
                value=29.9,
                start_month=1,
                start_year=2026,
                interval_months=1,
                occurrences=3,
            )
            recurrence_repo.add(recurrence)
            expenses, incomes = apply_recurrence(recurrence, expense_repo, income_repo)
            assert len(expenses) == 3
            assert len(incomes) == 0
        finally:
            recurrence_repo.close()
            income_repo.close()
            expense_repo.close()

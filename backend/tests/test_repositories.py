import os
import tempfile

from backend.domain.entities import Category, Expense, Income, Card, Goal
from backend.repositories.sqlite.categoria_repo import SQLiteCategoryRepository
from backend.repositories.sqlite.cartao_repo import SQLiteCardRepository
from backend.repositories.sqlite.entrada_repo import SQLiteIncomeRepository
from backend.repositories.sqlite.gasto_repo import SQLiteExpenseRepository
from backend.repositories.sqlite.meta_repo import SQLiteGoalRepository


def test_category_repository_crud():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        repo = SQLiteCategoryRepository(db_path)
        created = repo.add(Category(name="Alimentação", description="Mercado"))
        assert created.id is not None
        fetched = repo.get(created.id)
        assert fetched is not None
        assert fetched.name == "Alimentação"


def test_expense_repository_crud():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        repo = SQLiteExpenseRepository(db_path)
        created = repo.add(Expense(name="Almoço", value=30.0, month=2, year=2026))
        assert created.id is not None
        fetched = repo.get(created.id)
        assert fetched is not None
        assert fetched.value == 30.0


def test_income_repository_crud():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        repo = SQLiteIncomeRepository(db_path)
        created = repo.add(Income(name="Salário", value=2500.0, month=2, year=2026))
        assert created.id is not None
        fetched = repo.get(created.id)
        assert fetched is not None
        assert fetched.name == "Salário"


def test_card_repository_crud():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        repo = SQLiteCardRepository(db_path)
        created = repo.add(Card(name="Cartão", limit=5000.0, closing_day=5, due_day=15))
        assert created.id is not None
        fetched = repo.get(created.id)
        assert fetched is not None
        assert fetched.limit == 5000.0


def test_goal_repository_crud():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        repo = SQLiteGoalRepository(db_path)
        created = repo.add(Goal(name="Meta mês", limit_value=1000.0, month=2, year=2026))
        assert created.id is not None
        fetched = repo.get(created.id)
        assert fetched is not None
        assert fetched.limit_value == 1000.0

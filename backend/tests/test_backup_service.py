import os
import tempfile

import pytest

from backend.domain.entities import Card, Category, Expense, Goal, Income, Installment, Recurrence
from backend.repositories.sqlite.cartao_repo import SQLiteCardRepository
from backend.repositories.sqlite.categoria_repo import SQLiteCategoryRepository
from backend.repositories.sqlite.entrada_repo import SQLiteIncomeRepository
from backend.repositories.sqlite.gasto_repo import SQLiteExpenseRepository
from backend.repositories.sqlite.meta_repo import SQLiteGoalRepository
from backend.repositories.sqlite.parcela_repo import SQLiteInstallmentRepository
from backend.repositories.sqlite.recorrencia_repo import SQLiteRecurrenceRepository
from backend.services.backup_service import BackupValidationError, export_backup_payload, restore_backup_payload


def _init_repositories(db_path: str):
    return {
        "category": SQLiteCategoryRepository(db_path),
        "card": SQLiteCardRepository(db_path),
        "expense": SQLiteExpenseRepository(db_path),
        "income": SQLiteIncomeRepository(db_path),
        "installment": SQLiteInstallmentRepository(db_path),
        "recurrence": SQLiteRecurrenceRepository(db_path),
        "goal": SQLiteGoalRepository(db_path),
    }


def _close_repositories(repos: dict[str, object]) -> None:
    for repo in repos.values():
        close = getattr(repo, "close", None)
        if callable(close):
            close()


def test_export_backup_payload_contains_expected_keys():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        repos = _init_repositories(db_path)
        try:
            category = repos["category"].add(Category(name="Casa", description="Contas"))
            card = repos["card"].add(Card(name="Cartão A", limit=1000, closing_day=5, due_day=15))
            expense = repos["expense"].add(Expense(name="Luz", value=120.5, month=2, year=2026, category_id=category.id))
            income = repos["income"].add(Income(name="Salário", value=3500, month=2, year=2026, confirmed=True))
            recurrence = repos["recurrence"].add(
                Recurrence(kind="expense", name="Internet", value=99.9, start_month=2, start_year=2026)
            )
            installment = repos["installment"].add(
                Installment(
                    card_id=card.id,
                    expense_name="Notebook",
                    installment_number=1,
                    total_installments=10,
                    value=300,
                    month=2,
                    year=2026,
                )
            )
            goal = repos["goal"].add(Goal(name="Meta geral", limit_value=1000, month=2, year=2026, category_id=category.id))

            payload = export_backup_payload(
                cards=[card],
                categories=[category],
                expenses=[expense],
                goals=[goal],
                incomes=[income],
                installments=[installment],
                recurrences=[recurrence],
            )

            assert payload["version"] == "1.0"
            assert set(payload.keys()) == {
                "version",
                "exportedAt",
                "cards",
                "expenses",
                "recurringExpenses",
                "income",
                "categories",
                "installments",
                "goals",
                "settings",
            }
        finally:
            _close_repositories(repos)


def test_restore_backup_payload_replaces_existing_data():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        repos = _init_repositories(db_path)
        try:
            category = repos["category"].add(Category(name="Velha categoria"))
            repos["expense"].add(Expense(name="Antigo", value=10, month=1, year=2026, category_id=category.id))

            payload = {
            "version": "1.0",
            "exportedAt": "2026-02-23",
            "cards": [
                {
                    "id": 11,
                    "name": "Cartão Novo",
                    "limit": 2500,
                    "bank": "Banco X",
                    "brand": "Visa",
                    "closing_day": 8,
                    "due_day": 18,
                }
            ],
            "expenses": [
                {
                    "id": 21,
                    "name": "Mercado",
                    "value": 150,
                    "month": 2,
                    "year": 2026,
                    "category_id": 31,
                    "payment_method": "debit",
                    "notes": None,
                }
            ],
            "recurringExpenses": [
                {
                    "id": 41,
                    "kind": "expense",
                    "name": "Streaming",
                    "value": 29.9,
                    "start_month": 2,
                    "start_year": 2026,
                    "interval_months": 1,
                    "occurrences": 12,
                    "category_id": 31,
                    "payment_method": "debit",
                    "confirmed": None,
                    "notes": None,
                }
            ],
            "income": [
                {
                    "id": 51,
                    "name": "Salário",
                    "value": 5000,
                    "month": 2,
                    "year": 2026,
                    "confirmed": True,
                    "notes": None,
                }
            ],
            "categories": [
                {
                    "id": 31,
                    "name": "Alimentação",
                    "description": None,
                }
            ],
            "installments": [
                {
                    "id": 61,
                    "card_id": 11,
                    "expense_name": "Geladeira",
                    "installment_number": 1,
                    "total_installments": 8,
                    "value": 400,
                    "month": 2,
                    "year": 2026,
                    "status": "pendente",
                }
            ],
            "goals": [
                {
                    "id": 71,
                    "name": "Limite mercado",
                    "limit_value": 600,
                    "month": 2,
                    "year": 2026,
                    "category_id": 31,
                }
            ],
            "settings": {},
            }

            restore_backup_payload(db_path, payload)

            categories = repos["category"].list()
            expenses = repos["expense"].list()
            cards = repos["card"].list()

            assert len(categories) == 1
            assert categories[0].name == "Alimentação"
            assert len(expenses) == 1
            assert expenses[0].name == "Mercado"
            assert len(cards) == 1
            assert cards[0].id == 11
        finally:
            _close_repositories(repos)


def test_restore_backup_payload_rejects_incompatible_version():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        repos = _init_repositories(db_path)
        try:
            payload = {
                "version": "2.0",
                "cards": [],
                "expenses": [],
                "recurringExpenses": [],
                "income": [],
                "categories": [],
                "settings": {},
            }

            with pytest.raises(BackupValidationError):
                restore_backup_payload(db_path, payload)
        finally:
            _close_repositories(repos)


def test_restore_backup_payload_keeps_current_data_on_failure():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        repos = _init_repositories(db_path)
        try:
            original_category = repos["category"].add(Category(name="Original"))
            repos["expense"].add(
                Expense(name="Conta existente", value=42, month=2, year=2026, category_id=original_category.id)
            )

            invalid_payload = {
                "version": "1.0",
                "cards": [],
                "expenses": [
                    {
                        "id": 1,
                        "name": "Novo gasto inválido",
                        "value": 10,
                        "month": 2,
                        "year": 2026,
                        "category_id": 9999,
                        "payment_method": "debit",
                        "notes": None,
                    }
                ],
                "recurringExpenses": [],
                "income": [],
                "categories": [],
                "settings": {},
            }

            with pytest.raises(BackupValidationError):
                restore_backup_payload(db_path, invalid_payload)

            categories = repos["category"].list()
            expenses = repos["expense"].list()
            assert len(categories) == 1
            assert categories[0].name == "Original"
            assert len(expenses) == 1
            assert expenses[0].name == "Conta existente"
        finally:
            _close_repositories(repos)

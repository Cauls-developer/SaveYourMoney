import os
import tempfile

import pytest

import backend.app as app_module
from backend.repositories.sqlite.cartao_repo import SQLiteCardRepository
from backend.repositories.sqlite.categoria_repo import SQLiteCategoryRepository
from backend.repositories.sqlite.entrada_repo import SQLiteIncomeRepository
from backend.repositories.sqlite.gasto_repo import SQLiteExpenseRepository
from backend.repositories.sqlite.meta_repo import SQLiteGoalRepository
from backend.repositories.sqlite.parcela_repo import SQLiteInstallmentRepository
from backend.repositories.sqlite.recorrencia_repo import SQLiteRecurrenceRepository


@pytest.fixture()
def client_and_repos(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        repos = {
            "category": SQLiteCategoryRepository(db_path),
            "expense": SQLiteExpenseRepository(db_path),
            "income": SQLiteIncomeRepository(db_path),
            "card": SQLiteCardRepository(db_path),
            "installment": SQLiteInstallmentRepository(db_path),
            "recurrence": SQLiteRecurrenceRepository(db_path),
            "goal": SQLiteGoalRepository(db_path),
        }
        monkeypatch.setattr(app_module, "category_repo", repos["category"])
        monkeypatch.setattr(app_module, "expense_repo", repos["expense"])
        monkeypatch.setattr(app_module, "income_repo", repos["income"])
        monkeypatch.setattr(app_module, "card_repo", repos["card"])
        monkeypatch.setattr(app_module, "installment_repo", repos["installment"])
        monkeypatch.setattr(app_module, "recurrence_repo", repos["recurrence"])
        monkeypatch.setattr(app_module, "goal_repo", repos["goal"])
        app_module.sync_state()
        try:
            yield app_module.app.test_client(), repos
        finally:
            for repo in repos.values():
                repo.close()


def test_create_goal_rejects_unknown_category(client_and_repos):
    client, _ = client_and_repos
    response = client.post(
        "/metas",
        json={
            "name": "Meta inválida",
            "limit_value": 1000,
            "month": 2,
            "year": 2026,
            "category_id": 999,
        },
    )
    assert response.status_code == 400
    assert "Categoria não encontrada" in response.get_json()["error"]


def test_update_goal_allows_clearing_category(client_and_repos):
    client, repos = client_and_repos
    category = repos["category"].add(app_module.Category(name="Mercado"))
    goal = repos["goal"].add(
        app_module.Goal(name="Meta mercado", limit_value=500, month=2, year=2026, category_id=category.id)
    )

    response = client.put(
        f"/metas/{goal.id}",
        json={
            "name": "Meta mercado",
            "limit_value": 500,
            "month": 2,
            "year": 2026,
            "category_id": None,
        },
    )
    assert response.status_code == 200
    assert response.get_json()["category_id"] is None


def test_create_expense_rejects_unknown_card_for_installments(client_and_repos):
    client, _ = client_and_repos
    response = client.post(
        "/gastos",
        json={
            "name": "Notebook",
            "value": 3000,
            "month": 2,
            "year": 2026,
            "payment_method": "credit",
            "installments": {"card_id": 999, "total": 10},
        },
    )
    assert response.status_code == 400
    assert "Cartão não encontrado" in response.get_json()["error"]


def test_delete_category_returns_409_when_linked_to_goal(client_and_repos):
    client, repos = client_and_repos
    category = repos["category"].add(app_module.Category(name="Moradia"))
    repos["goal"].add(app_module.Goal(name="Meta casa", limit_value=700, month=2, year=2026, category_id=category.id))

    response = client.delete(f"/categorias/{category.id}")
    assert response.status_code == 409


def test_post_income_parses_confirmed_string_false(client_and_repos):
    client, _ = client_and_repos
    response = client.post(
        "/entradas",
        json={
            "name": "Reembolso",
            "value": 120,
            "month": 2,
            "year": 2026,
            "confirmed": "false",
        },
    )
    assert response.status_code == 201
    assert response.get_json()["confirmed"] is False


def test_create_recurrence_rejects_unknown_category(client_and_repos):
    client, _ = client_and_repos
    response = client.post(
        "/recorrencias",
        json={
            "kind": "expense",
            "name": "Assinatura",
            "value": 39.9,
            "start_month": 2,
            "start_year": 2026,
            "interval_months": 1,
            "occurrences": 6,
            "category_id": 1234,
        },
    )
    assert response.status_code == 400
    assert "Categoria não encontrada" in response.get_json()["error"]


def test_report_month_pdf_returns_file(client_and_repos):
    client, repos = client_and_repos
    category = repos["category"].add(app_module.Category(name="Mercado"))
    repos["expense"].add(app_module.Expense(name="Compra do mês", value=350.0, month=2, year=2026, category_id=category.id))
    repos["income"].add(app_module.Income(name="Salário", value=4000.0, month=2, year=2026, confirmed=True))
    repos["goal"].add(
        app_module.Goal(name="Meta Mercado", limit_value=500.0, month=2, year=2026, category_id=category.id)
    )

    response = client.get("/relatorios/mes/pdf?mes=2&ano=2026")

    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert "relatorio_02_2026.pdf" in response.headers.get("Content-Disposition", "")
    assert response.data.startswith(b"%PDF")
    assert len(response.data) > 1500

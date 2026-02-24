"""Servidor HTTP para o backend do Save Your Money."""
from __future__ import annotations

import os

from flask import Flask, jsonify

from . import state
from .domain.entities import Category, Expense, Income, Card, Installment, Recurrence, Goal
from .repositories.sqlite.categoria_repo import SQLiteCategoryRepository
from .repositories.sqlite.entrada_repo import SQLiteIncomeRepository
from .repositories.sqlite.gasto_repo import SQLiteExpenseRepository
from .repositories.sqlite.cartao_repo import SQLiteCardRepository
from .repositories.sqlite.parcela_repo import SQLiteInstallmentRepository
from .repositories.sqlite.recorrencia_repo import SQLiteRecurrenceRepository
from .repositories.sqlite.meta_repo import SQLiteGoalRepository
from .routes.backup import bp as backup_bp
from .routes.calculator import bp as calculator_bp
from .routes.cards import bp as cards_bp
from .routes.categories import bp as categories_bp
from .routes.docs import bp as docs_bp
from .routes.expenses import bp as expenses_bp
from .routes.goals import bp as goals_bp
from .routes.health import bp as health_bp
from .routes.incomes import bp as incomes_bp
from .routes.installments import bp as installments_bp
from .routes.recurrences import bp as recurrences_bp
from .routes.reports import bp as reports_bp
from .errors import HttpError


BASE_DATA_DIR = os.environ.get("SAVEYOURMONEY_DATA_DIR", ".")
os.makedirs(BASE_DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(BASE_DATA_DIR, "saveyourmoney.db")
BACKUP_DIR = os.path.join(BASE_DATA_DIR, "backups")

category_repo = SQLiteCategoryRepository(DB_PATH)
expense_repo = SQLiteExpenseRepository(DB_PATH)
income_repo = SQLiteIncomeRepository(DB_PATH)
card_repo = SQLiteCardRepository(DB_PATH)
installment_repo = SQLiteInstallmentRepository(DB_PATH)
recurrence_repo = SQLiteRecurrenceRepository(DB_PATH)
goal_repo = SQLiteGoalRepository(DB_PATH)


def _sync_state() -> None:
    state.BASE_DATA_DIR = BASE_DATA_DIR
    state.DB_PATH = DB_PATH
    state.BACKUP_DIR = BACKUP_DIR
    state.category_repo = category_repo
    state.expense_repo = expense_repo
    state.income_repo = income_repo
    state.card_repo = card_repo
    state.installment_repo = installment_repo
    state.recurrence_repo = recurrence_repo
    state.goal_repo = goal_repo


def create_app() -> Flask:
    _sync_state()
    app = Flask(__name__)
    app.register_blueprint(health_bp)
    app.register_blueprint(calculator_bp)
    app.register_blueprint(backup_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(incomes_bp)
    app.register_blueprint(cards_bp)
    app.register_blueprint(installments_bp)
    app.register_blueprint(recurrences_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(docs_bp)

    @app.errorhandler(HttpError)
    def handle_http_error(error: HttpError):
        return jsonify(error.to_payload()), error.status_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        return jsonify({"error": "Erro interno inesperado."}), 500
    return app


def sync_state() -> None:
    _sync_state()


app = create_app()


__all__ = [
    "app",
    "create_app",
    "Category",
    "Expense",
    "Income",
    "Card",
    "Installment",
    "Recurrence",
    "Goal",
    "BASE_DATA_DIR",
    "DB_PATH",
    "BACKUP_DIR",
    "category_repo",
    "expense_repo",
    "income_repo",
    "card_repo",
    "installment_repo",
    "recurrence_repo",
    "goal_repo",
    "sync_state",
]


if __name__ == "__main__":
    debug_mode = os.environ.get("SAVEYOURMONEY_DEBUG") == "1"
    app.run(port=5000, debug=debug_mode, use_reloader=debug_mode)

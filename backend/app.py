"""Servidor HTTP para o backend do Save Your Money."""
from __future__ import annotations

from dataclasses import asdict
from io import BytesIO, StringIO
import csv
import os
from datetime import datetime

from flask import Flask, jsonify, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .domain.entities import Category, Expense, Income, Card, Installment, Recurrence, Goal
from .repositories.sqlite.categoria_repo import SQLiteCategoryRepository
from .repositories.sqlite.entrada_repo import SQLiteIncomeRepository
from .repositories.sqlite.gasto_repo import SQLiteExpenseRepository
from .repositories.sqlite.cartao_repo import SQLiteCardRepository
from .repositories.sqlite.parcela_repo import SQLiteInstallmentRepository
from .repositories.sqlite.recorrencia_repo import SQLiteRecurrenceRepository
from .repositories.sqlite.meta_repo import SQLiteGoalRepository
from .use_cases.create_category import create_category
from .use_cases.create_card import create_card
from .use_cases.create_expense import create_expense
from .use_cases.create_income import create_income
from .use_cases.create_installments import create_installments
from .use_cases.create_recurrence import create_recurrence
from .use_cases.create_goal import create_goal
from .use_cases.list_categories import list_categories
from .use_cases.list_cards import list_cards
from .use_cases.list_expenses import list_expenses
from .use_cases.list_incomes import list_incomes
from .use_cases.list_installments import list_installments
from .use_cases.list_recurrences import list_recurrences
from .use_cases.list_goals import list_goals
from .use_cases.apply_recurrence import apply_recurrence
from .services.finance_service import (
    calculate_basic,
    calculate_compound_interest,
    calculate_discount,
    calculate_invoice,
    calculate_monthly_return,
    calculate_simple_interest,
    generate_installments,
    simulate_debt_payoff,
    simulate_installment,
)
from .services.backup_service import BackupValidationError, export_backup_payload, restore_backup_payload


app = Flask(__name__)
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


def _parse_optional_bool(raw_value):
    if raw_value is None:
        return None
    if isinstance(raw_value, bool):
        return raw_value
    normalized = str(raw_value).strip().lower()
    if normalized in {"1", "true", "sim", "yes"}:
        return True
    if normalized in {"0", "false", "nao", "não", "no"}:
        return False
    raise ValueError("Valor booleano inválido.")


def _parse_edit_scope(raw_value: str | None) -> str:
    scope = (raw_value or "this").strip().lower()
    if scope not in {"this", "future"}:
        raise ValueError("Escopo de edição inválido. Use 'this' ou 'future'.")
    return scope


def _parse_cancel_scope(raw_value: str | None) -> str:
    scope = (raw_value or "all").strip().lower()
    if scope not in {"this", "future", "all"}:
        raise ValueError("Escopo de cancelamento inválido. Use 'this', 'future' ou 'all'.")
    return scope


@app.get("/health")
def health() -> tuple[dict, int]:
    return {"status": "ok"}, 200


@app.post("/calculadora")
def calculator():
    data = request.get_json(silent=True) or {}
    operation = (data.get("operation") or "").strip().lower()
    try:
        if operation in {"soma", "subtracao", "multiplicacao", "divisao"}:
            a = float(data.get("a"))
            b = float(data.get("b"))
            result = calculate_basic(operation, a, b)
            return jsonify({"operation": operation, "result": result}), 200
        if operation == "juros_simples":
            result = calculate_simple_interest(
                principal=float(data.get("principal")),
                monthly_rate_percent=float(data.get("rate")),
                months=int(data.get("months")),
            )
            return jsonify({"operation": operation, "result": result}), 200
        if operation == "juros_compostos":
            result = calculate_compound_interest(
                principal=float(data.get("principal")),
                monthly_rate_percent=float(data.get("rate")),
                months=int(data.get("months")),
            )
            return jsonify({"operation": operation, "result": result}), 200
        if operation == "parcelamento":
            result = simulate_installment(
                principal=float(data.get("principal")),
                monthly_rate_percent=float(data.get("rate")),
                months=int(data.get("months")),
            )
            return jsonify({"operation": operation, "result": result}), 200
        if operation == "desconto":
            result = calculate_discount(
                original_value=float(data.get("principal")),
                discount_percent=float(data.get("rate")),
            )
            return jsonify({"operation": operation, "result": result}), 200
        if operation == "rendimento_mensal":
            result = calculate_monthly_return(
                principal=float(data.get("principal")),
                monthly_rate_percent=float(data.get("rate")),
            )
            return jsonify({"operation": operation, "result": result}), 200
        if operation == "quitacao_divida":
            result = simulate_debt_payoff(
                debt_value=float(data.get("principal")),
                payment_per_month=float(data.get("payment")),
                monthly_rate_percent=float(data.get("rate")),
            )
            return jsonify({"operation": operation, "result": result}), 200
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Parâmetros inválidos para a calculadora. {exc}"}), 400
    return jsonify({"error": "Operação de calculadora inválida."}), 400


@app.get("/backup/exportar")
def export_backup():
    payload = export_backup_payload(
        cards=list_cards(card_repo),
        categories=list_categories(category_repo),
        expenses=list_expenses(expense_repo),
        goals=list_goals(goal_repo),
        incomes=list_incomes(income_repo),
        installments=list_installments(installment_repo),
        recurrences=list_recurrences(recurrence_repo),
    )
    return jsonify(payload)


@app.post("/backup/restaurar")
def restore_backup():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Envie um JSON de backup válido."}), 400
    try:
        counts = restore_backup_payload(DB_PATH, data)
    except BackupValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        return jsonify({"error": "Não foi possível restaurar o backup. Verifique se o arquivo é válido."}), 500
    return jsonify({"message": "Backup restaurado com sucesso.", "imported": counts}), 200


@app.get("/categorias")
def get_categories():
    categories = list_categories(category_repo)
    return jsonify([asdict(category) for category in categories])


@app.post("/categorias")
def post_category():
    data = request.get_json(silent=True) or {}
    name = data.get("name") or data.get("nome")
    description = data.get("description") or data.get("descricao")
    if not name:
        return jsonify({"error": "Nome da categoria é obrigatório."}), 400
    category = create_category(category_repo, name=name, description=description)
    return jsonify(asdict(category)), 201


@app.put("/categorias/<int:category_id>")
def put_category(category_id: int):
    existing = category_repo.get(category_id)
    if not existing:
        return jsonify({"error": "Categoria não encontrada."}), 404
    data = request.get_json(silent=True) or {}
    name = data.get("name") or data.get("nome") or existing.name
    description = data.get("description") or data.get("descricao") or existing.description
    try:
        updated = Category(id=category_id, name=name, description=description)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    category_repo.update(updated)
    return jsonify(asdict(updated)), 200


@app.delete("/categorias/<int:category_id>")
def delete_category(category_id: int):
    if not category_repo.get(category_id):
        return jsonify({"error": "Categoria não encontrada."}), 404
    has_expense_link = any(exp.category_id == category_id for exp in expense_repo.list())
    has_recurrence_link = any(rec.category_id == category_id for rec in recurrence_repo.list())
    has_goal_link = any(goal.category_id == category_id for goal in goal_repo.list())
    if has_expense_link or has_recurrence_link or has_goal_link:
        return jsonify({"error": "Não é possível excluir categoria com itens vinculados."}), 409
    category_repo.delete(category_id)
    return jsonify({"message": "Categoria excluída com sucesso."}), 200


@app.get("/gastos")
def get_expenses():
    month = request.args.get("mes", type=int)
    year = request.args.get("ano", type=int)
    recurring_filter = (request.args.get("recorrente") or "todos").strip().lower()
    expenses = list_expenses(expense_repo, month=month, year=year)
    if recurring_filter == "sim":
        expenses = [item for item in expenses if item.recurrence_id is not None]
    elif recurring_filter == "nao":
        expenses = [item for item in expenses if item.recurrence_id is None]
    return jsonify([asdict(expense) for expense in expenses])


@app.post("/gastos")
def post_expense():
    data = request.get_json(silent=True) or {}
    try:
        recurring_data = data.get("recurring") or {}
        recurrence_id = None
        if recurring_data.get("enabled"):
            frequency = str(recurring_data.get("frequency") or "mensal").strip().lower()
            interval_by_frequency = {"semanal": 1, "mensal": 1, "anual": 12}
            interval_months = int(recurring_data.get("interval_months") or interval_by_frequency.get(frequency, 1))
            if interval_months <= 0:
                raise ValueError("interval_months deve ser maior que zero.")
            occurrences = int(recurring_data.get("occurrences") or 12)
            if recurring_data.get("end_month") and recurring_data.get("end_year"):
                end_month = int(recurring_data.get("end_month"))
                end_year = int(recurring_data.get("end_year"))
                start_index = int(data.get("year") or data.get("ano")) * 12 + int(data.get("month") or data.get("mes"))
                end_index = end_year * 12 + end_month
                total_months = max(end_index - start_index, 0)
                occurrences = max((total_months // interval_months) + 1, 1)
            created_recurrence = create_recurrence(
                recurrence_repo,
                Recurrence(
                    kind="expense",
                    name=data.get("name") or data.get("nome"),
                    value=float(data.get("value") or data.get("valor")),
                    start_month=int(data.get("month") or data.get("mes")),
                    start_year=int(data.get("year") or data.get("ano")),
                    interval_months=interval_months,
                    occurrences=occurrences,
                    category_id=data.get("category_id") or data.get("categoria_id"),
                    payment_method=data.get("payment_method") or data.get("forma") or "debit",
                    notes=data.get("notes") or data.get("observacao"),
                ),
            )
            recurrence_id = created_recurrence.id

        expense = Expense(
            name=data.get("name") or data.get("nome"),
            value=float(data.get("value") or data.get("valor")),
            month=int(data.get("month") or data.get("mes")),
            year=int(data.get("year") or data.get("ano")),
            category_id=data.get("category_id") or data.get("categoria_id"),
            recurrence_id=recurrence_id,
            payment_method=data.get("payment_method") or data.get("forma") or "debit",
            notes=data.get("notes") or data.get("observacao"),
        )
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Dados inválidos para gasto. {exc}"}), 400
    expense = create_expense(expense_repo, expense)
    installments_payload = data.get("installments") or data.get("parcelas")
    if installments_payload:
        card_id = installments_payload.get("card_id") or installments_payload.get("cartao_id")
        num_installments = int(installments_payload.get("total") or installments_payload.get("total_parcelas") or 1)
        if not card_id:
            return jsonify({"error": "cartao_id é obrigatório para parcelas."}), 400
        values = generate_installments(expense.value, num_installments)
        created_installments = []
        month = expense.month
        year = expense.year
        for index, value in enumerate(values, start=1):
            installment = Installment(
                card_id=int(card_id),
                expense_name=expense.name,
                installment_number=index,
                total_installments=num_installments,
                value=value,
                month=month,
                year=year,
                status="pendente",
            )
            created_installments.append(installment)
            month += 1
            if month > 12:
                month = 1
                year += 1
        create_installments(installment_repo, created_installments)
    return jsonify(asdict(expense)), 201


@app.put("/gastos/<int:expense_id>")
def put_expense(expense_id: int):
    existing = expense_repo.get(expense_id)
    if not existing:
        return jsonify({"error": "Gasto não encontrado."}), 404
    data = request.get_json(silent=True) or {}
    try:
        scope = _parse_edit_scope(data.get("scope"))
        payload = Expense(
            id=expense_id,
            name=data.get("name") or data.get("nome") or existing.name,
            value=float(data.get("value") or data.get("valor") or existing.value),
            month=int(data.get("month") or data.get("mes") or existing.month),
            year=int(data.get("year") or data.get("ano") or existing.year),
            category_id=data.get("category_id") or data.get("categoria_id") or existing.category_id,
            recurrence_id=existing.recurrence_id,
            payment_method=data.get("payment_method") or data.get("forma") or existing.payment_method,
            notes=data.get("notes") or data.get("observacao") or existing.notes,
        )
        expense_repo.update(payload)
        if scope == "future" and existing.recurrence_id:
            recurrence = recurrence_repo.get(existing.recurrence_id)
            if recurrence:
                recurrence.name = payload.name
                recurrence.value = payload.value
                recurrence.category_id = payload.category_id
                recurrence.payment_method = payload.payment_method
                recurrence.notes = payload.notes
                recurrence_repo.update(recurrence)
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Dados inválidos para gasto. {exc}"}), 400
    return jsonify(asdict(payload)), 200


@app.delete("/gastos/<int:expense_id>")
def delete_expense(expense_id: int):
    existing = expense_repo.get(expense_id)
    if not existing:
        return jsonify({"error": "Gasto não encontrado."}), 404
    data = request.get_json(silent=True) or {}
    try:
        scope = _parse_cancel_scope(data.get("scope"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    if existing.recurrence_id and scope in {"future", "all"}:
        recurrence_repo.delete(existing.recurrence_id)
        for expense in expense_repo.list():
            if expense.recurrence_id == existing.recurrence_id:
                expense_repo.delete(expense.id)
        return jsonify({"message": "Recorrência cancelada com sucesso."}), 200
    expense_repo.delete(expense_id)
    return jsonify({"message": "Gasto excluído com sucesso."}), 200


@app.get("/entradas")
def get_incomes():
    month = request.args.get("mes", type=int)
    year = request.args.get("ano", type=int)
    incomes = list_incomes(income_repo, month=month, year=year)
    return jsonify([asdict(income) for income in incomes])


@app.post("/entradas")
def post_income():
    data = request.get_json(silent=True) or {}
    try:
        income = Income(
            name=data.get("name") or data.get("nome"),
            value=float(data.get("value") or data.get("valor")),
            month=int(data.get("month") or data.get("mes")),
            year=int(data.get("year") or data.get("ano")),
            confirmed=bool(data.get("confirmed", data.get("confirmado", True))),
            notes=data.get("notes") or data.get("observacao"),
        )
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Dados inválidos para entrada. {exc}"}), 400
    income = create_income(income_repo, income)
    return jsonify(asdict(income)), 201


@app.put("/entradas/<int:income_id>")
def put_income(income_id: int):
    existing = income_repo.get(income_id)
    if not existing:
        return jsonify({"error": "Entrada não encontrada."}), 404
    data = request.get_json(silent=True) or {}
    try:
        confirmed_raw = data.get("confirmed", data.get("confirmado"))
        payload = Income(
            id=income_id,
            name=data.get("name") or data.get("nome") or existing.name,
            value=float(data.get("value") or data.get("valor") or existing.value),
            month=int(data.get("month") or data.get("mes") or existing.month),
            year=int(data.get("year") or data.get("ano") or existing.year),
            confirmed=_parse_optional_bool(confirmed_raw) if confirmed_raw is not None else existing.confirmed,
            notes=data.get("notes") or data.get("observacao") or existing.notes,
        )
        income_repo.update(payload)
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Dados inválidos para entrada. {exc}"}), 400
    return jsonify(asdict(payload)), 200


@app.delete("/entradas/<int:income_id>")
def delete_income(income_id: int):
    if not income_repo.get(income_id):
        return jsonify({"error": "Entrada não encontrada."}), 404
    income_repo.delete(income_id)
    return jsonify({"message": "Entrada excluída com sucesso."}), 200


@app.get("/cartoes")
def get_cards():
    cards = list_cards(card_repo)
    return jsonify([asdict(card) for card in cards])


@app.post("/cartoes")
def post_card():
    data = request.get_json(silent=True) or {}
    try:
        limit_raw = data.get("limit", data.get("limite"))
        limit_value = float(limit_raw) if limit_raw not in (None, "") else 0.0
        card = Card(
            name=data.get("name") or data.get("nome"),
            limit=limit_value,
            bank=data.get("bank") or data.get("banco"),
            brand=data.get("brand") or data.get("bandeira"),
            closing_day=int(data.get("closing_day") or data.get("dia_fechamento") or 1),
            due_day=int(data.get("due_day") or data.get("dia_vencimento") or 1),
        )
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Dados inválidos para cartão. {exc}"}), 400
    card = create_card(card_repo, card)
    return jsonify(asdict(card)), 201


@app.put("/cartoes/<int:card_id>")
def put_card(card_id: int):
    existing = card_repo.get(card_id)
    if not existing:
        return jsonify({"error": "Cartão não encontrado."}), 404
    data = request.get_json(silent=True) or {}
    try:
        limit_raw = data.get("limit", data.get("limite"))
        limit_value = float(limit_raw) if limit_raw not in (None, "") else existing.limit
        payload = Card(
            id=card_id,
            name=data.get("name") or data.get("nome") or existing.name,
            limit=limit_value,
            bank=data.get("bank") or data.get("banco") or existing.bank,
            brand=data.get("brand") or data.get("bandeira") or existing.brand,
            closing_day=int(data.get("closing_day") or data.get("dia_fechamento") or existing.closing_day),
            due_day=int(data.get("due_day") or data.get("dia_vencimento") or existing.due_day),
        )
        card_repo.update(payload)
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Dados inválidos para cartão. {exc}"}), 400
    return jsonify(asdict(payload)), 200


@app.delete("/cartoes/<int:card_id>")
def delete_card(card_id: int):
    if not card_repo.get(card_id):
        return jsonify({"error": "Cartão não encontrado."}), 404
    has_installments = any(installment.card_id == card_id for installment in installment_repo.list())
    if has_installments:
        return jsonify({"error": "Não é possível excluir cartão com parcelas vinculadas."}), 409
    card_repo.delete(card_id)
    return jsonify({"message": "Cartão excluído com sucesso."}), 200


@app.get("/parcelas")
def get_installments():
    card_id = request.args.get("cartao_id", type=int) or request.args.get("card_id", type=int)
    month = request.args.get("mes", type=int)
    year = request.args.get("ano", type=int)
    installments = list_installments(installment_repo, card_id=card_id, month=month, year=year)
    return jsonify([asdict(installment) for installment in installments])


@app.get("/faturas")
def get_invoice():
    card_id = request.args.get("cartao_id", type=int) or request.args.get("card_id", type=int)
    month = request.args.get("mes", type=int)
    year = request.args.get("ano", type=int)
    if not card_id or not month or not year:
        return jsonify({"error": "cartao_id, mes e ano são obrigatórios."}), 400
    installments = list_installments(installment_repo, card_id=card_id, month=month, year=year)
    total = calculate_invoice([installment.value for installment in installments])
    return jsonify({"total": total, "parcelas": [asdict(item) for item in installments]})


@app.get("/recorrencias")
def get_recurrences():
    recurrences = list_recurrences(recurrence_repo)
    return jsonify([asdict(recurrence) for recurrence in recurrences])


@app.post("/recorrencias")
def post_recurrence():
    data = request.get_json(silent=True) or {}
    try:
        recurrence = Recurrence(
            kind=data.get("kind") or data.get("tipo"),
            name=data.get("name") or data.get("nome"),
            value=float(data.get("value") or data.get("valor")),
            start_month=int(data.get("start_month") or data.get("mes_inicio")),
            start_year=int(data.get("start_year") or data.get("ano_inicio")),
            interval_months=int(data.get("interval_months") or data.get("intervalo_meses") or 1),
            occurrences=int(data.get("occurrences") or data.get("ocorrencias") or 12),
            category_id=data.get("category_id") or data.get("categoria_id"),
            payment_method=data.get("payment_method") or data.get("forma"),
            confirmed=data.get("confirmed"),
            notes=data.get("notes") or data.get("observacao"),
        )
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Dados inválidos para recorrência. {exc}"}), 400
    recurrence = create_recurrence(recurrence_repo, recurrence)
    return jsonify(asdict(recurrence)), 201


@app.put("/recorrencias/<int:recurrence_id>")
def put_recurrence(recurrence_id: int):
    existing = recurrence_repo.get(recurrence_id)
    if not existing:
        return jsonify({"error": "Recorrência não encontrada."}), 404
    data = request.get_json(silent=True) or {}
    try:
        confirmed_raw = data.get("confirmed")
        payload = Recurrence(
            id=recurrence_id,
            kind=data.get("kind") or data.get("tipo") or existing.kind,
            name=data.get("name") or data.get("nome") or existing.name,
            value=float(data.get("value") or data.get("valor") or existing.value),
            start_month=int(data.get("start_month") or data.get("mes_inicio") or existing.start_month),
            start_year=int(data.get("start_year") or data.get("ano_inicio") or existing.start_year),
            interval_months=int(data.get("interval_months") or data.get("intervalo_meses") or existing.interval_months),
            occurrences=int(data.get("occurrences") or data.get("ocorrencias") or existing.occurrences),
            category_id=data.get("category_id") or data.get("categoria_id") or existing.category_id,
            payment_method=data.get("payment_method") or data.get("forma") or existing.payment_method,
            confirmed=_parse_optional_bool(confirmed_raw) if confirmed_raw is not None else existing.confirmed,
            notes=data.get("notes") or data.get("observacao") or existing.notes,
        )
        recurrence_repo.update(payload)
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Dados inválidos para recorrência. {exc}"}), 400
    return jsonify(asdict(payload)), 200


@app.delete("/recorrencias/<int:recurrence_id>")
def delete_recurrence(recurrence_id: int):
    if not recurrence_repo.get(recurrence_id):
        return jsonify({"error": "Recorrência não encontrada."}), 404
    recurrence_repo.delete(recurrence_id)
    for expense in expense_repo.list():
        if expense.recurrence_id == recurrence_id:
            expense_repo.delete(expense.id)
    return jsonify({"message": "Recorrência excluída com sucesso."}), 200


@app.post("/recorrencias/aplicar")
def apply_recurrence_endpoint():
    data = request.get_json(silent=True) or {}
    recurrence_id = data.get("id")
    if not recurrence_id:
        return jsonify({"error": "ID da recorrência é obrigatório."}), 400
    recurrence = recurrence_repo.get(int(recurrence_id))
    if not recurrence:
        return jsonify({"error": "Recorrência não encontrada."}), 404
    expenses, incomes = apply_recurrence(recurrence, expense_repo, income_repo)
    return jsonify({"expenses": [asdict(e) for e in expenses], "incomes": [asdict(i) for i in incomes]})


@app.get("/metas")
def get_goals():
    month = request.args.get("mes", type=int)
    year = request.args.get("ano", type=int)
    goals = list_goals(goal_repo, month=month, year=year)
    return jsonify([asdict(goal) for goal in goals])


@app.post("/metas")
def post_goal():
    data = request.get_json(silent=True) or {}
    try:
        goal = Goal(
            name=data.get("name") or data.get("nome"),
            limit_value=float(data.get("limit_value") or data.get("valor_limite")),
            month=int(data.get("month") or data.get("mes")),
            year=int(data.get("year") or data.get("ano")),
            category_id=data.get("category_id") or data.get("categoria_id"),
        )
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Dados inválidos para meta. {exc}"}), 400
    goal = create_goal(goal_repo, goal)
    return jsonify(asdict(goal)), 201


@app.put("/metas/<int:goal_id>")
def put_goal(goal_id: int):
    existing = goal_repo.get(goal_id)
    if not existing:
        return jsonify({"error": "Meta não encontrada."}), 404
    data = request.get_json(silent=True) or {}
    try:
        payload = Goal(
            id=goal_id,
            name=data.get("name") or data.get("nome") or existing.name,
            limit_value=float(data.get("limit_value") or data.get("valor_limite") or existing.limit_value),
            month=int(data.get("month") or data.get("mes") or existing.month),
            year=int(data.get("year") or data.get("ano") or existing.year),
            category_id=data.get("category_id") or data.get("categoria_id") or existing.category_id,
        )
        goal_repo.update(payload)
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Dados inválidos para meta. {exc}"}), 400
    return jsonify(asdict(payload)), 200


@app.delete("/metas/<int:goal_id>")
def delete_goal(goal_id: int):
    if not goal_repo.get(goal_id):
        return jsonify({"error": "Meta não encontrada."}), 404
    goal_repo.delete(goal_id)
    return jsonify({"message": "Meta excluída com sucesso."}), 200


@app.get("/relatorios/mes")
def report_month():
    month = request.args.get("mes", type=int)
    year = request.args.get("ano", type=int)
    if not month or not year:
        return jsonify({"error": "mes e ano são obrigatórios."}), 400
    report = build_month_report(month, year)
    return jsonify(report)


def build_month_report(month: int, year: int) -> dict:
    expenses = list_expenses(expense_repo, month=month, year=year)
    incomes = list_incomes(income_repo, month=month, year=year)
    categories = {category.id: category.name for category in list_categories(category_repo)}
    total_expenses = sum(expense.value for expense in expenses)
    total_incomes = sum(income.value for income in incomes)
    by_category = {}
    for expense in expenses:
        label = categories.get(expense.category_id, "Sem categoria")
        by_category[label] = by_category.get(label, 0) + expense.value
    goals = list_goals(goal_repo, month=month, year=year)
    goal_status = []
    for goal in goals:
        if goal.category_id:
            spent = sum(exp.value for exp in expenses if exp.category_id == goal.category_id)
        else:
            spent = total_expenses
        goal_status.append(
            {
                "id": goal.id,
                "name": goal.name,
                "limit_value": goal.limit_value,
                "spent": round(spent, 2),
                "remaining": round(goal.limit_value - spent, 2),
            }
        )
    return {
        "month": month,
        "year": year,
        "total_expenses": round(total_expenses, 2),
        "total_incomes": round(total_incomes, 2),
        "balance": round(total_incomes - total_expenses, 2),
        "by_category": by_category,
        "goals": goal_status,
    }


@app.get("/relatorios/mes/csv")
def report_month_csv():
    month = request.args.get("mes", type=int)
    year = request.args.get("ano", type=int)
    if not month or not year:
        return jsonify({"error": "mes e ano são obrigatórios."}), 400
    report = build_month_report(month, year)
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["tipo", "nome", "valor", "extra"])
    writer.writerow(["total", "Total de gastos", report["total_expenses"], ""])
    writer.writerow(["total", "Total de entradas", report["total_incomes"], ""])
    writer.writerow(["total", "Saldo", report["balance"], ""])
    for name, value in report["by_category"].items():
        writer.writerow(["categoria", name, value, ""])
    for goal in report["goals"]:
        writer.writerow(
            ["meta", goal["name"], goal["spent"], f"limite={goal['limit_value']}; restante={goal['remaining']}"]
        )
    output = BytesIO(buffer.getvalue().encode("utf-8"))
    filename = f"relatorio_{month:02d}_{year}.csv"
    return send_file(output, mimetype="text/csv", as_attachment=True, download_name=filename)


@app.get("/relatorios/mes/pdf")
def report_month_pdf():
    month = request.args.get("mes", type=int)
    year = request.args.get("ano", type=int)
    if not month or not year:
        return jsonify({"error": "mes e ano são obrigatórios."}), 400
    report = build_month_report(month, year)
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, f"Relatório mensal {month:02d}/{year}")
    y -= 30
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Total de gastos: R$ {report['total_expenses']:.2f}")
    y -= 18
    pdf.drawString(50, y, f"Total de entradas: R$ {report['total_incomes']:.2f}")
    y -= 18
    pdf.drawString(50, y, f"Saldo: R$ {report['balance']:.2f}")
    y -= 28
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Gastos por categoria")
    y -= 18
    pdf.setFont("Helvetica", 11)
    if report["by_category"]:
        for name, value in report["by_category"].items():
            pdf.drawString(60, y, f"- {name}: R$ {value:.2f}")
            y -= 16
            if y < 80:
                pdf.showPage()
                y = height - 50
    else:
        pdf.drawString(60, y, "Sem registros.")
        y -= 18
    y -= 10
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Metas do mês")
    y -= 18
    pdf.setFont("Helvetica", 11)
    if report["goals"]:
        for goal in report["goals"]:
            pdf.drawString(
                60,
                y,
                f"- {goal['name']}: gasto R$ {goal['spent']:.2f} / limite R$ {goal['limit_value']:.2f}",
            )
            y -= 16
            if y < 80:
                pdf.showPage()
                y = height - 50
    else:
        pdf.drawString(60, y, "Sem metas.")
        y -= 18
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    filename = f"relatorio_{month:02d}_{year}.pdf"
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=filename)


@app.post("/backup")
def backup_database():
    if not os.path.exists(DB_PATH):
        return jsonify({"error": "Banco de dados não encontrado."}), 404
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"saveyourmoney_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    with open(DB_PATH, "rb") as source, open(backup_path, "wb") as target:
        target.write(source.read())
    return jsonify({"backup": backup_name, "path": backup_path}), 201


if __name__ == "__main__":
    debug_mode = os.environ.get("SAVEYOURMONEY_DEBUG") == "1"
    app.run(port=5000, debug=debug_mode, use_reloader=debug_mode)

from __future__ import annotations

from dataclasses import asdict

from flask import Blueprint, jsonify, request

from .. import state
from ..domain.entities import Installment, Recurrence
from ..errors import bad_request, not_found
from ..routes.utils import ensure_card_exists, ensure_category_exists
from ..schemas.common import parse_cancel_scope, parse_edit_scope, parse_optional_int
from ..schemas.expenses import ExpenseCreate, ExpenseUpdate
from ..use_cases.create_expense import create_expense
from ..use_cases.create_installments import create_installments
from ..use_cases.create_recurrence import create_recurrence
from ..use_cases.list_expenses import list_expenses
from ..services.finance_service import generate_installments

bp = Blueprint("expenses", __name__)


@bp.get("/gastos")
def get_expenses():
    month = request.args.get("mes", type=int)
    year = request.args.get("ano", type=int)
    recurring_filter = (request.args.get("recorrente") or "todos").strip().lower()
    expenses = list_expenses(state.expense_repo, month=month, year=year)
    if recurring_filter == "sim":
        expenses = [item for item in expenses if item.recurrence_id is not None]
    elif recurring_filter == "nao":
        expenses = [item for item in expenses if item.recurrence_id is None]
    return jsonify([asdict(expense) for expense in expenses])


@bp.post("/gastos")
def post_expense():
    data = request.get_json(silent=True) or {}
    try:
        expense_payload = ExpenseCreate.from_payload(data)
        ensure_category_exists(expense_payload.category_id)
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
                start_index = expense_payload.year * 12 + expense_payload.month
                end_index = end_year * 12 + end_month
                total_months = max(end_index - start_index, 0)
                occurrences = max((total_months // interval_months) + 1, 1)
            created_recurrence = create_recurrence(
                state.recurrence_repo,
                Recurrence(
                    kind="expense",
                    name=expense_payload.name,
                    value=expense_payload.value,
                    start_month=expense_payload.month,
                    start_year=expense_payload.year,
                    interval_months=interval_months,
                    occurrences=occurrences,
                    category_id=expense_payload.category_id,
                    payment_method=expense_payload.payment_method,
                    notes=expense_payload.notes,
                ),
            )
            recurrence_id = created_recurrence.id

        expense = create_expense(state.expense_repo, expense_payload.to_entity(recurrence_id))
    except (TypeError, ValueError) as exc:
        raise bad_request(f"Dados inválidos para gasto. {exc}")

    installments_payload = data.get("installments") or data.get("parcelas")
    if installments_payload:
        card_id = parse_optional_int(
            installments_payload.get("card_id") or installments_payload.get("cartao_id"),
            "Cartão",
        )
        num_installments = int(installments_payload.get("total") or installments_payload.get("total_parcelas") or 1)
        if not card_id:
            raise bad_request("cartao_id é obrigatório para parcelas.")
        try:
            ensure_card_exists(card_id)
        except ValueError as exc:
            raise bad_request(str(exc))
        values = generate_installments(expense.value, num_installments)
        created_installments = []
        month = expense.month
        year = expense.year
        for index, value in enumerate(values, start=1):
            installment = Installment(
                card_id=card_id,
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
        create_installments(state.installment_repo, created_installments)
    return jsonify(asdict(expense)), 201


@bp.put("/gastos/<int:expense_id>")
def put_expense(expense_id: int):
    existing = state.expense_repo.get(expense_id)
    if not existing:
        raise not_found("Gasto não encontrado.")
    data = request.get_json(silent=True) or {}
    try:
        scope = parse_edit_scope(data.get("scope"))
        payload = ExpenseUpdate.from_payload(data, existing)
        ensure_category_exists(payload.category_id)
        entity = payload.to_entity(expense_id, existing.recurrence_id)
        state.expense_repo.update(entity)
        if scope == "future" and existing.recurrence_id:
            recurrence = state.recurrence_repo.get(existing.recurrence_id)
            if recurrence:
                recurrence.name = entity.name
                recurrence.value = entity.value
                recurrence.category_id = entity.category_id
                recurrence.payment_method = entity.payment_method
                recurrence.notes = entity.notes
                state.recurrence_repo.update(recurrence)
    except (TypeError, ValueError) as exc:
        raise bad_request(f"Dados inválidos para gasto. {exc}")
    return jsonify(asdict(entity)), 200


@bp.delete("/gastos/<int:expense_id>")
def delete_expense(expense_id: int):
    existing = state.expense_repo.get(expense_id)
    if not existing:
        raise not_found("Gasto não encontrado.")
    data = request.get_json(silent=True) or {}
    try:
        scope = parse_cancel_scope(data.get("scope"))
    except ValueError as exc:
        raise bad_request(str(exc))
    if existing.recurrence_id and scope in {"future", "all"}:
        state.recurrence_repo.delete(existing.recurrence_id)
        for expense in state.expense_repo.list():
            if expense.recurrence_id == existing.recurrence_id:
                state.expense_repo.delete(expense.id)
        return jsonify({"message": "Recorrência cancelada com sucesso."}), 200
    state.expense_repo.delete(expense_id)
    return jsonify({"message": "Gasto excluído com sucesso."}), 200

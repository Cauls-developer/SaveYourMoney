from __future__ import annotations

from dataclasses import asdict

from flask import Blueprint, jsonify, request

from .. import state
from ..errors import bad_request, not_found
from ..routes.utils import ensure_category_exists
from ..schemas.recurrences import RecurrenceCreate, RecurrenceUpdate
from ..use_cases.apply_recurrence import apply_recurrence
from ..use_cases.create_recurrence import create_recurrence
from ..use_cases.list_recurrences import list_recurrences

bp = Blueprint("recurrences", __name__)


@bp.get("/recorrencias")
def get_recurrences():
    recurrences = list_recurrences(state.recurrence_repo)
    return jsonify([asdict(recurrence) for recurrence in recurrences])


@bp.post("/recorrencias")
def post_recurrence():
    data = request.get_json(silent=True) or {}
    try:
        payload = RecurrenceCreate.from_payload(data)
        ensure_category_exists(payload.category_id)
        recurrence = create_recurrence(state.recurrence_repo, payload.to_entity())
    except (TypeError, ValueError) as exc:
        raise bad_request(f"Dados inválidos para recorrência. {exc}")
    return jsonify(asdict(recurrence)), 201


@bp.put("/recorrencias/<int:recurrence_id>")
def put_recurrence(recurrence_id: int):
    existing = state.recurrence_repo.get(recurrence_id)
    if not existing:
        raise not_found("Recorrência não encontrada.")
    data = request.get_json(silent=True) or {}
    try:
        payload = RecurrenceUpdate.from_payload(data, existing)
        ensure_category_exists(payload.category_id)
        updated = payload.to_entity(recurrence_id)
        state.recurrence_repo.update(updated)
    except (TypeError, ValueError) as exc:
        raise bad_request(f"Dados inválidos para recorrência. {exc}")
    return jsonify(asdict(updated)), 200


@bp.delete("/recorrencias/<int:recurrence_id>")
def delete_recurrence(recurrence_id: int):
    if not state.recurrence_repo.get(recurrence_id):
        raise not_found("Recorrência não encontrada.")
    state.recurrence_repo.delete(recurrence_id)
    for expense in state.expense_repo.list():
        if expense.recurrence_id == recurrence_id:
            state.expense_repo.delete(expense.id)
    return jsonify({"message": "Recorrência excluída com sucesso."}), 200


@bp.post("/recorrencias/aplicar")
def apply_recurrence_endpoint():
    data = request.get_json(silent=True) or {}
    recurrence_id = data.get("id")
    if not recurrence_id:
        raise bad_request("ID da recorrência é obrigatório.")
    recurrence = state.recurrence_repo.get(int(recurrence_id))
    if not recurrence:
        raise not_found("Recorrência não encontrada.")
    expenses, incomes = apply_recurrence(recurrence, state.expense_repo, state.income_repo)
    return jsonify({"expenses": [asdict(e) for e in expenses], "incomes": [asdict(i) for i in incomes]})

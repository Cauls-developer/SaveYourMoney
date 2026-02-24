from __future__ import annotations

from dataclasses import asdict

from flask import Blueprint, jsonify, request

from .. import state
from ..errors import bad_request, not_found
from ..schemas.incomes import IncomeCreate, IncomeUpdate
from ..use_cases.create_income import create_income
from ..use_cases.list_incomes import list_incomes

bp = Blueprint("incomes", __name__)


@bp.get("/entradas")
def get_incomes():
    month = request.args.get("mes", type=int)
    year = request.args.get("ano", type=int)
    incomes = list_incomes(state.income_repo, month=month, year=year)
    return jsonify([asdict(income) for income in incomes])


@bp.post("/entradas")
def post_income():
    data = request.get_json(silent=True) or {}
    try:
        payload = IncomeCreate.from_payload(data)
        income = create_income(state.income_repo, payload.to_entity())
    except (TypeError, ValueError) as exc:
        raise bad_request(f"Dados inválidos para entrada. {exc}")
    return jsonify(asdict(income)), 201


@bp.put("/entradas/<int:income_id>")
def put_income(income_id: int):
    existing = state.income_repo.get(income_id)
    if not existing:
        raise not_found("Entrada não encontrada.")
    data = request.get_json(silent=True) or {}
    try:
        payload = IncomeUpdate.from_payload(data, existing)
        updated = payload.to_entity(income_id)
        state.income_repo.update(updated)
    except (TypeError, ValueError) as exc:
        raise bad_request(f"Dados inválidos para entrada. {exc}")
    return jsonify(asdict(updated)), 200


@bp.delete("/entradas/<int:income_id>")
def delete_income(income_id: int):
    if not state.income_repo.get(income_id):
        raise not_found("Entrada não encontrada.")
    state.income_repo.delete(income_id)
    return jsonify({"message": "Entrada excluída com sucesso."}), 200

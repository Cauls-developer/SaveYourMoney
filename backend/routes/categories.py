from __future__ import annotations

from dataclasses import asdict

from flask import Blueprint, jsonify, request

from .. import state
from ..errors import bad_request, conflict, not_found
from ..schemas.categories import CategoryCreate, CategoryUpdate
from ..use_cases.create_category import create_category
from ..use_cases.list_categories import list_categories

bp = Blueprint("categories", __name__)


@bp.get("/categorias")
def get_categories():
    categories = list_categories(state.category_repo)
    return jsonify([asdict(category) for category in categories])


@bp.post("/categorias")
def post_category():
    data = request.get_json(silent=True) or {}
    try:
        payload = CategoryCreate.from_payload(data)
        category = create_category(state.category_repo, payload.to_entity())
    except ValueError as exc:
        raise bad_request(str(exc))
    return jsonify(asdict(category)), 201


@bp.put("/categorias/<int:category_id>")
def put_category(category_id: int):
    existing = state.category_repo.get(category_id)
    if not existing:
        raise not_found("Categoria não encontrada.")
    data = request.get_json(silent=True) or {}
    try:
        payload = CategoryUpdate.from_payload(data, existing)
        updated = payload.to_entity(category_id)
    except ValueError as exc:
        raise bad_request(str(exc))
    state.category_repo.update(updated)
    return jsonify(asdict(updated)), 200


@bp.delete("/categorias/<int:category_id>")
def delete_category(category_id: int):
    if not state.category_repo.get(category_id):
        raise not_found("Categoria não encontrada.")
    has_expense_link = any(exp.category_id == category_id for exp in state.expense_repo.list())
    has_recurrence_link = any(rec.category_id == category_id for rec in state.recurrence_repo.list())
    has_goal_link = any(goal.category_id == category_id for goal in state.goal_repo.list())
    if has_expense_link or has_recurrence_link or has_goal_link:
        raise conflict("Não é possível excluir categoria com itens vinculados.")
    state.category_repo.delete(category_id)
    return jsonify({"message": "Categoria excluída com sucesso."}), 200

from __future__ import annotations

from dataclasses import asdict

from flask import Blueprint, jsonify, request

from .. import state
from ..errors import bad_request, not_found
from ..routes.utils import ensure_category_exists
from ..schemas.goals import GoalCreate, GoalUpdate
from ..use_cases.create_goal import create_goal
from ..use_cases.list_goals import list_goals

bp = Blueprint("goals", __name__)


@bp.get("/metas")
def get_goals():
    month = request.args.get("mes", type=int)
    year = request.args.get("ano", type=int)
    goals = list_goals(state.goal_repo, month=month, year=year)
    return jsonify([asdict(goal) for goal in goals])


@bp.post("/metas")
def post_goal():
    data = request.get_json(silent=True) or {}
    try:
        payload = GoalCreate.from_payload(data)
        ensure_category_exists(payload.category_id)
        goal = create_goal(state.goal_repo, payload.to_entity())
    except (TypeError, ValueError) as exc:
        raise bad_request(f"Dados inválidos para meta. {exc}")
    return jsonify(asdict(goal)), 201


@bp.put("/metas/<int:goal_id>")
def put_goal(goal_id: int):
    existing = state.goal_repo.get(goal_id)
    if not existing:
        raise not_found("Meta não encontrada.")
    data = request.get_json(silent=True) or {}
    try:
        payload = GoalUpdate.from_payload(data, existing)
        ensure_category_exists(payload.category_id)
        updated = payload.to_entity(goal_id)
        state.goal_repo.update(updated)
    except (TypeError, ValueError) as exc:
        raise bad_request(f"Dados inválidos para meta. {exc}")
    return jsonify(asdict(updated)), 200


@bp.delete("/metas/<int:goal_id>")
def delete_goal(goal_id: int):
    if not state.goal_repo.get(goal_id):
        raise not_found("Meta não encontrada.")
    state.goal_repo.delete(goal_id)
    return jsonify({"message": "Meta excluída com sucesso."}), 200

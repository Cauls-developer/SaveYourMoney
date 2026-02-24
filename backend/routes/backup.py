from __future__ import annotations

import os
from datetime import datetime

from flask import Blueprint, jsonify, request

from .. import state
from ..errors import bad_request, not_found
from ..services.backup_service import BackupValidationError, export_backup_payload, restore_backup_payload
from ..use_cases.list_cards import list_cards
from ..use_cases.list_categories import list_categories
from ..use_cases.list_expenses import list_expenses
from ..use_cases.list_goals import list_goals
from ..use_cases.list_incomes import list_incomes
from ..use_cases.list_installments import list_installments
from ..use_cases.list_recurrences import list_recurrences

bp = Blueprint("backup", __name__)


@bp.get("/backup/exportar")
def export_backup():
    payload = export_backup_payload(
        cards=list_cards(state.card_repo),
        categories=list_categories(state.category_repo),
        expenses=list_expenses(state.expense_repo),
        goals=list_goals(state.goal_repo),
        incomes=list_incomes(state.income_repo),
        installments=list_installments(state.installment_repo),
        recurrences=list_recurrences(state.recurrence_repo),
    )
    return jsonify(payload)


@bp.post("/backup/restaurar")
def restore_backup():
    data = request.get_json(silent=True)
    if data is None:
        raise bad_request("Envie um JSON de backup válido.")
    try:
        counts = restore_backup_payload(state.DB_PATH, data)
    except BackupValidationError as exc:
        raise bad_request(str(exc))
    except Exception:
        return jsonify({"error": "Não foi possível restaurar o backup. Verifique se o arquivo é válido."}), 500
    return jsonify({"message": "Backup restaurado com sucesso.", "imported": counts}), 200


@bp.post("/backup")
def backup_database():
    if not state.DB_PATH or not os.path.exists(state.DB_PATH):
        raise not_found("Banco de dados não encontrado.")
    os.makedirs(state.BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"saveyourmoney_{timestamp}.db"
    backup_path = os.path.join(state.BACKUP_DIR, backup_name)
    with open(state.DB_PATH, "rb") as source, open(backup_path, "wb") as target:
        target.write(source.read())
    return jsonify({"backup": backup_name, "path": backup_path}), 201

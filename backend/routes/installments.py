from __future__ import annotations

from dataclasses import asdict

from flask import Blueprint, jsonify, request

from .. import state
from ..errors import bad_request
from ..services.finance_service import calculate_invoice
from ..use_cases.list_installments import list_installments

bp = Blueprint("installments", __name__)


@bp.get("/parcelas")
def get_installments():
    card_id = request.args.get("cartao_id", type=int) or request.args.get("card_id", type=int)
    month = request.args.get("mes", type=int)
    year = request.args.get("ano", type=int)
    installments = list_installments(state.installment_repo, card_id=card_id, month=month, year=year)
    return jsonify([asdict(installment) for installment in installments])


@bp.get("/faturas")
def get_invoice():
    card_id = request.args.get("cartao_id", type=int) or request.args.get("card_id", type=int)
    month = request.args.get("mes", type=int)
    year = request.args.get("ano", type=int)
    if not card_id or not month or not year:
        raise bad_request("cartao_id, mes e ano são obrigatórios.")
    installments = list_installments(state.installment_repo, card_id=card_id, month=month, year=year)
    total = calculate_invoice([installment.value for installment in installments])
    return jsonify({"total": total, "parcelas": [asdict(item) for item in installments]})

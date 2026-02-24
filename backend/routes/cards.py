from __future__ import annotations

from dataclasses import asdict

from flask import Blueprint, jsonify, request

from .. import state
from ..errors import bad_request, conflict, not_found
from ..schemas.cards import CardCreate, CardUpdate
from ..use_cases.create_card import create_card
from ..use_cases.list_cards import list_cards

bp = Blueprint("cards", __name__)


@bp.get("/cartoes")
def get_cards():
    cards = list_cards(state.card_repo)
    return jsonify([asdict(card) for card in cards])


@bp.post("/cartoes")
def post_card():
    data = request.get_json(silent=True) or {}
    try:
        payload = CardCreate.from_payload(data)
        card = create_card(state.card_repo, payload.to_entity())
    except (TypeError, ValueError) as exc:
        raise bad_request(f"Dados inválidos para cartão. {exc}")
    return jsonify(asdict(card)), 201


@bp.put("/cartoes/<int:card_id>")
def put_card(card_id: int):
    existing = state.card_repo.get(card_id)
    if not existing:
        raise not_found("Cartão não encontrado.")
    data = request.get_json(silent=True) or {}
    try:
        payload = CardUpdate.from_payload(data, existing)
        updated = payload.to_entity(card_id)
        state.card_repo.update(updated)
    except (TypeError, ValueError) as exc:
        raise bad_request(f"Dados inválidos para cartão. {exc}")
    return jsonify(asdict(updated)), 200


@bp.delete("/cartoes/<int:card_id>")
def delete_card(card_id: int):
    if not state.card_repo.get(card_id):
        raise not_found("Cartão não encontrado.")
    has_installments = any(installment.card_id == card_id for installment in state.installment_repo.list())
    if has_installments:
        raise conflict("Não é possível excluir cartão com parcelas vinculadas.")
    state.card_repo.delete(card_id)
    return jsonify({"message": "Cartão excluído com sucesso."}), 200

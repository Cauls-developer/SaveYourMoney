"""Shared helpers for route handlers."""
from __future__ import annotations

from .. import state


def ensure_category_exists(category_id: int | None) -> None:
    if category_id is None:
        return
    if not state.category_repo or not state.category_repo.get(category_id):
        raise ValueError("Categoria não encontrada.")


def ensure_card_exists(card_id: int | None) -> None:
    if card_id is None:
        return
    if not state.card_repo or not state.card_repo.get(card_id):
        raise ValueError("Cartão não encontrado.")

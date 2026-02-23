"""Caso de uso para criação de um cartão."""
from ..domain.entities import Card
from ..repositories.base import Repository


def create_card(repo: Repository[Card], card: Card) -> Card:
    return repo.add(card)

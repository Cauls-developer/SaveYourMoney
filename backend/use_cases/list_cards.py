"""Caso de uso para listagem de cartões."""
from typing import List

from ..domain.entities import Card
from ..repositories.base import Repository


def list_cards(repo: Repository[Card]) -> List[Card]:
    return repo.list()

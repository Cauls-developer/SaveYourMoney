"""Caso de uso para criação de uma recorrência."""
from ..domain.entities import Recurrence
from ..repositories.base import Repository


def create_recurrence(repo: Repository[Recurrence], recurrence: Recurrence) -> Recurrence:
    return repo.add(recurrence)

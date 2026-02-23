"""Caso de uso para listagem de recorrências."""
from typing import List

from ..domain.entities import Recurrence
from ..repositories.base import Repository


def list_recurrences(repo: Repository[Recurrence]) -> List[Recurrence]:
    return repo.list()

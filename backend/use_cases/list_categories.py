"""Caso de uso para listagem de categorias."""
from typing import List

from ..domain.entities import Category
from ..repositories.base import Repository


def list_categories(repo: Repository[Category]) -> List[Category]:
    return repo.list()

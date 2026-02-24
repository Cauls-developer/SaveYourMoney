"""Caso de uso para criação de uma categoria."""
from ..domain.entities import Category
from ..repositories.base import Repository


def create_category(repo: Repository[Category], category: Category) -> Category:
    return repo.add(category)

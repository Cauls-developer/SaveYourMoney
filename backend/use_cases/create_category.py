"""Caso de uso para criação de uma categoria."""
from ..domain.entities import Category
from ..repositories.base import Repository


def create_category(repo: Repository[Category], name: str, description: str | None = None) -> Category:
    category = Category(name=name, description=description)
    return repo.add(category)

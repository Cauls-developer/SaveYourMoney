"""Caso de uso para criação de uma entrada de dinheiro."""
from ..domain.entities import Income
from ..repositories.base import Repository


def create_income(repo: Repository[Income], income: Income) -> Income:
    return repo.add(income)

"""Caso de uso para criação de um gasto."""
from ..domain.entities import Expense
from ..repositories.base import Repository


def create_expense(repo: Repository[Expense], expense: Expense) -> Expense:
    """Insere um novo gasto usando o repositório fornecido."""
    return repo.add(expense)

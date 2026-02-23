"""Caso de uso para listagem de entradas."""
from typing import List, Optional

from ..domain.entities import Income
from ..repositories.base import Repository


def list_incomes(repo: Repository[Income], month: Optional[int] = None, year: Optional[int] = None) -> List[Income]:
    incomes = repo.list()
    if month is None and year is None:
        return incomes
    return [
        income
        for income in incomes
        if (month is None or income.month == month) and (year is None or income.year == year)
    ]

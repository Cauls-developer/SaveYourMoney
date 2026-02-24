"""Caso de uso para listagem de gastos."""
from typing import List, Optional
from ..domain.entities import Expense
from ..repositories.base import Repository


def list_expenses(repo: Repository[Expense], month: Optional[int] = None, year: Optional[int] = None) -> List[Expense]:
    if hasattr(repo, "list_filtered"):
        return repo.list_filtered(month=month, year=year)  # type: ignore[attr-defined]
    expenses = repo.list()
    if month is None and year is None:
        return expenses
    return [
        expense
        for expense in expenses
        if (month is None or expense.month == month) and (year is None or expense.year == year)
    ]

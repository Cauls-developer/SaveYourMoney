"""Caso de uso para aplicar uma recorrência e gerar lançamentos."""
from __future__ import annotations

from typing import List, Tuple

from ..domain.entities import Expense, Income, Recurrence
from ..repositories.base import Repository
from ..services.finance_service import generate_competences


def apply_recurrence(
    recurrence: Recurrence,
    expense_repo: Repository[Expense],
    income_repo: Repository[Income],
) -> Tuple[List[Expense], List[Income]]:
    competences = generate_competences(
        start_month=recurrence.start_month,
        start_year=recurrence.start_year,
        interval_months=recurrence.interval_months,
        occurrences=recurrence.occurrences,
    )
    created_expenses: List[Expense] = []
    created_incomes: List[Income] = []
    if recurrence.kind == "expense":
        for competence in competences:
            expense = Expense(
                name=recurrence.name,
                value=recurrence.value,
                month=competence.month,
                year=competence.year,
                category_id=recurrence.category_id,
                payment_method=recurrence.payment_method or "debit",
                notes=recurrence.notes,
            )
            created_expenses.append(expense_repo.add(expense))
    else:
        for competence in competences:
            income = Income(
                name=recurrence.name,
                value=recurrence.value,
                month=competence.month,
                year=competence.year,
                confirmed=recurrence.confirmed if recurrence.confirmed is not None else True,
                notes=recurrence.notes,
            )
            created_incomes.append(income_repo.add(income))
    return created_expenses, created_incomes

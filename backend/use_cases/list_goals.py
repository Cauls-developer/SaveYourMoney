"""Caso de uso para listagem de metas."""
from typing import List, Optional

from ..domain.entities import Goal
from ..repositories.base import Repository


def list_goals(repo: Repository[Goal], month: Optional[int] = None, year: Optional[int] = None) -> List[Goal]:
    goals = repo.list()
    return [
        goal
        for goal in goals
        if (month is None or goal.month == month) and (year is None or goal.year == year)
    ]

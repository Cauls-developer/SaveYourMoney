"""Caso de uso para criação de uma meta."""
from ..domain.entities import Goal
from ..repositories.base import Repository


def create_goal(repo: Repository[Goal], goal: Goal) -> Goal:
    return repo.add(goal)

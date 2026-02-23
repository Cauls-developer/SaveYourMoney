"""Caso de uso para criação de parcelas no cartão."""
from typing import List

from ..domain.entities import Installment
from ..repositories.base import Repository


def create_installments(repo: Repository[Installment], installments: List[Installment]) -> List[Installment]:
    created: List[Installment] = []
    for installment in installments:
        created.append(repo.add(installment))
    return created

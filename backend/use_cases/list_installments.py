"""Caso de uso para listagem de parcelas."""
from typing import List, Optional

from ..domain.entities import Installment
from ..repositories.base import Repository


def list_installments(
    repo: Repository[Installment],
    card_id: Optional[int] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
) -> List[Installment]:
    if hasattr(repo, "list_filtered"):
        return repo.list_filtered(card_id=card_id, month=month, year=year)  # type: ignore[attr-defined]
    installments = repo.list()
    return [
        installment
        for installment in installments
        if (card_id is None or installment.card_id == card_id)
        and (month is None or installment.month == month)
        and (year is None or installment.year == year)
    ]

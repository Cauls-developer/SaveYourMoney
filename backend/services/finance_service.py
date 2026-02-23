"""Serviços de negócio relacionados a finanças.

Este módulo contém funções que realizam operações de domínio que vão além de
simples CRUD, como gerar parcelas ou calcular faturas. Estas funções são
simplificadas e servirão como base para implementações futuras mais robustas.
"""

from typing import List
from ..domain.value_objects import MonthlyCompetence


def generate_installments(total_value: float, num_installments: int) -> List[float]:
    """Divide um valor total em parcelas iguais.

    Args:
        total_value: valor total a ser parcelado.
        num_installments: número de parcelas.
    Returns:
        Lista de valores de cada parcela.
    """
    if num_installments <= 0:
        raise ValueError("Número de parcelas deve ser maior que zero.")
    installment_value = round(total_value / num_installments, 2)
    return [installment_value] * num_installments


def calculate_invoice(installments: List[float]) -> float:
    return round(sum(installments), 2)


def generate_competences(start_month: int, start_year: int, interval_months: int, occurrences: int) -> List[MonthlyCompetence]:
    competences: List[MonthlyCompetence] = []
    current = MonthlyCompetence(month=start_month, year=start_year)
    for _ in range(occurrences):
        competences.append(current)
        for _ in range(interval_months):
            current = current.next()
    return competences

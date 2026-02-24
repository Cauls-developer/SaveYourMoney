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
    base = round(total_value / num_installments, 2)
    installments = [base] * num_installments
    diff = round(total_value - sum(installments), 2)
    installments[-1] = round(installments[-1] + diff, 2)
    return installments


def calculate_invoice(installments: List[float]) -> float:
    return round(sum(installments), 2)


def calculate_basic(operation: str, a: float, b: float) -> float:
    if operation == "soma":
        return round(a + b, 2)
    if operation == "subtracao":
        return round(a - b, 2)
    if operation == "multiplicacao":
        return round(a * b, 2)
    if operation == "divisao":
        if b == 0:
            raise ValueError("Não é possível dividir por zero.")
        return round(a / b, 2)
    raise ValueError("Operação básica inválida.")


def calculate_simple_interest(principal: float, monthly_rate_percent: float, months: int) -> dict:
    rate = monthly_rate_percent / 100.0
    interest = principal * rate * months
    total = principal + interest
    return {
        "juros": round(interest, 2),
        "total": round(total, 2),
    }


def calculate_compound_interest(principal: float, monthly_rate_percent: float, months: int) -> dict:
    rate = monthly_rate_percent / 100.0
    total = principal * ((1 + rate) ** months)
    interest = total - principal
    return {
        "juros": round(interest, 2),
        "total": round(total, 2),
    }


def simulate_installment(principal: float, monthly_rate_percent: float, months: int) -> dict:
    if months <= 0:
        raise ValueError("Quantidade de parcelas deve ser maior que zero.")
    rate = monthly_rate_percent / 100.0
    if rate == 0:
        installment = principal / months
    else:
        installment = principal * (rate * ((1 + rate) ** months)) / (((1 + rate) ** months) - 1)
    total = installment * months
    return {
        "parcela": round(installment, 2),
        "total": round(total, 2),
        "juros": round(total - principal, 2),
    }


def calculate_discount(original_value: float, discount_percent: float) -> dict:
    discount_value = original_value * (discount_percent / 100.0)
    final_value = original_value - discount_value
    return {
        "desconto": round(discount_value, 2),
        "valor_final": round(final_value, 2),
    }


def calculate_monthly_return(principal: float, monthly_rate_percent: float) -> dict:
    gain = principal * (monthly_rate_percent / 100.0)
    return {
        "rendimento": round(gain, 2),
        "total": round(principal + gain, 2),
    }


def simulate_debt_payoff(debt_value: float, payment_per_month: float, monthly_rate_percent: float) -> dict:
    if payment_per_month <= 0:
        raise ValueError("Pagamento mensal deve ser maior que zero.")
    rate = monthly_rate_percent / 100.0
    current = debt_value
    paid_total = 0.0
    months = 0
    while current > 0 and months < 1200:
        current = current * (1 + rate)
        if payment_per_month <= current * rate:
            raise ValueError("Pagamento mensal insuficiente para quitar a dívida com essa taxa.")
        payment = min(payment_per_month, current)
        current -= payment
        paid_total += payment
        months += 1
    if current > 0:
        raise ValueError("Não foi possível calcular a quitação da dívida.")
    return {
        "meses": months,
        "total_pago": round(paid_total, 2),
        "juros_pago": round(paid_total - debt_value, 2),
    }


def generate_competences(start_month: int, start_year: int, interval_months: int, occurrences: int) -> List[MonthlyCompetence]:
    competences: List[MonthlyCompetence] = []
    current = MonthlyCompetence(month=start_month, year=start_year)
    for _ in range(occurrences):
        competences.append(current)
        for _ in range(interval_months):
            current = current.next()
    return competences

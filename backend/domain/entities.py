"""Definições de classes de domínio para o aplicativo Save Your Money."""
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Category:
    """Uma categoria de gastos (ex.: Alimentação, Transporte)."""
    name: str
    description: Optional[str] = None
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Nome da categoria é obrigatório.")

@dataclass
class Expense:
    """Representa um gasto, que pode ser à vista ou parcelado."""
    name: str
    value: float
    month: int  # 1-12
    year: int
    category_id: Optional[int] = None
    recurrence_id: Optional[int] = None
    payment_method: str = "debit"  # ou "credit"
    notes: Optional[str] = None
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Nome do gasto é obrigatório.")
        if self.value < 0:
            raise ValueError("Valor do gasto não pode ser negativo.")
        if not 1 <= self.month <= 12:
            raise ValueError("Mês do gasto deve estar entre 1 e 12.")
        if self.year <= 0:
            raise ValueError("Ano do gasto deve ser positivo.")

@dataclass
class Income:
    """Representa uma entrada de dinheiro (salário, bônus etc.)."""
    name: str
    value: float
    month: int
    year: int
    confirmed: bool = True
    notes: Optional[str] = None
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Nome da entrada é obrigatório.")
        if self.value < 0:
            raise ValueError("Valor da entrada não pode ser negativo.")
        if not 1 <= self.month <= 12:
            raise ValueError("Mês da entrada deve estar entre 1 e 12.")
        if self.year <= 0:
            raise ValueError("Ano da entrada deve ser positivo.")

@dataclass
class Card:
    """Representa um cartão de crédito."""
    name: str
    limit: float
    bank: Optional[str] = None
    brand: Optional[str] = None
    closing_day: int = 1
    due_day: int = 1
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Nome do cartão é obrigatório.")
        if self.limit < 0:
            raise ValueError("Limite do cartão não pode ser negativo.")
        if not 1 <= self.closing_day <= 31:
            raise ValueError("Dia de fechamento deve estar entre 1 e 31.")
        if not 1 <= self.due_day <= 31:
            raise ValueError("Dia de vencimento deve estar entre 1 e 31.")


@dataclass
class Installment:
    """Parcela de um gasto no cartão."""
    card_id: int
    expense_name: str
    installment_number: int
    total_installments: int
    value: float
    month: int
    year: int
    status: str = "pendente"
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if self.card_id <= 0:
            raise ValueError("Cartão inválido.")
        if not self.expense_name or not self.expense_name.strip():
            raise ValueError("Nome do gasto é obrigatório.")
        if self.value < 0:
            raise ValueError("Valor da parcela não pode ser negativo.")
        if self.installment_number <= 0 or self.total_installments <= 0:
            raise ValueError("Número de parcela inválido.")
        if self.installment_number > self.total_installments:
            raise ValueError("Parcela maior que o total.")
        if not 1 <= self.month <= 12:
            raise ValueError("Mês da parcela deve estar entre 1 e 12.")
        if self.year <= 0:
            raise ValueError("Ano da parcela deve ser positivo.")


@dataclass
class Recurrence:
    """Regra de recorrência para gerar gastos/entradas."""
    kind: str  # "expense" ou "income"
    name: str
    value: float
    start_month: int
    start_year: int
    interval_months: int = 1
    occurrences: int = 12
    category_id: Optional[int] = None
    payment_method: Optional[str] = None
    confirmed: Optional[bool] = None
    notes: Optional[str] = None
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if self.kind not in ("expense", "income"):
            raise ValueError("Tipo de recorrência inválido.")
        if not self.name or not self.name.strip():
            raise ValueError("Nome da recorrência é obrigatório.")
        if self.value < 0:
            raise ValueError("Valor da recorrência não pode ser negativo.")
        if not 1 <= self.start_month <= 12:
            raise ValueError("Mês inicial inválido.")
        if self.start_year <= 0:
            raise ValueError("Ano inicial inválido.")
        if self.interval_months <= 0:
            raise ValueError("Intervalo deve ser maior que zero.")
        if self.occurrences <= 0:
            raise ValueError("Ocorrências deve ser maior que zero.")


@dataclass
class Goal:
    """Meta financeira mensal."""
    name: str
    limit_value: float
    month: int
    year: int
    category_id: Optional[int] = None
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Nome da meta é obrigatório.")
        if self.limit_value <= 0:
            raise ValueError("Valor da meta deve ser positivo.")
        if not 1 <= self.month <= 12:
            raise ValueError("Mês da meta deve estar entre 1 e 12.")
        if self.year <= 0:
            raise ValueError("Ano da meta deve ser positivo.")

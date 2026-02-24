"""DTOs for expenses."""
from __future__ import annotations

from dataclasses import dataclass

from .common import parse_float, parse_int, parse_optional_int, parse_optional_str, parse_required_str, pick
from ..domain.entities import Expense


@dataclass(frozen=True)
class ExpenseCreate:
    name: str
    value: float
    month: int
    year: int
    category_id: int | None
    payment_method: str
    notes: str | None

    @classmethod
    def from_payload(cls, data: dict) -> "ExpenseCreate":
        name = parse_required_str(data, "name", "nome", field_name="Nome do gasto")
        return cls(
            name=name,
            value=parse_float(pick(data, "value", "valor"), "Valor"),
            month=parse_int(pick(data, "month", "mes"), "Mês"),
            year=parse_int(pick(data, "year", "ano"), "Ano"),
            category_id=parse_optional_int(pick(data, "category_id", "categoria_id"), "Categoria"),
            payment_method=str(pick(data, "payment_method", "forma", default="debit") or "debit"),
            notes=parse_optional_str(data, "notes", "observacao"),
        )

    def to_entity(self, recurrence_id: int | None) -> Expense:
        return Expense(
            name=self.name,
            value=self.value,
            month=self.month,
            year=self.year,
            category_id=self.category_id,
            recurrence_id=recurrence_id,
            payment_method=self.payment_method,
            notes=self.notes,
        )


@dataclass(frozen=True)
class ExpenseUpdate:
    name: str
    value: float
    month: int
    year: int
    category_id: int | None
    payment_method: str
    notes: str | None

    @classmethod
    def from_payload(cls, data: dict, existing: Expense) -> "ExpenseUpdate":
        return cls(
            name=pick(data, "name", "nome", default=existing.name),
            value=parse_float(pick(data, "value", "valor", default=existing.value), "Valor"),
            month=parse_int(pick(data, "month", "mes", default=existing.month), "Mês"),
            year=parse_int(pick(data, "year", "ano", default=existing.year), "Ano"),
            category_id=parse_optional_int(
                pick(data, "category_id", "categoria_id", default=existing.category_id),
                "Categoria",
            ),
            payment_method=pick(data, "payment_method", "forma", default=existing.payment_method),
            notes=pick(data, "notes", "observacao", default=existing.notes),
        )

    def to_entity(self, expense_id: int, recurrence_id: int | None) -> Expense:
        return Expense(
            id=expense_id,
            name=self.name,
            value=self.value,
            month=self.month,
            year=self.year,
            category_id=self.category_id,
            recurrence_id=recurrence_id,
            payment_method=self.payment_method,
            notes=self.notes,
        )

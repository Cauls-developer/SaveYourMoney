"""DTOs for incomes."""
from __future__ import annotations

from dataclasses import dataclass

from .common import parse_float, parse_int, parse_optional_bool, parse_optional_str, parse_required_str, pick
from ..domain.entities import Income


@dataclass(frozen=True)
class IncomeCreate:
    name: str
    value: float
    month: int
    year: int
    confirmed: bool
    notes: str | None

    @classmethod
    def from_payload(cls, data: dict) -> "IncomeCreate":
        name = parse_required_str(data, "name", "nome", field_name="Nome da entrada")
        value = parse_float(pick(data, "value", "valor"), "Valor")
        month = parse_int(pick(data, "month", "mes"), "Mês")
        year = parse_int(pick(data, "year", "ano"), "Ano")
        confirmed_raw = pick(data, "confirmed", "confirmado", default=True)
        confirmed = parse_optional_bool(confirmed_raw)
        if confirmed is None:
            confirmed = True
        notes = parse_optional_str(data, "notes", "observacao")
        return cls(name=name, value=value, month=month, year=year, confirmed=confirmed, notes=notes)

    def to_entity(self) -> Income:
        return Income(
            name=self.name,
            value=self.value,
            month=self.month,
            year=self.year,
            confirmed=self.confirmed,
            notes=self.notes,
        )


@dataclass(frozen=True)
class IncomeUpdate:
    name: str
    value: float
    month: int
    year: int
    confirmed: bool
    notes: str | None

    @classmethod
    def from_payload(cls, data: dict, existing: Income) -> "IncomeUpdate":
        confirmed_raw = pick(data, "confirmed", "confirmado", default=existing.confirmed)
        confirmed = parse_optional_bool(confirmed_raw) if confirmed_raw is not None else existing.confirmed
        return cls(
            name=pick(data, "name", "nome", default=existing.name),
            value=parse_float(pick(data, "value", "valor", default=existing.value), "Valor"),
            month=parse_int(pick(data, "month", "mes", default=existing.month), "Mês"),
            year=parse_int(pick(data, "year", "ano", default=existing.year), "Ano"),
            confirmed=confirmed,
            notes=pick(data, "notes", "observacao", default=existing.notes),
        )

    def to_entity(self, income_id: int) -> Income:
        return Income(
            id=income_id,
            name=self.name,
            value=self.value,
            month=self.month,
            year=self.year,
            confirmed=self.confirmed,
            notes=self.notes,
        )

"""DTOs for recurrences."""
from __future__ import annotations

from dataclasses import dataclass

from .common import parse_float, parse_int, parse_optional_bool, parse_optional_int, parse_optional_str, parse_required_str, pick
from ..domain.entities import Recurrence


@dataclass(frozen=True)
class RecurrenceCreate:
    kind: str
    name: str
    value: float
    start_month: int
    start_year: int
    interval_months: int
    occurrences: int
    category_id: int | None
    payment_method: str | None
    confirmed: bool | None
    notes: str | None

    @classmethod
    def from_payload(cls, data: dict) -> "RecurrenceCreate":
        kind = parse_required_str(data, "kind", "tipo", field_name="Tipo de recorrência")
        name = parse_required_str(data, "name", "nome", field_name="Nome da recorrência")
        return cls(
            kind=kind,
            name=name,
            value=parse_float(pick(data, "value", "valor"), "Valor"),
            start_month=parse_int(pick(data, "start_month", "mes_inicio"), "Mês inicial"),
            start_year=parse_int(pick(data, "start_year", "ano_inicio"), "Ano inicial"),
            interval_months=parse_int(
                pick(data, "interval_months", "intervalo_meses", default=1),
                "Intervalo de meses",
            ),
            occurrences=parse_int(pick(data, "occurrences", "ocorrencias", default=12), "Ocorrências"),
            category_id=parse_optional_int(pick(data, "category_id", "categoria_id"), "Categoria"),
            payment_method=parse_optional_str(data, "payment_method", "forma"),
            confirmed=parse_optional_bool(pick(data, "confirmed", "confirmado")),
            notes=parse_optional_str(data, "notes", "observacao"),
        )

    def to_entity(self) -> Recurrence:
        return Recurrence(
            kind=self.kind,
            name=self.name,
            value=self.value,
            start_month=self.start_month,
            start_year=self.start_year,
            interval_months=self.interval_months,
            occurrences=self.occurrences,
            category_id=self.category_id,
            payment_method=self.payment_method,
            confirmed=self.confirmed,
            notes=self.notes,
        )


@dataclass(frozen=True)
class RecurrenceUpdate:
    kind: str
    name: str
    value: float
    start_month: int
    start_year: int
    interval_months: int
    occurrences: int
    category_id: int | None
    payment_method: str | None
    confirmed: bool | None
    notes: str | None

    @classmethod
    def from_payload(cls, data: dict, existing: Recurrence) -> "RecurrenceUpdate":
        confirmed_raw = pick(data, "confirmed", "confirmado", default=existing.confirmed)
        confirmed = parse_optional_bool(confirmed_raw) if confirmed_raw is not None else existing.confirmed
        return cls(
            kind=pick(data, "kind", "tipo", default=existing.kind),
            name=pick(data, "name", "nome", default=existing.name),
            value=parse_float(pick(data, "value", "valor", default=existing.value), "Valor"),
            start_month=parse_int(pick(data, "start_month", "mes_inicio", default=existing.start_month), "Mês inicial"),
            start_year=parse_int(pick(data, "start_year", "ano_inicio", default=existing.start_year), "Ano inicial"),
            interval_months=parse_int(
                pick(data, "interval_months", "intervalo_meses", default=existing.interval_months),
                "Intervalo de meses",
            ),
            occurrences=parse_int(pick(data, "occurrences", "ocorrencias", default=existing.occurrences), "Ocorrências"),
            category_id=parse_optional_int(
                pick(data, "category_id", "categoria_id", default=existing.category_id),
                "Categoria",
            ),
            payment_method=pick(data, "payment_method", "forma", default=existing.payment_method),
            confirmed=confirmed,
            notes=pick(data, "notes", "observacao", default=existing.notes),
        )

    def to_entity(self, recurrence_id: int) -> Recurrence:
        return Recurrence(
            id=recurrence_id,
            kind=self.kind,
            name=self.name,
            value=self.value,
            start_month=self.start_month,
            start_year=self.start_year,
            interval_months=self.interval_months,
            occurrences=self.occurrences,
            category_id=self.category_id,
            payment_method=self.payment_method,
            confirmed=self.confirmed,
            notes=self.notes,
        )

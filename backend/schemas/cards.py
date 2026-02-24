"""DTOs for cards."""
from __future__ import annotations

from dataclasses import dataclass

from .common import parse_float, parse_int, parse_optional_str, parse_required_str, pick
from ..domain.entities import Card


@dataclass(frozen=True)
class CardCreate:
    name: str
    limit: float
    bank: str | None
    brand: str | None
    closing_day: int
    due_day: int

    @classmethod
    def from_payload(cls, data: dict) -> "CardCreate":
        name = parse_required_str(data, "name", "nome", field_name="Nome do cartão")
        limit_raw = pick(data, "limit", "limite", default=0)
        limit = 0.0 if limit_raw in ("", None) else parse_float(limit_raw, "Limite")
        return cls(
            name=name,
            limit=limit,
            bank=parse_optional_str(data, "bank", "banco"),
            brand=parse_optional_str(data, "brand", "bandeira"),
            closing_day=parse_int(pick(data, "closing_day", "dia_fechamento", default=1), "Dia de fechamento"),
            due_day=parse_int(pick(data, "due_day", "dia_vencimento", default=1), "Dia de vencimento"),
        )

    def to_entity(self) -> Card:
        return Card(
            name=self.name,
            limit=self.limit,
            bank=self.bank,
            brand=self.brand,
            closing_day=self.closing_day,
            due_day=self.due_day,
        )


@dataclass(frozen=True)
class CardUpdate:
    name: str
    limit: float
    bank: str | None
    brand: str | None
    closing_day: int
    due_day: int

    @classmethod
    def from_payload(cls, data: dict, existing: Card) -> "CardUpdate":
        limit_raw = pick(data, "limit", "limite", default=existing.limit)
        limit = existing.limit if limit_raw in ("", None) else parse_float(limit_raw, "Limite")
        return cls(
            name=pick(data, "name", "nome", default=existing.name),
            limit=limit,
            bank=pick(data, "bank", "banco", default=existing.bank),
            brand=pick(data, "brand", "bandeira", default=existing.brand),
            closing_day=parse_int(
                pick(data, "closing_day", "dia_fechamento", default=existing.closing_day),
                "Dia de fechamento",
            ),
            due_day=parse_int(
                pick(data, "due_day", "dia_vencimento", default=existing.due_day),
                "Dia de vencimento",
            ),
        )

    def to_entity(self, card_id: int) -> Card:
        return Card(
            id=card_id,
            name=self.name,
            limit=self.limit,
            bank=self.bank,
            brand=self.brand,
            closing_day=self.closing_day,
            due_day=self.due_day,
        )

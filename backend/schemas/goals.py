"""DTOs for goals."""
from __future__ import annotations

from dataclasses import dataclass

from .common import parse_float, parse_int, parse_optional_int, parse_required_str, pick
from ..domain.entities import Goal


@dataclass(frozen=True)
class GoalCreate:
    name: str
    limit_value: float
    month: int
    year: int
    category_id: int | None

    @classmethod
    def from_payload(cls, data: dict) -> "GoalCreate":
        name = parse_required_str(data, "name", "nome", field_name="Nome da meta")
        return cls(
            name=name,
            limit_value=parse_float(pick(data, "limit_value", "valor_limite"), "Valor limite"),
            month=parse_int(pick(data, "month", "mes"), "Mês"),
            year=parse_int(pick(data, "year", "ano"), "Ano"),
            category_id=parse_optional_int(pick(data, "category_id", "categoria_id"), "Categoria"),
        )

    def to_entity(self) -> Goal:
        return Goal(
            name=self.name,
            limit_value=self.limit_value,
            month=self.month,
            year=self.year,
            category_id=self.category_id,
        )


@dataclass(frozen=True)
class GoalUpdate:
    name: str
    limit_value: float
    month: int
    year: int
    category_id: int | None

    @classmethod
    def from_payload(cls, data: dict, existing: Goal) -> "GoalUpdate":
        return cls(
            name=pick(data, "name", "nome", default=existing.name),
            limit_value=parse_float(pick(data, "limit_value", "valor_limite", default=existing.limit_value), "Valor limite"),
            month=parse_int(pick(data, "month", "mes", default=existing.month), "Mês"),
            year=parse_int(pick(data, "year", "ano", default=existing.year), "Ano"),
            category_id=parse_optional_int(
                pick(data, "category_id", "categoria_id", default=existing.category_id),
                "Categoria",
            ),
        )

    def to_entity(self, goal_id: int) -> Goal:
        return Goal(
            id=goal_id,
            name=self.name,
            limit_value=self.limit_value,
            month=self.month,
            year=self.year,
            category_id=self.category_id,
        )

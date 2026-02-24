"""DTOs for categories."""
from __future__ import annotations

from dataclasses import dataclass

from .common import parse_optional_str, parse_required_str
from ..domain.entities import Category


@dataclass(frozen=True)
class CategoryCreate:
    name: str
    description: str | None

    @classmethod
    def from_payload(cls, data: dict) -> "CategoryCreate":
        name = parse_required_str(data, "name", "nome", field_name="Nome da categoria")
        description = parse_optional_str(data, "description", "descricao")
        return cls(name=name, description=description)

    def to_entity(self) -> Category:
        return Category(name=self.name, description=self.description)


@dataclass(frozen=True)
class CategoryUpdate:
    name: str
    description: str | None

    @classmethod
    def from_payload(cls, data: dict, existing: Category) -> "CategoryUpdate":
        name = parse_required_str(
            {"name": data.get("name", data.get("nome", existing.name))},
            "name",
            field_name="Nome da categoria",
        )
        description = data.get("description", data.get("descricao", existing.description))
        description = description if description not in ("", None) else None
        return cls(name=name, description=description)

    def to_entity(self, category_id: int) -> Category:
        return Category(id=category_id, name=self.name, description=self.description)

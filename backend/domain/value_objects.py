"""Objetos de valor utilizados no domínio."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Currency:
    code: str = "BRL"
    symbol: str = "R$"


@dataclass(frozen=True)
class MonthlyCompetence:
    month: int
    year: int

    def __post_init__(self) -> None:
        if not 1 <= self.month <= 12:
            raise ValueError("Mês deve estar entre 1 e 12.")
        if self.year <= 0:
            raise ValueError("Ano deve ser positivo.")

    def next(self) -> "MonthlyCompetence":
        if self.month == 12:
            return MonthlyCompetence(month=1, year=self.year + 1)
        return MonthlyCompetence(month=self.month + 1, year=self.year)

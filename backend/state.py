"""Shared state for repositories and storage paths."""
from __future__ import annotations

from typing import Optional

from .repositories.sqlite.categoria_repo import SQLiteCategoryRepository
from .repositories.sqlite.gasto_repo import SQLiteExpenseRepository
from .repositories.sqlite.entrada_repo import SQLiteIncomeRepository
from .repositories.sqlite.cartao_repo import SQLiteCardRepository
from .repositories.sqlite.parcela_repo import SQLiteInstallmentRepository
from .repositories.sqlite.recorrencia_repo import SQLiteRecurrenceRepository
from .repositories.sqlite.meta_repo import SQLiteGoalRepository

BASE_DATA_DIR: str | None = None
DB_PATH: str | None = None
BACKUP_DIR: str | None = None

category_repo: Optional[SQLiteCategoryRepository] = None
expense_repo: Optional[SQLiteExpenseRepository] = None
income_repo: Optional[SQLiteIncomeRepository] = None
card_repo: Optional[SQLiteCardRepository] = None
installment_repo: Optional[SQLiteInstallmentRepository] = None
recurrence_repo: Optional[SQLiteRecurrenceRepository] = None
goal_repo: Optional[SQLiteGoalRepository] = None

"""Implementação SQLite para o repositório de gastos."""
import sqlite3
from typing import Optional, List
from ...domain.entities import Expense
from ..base import Repository

class SQLiteExpenseRepository(Repository[Expense]):
    def __init__(self, db_path: str = "saveyourmoney.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                category_id INTEGER,
                recurrence_id INTEGER,
                payment_method TEXT,
                notes TEXT
            )
            """
        )
        cur.execute("PRAGMA table_info(expenses)")
        columns = {row[1] for row in cur.fetchall()}
        if "recurrence_id" not in columns:
            cur.execute("ALTER TABLE expenses ADD COLUMN recurrence_id INTEGER")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_expenses_month_year ON expenses(month, year)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_expenses_category_month_year ON expenses(category_id, month, year)")
        self.conn.commit()

    def add(self, entity: Expense) -> Expense:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO expenses (name, value, month, year, category_id, recurrence_id, payment_method, notes) VALUES (?,?,?,?,?,?,?,?)",
            (
                entity.name,
                entity.value,
                entity.month,
                entity.year,
                entity.category_id,
                entity.recurrence_id,
                entity.payment_method,
                entity.notes,
            ),
        )
        entity.id = cur.lastrowid
        self.conn.commit()
        return entity

    def get(self, entity_id: int) -> Optional[Expense]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, name, value, month, year, category_id, recurrence_id, payment_method, notes FROM expenses WHERE id=?",
            (entity_id,),
        )
        row = cur.fetchone()
        if row:
            return Expense(
                id=row[0],
                name=row[1],
                value=row[2],
                month=row[3],
                year=row[4],
                category_id=row[5],
                recurrence_id=row[6],
                payment_method=row[7],
                notes=row[8],
            )
        return None

    def list(self) -> List[Expense]:
        return self.list_filtered()

    def list_filtered(
        self,
        *,
        month: Optional[int] = None,
        year: Optional[int] = None,
        category_id: Optional[int] = None,
    ) -> List[Expense]:
        cur = self.conn.cursor()
        query = "SELECT id, name, value, month, year, category_id, recurrence_id, payment_method, notes FROM expenses"
        conditions = []
        params = []
        if month is not None:
            conditions.append("month=?")
            params.append(month)
        if year is not None:
            conditions.append("year=?")
            params.append(year)
        if category_id is not None:
            conditions.append("category_id=?")
            params.append(category_id)
        if conditions:
            query = f"{query} WHERE {' AND '.join(conditions)}"
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        return [
            Expense(
                id=r[0],
                name=r[1],
                value=r[2],
                month=r[3],
                year=r[4],
                category_id=r[5],
                recurrence_id=r[6],
                payment_method=r[7],
                notes=r[8],
            )
            for r in rows
        ]

    def update(self, entity: Expense) -> Expense:
        if entity.id is None:
            raise ValueError("Entidade precisa ter ID para ser atualizada.")
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE expenses SET name=?, value=?, month=?, year=?, category_id=?, recurrence_id=?, payment_method=?, notes=? WHERE id=?",
            (
                entity.name,
                entity.value,
                entity.month,
                entity.year,
                entity.category_id,
                entity.recurrence_id,
                entity.payment_method,
                entity.notes,
                entity.id,
            ),
        )
        self.conn.commit()
        return entity

    def delete(self, entity_id: int) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM expenses WHERE id=?", (entity_id,))
        self.conn.commit()

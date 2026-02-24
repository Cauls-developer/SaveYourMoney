"""Implementação SQLite para o repositório de entradas."""
import sqlite3
from typing import Optional, List

from ...domain.entities import Income
from ..base import Repository


class SQLiteIncomeRepository(Repository[Income]):
    def __init__(self, db_path: str = "saveyourmoney.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                confirmed INTEGER NOT NULL,
                notes TEXT
            )
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_incomes_month_year ON incomes(month, year)")
        self.conn.commit()

    def add(self, entity: Income) -> Income:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO incomes (name, value, month, year, confirmed, notes) VALUES (?,?,?,?,?,?)",
            (entity.name, entity.value, entity.month, entity.year, int(entity.confirmed), entity.notes),
        )
        entity.id = cur.lastrowid
        self.conn.commit()
        return entity

    def get(self, entity_id: int) -> Optional[Income]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, value, month, year, confirmed, notes FROM incomes WHERE id=?", (entity_id,))
        row = cur.fetchone()
        if row:
            return Income(
                id=row[0],
                name=row[1],
                value=row[2],
                month=row[3],
                year=row[4],
                confirmed=bool(row[5]),
                notes=row[6],
            )
        return None

    def list(self) -> List[Income]:
        return self.list_filtered()

    def list_filtered(self, *, month: Optional[int] = None, year: Optional[int] = None) -> List[Income]:
        cur = self.conn.cursor()
        query = "SELECT id, name, value, month, year, confirmed, notes FROM incomes"
        conditions = []
        params = []
        if month is not None:
            conditions.append("month=?")
            params.append(month)
        if year is not None:
            conditions.append("year=?")
            params.append(year)
        if conditions:
            query = f"{query} WHERE {' AND '.join(conditions)}"
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        return [
            Income(
                id=r[0],
                name=r[1],
                value=r[2],
                month=r[3],
                year=r[4],
                confirmed=bool(r[5]),
                notes=r[6],
            )
            for r in rows
        ]

    def update(self, entity: Income) -> Income:
        if entity.id is None:
            raise ValueError("Entidade precisa ter ID para ser atualizada.")
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE incomes SET name=?, value=?, month=?, year=?, confirmed=?, notes=? WHERE id=?",
            (entity.name, entity.value, entity.month, entity.year, int(entity.confirmed), entity.notes, entity.id),
        )
        self.conn.commit()
        return entity

    def delete(self, entity_id: int) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM incomes WHERE id=?", (entity_id,))
        self.conn.commit()

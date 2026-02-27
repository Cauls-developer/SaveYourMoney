"""Implementação SQLite para o repositório de metas."""
import sqlite3
from typing import Optional, List

from ...domain.entities import Goal
from ..base import Repository


class SQLiteGoalRepository(Repository[Goal]):
    def __init__(self, db_path: str = "saveyourmoney.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                limit_value REAL NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                category_id INTEGER
            )
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_goals_month_year_category ON goals(month, year, category_id)")
        self.conn.commit()

    def add(self, entity: Goal) -> Goal:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO goals (name, limit_value, month, year, category_id) VALUES (?,?,?,?,?)",
            (entity.name, entity.limit_value, entity.month, entity.year, entity.category_id),
        )
        entity.id = cur.lastrowid
        self.conn.commit()
        return entity

    def get(self, entity_id: int) -> Optional[Goal]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, limit_value, month, year, category_id FROM goals WHERE id=?", (entity_id,))
        row = cur.fetchone()
        if row:
            return Goal(
                id=row[0],
                name=row[1],
                limit_value=row[2],
                month=row[3],
                year=row[4],
                category_id=row[5],
            )
        return None

    def list(self) -> List[Goal]:
        return self.list_filtered()

    def list_filtered(
        self,
        *,
        month: Optional[int] = None,
        year: Optional[int] = None,
        category_id: Optional[int] = None,
    ) -> List[Goal]:
        cur = self.conn.cursor()
        query = "SELECT id, name, limit_value, month, year, category_id FROM goals"
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
            Goal(
                id=r[0],
                name=r[1],
                limit_value=r[2],
                month=r[3],
                year=r[4],
                category_id=r[5],
            )
            for r in rows
        ]

    def update(self, entity: Goal) -> Goal:
        if entity.id is None:
            raise ValueError("Entidade precisa ter ID para ser atualizada.")
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE goals SET name=?, limit_value=?, month=?, year=?, category_id=? WHERE id=?",
            (entity.name, entity.limit_value, entity.month, entity.year, entity.category_id, entity.id),
        )
        self.conn.commit()
        return entity

    def delete(self, entity_id: int) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM goals WHERE id=?", (entity_id,))
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

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
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, limit_value, month, year, category_id FROM goals")
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

"""Implementação SQLite para o repositório de cartões."""
import sqlite3
from typing import Optional, List

from ...domain.entities import Card
from ..base import Repository


class SQLiteCardRepository(Repository[Card]):
    def __init__(self, db_path: str = "saveyourmoney.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                limit_value REAL NOT NULL,
                bank TEXT,
                brand TEXT,
                closing_day INTEGER NOT NULL,
                due_day INTEGER NOT NULL
            )
            """
        )
        self.conn.commit()

    def add(self, entity: Card) -> Card:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO cards (name, limit_value, bank, brand, closing_day, due_day) VALUES (?,?,?,?,?,?)",
            (entity.name, entity.limit, entity.bank, entity.brand, entity.closing_day, entity.due_day),
        )
        entity.id = cur.lastrowid
        self.conn.commit()
        return entity

    def get(self, entity_id: int) -> Optional[Card]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, name, limit_value, bank, brand, closing_day, due_day FROM cards WHERE id=?",
            (entity_id,),
        )
        row = cur.fetchone()
        if row:
            return Card(
                id=row[0],
                name=row[1],
                limit=row[2],
                bank=row[3],
                brand=row[4],
                closing_day=row[5],
                due_day=row[6],
            )
        return None

    def list(self) -> List[Card]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, limit_value, bank, brand, closing_day, due_day FROM cards")
        rows = cur.fetchall()
        return [
            Card(
                id=r[0],
                name=r[1],
                limit=r[2],
                bank=r[3],
                brand=r[4],
                closing_day=r[5],
                due_day=r[6],
            )
            for r in rows
        ]

    def update(self, entity: Card) -> Card:
        if entity.id is None:
            raise ValueError("Entidade precisa ter ID para ser atualizada.")
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE cards SET name=?, limit_value=?, bank=?, brand=?, closing_day=?, due_day=? WHERE id=?",
            (entity.name, entity.limit, entity.bank, entity.brand, entity.closing_day, entity.due_day, entity.id),
        )
        self.conn.commit()
        return entity

    def delete(self, entity_id: int) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM cards WHERE id=?", (entity_id,))
        self.conn.commit()

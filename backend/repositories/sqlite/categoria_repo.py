"""Implementação SQLite para o repositório de categorias."""
import sqlite3
from typing import Optional, List

from ...domain.entities import Category
from ..base import Repository


class SQLiteCategoryRepository(Repository[Category]):
    def __init__(self, db_path: str = "saveyourmoney.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
            """
        )
        self.conn.commit()

    def add(self, entity: Category) -> Category:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO categories (name, description) VALUES (?, ?)",
            (entity.name, entity.description),
        )
        entity.id = cur.lastrowid
        self.conn.commit()
        return entity

    def get(self, entity_id: int) -> Optional[Category]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, description FROM categories WHERE id=?", (entity_id,))
        row = cur.fetchone()
        if row:
            return Category(id=row[0], name=row[1], description=row[2])
        return None

    def list(self) -> List[Category]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, description FROM categories")
        rows = cur.fetchall()
        return [Category(id=r[0], name=r[1], description=r[2]) for r in rows]

    def update(self, entity: Category) -> Category:
        if entity.id is None:
            raise ValueError("Entidade precisa ter ID para ser atualizada.")
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE categories SET name=?, description=? WHERE id=?",
            (entity.name, entity.description, entity.id),
        )
        self.conn.commit()
        return entity

    def delete(self, entity_id: int) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM categories WHERE id=?", (entity_id,))
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

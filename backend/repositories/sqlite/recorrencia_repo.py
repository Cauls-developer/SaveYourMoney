"""Implementação SQLite para o repositório de recorrências."""
import sqlite3
from typing import Optional, List

from ...domain.entities import Recurrence
from ..base import Repository


class SQLiteRecurrenceRepository(Repository[Recurrence]):
    def __init__(self, db_path: str = "saveyourmoney.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS recurrences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                start_month INTEGER NOT NULL,
                start_year INTEGER NOT NULL,
                interval_months INTEGER NOT NULL,
                occurrences INTEGER NOT NULL,
                category_id INTEGER,
                payment_method TEXT,
                confirmed INTEGER,
                notes TEXT
            )
            """
        )
        self.conn.commit()

    def add(self, entity: Recurrence) -> Recurrence:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO recurrences (kind, name, value, start_month, start_year, interval_months, occurrences, category_id, payment_method, confirmed, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                entity.kind,
                entity.name,
                entity.value,
                entity.start_month,
                entity.start_year,
                entity.interval_months,
                entity.occurrences,
                entity.category_id,
                entity.payment_method,
                None if entity.confirmed is None else int(entity.confirmed),
                entity.notes,
            ),
        )
        entity.id = cur.lastrowid
        self.conn.commit()
        return entity

    def get(self, entity_id: int) -> Optional[Recurrence]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, kind, name, value, start_month, start_year, interval_months, occurrences, category_id, payment_method, confirmed, notes FROM recurrences WHERE id=?",
            (entity_id,),
        )
        row = cur.fetchone()
        if row:
            return Recurrence(
                id=row[0],
                kind=row[1],
                name=row[2],
                value=row[3],
                start_month=row[4],
                start_year=row[5],
                interval_months=row[6],
                occurrences=row[7],
                category_id=row[8],
                payment_method=row[9],
                confirmed=None if row[10] is None else bool(row[10]),
                notes=row[11],
            )
        return None

    def list(self) -> List[Recurrence]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, kind, name, value, start_month, start_year, interval_months, occurrences, category_id, payment_method, confirmed, notes FROM recurrences"
        )
        rows = cur.fetchall()
        return [
            Recurrence(
                id=r[0],
                kind=r[1],
                name=r[2],
                value=r[3],
                start_month=r[4],
                start_year=r[5],
                interval_months=r[6],
                occurrences=r[7],
                category_id=r[8],
                payment_method=r[9],
                confirmed=None if r[10] is None else bool(r[10]),
                notes=r[11],
            )
            for r in rows
        ]

    def update(self, entity: Recurrence) -> Recurrence:
        if entity.id is None:
            raise ValueError("Entidade precisa ter ID para ser atualizada.")
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE recurrences SET kind=?, name=?, value=?, start_month=?, start_year=?, interval_months=?, occurrences=?, category_id=?, payment_method=?, confirmed=?, notes=? WHERE id=?",
            (
                entity.kind,
                entity.name,
                entity.value,
                entity.start_month,
                entity.start_year,
                entity.interval_months,
                entity.occurrences,
                entity.category_id,
                entity.payment_method,
                None if entity.confirmed is None else int(entity.confirmed),
                entity.notes,
                entity.id,
            ),
        )
        self.conn.commit()
        return entity

    def delete(self, entity_id: int) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM recurrences WHERE id=?", (entity_id,))
        self.conn.commit()

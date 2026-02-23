"""Implementação SQLite para o repositório de parcelas."""
import sqlite3
from typing import Optional, List

from ...domain.entities import Installment
from ..base import Repository


class SQLiteInstallmentRepository(Repository[Installment]):
    def __init__(self, db_path: str = "saveyourmoney.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS installments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER NOT NULL,
                expense_name TEXT NOT NULL,
                installment_number INTEGER NOT NULL,
                total_installments INTEGER NOT NULL,
                value REAL NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                status TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def add(self, entity: Installment) -> Installment:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO installments (card_id, expense_name, installment_number, total_installments, value, month, year, status) VALUES (?,?,?,?,?,?,?,?)",
            (
                entity.card_id,
                entity.expense_name,
                entity.installment_number,
                entity.total_installments,
                entity.value,
                entity.month,
                entity.year,
                entity.status,
            ),
        )
        entity.id = cur.lastrowid
        self.conn.commit()
        return entity

    def get(self, entity_id: int) -> Optional[Installment]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, card_id, expense_name, installment_number, total_installments, value, month, year, status FROM installments WHERE id=?",
            (entity_id,),
        )
        row = cur.fetchone()
        if row:
            return Installment(
                id=row[0],
                card_id=row[1],
                expense_name=row[2],
                installment_number=row[3],
                total_installments=row[4],
                value=row[5],
                month=row[6],
                year=row[7],
                status=row[8],
            )
        return None

    def list(self) -> List[Installment]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, card_id, expense_name, installment_number, total_installments, value, month, year, status FROM installments"
        )
        rows = cur.fetchall()
        return [
            Installment(
                id=r[0],
                card_id=r[1],
                expense_name=r[2],
                installment_number=r[3],
                total_installments=r[4],
                value=r[5],
                month=r[6],
                year=r[7],
                status=r[8],
            )
            for r in rows
        ]

    def update(self, entity: Installment) -> Installment:
        if entity.id is None:
            raise ValueError("Entidade precisa ter ID para ser atualizada.")
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE installments SET card_id=?, expense_name=?, installment_number=?, total_installments=?, value=?, month=?, year=?, status=? WHERE id=?",
            (
                entity.card_id,
                entity.expense_name,
                entity.installment_number,
                entity.total_installments,
                entity.value,
                entity.month,
                entity.year,
                entity.status,
                entity.id,
            ),
        )
        self.conn.commit()
        return entity

    def delete(self, entity_id: int) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM installments WHERE id=?", (entity_id,))
        self.conn.commit()

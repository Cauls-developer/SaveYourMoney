"""Serviços de exportação e restauração de backup JSON."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import sqlite3
from typing import Any

from ..domain.entities import Card, Category, Expense, Goal, Income, Installment, Recurrence

BACKUP_VERSION = "1.0"
SUPPORTED_BACKUP_MAJOR = "1"


class BackupValidationError(ValueError):
    """Erro de validação do payload de backup."""


def export_backup_payload(
    *,
    cards: list[Card],
    categories: list[Category],
    expenses: list[Expense],
    goals: list[Goal],
    incomes: list[Income],
    installments: list[Installment],
    recurrences: list[Recurrence],
) -> dict[str, Any]:
    return {
        "version": BACKUP_VERSION,
        "exportedAt": datetime.utcnow().date().isoformat(),
        "cards": [asdict(item) for item in cards],
        "expenses": [asdict(item) for item in expenses],
        "recurringExpenses": [asdict(item) for item in recurrences],
        "income": [asdict(item) for item in incomes],
        "categories": [asdict(item) for item in categories],
        "installments": [asdict(item) for item in installments],
        "goals": [asdict(item) for item in goals],
        "settings": {},
    }


def restore_backup_payload(db_path: str, payload: Any) -> dict[str, int]:
    data = _validate_payload(payload)
    categories = [_parse_category(item) for item in data["categories"]]
    cards = [_parse_card(item) for item in data["cards"]]
    expenses = [_parse_expense(item) for item in data["expenses"]]
    recurrences = [_parse_recurrence(item) for item in data["recurrences"]]
    incomes = [_parse_income(item) for item in data["incomes"]]
    installments = [_parse_installment(item) for item in data["installments"]]
    goals = [_parse_goal(item) for item in data["goals"]]

    _validate_relationships(
        categories=categories,
        cards=cards,
        expenses=expenses,
        recurrences=recurrences,
        goals=goals,
        installments=installments,
    )

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("BEGIN")

        tables = [
            "installments",
            "expenses",
            "incomes",
            "recurrences",
            "goals",
            "cards",
            "categories",
        ]
        for table in tables:
            conn.execute(f"DELETE FROM {table}")

        for category in categories:
            conn.execute(
                "INSERT INTO categories (id, name, description) VALUES (?, ?, ?)",
                (category.id, category.name, category.description),
            )

        for card in cards:
            conn.execute(
                (
                    "INSERT INTO cards "
                    "(id, name, limit_value, bank, brand, closing_day, due_day) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)"
                ),
                (card.id, card.name, card.limit, card.bank, card.brand, card.closing_day, card.due_day),
            )

        for expense in expenses:
            conn.execute(
                (
                    "INSERT INTO expenses "
                    "(id, name, value, month, year, category_id, recurrence_id, payment_method, notes) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
                ),
                (
                    expense.id,
                    expense.name,
                    expense.value,
                    expense.month,
                    expense.year,
                    expense.category_id,
                    expense.recurrence_id,
                    expense.payment_method,
                    expense.notes,
                ),
            )

        for income in incomes:
            conn.execute(
                "INSERT INTO incomes (id, name, value, month, year, confirmed, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (income.id, income.name, income.value, income.month, income.year, int(income.confirmed), income.notes),
            )

        for recurrence in recurrences:
            conn.execute(
                (
                    "INSERT INTO recurrences "
                    "(id, kind, name, value, start_month, start_year, interval_months, occurrences, "
                    "category_id, payment_method, confirmed, notes) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                ),
                (
                    recurrence.id,
                    recurrence.kind,
                    recurrence.name,
                    recurrence.value,
                    recurrence.start_month,
                    recurrence.start_year,
                    recurrence.interval_months,
                    recurrence.occurrences,
                    recurrence.category_id,
                    recurrence.payment_method,
                    None if recurrence.confirmed is None else int(recurrence.confirmed),
                    recurrence.notes,
                ),
            )

        for installment in installments:
            conn.execute(
                (
                    "INSERT INTO installments "
                    "(id, card_id, expense_name, installment_number, total_installments, value, month, year, status) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
                ),
                (
                    installment.id,
                    installment.card_id,
                    installment.expense_name,
                    installment.installment_number,
                    installment.total_installments,
                    installment.value,
                    installment.month,
                    installment.year,
                    installment.status,
                ),
            )

        for goal in goals:
            conn.execute(
                "INSERT INTO goals (id, name, limit_value, month, year, category_id) VALUES (?, ?, ?, ?, ?, ?)",
                (goal.id, goal.name, goal.limit_value, goal.month, goal.year, goal.category_id),
            )

        _reset_sequences(conn, "categories", categories)
        _reset_sequences(conn, "cards", cards)
        _reset_sequences(conn, "expenses", expenses)
        _reset_sequences(conn, "incomes", incomes)
        _reset_sequences(conn, "recurrences", recurrences)
        _reset_sequences(conn, "installments", installments)
        _reset_sequences(conn, "goals", goals)

        conn.commit()
        return {
            "cards": len(cards),
            "categories": len(categories),
            "expenses": len(expenses),
            "incomes": len(incomes),
            "recurrences": len(recurrences),
            "installments": len(installments),
            "goals": len(goals),
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _validate_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise BackupValidationError("Arquivo inválido: estrutura JSON deve ser um objeto.")

    version = payload.get("version")
    if not isinstance(version, str) or not version.strip():
        raise BackupValidationError("Arquivo inválido: versão de backup ausente.")
    if version.split(".", 1)[0] != SUPPORTED_BACKUP_MAJOR:
        raise BackupValidationError("Versão de backup incompatível com esta aplicação.")

    required_list_fields = ["cards", "expenses", "categories"]
    for field in required_list_fields:
        if not isinstance(payload.get(field), list):
            raise BackupValidationError(f"Arquivo inválido: campo '{field}' deve ser uma lista.")

    recurring = payload.get("recurringExpenses")
    if recurring is None:
        recurring = payload.get("recurrences", [])
    if not isinstance(recurring, list):
        raise BackupValidationError("Arquivo inválido: campo 'recurringExpenses' deve ser uma lista.")

    incomes = payload.get("income")
    if incomes is None:
        incomes = payload.get("incomes", [])
    if not isinstance(incomes, list):
        raise BackupValidationError("Arquivo inválido: campo 'income' deve ser uma lista.")

    installments = payload.get("installments", [])
    if not isinstance(installments, list):
        raise BackupValidationError("Arquivo inválido: campo 'installments' deve ser uma lista.")

    goals = payload.get("goals", [])
    if not isinstance(goals, list):
        raise BackupValidationError("Arquivo inválido: campo 'goals' deve ser uma lista.")

    settings = payload.get("settings", {})
    if not isinstance(settings, dict):
        raise BackupValidationError("Arquivo inválido: campo 'settings' deve ser um objeto.")

    return {
        "version": version,
        "cards": payload["cards"],
        "expenses": payload["expenses"],
        "categories": payload["categories"],
        "recurrences": recurring,
        "incomes": incomes,
        "installments": installments,
        "goals": goals,
        "settings": settings,
    }


def _parse_record(item: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise BackupValidationError(f"Arquivo inválido: item em '{field_name}' deve ser um objeto.")
    return item


def _require_int(item: dict[str, Any], field: str, collection: str) -> int:
    try:
        return int(item[field])
    except (TypeError, ValueError, KeyError) as exc:
        raise BackupValidationError(f"Campo '{field}' inválido em '{collection}'.") from exc


def _require_float(item: dict[str, Any], field: str, collection: str) -> float:
    try:
        return float(item[field])
    except (TypeError, ValueError, KeyError) as exc:
        raise BackupValidationError(f"Campo '{field}' inválido em '{collection}'.") from exc


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _optional_bool(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "sim", "yes"}:
        return True
    if normalized in {"0", "false", "nao", "não", "no"}:
        return False
    raise ValueError("Valor booleano inválido.")


def _parse_category(raw: Any) -> Category:
    item = _parse_record(raw, "categories")
    try:
        return Category(
            id=_require_int(item, "id", "categories"),
            name=str(item["name"]),
            description=item.get("description"),
        )
    except (TypeError, ValueError, KeyError) as exc:
        raise BackupValidationError("Registro inválido em 'categories'.") from exc


def _parse_card(raw: Any) -> Card:
    item = _parse_record(raw, "cards")
    try:
        return Card(
            id=_require_int(item, "id", "cards"),
            name=str(item["name"]),
            limit=_require_float(item, "limit", "cards"),
            bank=item.get("bank"),
            brand=item.get("brand"),
            closing_day=_require_int(item, "closing_day", "cards"),
            due_day=_require_int(item, "due_day", "cards"),
        )
    except (TypeError, ValueError, KeyError) as exc:
        raise BackupValidationError("Registro inválido em 'cards'.") from exc


def _parse_expense(raw: Any) -> Expense:
    item = _parse_record(raw, "expenses")
    try:
        return Expense(
            id=_require_int(item, "id", "expenses"),
            name=str(item["name"]),
            value=_require_float(item, "value", "expenses"),
            month=_require_int(item, "month", "expenses"),
            year=_require_int(item, "year", "expenses"),
            category_id=_optional_int(item.get("category_id")),
            recurrence_id=_optional_int(item.get("recurrence_id")),
            payment_method=str(item.get("payment_method") or "debit"),
            notes=item.get("notes"),
        )
    except (TypeError, ValueError, KeyError) as exc:
        raise BackupValidationError("Registro inválido em 'expenses'.") from exc


def _parse_income(raw: Any) -> Income:
    item = _parse_record(raw, "income")
    try:
        confirmed = _optional_bool(item.get("confirmed", True))
        if confirmed is None:
            confirmed = True
        return Income(
            id=_require_int(item, "id", "income"),
            name=str(item["name"]),
            value=_require_float(item, "value", "income"),
            month=_require_int(item, "month", "income"),
            year=_require_int(item, "year", "income"),
            confirmed=confirmed,
            notes=item.get("notes"),
        )
    except (TypeError, ValueError, KeyError) as exc:
        raise BackupValidationError("Registro inválido em 'income'.") from exc


def _parse_recurrence(raw: Any) -> Recurrence:
    item = _parse_record(raw, "recurringExpenses")
    confirmed = _optional_bool(item.get("confirmed"))
    try:
        return Recurrence(
            id=_require_int(item, "id", "recurringExpenses"),
            kind=str(item["kind"]),
            name=str(item["name"]),
            value=_require_float(item, "value", "recurringExpenses"),
            start_month=_require_int(item, "start_month", "recurringExpenses"),
            start_year=_require_int(item, "start_year", "recurringExpenses"),
            interval_months=_require_int(item, "interval_months", "recurringExpenses"),
            occurrences=_require_int(item, "occurrences", "recurringExpenses"),
            category_id=_optional_int(item.get("category_id")),
            payment_method=item.get("payment_method"),
            confirmed=confirmed,
            notes=item.get("notes"),
        )
    except (TypeError, ValueError, KeyError) as exc:
        raise BackupValidationError("Registro inválido em 'recurringExpenses'.") from exc


def _parse_installment(raw: Any) -> Installment:
    item = _parse_record(raw, "installments")
    try:
        return Installment(
            id=_require_int(item, "id", "installments"),
            card_id=_require_int(item, "card_id", "installments"),
            expense_name=str(item["expense_name"]),
            installment_number=_require_int(item, "installment_number", "installments"),
            total_installments=_require_int(item, "total_installments", "installments"),
            value=_require_float(item, "value", "installments"),
            month=_require_int(item, "month", "installments"),
            year=_require_int(item, "year", "installments"),
            status=str(item.get("status") or "pendente"),
        )
    except (TypeError, ValueError, KeyError) as exc:
        raise BackupValidationError("Registro inválido em 'installments'.") from exc


def _parse_goal(raw: Any) -> Goal:
    item = _parse_record(raw, "goals")
    try:
        return Goal(
            id=_require_int(item, "id", "goals"),
            name=str(item["name"]),
            limit_value=_require_float(item, "limit_value", "goals"),
            month=_require_int(item, "month", "goals"),
            year=_require_int(item, "year", "goals"),
            category_id=_optional_int(item.get("category_id")),
        )
    except (TypeError, ValueError, KeyError) as exc:
        raise BackupValidationError("Registro inválido em 'goals'.") from exc


def _validate_relationships(
    *,
    categories: list[Category],
    cards: list[Card],
    expenses: list[Expense],
    recurrences: list[Recurrence],
    goals: list[Goal],
    installments: list[Installment],
) -> None:
    category_ids = {item.id for item in categories}
    card_ids = {item.id for item in cards}

    for expense in expenses:
        if expense.category_id is not None and expense.category_id not in category_ids:
            raise BackupValidationError("Integridade inválida: gasto referencia categoria inexistente.")

    for recurrence in recurrences:
        if recurrence.category_id is not None and recurrence.category_id not in category_ids:
            raise BackupValidationError("Integridade inválida: recorrência referencia categoria inexistente.")

    recurrence_ids = {item.id for item in recurrences}
    for expense in expenses:
        if expense.recurrence_id is not None and expense.recurrence_id not in recurrence_ids:
            raise BackupValidationError("Integridade inválida: gasto recorrente referencia recorrência inexistente.")

    for goal in goals:
        if goal.category_id is not None and goal.category_id not in category_ids:
            raise BackupValidationError("Integridade inválida: meta referencia categoria inexistente.")

    for installment in installments:
        if installment.card_id not in card_ids:
            raise BackupValidationError("Integridade inválida: parcela referencia cartão inexistente.")


def _reset_sequences(conn: sqlite3.Connection, table_name: str, rows: list[Any]) -> None:
    max_id = max((item.id or 0 for item in rows), default=0)
    conn.execute("DELETE FROM sqlite_sequence WHERE name=?", (table_name,))
    if max_id > 0:
        conn.execute("INSERT INTO sqlite_sequence (name, seq) VALUES (?, ?)", (table_name, max_id))


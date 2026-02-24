"""Helpers for parsing and validating request payloads."""
from __future__ import annotations


def pick(data: dict, *keys: str, default=None):
    for key in keys:
        if key in data:
            return data[key]
    return default


def parse_optional_bool(raw_value):
    if raw_value is None:
        return None
    if isinstance(raw_value, bool):
        return raw_value
    normalized = str(raw_value).strip().lower()
    if normalized in {"1", "true", "sim", "yes"}:
        return True
    if normalized in {"0", "false", "nao", "não", "no"}:
        return False
    raise ValueError("Valor booleano inválido.")


def parse_required_str(data: dict, *keys: str, field_name: str) -> str:
    raw = pick(data, *keys)
    value = str(raw or "").strip()
    if not value:
        raise ValueError(f"{field_name} é obrigatório.")
    return value


def parse_optional_str(data: dict, *keys: str):
    raw = pick(data, *keys)
    if raw is None:
        return None
    value = str(raw).strip()
    return value if value else None


def parse_float(raw_value, field_name: str) -> float:
    try:
        return float(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} inválido.") from exc


def parse_int(raw_value, field_name: str) -> int:
    try:
        return int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} inválido.") from exc


def parse_optional_int(raw_value, field_name: str) -> int | None:
    if raw_value in (None, ""):
        return None
    value = parse_int(raw_value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} inválido.")
    return value


def parse_edit_scope(raw_value: str | None) -> str:
    scope = (raw_value or "this").strip().lower()
    if scope not in {"this", "future"}:
        raise ValueError("Escopo de edição inválido. Use 'this' ou 'future'.")
    return scope


def parse_cancel_scope(raw_value: str | None) -> str:
    scope = (raw_value or "all").strip().lower()
    if scope not in {"this", "future", "all"}:
        raise ValueError("Escopo de cancelamento inválido. Use 'this', 'future' ou 'all'.")
    return scope

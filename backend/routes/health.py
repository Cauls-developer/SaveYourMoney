from __future__ import annotations

from flask import Blueprint

bp = Blueprint("health", __name__)


@bp.get("/health")
def health() -> tuple[dict, int]:
    return {"status": "ok"}, 200

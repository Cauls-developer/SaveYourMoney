"""HTTP error handling utilities."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HttpError(Exception):
    message: str
    status_code: int = 400

    def to_payload(self) -> dict:
        return {"error": self.message}


def bad_request(message: str) -> HttpError:
    return HttpError(message=message, status_code=400)


def not_found(message: str) -> HttpError:
    return HttpError(message=message, status_code=404)


def conflict(message: str) -> HttpError:
    return HttpError(message=message, status_code=409)

"""Extraction evaluation placeholder."""

from __future__ import annotations

from typing import Any


def evaluate_extraction(_predicted: list[dict], _gold: list[dict] | None) -> dict[str, Any]:
    return {"status": "placeholder", "note": "Add field-level F1 / EM when gold is available"}

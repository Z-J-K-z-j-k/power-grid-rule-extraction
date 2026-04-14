"""Segmentation evaluation placeholder."""

from __future__ import annotations

from typing import Any


def evaluate_segmentation(_predicted: list[dict], _gold: list[dict] | None) -> dict[str, Any]:
    return {"status": "placeholder", "note": "Add boundary P/R/F1 when gold is available"}

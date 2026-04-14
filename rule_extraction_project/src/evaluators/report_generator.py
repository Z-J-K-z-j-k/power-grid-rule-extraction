"""Merge eval outputs into one report."""

from __future__ import annotations

from typing import Any


def build_report(segmentation: dict[str, Any], extraction: dict[str, Any]) -> dict[str, Any]:
    return {"segmentation": segmentation, "extraction": extraction}

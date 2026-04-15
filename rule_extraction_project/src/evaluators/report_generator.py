"""Merge eval outputs into one report."""

from __future__ import annotations

from typing import Any


def build_report(
    segmentation: dict[str, Any],
    extraction: dict[str, Any],
    *,
    side_tables: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {"segmentation": segmentation, "extraction": extraction}
    if side_tables:
        out["side_tables"] = side_tables
    return out

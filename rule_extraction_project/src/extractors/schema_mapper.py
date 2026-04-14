"""Flatten ExtractedRule to table rows (CSV-friendly)."""

from __future__ import annotations

from ..config.schemas import ExtractedRule


def rule_to_row(rule: ExtractedRule) -> dict[str, str]:
    return rule.model_dump()

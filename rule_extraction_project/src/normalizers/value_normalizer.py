"""Normalize subject strings and value expressions (light)."""

from __future__ import annotations

import re

from ..config.schemas import ExtractedRule


def normalize_values(rule: ExtractedRule) -> ExtractedRule:
    data = rule.model_dump()
    for key in ("subject", "object", "location_or_scope"):
        val = data.get(key, "")
        if isinstance(val, str):
            data[key] = re.sub(r"\s+", " ", val).strip()
    return ExtractedRule(**data)

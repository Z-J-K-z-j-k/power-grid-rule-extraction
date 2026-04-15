"""Mark formula traces in text fields (lightweight)."""

from __future__ import annotations

import re

from ..config.schemas import ExtractedRule


def tag_formulas(rule: ExtractedRule) -> ExtractedRule:
    data = rule.model_dump()
    for key in ("condition", "trigger_condition_text", "action", "basis_text"):
        val = data.get(key, "")
        if isinstance(val, str) and re.search(r"[=＝]\s*[\d.%]", val):
            data[key] = "[formula] " + val
    return ExtractedRule(**data)

"""Normalize rule_type and modal verbs."""

from __future__ import annotations

import re

from ..config.schemas import ExtractedRule

_MODAL_MAP = [
    (re.compile(r"不得|MUST_NOT|禁止"), "MUST_NOT"),
    (re.compile(r"应当|必须|MUST"), "MUST"),
    (re.compile(r"可以|MAY"), "MAY"),
    (re.compile(r"应当鼓励|SHOULD|最好"), "SHOULD"),
]


def normalize_rule_fields(rule: ExtractedRule) -> ExtractedRule:
    rt = rule.rule_type.strip()
    if not rt:
        text = (rule.action + rule.condition + rule.basis_text)[:500]
        for pat, mapped in _MODAL_MAP:
            if pat.search(text):
                rt = mapped
                break
        if not rt:
            rt = "OTHER"
    data = rule.model_dump()
    data["rule_type"] = rt
    return ExtractedRule(**data)

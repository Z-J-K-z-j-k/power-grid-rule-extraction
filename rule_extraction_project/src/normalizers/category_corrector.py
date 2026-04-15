"""Lightweight rule_category / modality fixes for cap-like and scope-like sentences."""

from __future__ import annotations

import re

from ..config.schemas import ExtractedRule

_CAP_PAT = re.compile(r"不超过|不高于|不高于|上限|最大值|累计.*不超过|不得超过")
_SCOPE_PAT = re.compile(r"适用于|本细则适用于|下列|以下并网主体")


def correct_rule_categories(rule: ExtractedRule) -> ExtractedRule:
    d = rule.model_dump()
    blob = (
        (d.get("basis_text") or "")
        + (d.get("consequence") or "")
        + (d.get("trigger_condition_text") or "")
    )
    cat = (d.get("rule_category") or "").lower()
    mod = (d.get("modality") or "").upper()

    if cat == "special_case_rule" and _CAP_PAT.search(blob) and "免" not in blob[:80]:
        d["rule_category"] = "penalty_rule"
    if mod == "MUST_NOT" and _CAP_PAT.search(blob) and "不得" not in blob[:120]:
        if "不超过" in blob or "上限" in blob:
            d["modality"] = "NOT_APPLICABLE"
            d["rule_type"] = d["modality"]

    if cat == "obligation" and _SCOPE_PAT.search(d.get("basis_text") or ""):
        d["rule_category"] = "scope"
        d["modality"] = "NOT_APPLICABLE"
        d["rule_type"] = d["modality"]

    if d.get("modality"):
        d["rule_type"] = str(d["modality"])

    return ExtractedRule(**d)

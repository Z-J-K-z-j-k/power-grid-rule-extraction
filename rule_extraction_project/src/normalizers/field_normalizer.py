"""Normalize rule_category, modality, and legacy rule_type."""

from __future__ import annotations

import re

from ..config.schemas import ExtractedRule

_MODAL_MAP = [
    (re.compile(r"不得|MUST_NOT|禁止"), "MUST_NOT"),
    (re.compile(r"应当|必须|MUST"), "MUST"),
    (re.compile(r"可以|MAY"), "MAY"),
    (re.compile(r"应当鼓励|SHOULD|最好"), "SHOULD"),
]

_OTHER_LIKE_CATEGORIES = {"other", "OTHER", ""}


def normalize_rule_fields(rule: ExtractedRule) -> ExtractedRule:
    data = rule.model_dump()
    mod = str(data.get("modality") or "").strip()
    rc = str(data.get("rule_category") or "").strip()
    rt = str(data.get("rule_type") or "").strip()

    if mod:
        data["modality"] = mod
        data["rule_type"] = mod
    elif rt:
        data["modality"] = rt
        data["rule_type"] = rt
    else:
        text = (data.get("action") or "") + (data.get("condition") or "") + (data.get("basis_text") or "")
        text = text[:500]
        for pat, mapped in _MODAL_MAP:
            if pat.search(text):
                data["modality"] = mapped
                data["rule_type"] = mapped
                break
        if not data.get("modality"):
            data["modality"] = "NOT_APPLICABLE" if "公式" in text or "计算" in text else ""
            data["rule_type"] = data["modality"] or "OTHER"

    if rc in _OTHER_LIKE_CATEGORIES or rc.upper() == "OTHER":
        # nudge: infer coarse category from keywords
        blob = (
            (data.get("consequence") or "")
            + (data.get("exception") or "")
            + (data.get("basis_text") or "")
        )
        if re.search(r"免考|豁免|除外", blob):
            data["rule_category"] = "exemption_rule"
        elif re.search(r"考核|处罚|倍|电量", blob):
            data["rule_category"] = "penalty_rule"
        elif re.search(r"公式|计算|准确率", blob):
            data["rule_category"] = "calculation_rule"
        elif not rc:
            data["rule_category"] = "obligation"
        else:
            data["rule_category"] = "special_case_rule"

    return ExtractedRule(**data)

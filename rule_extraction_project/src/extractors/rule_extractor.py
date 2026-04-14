"""Call DeepSeek to extract rules from a Segment."""

from __future__ import annotations

from ..config.prompts import EXTRACTION_SYSTEM, extraction_user_prompt
from ..config.schemas import ExtractedRule, Segment
from ..llm.deepseek_adapter import DeepSeekAdapter
from ..llm.response_parser import extract_json_object
from ..utils.id_generator import new_rule_id


def extract_rules_from_segment(segment: Segment) -> list[ExtractedRule]:
    adapter = DeepSeekAdapter()
    raw = adapter.complete(EXTRACTION_SYSTEM, extraction_user_prompt(segment.text))
    data = extract_json_object(raw) or {}
    rules_raw = data.get("rules")
    if not isinstance(rules_raw, list):
        return []

    out: list[ExtractedRule] = []
    for item in rules_raw:
        if not isinstance(item, dict):
            continue
        out.append(
            ExtractedRule(
                rule_id=new_rule_id(),
                segment_id=segment.segment_id,
                rule_type=str(item.get("rule_type", "") or ""),
                subject=str(item.get("subject", "") or ""),
                condition=str(item.get("condition", "") or ""),
                action=str(item.get("action", "") or ""),
                object=str(item.get("object", "") or ""),
                time_limit=str(item.get("time_limit", "") or ""),
                location_or_scope=str(item.get("location_or_scope", "") or ""),
                exception=str(item.get("exception", "") or ""),
                consequence=str(item.get("consequence", "") or ""),
                basis_text=str(item.get("basis_text", "") or ""),
            )
        )
    return out

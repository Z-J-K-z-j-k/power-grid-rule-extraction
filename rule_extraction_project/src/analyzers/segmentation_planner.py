"""Build SegmentationPlan from DocumentProfile; optional LLM plan."""

from __future__ import annotations

import json

from ..config.prompts import PLANNER_SYSTEM, planner_user_prompt
from ..config.schemas import DocumentProfile, SegmentationPlan
from ..config.settings import MIN_SEGMENT_CHARS, MERGE_SHORT_SEGMENTS, USE_LLM_PLANNER
from ..llm.deepseek_adapter import DeepSeekAdapter
from ..llm.response_parser import extract_json_object


def default_plan_from_profile(profile: DocumentProfile) -> SegmentationPlan:
    primary = "article"
    if not profile.is_regulation_like:
        primary = "section"
    return SegmentationPlan(
        primary_unit=primary,
        merge_short=MERGE_SHORT_SEGMENTS,
        min_chars=MIN_SEGMENT_CHARS,
        extra_rules=[],
        llm_rationale=None,
    )


def plan_with_llm(profile: DocumentProfile) -> SegmentationPlan:
    summary = json.dumps(profile.model_dump(), ensure_ascii=False)
    adapter = DeepSeekAdapter()
    raw = adapter.complete(PLANNER_SYSTEM, planner_user_prompt(summary))
    data = extract_json_object(raw) or {}
    return SegmentationPlan(
        primary_unit=str(data.get("primary_unit", "article")),
        merge_short=bool(data.get("merge_short", True)),
        min_chars=int(data.get("min_chars", MIN_SEGMENT_CHARS)),
        extra_rules=list(data.get("extra_rules") or []),
        llm_rationale=str(data.get("rationale", "")),
    )


def build_segmentation_plan(profile: DocumentProfile) -> SegmentationPlan:
    if USE_LLM_PLANNER:
        try:
            return plan_with_llm(profile)
        except Exception:
            return default_plan_from_profile(profile)
    return default_plan_from_profile(profile)

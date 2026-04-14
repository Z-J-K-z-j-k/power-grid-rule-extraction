"""Hybrid segmenter: rule-based + postprocessor (LLM repair hook later)."""

from __future__ import annotations

from ..config.schemas import Segment, SegmentationPlan
from .rule_based_segmenter import segment_by_plan
from .segment_postprocessor import postprocess_segments


def hybrid_segment(full_text: str, plan: SegmentationPlan) -> list[Segment]:
    raw = segment_by_plan(full_text, plan)
    return postprocess_segments(raw, plan.min_chars)

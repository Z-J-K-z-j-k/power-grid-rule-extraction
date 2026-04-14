"""Core data structures: DocumentProfile, SegmentationPlan, Segment, ExtractedRule."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DocumentProfile(BaseModel):
    """Document-level analysis before segmentation."""

    is_regulation_like: bool = True
    has_formulas: bool = False
    has_exceptions: bool = False
    has_penalty_or_assessment: bool = False
    subject_types_hint: list[str] = Field(default_factory=list)
    notes: str = ""
    raw_signals: dict[str, Any] = Field(default_factory=dict)


class SegmentationPlan(BaseModel):
    """Per-document segmentation strategy."""

    primary_unit: str = "article"  # e.g. article, section, clause
    merge_short: bool = True
    min_chars: int = 80
    extra_rules: list[str] = Field(default_factory=list)
    llm_rationale: str | None = None


class Segment(BaseModel):
    """One text chunk for extraction."""

    segment_id: str
    text: str
    page_start: int | None = None
    page_end: int | None = None
    structure_path: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExtractedRule(BaseModel):
    """Single extracted normative rule."""

    rule_id: str
    segment_id: str
    rule_type: str = ""
    subject: str = ""
    condition: str = ""
    action: str = ""
    object: str = ""
    time_limit: str = ""
    location_or_scope: str = ""
    exception: str = ""
    consequence: str = ""
    basis_text: str = ""

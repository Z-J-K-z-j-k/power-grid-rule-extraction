"""Core data structures: profiles, segments, rules v2, constraints, consequences."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DocumentProfile(BaseModel):
    """Document-level analysis before segmentation."""

    model_config = ConfigDict(extra="ignore")

    is_regulation_like: bool = True
    has_formulas: bool = False
    has_exceptions: bool = False
    has_penalty_or_assessment: bool = False
    subject_types_hint: list[str] = Field(default_factory=list)
    notes: str = ""
    raw_signals: dict[str, Any] = Field(default_factory=dict)


class SegmentationPlan(BaseModel):
    """Per-document segmentation strategy."""

    model_config = ConfigDict(extra="ignore")

    primary_unit: str = "article"
    merge_short: bool = True
    min_chars: int = 80
    extra_rules: list[str] = Field(default_factory=list)
    llm_rationale: str | None = None


class Segment(BaseModel):
    """One text chunk for extraction."""

    model_config = ConfigDict(extra="ignore")

    segment_id: str
    text: str
    page_start: int | None = None
    page_end: int | None = None
    structure_path: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConstraintRecord(BaseModel):
    """Structured threshold / metric / formula-input (attached to a rule)."""

    model_config = ConfigDict(extra="ignore")

    constraint_id: str
    rule_id: str
    segment_id: str = ""
    constraint_type: str = ""
    metric_name: str = ""
    metric_normalized: str = ""
    comparator: str = ""
    threshold_value: str = ""
    threshold_upper: str = ""
    threshold_lower: str = ""
    unit: str = ""
    qualifier_text: str = ""
    time_window_text: str = ""
    region_special_case_text: str = ""
    formula_text: str = ""
    notes: str = ""


class ConsequenceRecord(BaseModel):
    """Penalty / cap / exemption outcome (attached to a rule)."""

    model_config = ConfigDict(extra="ignore")

    consequence_id: str
    rule_id: str
    segment_id: str = ""
    consequence_type: str = ""
    penalty_mode: str = ""
    trigger_text: str = ""
    value_text: str = ""
    formula_text: str = ""
    cap_text: str = ""
    unit: str = ""
    notes: str = ""


class ExtractedRule(BaseModel):
    """Single extracted normative rule (v2: category + modality + hierarchy)."""

    model_config = ConfigDict(extra="ignore")

    rule_id: str
    segment_id: str

    # Legacy single field (kept for CSV compat); prefer modality + rule_category
    rule_type: str = ""

    rule_category: str = ""
    modality: str = ""
    rule_level: str = ""
    parent_rule_id: str = ""
    parent_rule_ref: str = ""

    chapter: str = ""
    section: str = ""
    article: str = ""
    clause: str = ""
    item: str = ""

    subject: str = ""
    condition: str = ""
    trigger_condition_text: str = ""
    action: str = ""
    object: str = ""
    time_limit: str = ""
    location_or_scope: str = ""
    exception: str = ""
    consequence: str = ""

    metric: str = ""
    comparator: str = ""
    threshold: str = ""
    unit: str = ""
    consequence_formula: str = ""
    cap: str = ""

    basis_text: str = ""
    has_formula: str = ""
    formula_parse_status: str = ""

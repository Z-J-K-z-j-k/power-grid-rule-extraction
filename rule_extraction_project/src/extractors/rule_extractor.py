"""Call DeepSeek to extract rules from a Segment (v2 + constraint/consequence sub-rows)."""

from __future__ import annotations

from ..config.prompts import EXTRACTION_SYSTEM, extraction_user_prompt
from ..config.schemas import ConsequenceRecord, ConstraintRecord, ExtractedRule, Segment
from ..llm.deepseek_adapter import DeepSeekAdapter
from ..llm.response_parser import extract_json_object
from ..utils.id_generator import new_consequence_id, new_constraint_id, new_rule_id
from ..utils.structure_refs import infer_structure_path


def extract_rules_from_segment(
    segment: Segment,
) -> tuple[list[ExtractedRule], list[ConstraintRecord], list[ConsequenceRecord]]:
    adapter = DeepSeekAdapter()
    raw = adapter.complete(EXTRACTION_SYSTEM, extraction_user_prompt(segment.text))
    data = extract_json_object(raw) or {}
    rules_raw = data.get("rules")
    if not isinstance(rules_raw, list):
        return [], [], []

    struct = infer_structure_path(segment.text)
    rules_out: list[ExtractedRule] = []
    cons_out: list[ConstraintRecord] = []
    csq_out: list[ConsequenceRecord] = []

    for item in rules_raw:
        if not isinstance(item, dict):
            continue
        rid = new_rule_id()
        rc = str(item.get("rule_category", "") or "")
        mod = str(item.get("modality", "") or "")
        legacy = mod if mod else str(item.get("rule_type", "") or "")

        def g(k: str) -> str:
            return str(item.get(k, "") or "")

        rule = ExtractedRule(
            rule_id=rid,
            segment_id=segment.segment_id,
            rule_type=legacy,
            rule_category=rc,
            modality=mod,
            rule_level=g("rule_level"),
            parent_rule_id=g("parent_rule_id"),
            parent_rule_ref=g("parent_rule_ref"),
            chapter=g("chapter") or struct["chapter"],
            section=g("section") or struct["section"],
            article=g("article") or struct["article"],
            clause=g("clause") or struct["clause"],
            item=g("item") or struct["item"],
            subject=g("subject"),
            condition=g("condition") or g("trigger_condition_text"),
            trigger_condition_text=g("trigger_condition_text") or g("condition"),
            action=g("action"),
            object=g("object"),
            time_limit=g("time_limit"),
            location_or_scope=g("location_or_scope"),
            exception=g("exception"),
            consequence=g("consequence"),
            metric=g("metric"),
            comparator=g("comparator"),
            threshold=g("threshold"),
            unit=g("unit"),
            consequence_formula=g("consequence_formula"),
            cap=g("cap"),
            basis_text=g("basis_text"),
            has_formula="true" if any(x in segment.text for x in ("=", "×", "%", "公式", "考核电量")) else "",
            formula_parse_status="text_only",
        )
        rules_out.append(rule)

        cr_list = item.get("constraints")
        if isinstance(cr_list, list):
            for c in cr_list:
                if not isinstance(c, dict):
                    continue
                cons_out.append(
                    ConstraintRecord(
                        constraint_id=new_constraint_id(),
                        rule_id=rid,
                        segment_id=segment.segment_id,
                        constraint_type=str(c.get("constraint_type", "") or ""),
                        metric_name=str(c.get("metric_name", "") or ""),
                        metric_normalized=str(c.get("metric_normalized", "") or ""),
                        comparator=str(c.get("comparator", "") or ""),
                        threshold_value=str(c.get("threshold_value", "") or ""),
                        threshold_upper=str(c.get("threshold_upper", "") or ""),
                        threshold_lower=str(c.get("threshold_lower", "") or ""),
                        unit=str(c.get("unit", "") or ""),
                        qualifier_text=str(c.get("qualifier_text", "") or ""),
                        time_window_text=str(c.get("time_window_text", "") or ""),
                        region_special_case_text=str(c.get("region_special_case_text", "") or ""),
                        formula_text=str(c.get("formula_text", "") or ""),
                        notes=str(c.get("notes", "") or ""),
                    )
                )

        cq_list = item.get("consequences")
        if isinstance(cq_list, list):
            for q in cq_list:
                if not isinstance(q, dict):
                    continue
                csq_out.append(
                    ConsequenceRecord(
                        consequence_id=new_consequence_id(),
                        rule_id=rid,
                        segment_id=segment.segment_id,
                        consequence_type=str(q.get("consequence_type", "") or ""),
                        penalty_mode=str(q.get("penalty_mode", "") or ""),
                        trigger_text=str(q.get("trigger_text", "") or ""),
                        value_text=str(q.get("value_text", "") or ""),
                        formula_text=str(q.get("formula_text", "") or ""),
                        cap_text=str(q.get("cap_text", "") or ""),
                        unit=str(q.get("unit", "") or ""),
                        notes=str(q.get("notes", "") or ""),
                    )
                )

    return rules_out, cons_out, csq_out

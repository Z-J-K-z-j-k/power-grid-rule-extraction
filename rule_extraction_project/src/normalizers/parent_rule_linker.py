"""Fill parent_rule_id within the same segment for attached/secondary/penalty/exemption rows."""

from __future__ import annotations

from collections import defaultdict

from ..config.schemas import ExtractedRule


def link_parent_rules(rules: list[ExtractedRule]) -> list[ExtractedRule]:
    """Heuristic: first primary (or first obligation-like) rule in a segment becomes parent."""
    by_seg: dict[str, list[ExtractedRule]] = defaultdict(list)
    order: list[str] = []
    for r in rules:
        if r.segment_id not in by_seg:
            order.append(r.segment_id)
        by_seg[r.segment_id].append(r)

    parent_for_segment: dict[str, str] = {}
    for seg_id in order:
        group = by_seg[seg_id]
        primary = None
        for r in group:
            if (r.rule_level or "").lower() == "primary":
                primary = r
                break
        if primary is None:
            for r in group:
                cat = (r.rule_category or "").lower()
                if cat in ("obligation", "prohibition", "scope", "definition", "responsibility"):
                    primary = r
                    break
        if primary is None and group:
            primary = group[0]
        if primary:
            parent_for_segment[seg_id] = primary.rule_id

    updates: dict[str, str] = {}
    for seg_id, group in by_seg.items():
        pid = parent_for_segment.get(seg_id)
        if not pid:
            continue
        for r in group:
            if r.rule_id == pid:
                continue
            if (r.parent_rule_id or "").strip():
                continue
            lvl = (r.rule_level or "").lower()
            cat = (r.rule_category or "").lower()
            if lvl in ("attached", "secondary") or cat in (
                "penalty_rule",
                "exemption_rule",
                "calculation_rule",
                "special_case_rule",
            ):
                updates[r.rule_id] = pid
            elif not lvl and cat in ("procedure", "reporting_rule", "testing_rule"):
                updates[r.rule_id] = pid

    out: list[ExtractedRule] = []
    for r in rules:
        d = r.model_dump()
        rid = d["rule_id"]
        if rid in updates:
            d["parent_rule_id"] = updates[rid]
        out.append(ExtractedRule(**d))
    return out

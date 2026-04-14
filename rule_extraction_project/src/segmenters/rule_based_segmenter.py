"""Primary segmenter: split by regulation hierarchy (e.g. 第X条)."""

from __future__ import annotations

import re

from ..config.schemas import Segment, SegmentationPlan
from ..utils.id_generator import new_segment_id
from ..utils.regex_patterns import RE_ARTICLE, RE_CHAPTER, RE_SECTION


def _marker_positions(text: str, plan: SegmentationPlan) -> list[tuple[int, str]]:
    positions: list[tuple[int, str]] = []
    if plan.primary_unit == "article":
        for m in RE_ARTICLE.finditer(text):
            positions.append((m.start(), "article"))
    elif plan.primary_unit == "section":
        for m in RE_SECTION.finditer(text):
            positions.append((m.start(), "section"))
    elif plan.primary_unit == "chapter":
        for m in RE_CHAPTER.finditer(text):
            positions.append((m.start(), "chapter"))
    else:
        for m in RE_ARTICLE.finditer(text):
            positions.append((m.start(), "article"))
    positions.sort(key=lambda x: x[0])
    return positions


def segment_by_plan(full_text: str, plan: SegmentationPlan) -> list[Segment]:
    text = full_text.strip()
    positions = _marker_positions(text, plan)
    if not positions:
        # Fallback: coarse splits by double newlines or chunk size
        chunks = [c.strip() for c in re.split(r"\n\s*\n+", text) if c.strip()]
        if len(chunks) <= 1:
            return [Segment(segment_id=new_segment_id(), text=text)]
        return [Segment(segment_id=new_segment_id(), text=c) for c in chunks]

    segs: list[Segment] = []
    for i, (start, _kind) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        chunk = text[start:end].strip()
        if chunk:
            segs.append(Segment(segment_id=new_segment_id(), text=chunk))
    return segs

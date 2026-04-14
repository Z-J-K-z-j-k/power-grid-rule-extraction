"""Detect regulation structure markers in text."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..utils.regex_patterns import RE_ARTICLE, RE_CHAPTER, RE_CN_ENUM_PAREN, RE_NUM_ITEM, RE_SECTION


@dataclass
class StructureHits:
    chapters: list[tuple[int, int]] = field(default_factory=list)
    sections: list[tuple[int, int]] = field(default_factory=list)
    articles: list[tuple[int, int]] = field(default_factory=list)
    cn_enum: list[tuple[int, int]] = field(default_factory=list)
    num_items: list[tuple[int, int]] = field(default_factory=list)


def find_spans(pattern, text: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in pattern.finditer(text)]


def detect_structure(text: str) -> StructureHits:
    return StructureHits(
        chapters=find_spans(RE_CHAPTER, text),
        sections=find_spans(RE_SECTION, text),
        articles=find_spans(RE_ARTICLE, text),
        cn_enum=find_spans(RE_CN_ENUM_PAREN, text),
        num_items=find_spans(RE_NUM_ITEM, text),
    )

"""Heuristic extraction of 章/节/条/款/项 from regulation text (fallback when LLM omits)."""

from __future__ import annotations

import re

RE_CHAPTER = re.compile(r"第[一二三四五六七八九十百千万零〇两]+章")
RE_SECTION = re.compile(r"第[一二三四五六七八九十百千万零〇两]+节")
RE_ARTICLE = re.compile(r"第[一二三四五六七八九十百千万零〇两]+条")
RE_CLAUSE = re.compile(r"[（(][一二三四五六七八九十百千万]+[）)]")
RE_ITEM = re.compile(r"(?:^|[\n\s])(\d{1,3})[\.．、]\s*")


def first_match(pattern: re.Pattern[str], text: str) -> str:
    m = pattern.search(text)
    return m.group(0).strip() if m else ""


def infer_structure_path(text: str) -> dict[str, str]:
    """Best-effort single path from segment opening lines."""
    head = text[:800]
    return {
        "chapter": first_match(RE_CHAPTER, head),
        "section": first_match(RE_SECTION, head),
        "article": first_match(RE_ARTICLE, head),
        "clause": first_match(RE_CLAUSE, head),
        "item": first_match(RE_ITEM, head),
    }

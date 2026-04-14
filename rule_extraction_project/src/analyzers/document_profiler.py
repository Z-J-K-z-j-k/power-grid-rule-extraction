"""Document-level profile: regulation-like, formulas, exceptions, penalties."""

from __future__ import annotations

import re

from ..config.schemas import DocumentProfile
from ..parsers.structure_detector import detect_structure


def profile_document(full_text: str) -> DocumentProfile:
    hits = detect_structure(full_text)
    article_count = len(hits.articles)
    is_reg = article_count > 0 or "条" in full_text[:5000]

    has_formula = bool(
        re.search(r"[=＝]\s*[\d.]", full_text)
        or "公式" in full_text
        or re.search(r"\b\d+\s*%\s*", full_text)
    )
    exc = bool(re.search(r"除外|例外|但书|但是|免于|不(?:予|受)考核", full_text))
    penalty = bool(re.search(r"处罚|罚款|扣分|考核|违反|吊销|责令", full_text))

    subjects: list[str] = []
    if re.search(r"单位|机关|部门|企业", full_text):
        subjects.append("organization")
    if re.search(r"个人|人员|公民", full_text):
        subjects.append("person")

    return DocumentProfile(
        is_regulation_like=is_reg,
        has_formulas=has_formula,
        has_exceptions=exc,
        has_penalty_or_assessment=penalty,
        subject_types_hint=subjects,
        raw_signals={
            "article_markers": article_count,
            "chapter_markers": len(hits.chapters),
        },
    )

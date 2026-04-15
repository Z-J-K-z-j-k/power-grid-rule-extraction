"""Unify 章/节/条/款/项 citation string format (spacing, full-width digits)."""

from __future__ import annotations

import re

from ..config.schemas import ExtractedRule

_RE_STRIP_ARTICLE = re.compile(r"^\s*第\s*(\d{1,3})\s*条\s*$")


def _normalize_article(s: str) -> str:
    s = re.sub(r"\s+", "", (s or "").strip())
    # Keep Chinese 第十三条 as-is; only normalize Arabic: "第13条" / "第 13 条"
    m = _RE_STRIP_ARTICLE.match(s.replace(" ", ""))
    if m:
        return f"第{int(m.group(1))}条"
    if re.match(r"^第[一二三四五六七八九十百千万零〇两]+条$", s):
        return s
    return s


def _normalize_clause_item(s: str) -> str:
    s = re.sub(r"\s+", "", (s or "").strip())
    s = s.replace("(", "（").replace(")", "）")
    return s


def normalize_citation_fields(rule: ExtractedRule) -> ExtractedRule:
    d = rule.model_dump()
    if d.get("article"):
        d["article"] = _normalize_article(str(d["article"]))
    if d.get("clause"):
        d["clause"] = _normalize_clause_item(str(d["clause"]))
    if d.get("item"):
        it = str(d["item"]).strip()
        it = re.sub(r"^(\d+)\s*[\.．、]\s*", r"\1、", it)
        d["item"] = it
    for k in ("chapter", "section"):
        if d.get(k):
            d[k] = re.sub(r"\s+", "", str(d[k]).strip())
    return ExtractedRule(**d)

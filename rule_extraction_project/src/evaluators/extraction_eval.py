"""Extraction quality stats without gold labels; optional field-level F1 when gold exists."""

from __future__ import annotations

from typing import Any


def evaluate_extraction(predicted: list[dict], gold: list[dict] | None) -> dict[str, Any]:
    if gold:
        return {
            "status": "gold_not_implemented",
            "note": "Add field-level F1 / EM when gold rows are wired",
            "predicted_count": len(predicted),
            "gold_count": len(gold),
        }

    if not predicted:
        return {"status": "empty", "rule_count": 0}

    n = len(predicted)
    basis_ok = sum(1 for r in predicted if (r.get("basis_text") or "").strip())
    parent_ok = sum(1 for r in predicted if (r.get("parent_rule_id") or "").strip())
    cat_ok = sum(1 for r in predicted if (r.get("rule_category") or "").strip())
    mod_ok = sum(1 for r in predicted if (r.get("modality") or "").strip())

    cats: dict[str, int] = {}
    for r in predicted:
        c = (r.get("rule_category") or "unknown").strip() or "unknown"
        cats[c] = cats.get(c, 0) + 1

    return {
        "status": "stats_only",
        "rule_count": n,
        "basis_text_non_empty_rate": round(basis_ok / n, 4) if n else 0.0,
        "parent_rule_id_filled_rate": round(parent_ok / n, 4) if n else 0.0,
        "rule_category_filled_rate": round(cat_ok / n, 4) if n else 0.0,
        "modality_filled_rate": round(mod_ok / n, 4) if n else 0.0,
        "rule_category_histogram_top": sorted(cats.items(), key=lambda x: -x[1])[:15],
        "note": "No gold set; rates describe completeness/coverage only, not correctness.",
    }

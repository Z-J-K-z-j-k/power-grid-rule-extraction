"""Lightweight stats for constraints / consequences tables."""

from __future__ import annotations

from typing import Any


def evaluate_side_tables(
    constraints: list[dict],
    consequences: list[dict],
    formulas: list[dict],
    variables: list[dict],
) -> dict[str, Any]:
    def _rate(rows: list[dict], key: str) -> float:
        if not rows:
            return 0.0
        ok = sum(1 for r in rows if (r.get(key) or "").strip())
        return round(ok / len(rows), 4)

    return {
        "constraint_count": len(constraints),
        "consequence_count": len(consequences),
        "formula_count": len(formulas),
        "variable_count": len(variables),
        "constraint_formula_id_rate": _rate(constraints, "formula_id"),
        "constraint_metric_rate": _rate(constraints, "metric_name"),
        "consequence_type_rate": _rate(consequences, "consequence_type"),
    }

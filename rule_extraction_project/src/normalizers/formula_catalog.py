"""Build formulas + variables tables; attach formula_id to constraints."""

from __future__ import annotations

import re
import uuid
from pathlib import Path

from ..config.schemas import ConstraintRecord, FormulaRecord, VariableRecord
from ..utils.io import read_json


_VAR_LINE = re.compile(
    r"(?m)^\s*([A-Za-z][A-Za-z0-9_]*|[PM][A-Za-z]?|\d+[A-Za-z]?)\s*[：:为]\s*([^。；\n]+)",
)


def _new_fid(prefix: str = "fmt") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def build_formula_catalog(
    stem: str,
    constraints: list[ConstraintRecord],
    interim_dir: Path,
) -> tuple[list[FormulaRecord], list[VariableRecord], list[ConstraintRecord]]:
    formulas: list[FormulaRecord] = []
    variables: list[VariableRecord] = []

    fb_path = interim_dir / f"{stem}_formula_blocks.json"
    block_index: dict[str, str] = {}
    if fb_path.is_file():
        data = read_json(fb_path)
        blocks = data.get("formula_blocks") or []
        for b in blocks:
            if not isinstance(b, dict):
                continue
            fid = str(b.get("formula_block_id") or _new_fid("fb"))
            block_index[fid] = str(b.get("text_preview") or "")[:4000]
            formulas.append(
                FormulaRecord(
                    formula_id=fid,
                    source="formula_block",
                    formula_block_id=str(b.get("formula_block_id") or ""),
                    char_start=b.get("char_start"),
                    char_end=b.get("char_end"),
                    trigger_matched=str(b.get("trigger_matched") or ""),
                    formula_text_raw=str(b.get("text_preview") or "")[:8000],
                    parse_note=str(b.get("parse_note") or ""),
                )
            )
            prev = str(b.get("text_preview") or "")
            nvars = 0
            for m in _VAR_LINE.finditer(prev):
                if nvars >= 25:
                    break
                sym, mean = m.group(1).strip(), m.group(2).strip()
                if len(sym) > 12 or len(mean) < 2:
                    continue
                variables.append(
                    VariableRecord(
                        variable_id=f"var_{uuid.uuid4().hex[:8]}",
                        formula_id=fid,
                        symbol=sym,
                        meaning=mean[:500],
                    )
                )
                nvars += 1

    cons_out: list[ConstraintRecord] = []
    for c in constraints:
        d = c.model_dump()
        ft = (d.get("formula_text") or "").strip()
        if ft:
            fid = _new_fid("fmtc")
            formulas.append(
                FormulaRecord(
                    formula_id=fid,
                    segment_id=d.get("segment_id") or "",
                    source="constraint_derived",
                    formula_text_raw=ft[:8000],
                    linked_rule_ids=d.get("rule_id") or "",
                    parse_note="Derived from extraction constraint row.",
                )
            )
            d["formula_id"] = fid
        cons_out.append(ConstraintRecord(**d))

    return formulas, variables, cons_out

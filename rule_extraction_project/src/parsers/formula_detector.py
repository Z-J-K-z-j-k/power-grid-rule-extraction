"""Detect formula-heavy blocks in parsed full text (triggers + symbol density)."""

from __future__ import annotations

import re
import uuid
from pathlib import Path

from ..utils.io import write_json

_TRIGGER_PATTERNS = [
    re.compile(p)
    for p in [
        r"计算公式为",
        r"按以下公式",
        r"考核公式",
        r"其计算公式",
        r"式中[：:]",
        r"定义为",
        r"取值如下",
        r"物理意义为",
    ]
]
_SYMBOL_LINE = re.compile(r"[∑∫√≤≥±×÷Δ%‰HzMWkVkWh]+|[=＝<>≤≥]")


def _window(full: str, center: int, radius: int = 1200) -> tuple[int, int, str]:
    lo = max(0, center - radius)
    hi = min(len(full), center + radius)
    return lo, hi, full[lo:hi]


def detect_formula_blocks(full_text: str, stem: str) -> list[dict]:
    """Return non-overlapping-ish blocks with previews (text layer may still be garbled)."""
    blocks: list[dict] = []
    seen_spans: set[tuple[int, int]] = set()

    for pat in _TRIGGER_PATTERNS:
        for m in pat.finditer(full_text):
            lo, hi, preview = _window(full_text, m.start())
            key = (lo // 500, hi // 500)
            if key in seen_spans:
                continue
            seen_spans.add(key)
            blocks.append(
                {
                    "formula_block_id": f"fb_{uuid.uuid4().hex[:10]}",
                    "char_start": lo,
                    "char_end": hi,
                    "trigger_matched": m.group(0)[:80],
                    "text_preview": preview[:2000],
                    "parse_note": "PDF text layer may be broken for math; use region render/OCR for real formulas.",
                }
            )

    # Symbol-dense lines (fallback)
    lines = full_text.split("\n")
    offset = 0
    for line in lines:
        if len(line) < 8:
            offset += len(line) + 1
            continue
        sym = len(_SYMBOL_LINE.findall(line))
        if sym >= 4 and any(c in line for c in "=×÷%≤≥"):
            lo, hi, preview = _window(full_text, offset + len(line) // 2, 800)
            key = (lo // 400, hi // 400)
            if key not in seen_spans:
                seen_spans.add(key)
                blocks.append(
                    {
                        "formula_block_id": f"fb_{uuid.uuid4().hex[:10]}",
                        "char_start": lo,
                        "char_end": hi,
                        "trigger_matched": "symbol_dense_line",
                        "text_preview": preview[:2000],
                        "parse_note": "Heuristic; verify in PDF.",
                    }
                )
        offset += len(line) + 1

    out = {"doc_stem": stem, "formula_blocks": blocks[:200]}  # cap
    return out["formula_blocks"]


def write_formula_blocks_report(blocks: list[dict], stem: str, interim_dir: Path) -> Path:
    p = interim_dir / f"{stem}_formula_blocks.json"
    write_json(p, {"formula_blocks": blocks, "count": len(blocks)})
    return p

"""Parse PDF to per-page text and standardized parsed_document.json."""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF

from ..config.settings import DATA_INTERIM
from ..utils.io import write_json
from .text_cleaner import normalize_whitespace


def parse_pdf_to_document(pdf_path: Path, stem: str) -> dict:
    doc = fitz.open(pdf_path)
    pages: list[dict] = []
    full_parts: list[str] = []
    for i in range(doc.page_count):
        page = doc.load_page(i)
        text = normalize_whitespace(page.get_text("text") or "")
        pages.append({"page_index": i + 1, "text": text})
        full_parts.append(text)
    doc.close()
    full_text = normalize_whitespace("\n\n".join(full_parts))
    out = {
        "source_pdf": str(pdf_path.resolve()),
        "page_count": len(pages),
        "pages": pages,
        "full_text": full_text,
    }
    interim_path = DATA_INTERIM / f"{stem}_parsed_document.json"
    write_json(interim_path, out)
    return out

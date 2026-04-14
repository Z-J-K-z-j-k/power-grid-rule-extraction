"""Basic whitespace and line normalization."""

from __future__ import annotations

import re


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_lines(text: str) -> list[str]:
    return [ln.strip() for ln in text.split("\n") if ln.strip()]

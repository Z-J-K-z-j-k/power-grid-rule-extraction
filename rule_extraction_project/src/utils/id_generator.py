"""IDs for segments and rules."""

from __future__ import annotations

import uuid


def new_segment_id(prefix: str = "seg") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def new_rule_id(prefix: str = "rule") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

"""Merge overly short segments, light cleanup."""

from __future__ import annotations

from ..config.schemas import Segment


def postprocess_segments(segments: list[Segment], min_chars: int) -> list[Segment]:
    if not segments:
        return []
    out: list[Segment] = []
    buf = segments[0]
    for seg in segments[1:]:
        if len(buf.text) < min_chars:
            merged_text = buf.text.rstrip() + "\n\n" + seg.text.lstrip()
            buf = Segment(
                segment_id=buf.segment_id,
                text=merged_text,
                page_start=buf.page_start,
                page_end=seg.page_end or buf.page_end,
                structure_path=buf.structure_path + seg.structure_path,
                metadata={**buf.metadata, "merged_from": seg.segment_id},
            )
        else:
            out.append(buf)
            buf = seg
    out.append(buf)
    return out

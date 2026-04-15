"""Pipeline entry: parse → profile → plan → segment → extract → normalize → evaluate."""

from __future__ import annotations

import argparse
import csv
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .analyzers.document_profiler import profile_document
from .analyzers.segmentation_planner import build_segmentation_plan
from .config.schemas import ConsequenceRecord, ConstraintRecord, ExtractedRule, Segment
from .evaluators.constraint_eval import evaluate_side_tables
from .config.settings import DATA_EVAL, DATA_INTERIM, DATA_PROCESSED, EXTRACT_MAX_WORKERS, OUTPUTS_TABLES
from .evaluators.extraction_eval import evaluate_extraction
from .evaluators.report_generator import build_report
from .evaluators.segmentation_eval import evaluate_segmentation
from .extractors.exception_linker import link_exceptions
from .extractors.rule_extractor import extract_rules_from_segment
from .normalizers.category_corrector import correct_rule_categories
from .normalizers.citation_normalizer import normalize_citation_fields
from .normalizers.field_normalizer import normalize_rule_fields
from .normalizers.formula_catalog import build_formula_catalog
from .normalizers.formula_handler import tag_formulas
from .normalizers.parent_rule_linker import link_parent_rules
from .normalizers.value_normalizer import normalize_values
from .parsers.pdf_parser import parse_pdf_to_document
from .segmenters.hybrid_segmenter import hybrid_segment
from .utils.io import read_json, write_json
from .utils.logger import get_logger

# NOTE: `python -m src.main` sets __name__ to "__main__", which is outside the
# configured "rule_extraction" logger tree — use a fixed name so INFO logs show.
log = get_logger("rule_extraction.pipeline")


def _stem(pdf: Path) -> str:
    return pdf.stem


def run_parse(pdf: Path) -> dict:
    stem = _stem(pdf)
    log.info("parse: %s", pdf)
    doc = parse_pdf_to_document(pdf, stem)
    from .parsers.formula_detector import detect_formula_blocks, write_formula_blocks_report

    blocks = detect_formula_blocks(doc["full_text"], stem)
    p = write_formula_blocks_report(blocks, stem, DATA_INTERIM)
    log.info("formula block hints: %d (see %s)", len(blocks), p.name)
    return doc


def run_profile(pdf: Path) -> dict:
    stem = _stem(pdf)
    parsed_path = DATA_INTERIM / f"{stem}_parsed_document.json"
    doc = read_json(parsed_path)
    profile = profile_document(doc["full_text"])
    out = profile.model_dump()
    write_json(DATA_PROCESSED / f"{stem}_profile.json", out)
    log.info("profile written: %s", stem)
    return out


def run_plan(pdf: Path) -> dict:
    stem = _stem(pdf)
    profile_data = read_json(DATA_PROCESSED / f"{stem}_profile.json")
    from .config.schemas import DocumentProfile

    profile = DocumentProfile(**profile_data)
    plan = build_segmentation_plan(profile)
    out = plan.model_dump()
    write_json(DATA_PROCESSED / f"{stem}_plan.json", out)
    log.info("plan written: %s", stem)
    return out


_log_lock = threading.Lock()


def _extract_one_segment(
    args: tuple[int, dict, int],
) -> tuple[int, list[ExtractedRule], list[ConstraintRecord], list[ConsequenceRecord]]:
    idx, row, total = args
    seg = Segment(**row)
    nchars = len(seg.text or "")
    preview = (seg.text or "")[:60].replace("\n", " ")
    with _log_lock:
        log.info(
            "extract [%d/%d] segment_id=%s chars=%d preview=%s…",
            idx,
            total,
            seg.segment_id,
            nchars,
            preview,
        )
    rules, cons, csq = extract_rules_from_segment(seg)
    with _log_lock:
        log.info(
            "extract [%d/%d] got %d rule(s), %d constraints, %d consequences",
            idx,
            total,
            len(rules),
            len(cons),
            len(csq),
        )
    return idx, rules, cons, csq


def run_segment(pdf: Path) -> list[dict]:
    stem = _stem(pdf)
    parsed = read_json(DATA_INTERIM / f"{stem}_parsed_document.json")
    plan_data = read_json(DATA_PROCESSED / f"{stem}_plan.json")
    from .config.schemas import SegmentationPlan

    plan = SegmentationPlan(**plan_data)
    segments = hybrid_segment(parsed["full_text"], plan)
    out = [s.model_dump() for s in segments]
    write_json(DATA_PROCESSED / f"{stem}_segments.json", out)
    log.info("segments: %d", len(out))
    return out


def _write_csv_dicts(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def run_extract(pdf: Path) -> list[dict]:
    stem = _stem(pdf)
    seg_data = read_json(DATA_PROCESSED / f"{stem}_segments.json")
    total = len(seg_data)
    workers = EXTRACT_MAX_WORKERS
    log.info(
        "extract: %d segment(s), one API call each; EXTRACT_MAX_WORKERS=%d; "
        "transient disconnects are retried (API_MAX_RETRIES).",
        total,
        workers,
    )
    all_rules: list[ExtractedRule] = []
    all_cons: list[ConstraintRecord] = []
    all_csq: list[ConsequenceRecord] = []
    if workers <= 1:
        for idx, row in enumerate(seg_data, start=1):
            _, rules, cons, csq = _extract_one_segment((idx, row, total))
            all_rules.extend(rules)
            all_cons.extend(cons)
            all_csq.extend(csq)
    else:
        args_list = [(i, row, total) for i, row in enumerate(seg_data, start=1)]
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for _, rules, cons, csq in ex.map(_extract_one_segment, args_list):
                all_rules.extend(rules)
                all_cons.extend(cons)
                all_csq.extend(csq)
    rows = [r.model_dump() for r in all_rules]
    write_json(DATA_PROCESSED / f"{stem}_extracted.json", rows)
    write_json(DATA_PROCESSED / f"{stem}_constraints.json", [c.model_dump() for c in all_cons])
    write_json(DATA_PROCESSED / f"{stem}_consequences.json", [c.model_dump() for c in all_csq])
    _write_csv_dicts(OUTPUTS_TABLES / f"{stem}_rules.csv", rows)
    _write_csv_dicts(OUTPUTS_TABLES / f"{stem}_constraints.csv", [c.model_dump() for c in all_cons])
    _write_csv_dicts(OUTPUTS_TABLES / f"{stem}_consequences.csv", [c.model_dump() for c in all_csq])
    log.info(
        "extracted rules: %d, constraints rows: %d, consequences rows: %d",
        len(rows),
        len(all_cons),
        len(all_csq),
    )
    return rows


def run_normalize(pdf: Path) -> list[dict]:
    stem = _stem(pdf)
    rows = read_json(DATA_PROCESSED / f"{stem}_extracted.json")
    normalized: list[ExtractedRule] = []
    for row in rows:
        r = ExtractedRule(**row)
        r = normalize_rule_fields(r)
        r = normalize_values(r)
        r = tag_formulas(r)
        r = correct_rule_categories(r)
        r = normalize_citation_fields(r)
        normalized.append(r)
    normalized = link_parent_rules(normalized)
    linked = link_exceptions(normalized)
    out = [r.model_dump() for r in linked]
    write_json(DATA_PROCESSED / f"{stem}_normalized.json", out)
    csv_path = OUTPUTS_TABLES / f"{stem}_rules_normalized.csv"
    if out:
        with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
            w.writeheader()
            w.writerows(out)
    log.info("normalized rules: %d", len(out))

    cpath = DATA_PROCESSED / f"{stem}_constraints.json"
    if cpath.is_file():
        raw_cons = read_json(cpath)
        cons_list = [ConstraintRecord(**x) for x in raw_cons]
        formulas, variables, cons_enriched = build_formula_catalog(stem, cons_list, DATA_INTERIM)
        write_json(DATA_PROCESSED / f"{stem}_formulas.json", [f.model_dump() for f in formulas])
        write_json(DATA_PROCESSED / f"{stem}_variables.json", [v.model_dump() for v in variables])
        write_json(DATA_PROCESSED / f"{stem}_constraints_enriched.json", [c.model_dump() for c in cons_enriched])
        _write_csv_dicts(OUTPUTS_TABLES / f"{stem}_formulas.csv", [f.model_dump() for f in formulas])
        _write_csv_dicts(OUTPUTS_TABLES / f"{stem}_variables.csv", [v.model_dump() for v in variables])
        _write_csv_dicts(OUTPUTS_TABLES / f"{stem}_constraints_enriched.csv", [c.model_dump() for c in cons_enriched])
        log.info(
            "formula catalog: %d formulas, %d variables, %d constraints (enriched)",
            len(formulas),
            len(variables),
            len(cons_enriched),
        )
    return out


def run_evaluate(pdf: Path) -> dict:
    stem = _stem(pdf)
    segs = read_json(DATA_PROCESSED / f"{stem}_segments.json")
    norm_path = DATA_PROCESSED / f"{stem}_normalized.json"
    if not norm_path.exists():
        norm_path = DATA_PROCESSED / f"{stem}_extracted.json"
    rules = read_json(norm_path) if norm_path.exists() else []
    seg_eval = evaluate_segmentation(segs, None)
    ext_eval = evaluate_extraction(rules, None)

    def _load(name: str) -> list[dict]:
        p = DATA_PROCESSED / f"{stem}_{name}.json"
        return read_json(p) if p.is_file() else []

    side = evaluate_side_tables(
        _load("constraints_enriched") or _load("constraints"),
        _load("consequences"),
        _load("formulas"),
        _load("variables"),
    )
    report = build_report(seg_eval, ext_eval, side_tables=side)
    write_json(DATA_EVAL / f"{stem}_eval_report.json", report)
    log.info("eval report: %s", stem)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Rule extraction pipeline")
    parser.add_argument("--pdf", type=Path, required=True, help="Path to PDF")
    parser.add_argument(
        "--run",
        choices=["parse", "profile", "plan", "segment", "extract", "normalize", "evaluate", "all"],
        default="all",
    )
    args = parser.parse_args()
    pdf = args.pdf.resolve()
    if not pdf.is_file():
        raise SystemExit(f"PDF not found: {pdf}")

    steps = (
        ["parse", "profile", "plan", "segment", "extract", "normalize", "evaluate"]
        if args.run == "all"
        else [args.run]
    )
    for step in steps:
        log.info("---------- step: %s ----------", step)
        if step == "parse":
            run_parse(pdf)
        elif step == "profile":
            run_profile(pdf)
        elif step == "plan":
            run_plan(pdf)
        elif step == "segment":
            run_segment(pdf)
        elif step == "extract":
            run_extract(pdf)
        elif step == "normalize":
            run_normalize(pdf)
        elif step == "evaluate":
            run_evaluate(pdf)
        log.info("---------- done: %s ----------", step)


if __name__ == "__main__":
    main()

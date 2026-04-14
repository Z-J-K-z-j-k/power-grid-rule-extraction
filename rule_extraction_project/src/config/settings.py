"""Project paths, DeepSeek config, segmentation thresholds."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")

DATA_RAW = _PROJECT_ROOT / "data" / "raw"
DATA_INTERIM = _PROJECT_ROOT / "data" / "interim"
DATA_PROCESSED = _PROJECT_ROOT / "data" / "processed"
DATA_EVAL = _PROJECT_ROOT / "data" / "eval"
OUTPUTS_FIGURES = _PROJECT_ROOT / "outputs" / "figures"
OUTPUTS_TABLES = _PROJECT_ROOT / "outputs" / "tables"

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-reasoner")

# Segmentation heuristics
MIN_SEGMENT_CHARS = int(os.getenv("MIN_SEGMENT_CHARS", "80"))
MERGE_SHORT_SEGMENTS = os.getenv("MERGE_SHORT_SEGMENTS", "true").lower() in ("1", "true", "yes")

# Planner
USE_LLM_PLANNER = os.getenv("USE_LLM_PLANNER", "false").lower() in ("1", "true", "yes")

# LLM HTTP: retries for incomplete body / dropped connections; extract parallelism
API_MAX_RETRIES = max(1, int(os.getenv("API_MAX_RETRIES", "6")))
API_RETRY_BASE_SECONDS = float(os.getenv("API_RETRY_BASE_SECONDS", "2"))
EXTRACT_MAX_WORKERS = max(1, int(os.getenv("EXTRACT_MAX_WORKERS", "2")))

PROJECT_ROOT = _PROJECT_ROOT

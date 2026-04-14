"""Simple logging setup."""

import logging
import sys


class _FlushingStreamHandler(logging.StreamHandler):
    """Ensure each log line appears immediately in the console (e.g. PowerShell)."""

    def emit(self, record: logging.LogRecord) -> None:
        super().emit(record)
        self.flush()


def get_logger(name: str | None = None) -> logging.Logger:
    root = logging.getLogger("rule_extraction")
    if not root.handlers:
        h = _FlushingStreamHandler(sys.stderr)
        h.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        root.addHandler(h)
        root.setLevel(logging.INFO)
    return logging.getLogger(name or "rule_extraction")

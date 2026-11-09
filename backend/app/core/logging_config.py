"""
Structured logging configuration for the application.
"""
from __future__ import annotations

import logging
import sys
from typing import Any, Dict

from app.core.config import settings


class _JSONFormatter(logging.Formatter):
    """Very lightweight JSON-ish formatter for structured log lines."""

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        import json
        import traceback

        log_entry: Dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            log_entry["exception"] = traceback.format_exception(*record.exc_info)
        return json.dumps(log_entry)


def setup_logging() -> None:
    """
    Configure root logger.

    - In DEBUG mode: coloured, human-readable output to stdout.
    - In production: JSON-structured output to stdout.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    handler = logging.StreamHandler(sys.stdout)

    if settings.DEBUG:
        fmt = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(fmt)
    else:
        handler.setFormatter(_JSONFormatter())

    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers.clear()
    root.addHandler(handler)

    # Silence noisy third-party loggers
    for noisy in ("pymongo", "motor", "httpx", "httpcore", "uvicorn.access"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

"""
Structured (JSON) logging.

Stdlib logging + a JSON formatter, rather than a dedicated library
(e.g. structlog) — this project's log volume doesn't justify the extra
dependency, and the stdlib's `extra=` kwarg already covers attaching
structured fields to a log line.
"""

import json
import logging
import sys
from datetime import datetime, timezone

_DEFAULT_RECORD_ATTRS = set(
    logging.LogRecord(
        name="", level=0, pathname="", lineno=0, msg="", args=(), exc_info=None
    ).__dict__.keys()
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        extra = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _DEFAULT_RECORD_ATTRS
        }
        payload.update(extra)

        return json.dumps(payload, default=str)


def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)

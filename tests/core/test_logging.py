"""
Tests for the JSON log formatter.
"""

import json
import logging

from app.core.logging import JsonFormatter


def _make_record(**extra) -> logging.LogRecord:
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_format_produces_valid_json():
    formatted = JsonFormatter().format(_make_record())

    json.loads(formatted)  # raises if not valid JSON


def test_format_includes_standard_fields():
    payload = json.loads(JsonFormatter().format(_make_record()))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "test.logger"
    assert payload["message"] == "hello world"
    assert "timestamp" in payload


def test_format_includes_extra_fields():
    payload = json.loads(
        JsonFormatter().format(_make_record(scan_id="abc-123", duration_ms=12.5))
    )

    assert payload["scan_id"] == "abc-123"
    assert payload["duration_ms"] == 12.5


def test_format_includes_exception_info():
    try:
        raise ValueError("boom")
    except ValueError:
        import sys

        record = _make_record()
        record.exc_info = sys.exc_info()

    payload = json.loads(JsonFormatter().format(record))

    assert "ValueError: boom" in payload["exc_info"]

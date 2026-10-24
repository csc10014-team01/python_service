"""Check the JSON log contract and stderr integration for CLI callers."""

import json
import logging

import pytest

from assistant_core.logging_setup import JsonFormatter, setup_logging


def test_formatter_serializes_event_and_allowed_metadata():
    record = logging.makeLogRecord(
        {
            "name": "assistant_core.service",
            "levelname": "INFO",
            "msg": "handled",
            "intent": "fee",
            "latency_ms": 0.1,
            "session": "local",
            "degraded": False,
            "llm_api_key": "test-only-secret",
            "text": "private question",
        }
    )
    assert json.loads(JsonFormatter().format(record)) == {
        "level": "INFO",
        "logger": "assistant_core.service",
        "msg": "handled",
        "intent": "fee",
        "latency_ms": 0.1,
        "session": "local",
        "degraded": False,
    }


def test_formatter_preserves_unicode_and_escapes_newlines():
    record = logging.makeLogRecord({"name": "assistant_core", "levelname": "WARNING", "msg": "Đã xử lý\n"})
    output = JsonFormatter().format(record)
    assert "Đã xử lý" in output
    assert len(output.splitlines()) == 1
    assert json.loads(output)["msg"] == "Đã xử lý\n"


@pytest.fixture
def application_logger():
    logger = logging.getLogger("assistant_core")
    old_handlers, old_level, old_propagate = logger.handlers[:], logger.level, logger.propagate
    logger.handlers = []
    try:
        yield logger
    finally:
        for handler in logger.handlers:
            handler.close()
        logger.handlers = old_handlers
        logger.setLevel(old_level)
        logger.propagate = old_propagate


def test_setup_writes_json_to_stderr_and_filters_level(application_logger, capsys):
    setup_logging("WARNING")
    logger = logging.getLogger("assistant_core.service")
    logger.info("handled")
    logger.warning("provider failed; using template fallback", extra={"degraded": True})
    captured = capsys.readouterr()
    assert captured.out == ""
    assert len(captured.err.splitlines()) == 1
    assert json.loads(captured.err)["degraded"] is True


def test_repeated_setup_updates_level_without_duplicate_logs(application_logger, capsys):
    setup_logging("WARNING")
    setup_logging("debug")
    application_logger.debug("handled")
    assert len(application_logger.handlers) == 1
    assert len(capsys.readouterr().err.splitlines()) == 1

"""Structured application logs on stderr; log events, never keys or user text."""

import json
import logging


class JsonFormatter(logging.Formatter):
    """Serialize an event and only the metadata fields defined by Lab 3.

    Callers must use static event messages such as 'handled'; user questions,
    credentials and exception text must never be interpolated into messages.
    """

    def format(self, record: logging.LogRecord) -> str:
        data = {"level": record.levelname, "logger": record.name, "msg": record.getMessage()}
        for key in ("intent", "latency_ms", "session", "degraded"):
            if hasattr(record, key):
                data[key] = getattr(record, key)
        return json.dumps(data, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    """Configure assistant_core and its child loggers once, without duplicate output.

    Call at CLI startup with settings.log_level. Answers remain on stdout.
    Unrelated application loggers and their handlers are left intact.
    """
    logger = logging.getLogger("assistant_core")
    logger.setLevel(level.upper())
    for handler in logger.handlers:
        if handler.get_name() == "assistant_core.json":
            return
    handler = logging.StreamHandler()
    handler.set_name("assistant_core.json")
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.propagate = False

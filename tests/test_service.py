import json
import logging
import sys
from pathlib import Path

import pytest

from assistant_core.__main__ import main
from assistant_core.knowledge import Handbook
from assistant_core.models import Intent, Message
from assistant_core.responder import StubLLMResponder


def test_greeting_intent(service):
    res = service.handle(Message(text="hi"))
    assert res.intent == Intent.GREETING
    assert "Hello" in res.answer
    assert not res.degraded


def test_office_lookup(service):
    res = service.handle(Message(text="where is the training office?"))
    assert res.intent == Intent.OFFICE
    assert "A.101" in res.answer


def test_fee_calculation(service):
    res = service.handle(Message(text="tuition for 18 credits and 2 retake"))
    assert res.intent == Intent.FEE
    assert "9,450,000" in res.answer


def test_rule_normal(service):
    res = service.handle(Message(text="thesis registration"))
    assert res.intent == Intent.RULE
    assert len(res.sources) == 1
    assert res.sources[0].id == "H26-5.3"
    assert res.sources[0].title == "Thesis Registration"
    assert not res.degraded


def test_fallback_when_provider_fails(service):
    service.responder = StubLLMResponder(fail=True)
    res = service.handle(Message(text="thesis registration"))

    assert res.intent == Intent.RULE
    assert res.degraded is True
    assert len(res.sources) > 0
    assert res.sources[0].id == "H26-5.3"
    assert "Thesis Registration" in res.answer


def test_rule_with_real_handbook(service):
    path = Path(__file__).resolve().parents[1] / "data" / "handbook.json"
    service.handbook = Handbook.from_json(path)

    res = service.handle(Message(text="thesis registration"))

    assert res.intent == Intent.RULE
    assert res.sources[0].id == "H26-5.3"
    assert "120" in res.answer
    assert not res.degraded


def test_unknown_rule(service):
    res = service.handle(Message(text="unrelated question"))
    assert res.intent == Intent.UNKNOWN
    assert res.sources == []


def test_invalid_fee_request(service):
    res = service.handle(Message(text="tuition please"))
    assert res.intent == Intent.FEE
    assert res.degraded


def test_unexpected_fee_error_is_not_hidden(service, monkeypatch):
    def broken_tuition(*args):
        raise RuntimeError("unexpected failure")

    monkeypatch.setattr("assistant_core.service.tuition", broken_tuition)
    with pytest.raises(RuntimeError, match="unexpected failure"):
        service.handle(Message(text="tuition for 18 credits"))


def test_cli_uses_json_logging(monkeypatch, capsys, mock_settings):
    mock_settings.data_dir = Path(__file__).resolve().parents[1] / "data"
    monkeypatch.setattr("assistant_core.__main__.load_settings", lambda: mock_settings)
    monkeypatch.setattr(sys, "argv", ["assistant_core", "thesis registration", "--session", "test-session"])
    logger = logging.getLogger("assistant_core")
    old_handlers, old_level, old_propagate = logger.handlers[:], logger.level, logger.propagate
    logger.handlers = []
    try:
        main()
        captured = capsys.readouterr()
        assert "120" in captured.out
        event = json.loads(captured.err)
        assert event["intent"] == "rule"
        assert event["session"] == "test-session"
        assert event["degraded"] is False
    finally:
        for handler in logger.handlers:
            handler.close()
        logger.handlers = old_handlers
        logger.setLevel(old_level)
        logger.propagate = old_propagate

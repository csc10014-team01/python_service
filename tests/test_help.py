"""Check the help feature through routing, the service, and the real CLI."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from assistant_core.models import Intent, Message, Response
from assistant_core.router import route
from assistant_core.service import AssistantService

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("text", ["help", "HELP", " /help ", "Help?!", "\thelp\n"])
def test_route_help_command(text: str) -> None:
    assert route(text, {"library"}) is Intent.HELP


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("help me calculate tuition for 18 credits", Intent.FEE),
        ("help me find the library", Intent.OFFICE),
        ("helpful thesis registration advice", Intent.RULE),
        ("helpdesk opening hours", Intent.RULE),
    ],
)
def test_help_does_not_override_regular_questions(text: str, expected: Intent) -> None:
    assert route(text, {"library"}) is expected


@pytest.mark.parametrize("text", ["help", "/help"])
def test_service_help_returns_a_typed_response(service: AssistantService, text: str) -> None:
    response = service.handle(Message(text=text))

    assert isinstance(response, Response)
    assert response.intent is Intent.HELP
    assert "Offices:" in response.answer
    assert "Tuition:" in response.answer
    assert "Handbook rules:" in response.answer
    assert response.sources == []
    assert response.degraded is False


def test_help_does_not_query_knowledge_or_call_a_provider(
    service: AssistantService, monkeypatch: pytest.MonkeyPatch
) -> None:
    def unexpected_call(*_args: object) -> str:
        raise AssertionError("Help must not query knowledge or call a responder")

    monkeypatch.setattr(service.offices, "find", unexpected_call)
    monkeypatch.setattr(service.handbook, "search", unexpected_call)
    monkeypatch.setattr(service.responder, "explain", unexpected_call)
    monkeypatch.setattr(service.fallback, "explain", unexpected_call)

    assert service.handle(Message(text="help")).intent is Intent.HELP


@pytest.mark.parametrize("text", ["help", " /HELP?! "])
def test_help_cli_keeps_answers_and_safe_json_logs_separate(text: str) -> None:
    secret = "h1-test-only-key"
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": str(PROJECT_ROOT / "src"),
            "ASSISTANT_DATA_DIR": str(PROJECT_ROOT / "data"),
            "LLM_PROVIDER": "stub",
            "LLM_API_KEY": secret,
            "CREDIT_RATE_VND": "450000",
            "RETAKE_MULTIPLIER": "1.5",
            "MAX_CREDITS": "30",
            "LOG_LEVEL": "INFO",
        }
    )
    result = subprocess.run(
        [sys.executable, "-m", "assistant_core", text, "--session", "h1-help-test"],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Offices:" in result.stdout
    assert "Tuition:" in result.stdout
    assert "Handbook rules:" in result.stdout
    event = json.loads(result.stderr)
    assert set(event) == {"level", "logger", "msg", "intent", "latency_ms", "session", "degraded"}
    assert event["msg"] == "handled"
    assert event["intent"] == "help"
    assert event["session"] == "h1-help-test"
    assert event["degraded"] is False
    assert event["latency_ms"] >= 0
    assert secret not in result.stdout + result.stderr

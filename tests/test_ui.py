import httpx
import pytest

from ui.api_client import AssistantClient, ChatResult
from ui.logic import format_sources, status_note, validate_input

OK = {
    "answer": "Room B.201",
    "intent": "office",
    "sources": [{"id": "S26#1", "title": "1 Library borrowing"}],
    "degraded": False,
    "escalate": False,
    "path": "deterministic",
    "request_id": "abc123",
}


def client_with(handler) -> AssistantClient:
    return AssistantClient("http://api.test", transport=httpx.MockTransport(handler))


def test_ask_ok():
    r = client_with(lambda req: httpx.Response(200, json=OK)).ask("where is the library", "s1")
    assert r.ok and r.answer == "Room B.201" and r.request_id == "abc123"


def test_ask_backend_down():
    def boom(req):
        raise httpx.ConnectError("refused", request=req)

    r = client_with(boom).ask("hi", "s1")
    assert not r.ok and "backend" in r.error


def test_ask_validation_and_server_errors():
    assert "type a question" in client_with(lambda req: httpx.Response(422)).ask("", "s").error
    assert "error 500" in client_with(lambda req: httpx.Response(500)).ask("x", "s").error


def test_feedback():
    assert client_with(lambda req: httpx.Response(201, json={})).send_feedback("abc123", 1)


def test_validate_input():
    assert validate_input("   ") == "Please type a question."
    assert validate_input("x" * 2001).startswith("Your question is too long")
    assert validate_input("hello") is None


# Remove this marker in the same PR that completes L1.
def test_format_sources():
    assert format_sources([]) == ""
    assert format_sources(OK["sources"]) == "Sources: S26#1 – 1 Library borrowing"


@pytest.mark.parametrize(
    ("escalate", "degraded", "expected"),
    [
        (False, False, None),
        (False, True, "Shown directly from the source document (the AI helper was unavailable)."),
        (
            True,
            False,
            "I could not find this in the official documents. A staff member can help: Training Office, room I.101.",
        ),
        (
            True,
            True,
            "I could not find this in the official documents. A staff member can help: Training Office, room I.101.",
        ),
    ],
)
def test_status_note(escalate, degraded, expected):
    assert status_note(ChatResult(ok=True, escalate=escalate, degraded=degraded)) == expected

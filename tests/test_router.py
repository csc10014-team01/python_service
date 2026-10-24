# pyrefly: ignore[missing-import]
from assistant_core.models import Intent
from assistant_core.router import route

OFFICES = {"library", "registrar"}


def test_greeting():
    assert route("Hello!", OFFICES) == Intent.GREETING


def test_fee():
    assert route("Tuition for 18 credits", OFFICES) == Intent.FEE


def test_office():
    assert route("Where is the library?", OFFICES) == Intent.OFFICE


def test_rule():
    assert route("thesis registration credits", OFFICES) == Intent.RULE

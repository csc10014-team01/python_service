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
    assert res.sources[0].id == "H26-1"
    assert not res.degraded


def test_fallback_when_provider_fails(service):
    service.responder = StubLLMResponder(fail=True)
    res = service.handle(Message(text="thesis registration"))

    assert res.intent == Intent.RULE
    assert res.degraded is True
    assert len(res.sources) > 0
    assert "Thesis Registration" in res.answer
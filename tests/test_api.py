from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient

from assistant_api.db import Repository, init_db, make_engine
from assistant_api.main import create_app
from assistant_api.weather import WeatherClient
from assistant_core.service import build_service

OK_JSON = {"current": {"time": "2026-10-05T09:00", "temperature_2m": 31.2, "weather_code": 3, "wind_speed_10m": 8.5}}


def weather_with(handler) -> WeatherClient:
    transport = httpx.MockTransport(handler)
    return WeatherClient("https://example.test/forecast", 10.76, 106.68, retries=1, transport=transport)


def client_with_address(app, address) -> TestClient:
    async def with_address(scope, receive, send):
        await app({**scope, "client": address}, receive, send)

    return TestClient(with_address)


@pytest.fixture
def repo():
    engine = make_engine("sqlite://")
    init_db(engine)
    yield Repository(engine, "test-salt")
    engine.dispose()


@pytest.fixture
def client(settings, service, repo):
    settings = settings.model_copy(update={"api_admin_key": "secret-admin", "rate_limit_per_min": 5})
    app = create_app(
        settings,
        service,
        weather_with(lambda req: httpx.Response(200, json=OK_JSON)),
        repo=repo,
    )
    return TestClient(app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


@pytest.mark.parametrize(("provider", "expected_path"), [("stub", "llm"), ("template", "retrieval")])
def test_chat_rag_metadata(settings, repo, provider, expected_path):
    settings = settings.model_copy(update={"llm_provider": provider, "llm_api_key": None})
    app = create_app(settings, build_service(settings), repo=repo)
    with TestClient(app) as client:
        response = client.post("/v1/chat", json={"message": "I lost my student card"})
    assert response.status_code == 200
    body = response.json()
    assert body["path"] == expected_path
    assert body["sources"][0]["id"] == "S26#3"
    assert body["escalate"] is False
    assert body["confidence"] == (0.7 if provider == "stub" else None)


def test_chat_fee(client):
    r = client.post("/v1/chat", json={"message": "tuition for 18 credits and 2 retake"})
    assert r.status_code == 200
    body = r.json()
    assert body["intent"] == "fee" and "9,450,000" in body["answer"] and body["request_id"]


def test_chat_validation_error(client):
    r = client.post("/v1/chat", json={"message": ""})
    assert r.status_code == 422 and r.json()["error"]["code"] == "invalid_request"


def test_rate_limit(client):
    for _ in range(5):
        assert client.post("/v1/chat", json={"message": "hi"}).status_code == 200

    response = client.post("/v1/chat", json={"message": "hi"})
    assert response.status_code == 429
    assert response.json() == {"error": {"code": "too_many_requests", "message": "Too many requests"}}


def test_rate_limit_is_per_client(client):
    first = client_with_address(client.app, ("192.0.2.1", 12345))
    second = client_with_address(client.app, ("192.0.2.2", 12345))
    for _ in range(5):
        assert first.post("/v1/chat", json={"message": "hi"}).status_code == 200
    assert first.post("/v1/chat", json={"message": "hi"}).status_code == 429

    assert second.post("/v1/chat", json={"message": "hi"}).status_code == 200
    # A different connection from the same IP still shares the limit.
    same_ip = client_with_address(client.app, ("192.0.2.1", 54321))
    assert same_ip.post("/v1/chat", json={"message": "hi"}).status_code == 429


def test_rate_limit_without_client_address(client):
    anonymous = client_with_address(client.app, None)
    codes = [anonymous.post("/v1/chat", json={"message": "hi"}).status_code for _ in range(6)]
    assert codes == [200] * 5 + [429]


def test_rate_limit_expires_after_one_minute(client, monkeypatch):
    now = [100.0]
    monkeypatch.setattr("assistant_api.ratelimit.time", SimpleNamespace(monotonic=lambda: now[0]))
    for _ in range(5):
        assert client.post("/v1/chat", json={"message": "hi"}).status_code == 200

    now[0] += 59
    assert client.post("/v1/chat", json={"message": "hi"}).status_code == 429
    now[0] += 2
    assert client.post("/v1/chat", json={"message": "hi"}).status_code == 200


def test_rate_limit_only_counts_valid_chat_requests(client):
    for _ in range(6):
        assert client.post("/v1/chat", json={"message": ""}).status_code == 422
        assert client.get("/health").status_code == 200
    for _ in range(5):
        chat = client.post("/v1/chat", json={"message": "hi"})
        assert chat.status_code == 200

    request_id = chat.json()["request_id"]
    assert client.post("/v1/chat", json={"message": "hi"}).status_code == 429
    assert client.get("/health").status_code == 200
    assert client.post("/v1/feedback", json={"request_id": request_id, "rating": 1}).status_code == 201


def test_feedback_roundtrip(client):
    chat = client.post("/v1/chat", json={"message": "hi"})
    assert chat.status_code == 200
    request_id = chat.json()["request_id"]
    r = client.post("/v1/feedback", json={"request_id": request_id, "rating": 1})
    assert r.status_code == 201 and r.json()["id"] == 1
    assert client.get("/v1/feedback").status_code == 401
    listed = client.get("/v1/feedback", headers={"X-API-Key": "secret-admin"})
    assert listed.status_code == 200 and len(listed.json()) == 1


def test_feedback_rating_out_of_range(client):
    assert client.post("/v1/feedback", json={"request_id": "x", "rating": 5}).status_code == 422


def test_weather_ok(client):
    r = client.get("/v1/weather")
    assert r.status_code == 200 and r.json()["description"] == "overcast"


def test_weather_down_returns_503(settings, service, repo):
    def boom(req):
        raise httpx.ConnectTimeout("timeout", request=req)

    app = create_app(settings, service, weather_with(boom), repo=repo)
    r = TestClient(app).get("/v1/weather")
    assert r.status_code == 503 and r.json()["error"]["code"] == "weather_service_unavailable"


def test_weather_stale_cache_when_upstream_fails():
    calls = {"n": 0}

    def flaky(req):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(200, json=OK_JSON)
        return httpx.Response(500)

    w = weather_with(flaky)
    w.cache_ttl_s = 0  # force a refresh on the second call
    assert not w.current().stale
    assert w.current().stale


def test_offices_returns_200(client):
    response = client.get("/v1/offices")

    assert response.status_code == 200


def test_offices_contains_library(client):
    response = client.get("/v1/offices")

    data = response.json()

    assert any(office["name"] == "Library" for office in data)


def test_feedback_unknown_request_id(client):
    response = client.post("/v1/feedback", json={"request_id": "missing-id", "rating": 1})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "unknown_request_id"

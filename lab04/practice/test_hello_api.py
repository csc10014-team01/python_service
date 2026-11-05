"""Run: python -m pytest -q test_hello_api.py."""

from fastapi.testclient import TestClient
from hello_api import app

client = TestClient(app)


def test_p1_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, CSC10014!"}


def test_p2_hello():
    response = client.get("/hello/Lan")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Lan!"}


def test_p3_square():
    response = client.get("/square?n=7")
    assert response.status_code == 200
    assert response.json() == {"n": 7, "square": 49}
    assert client.get("/square?n=abc").status_code == 422


def test_p4_add():
    response = client.post("/add", json={"a": 2, "b": 3})
    assert response.status_code == 200
    assert response.json() == {"sum": 5.0}


def test_p5_course():
    known = client.get("/courses/CSC10014")
    assert known.status_code == 200
    assert known.json() == {"code": "CSC10014", "name": "Computational Thinking"}
    unknown = client.get("/courses/XYZ")
    assert unknown.status_code == 404
    assert unknown.json() == {"detail": "Course not found"}

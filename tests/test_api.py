import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from praxis.api.app import app  # noqa: E402

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200
    assert "Praxis" in r.text


def test_ask_returns_grounded_answer():
    r = client.post(
        "/ask", json={"question": "Можно ли расторгнуть договор через суд при нарушении?"}
    )
    assert r.status_code == 200
    data = r.json()
    assert data["citations"]
    assert any(c["article_number"] == "450" for c in data["citations"])
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["steps"]


def test_search_endpoint():
    r = client.post("/search", json={"query": "толкование договора", "top_k": 3})
    assert r.status_code == 200
    hits = r.json()
    assert len(hits) <= 3
    assert all("citation" in h for h in hits)


def test_ask_rejects_empty_question():
    r = client.post("/ask", json={"question": ""})
    assert r.status_code == 422

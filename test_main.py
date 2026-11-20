from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_healthz_returns_ok():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_readyz_ready_when_db_available(monkeypatch):
    monkeypatch.setenv("DB_AVAILABLE", "true")
    r = client.get("/readyz")
    assert r.status_code == 200


def test_readyz_503_when_db_down(monkeypatch):
    monkeypatch.setenv("DB_AVAILABLE", "false")
    r = client.get("/readyz")
    assert r.status_code == 503

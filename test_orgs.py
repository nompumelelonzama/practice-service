import pytest
from fastapi.testclient import TestClient

from main import app
from orgs import repo

client = TestClient(app)

VALID = {
    "name": "Acme Logistics",
    "country": "ZA",
    "billing_currency": "ZAR",
    "admin_email": "thandi@example.com",
}


@pytest.fixture(autouse=True)
def clean_repo():
    if hasattr(repo, "ensure_schema"):
        repo.ensure_schema()
    repo.clear()
    yield
    repo.clear()


def test_register_org_returns_201_with_id():
    r = client.post("/orgs", json=VALID)
    assert r.status_code == 201
    assert r.json()["id"]
    assert r.json()["name"] == "Acme Logistics"


def test_registered_org_can_be_fetched():
    created = client.post("/orgs", json=VALID).json()
    r = client.get(f"/orgs/{created['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]


def test_duplicate_name_is_409_case_insensitive():
    client.post("/orgs", json=VALID)
    r = client.post("/orgs", json={**VALID, "name": "ACME logistics"})
    assert r.status_code == 409


def test_unsupported_currency_is_422():
    r = client.post("/orgs", json={**VALID, "billing_currency": "USD"})
    assert r.status_code == 422


def test_bad_email_is_422():
    r = client.post("/orgs", json={**VALID, "admin_email": "not-an-email"})
    assert r.status_code == 422


def test_unknown_org_is_404():
    assert client.get("/orgs/does-not-exist").status_code == 404
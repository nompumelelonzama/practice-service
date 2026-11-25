import os
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"), reason="DATABASE_URL not set"
)

from main import app  # noqa: E402
from orgs import DuplicateName, Org, PostgresOrgRepo, repo  # noqa: E402

client = TestClient(app)


def make_org(org_id, name):
    return Org(
        id=org_id,
        name=name,
        country="ZA",
        billing_currency="ZAR",
        admin_email="a@example.com",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture(autouse=True)
def clean():
    repo.ensure_schema()
    repo.clear()
    yield
    repo.clear()


def test_data_survives_a_new_repository_instance():
    repo.add(make_org("test-id-1", "Persisted Co"))
    fresh = PostgresOrgRepo(os.environ["DATABASE_URL"])
    assert fresh.get("test-id-1").name == "Persisted Co"


def test_database_enforces_case_insensitive_unique_names():
    repo.add(make_org("test-id-1", "Dup Co"))
    with pytest.raises(DuplicateName):
        repo.add(make_org("test-id-2", "DUP co"))


def test_readyz_is_200_with_a_real_database(monkeypatch):
    monkeypatch.delenv("DB_AVAILABLE", raising=False)
    assert client.get("/readyz").status_code == 200


def test_readyz_is_503_when_the_database_is_unreachable(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://identity:x@localhost:1/identity")
    assert client.get("/readyz").status_code == 503
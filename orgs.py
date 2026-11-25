import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/orgs", tags=["organisations"])

SUPPORTED_CURRENCIES = {"ZAR", "KES", "NGN", "GHS"}


class OrgCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    country: str = Field(pattern=r"^[A-Z]{2}$", description="ISO 3166-1 alpha-2")
    billing_currency: str = Field(pattern=r"^[A-Z]{3}$", description="ISO 4217")
    admin_email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)


class Org(BaseModel):
    id: str
    name: str
    country: str
    billing_currency: str
    admin_email: str
    created_at: datetime


class DuplicateName(Exception):
    pass


class InMemoryOrgRepo:
    def __init__(self):
        self._orgs: dict[str, Org] = {}

    def add(self, org: Org) -> None:
        if any(o.name.lower() == org.name.lower() for o in self._orgs.values()):
            raise DuplicateName()
        self._orgs[org.id] = org

    def get(self, org_id: str):
        return self._orgs.get(org_id)

    def clear(self) -> None:
        self._orgs.clear()


SCHEMA = """
CREATE TABLE IF NOT EXISTS organisations (
    id               TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    country          TEXT NOT NULL,
    billing_currency TEXT NOT NULL,
    admin_email      TEXT NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS organisations_name_lower_idx
    ON organisations (lower(name));
"""


class PostgresOrgRepo:
    """One short-lived connection per call. Simple on purpose; add a pool when load needs it."""

    def __init__(self, url: str):
        self._url = url

    def _connect(self):
        import psycopg

        return psycopg.connect(self._url, connect_timeout=3)

    def ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(SCHEMA)

    def add(self, org: Org) -> None:
        import psycopg

        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO organisations "
                    "(id, name, country, billing_currency, admin_email, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (org.id, org.name, org.country, org.billing_currency,
                     org.admin_email, org.created_at),
                )
        except psycopg.errors.UniqueViolation:
            raise DuplicateName()

    def get(self, org_id: str):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, name, country, billing_currency, admin_email, created_at "
                "FROM organisations WHERE id = %s",
                (org_id,),
            ).fetchone()
        if row is None:
            return None
        return Org(id=row[0], name=row[1], country=row[2],
                   billing_currency=row[3], admin_email=row[4], created_at=row[5])

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("TRUNCATE organisations")


def make_repo():
    url = os.getenv("DATABASE_URL")
    return PostgresOrgRepo(url) if url else InMemoryOrgRepo()


repo = make_repo()


@router.post("", response_model=Org, status_code=status.HTTP_201_CREATED)
def register_org(body: OrgCreate):
    if body.billing_currency not in SUPPORTED_CURRENCIES:
        raise HTTPException(status_code=422, detail="unsupported billing currency")
    org = Org(
        id=str(uuid.uuid4()),
        created_at=datetime.now(timezone.utc),
        **body.model_dump(),
    )
    try:
        repo.add(org)
    except DuplicateName:
        raise HTTPException(status_code=409, detail="organisation name already registered")
    return org


@router.get("/{org_id}", response_model=Org)
def get_org(org_id: str):
    org = repo.get(org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="organisation not found")
    return org
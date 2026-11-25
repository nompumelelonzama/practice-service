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


class InMemoryOrgRepo:
    def __init__(self):
        self._orgs: dict[str, Org] = {}

    def add(self, org: Org) -> None:
        self._orgs[org.id] = org

    def get(self, org_id: str):
        return self._orgs.get(org_id)

    def name_taken(self, name: str) -> bool:
        return any(o.name.lower() == name.lower() for o in self._orgs.values())

    def clear(self) -> None:
        self._orgs.clear()


repo = InMemoryOrgRepo()


@router.post("", response_model=Org, status_code=status.HTTP_201_CREATED)
def register_org(body: OrgCreate):
    if body.billing_currency not in SUPPORTED_CURRENCIES:
        raise HTTPException(status_code=422, detail="unsupported billing currency")
    if repo.name_taken(body.name):
        raise HTTPException(status_code=409, detail="organisation name already registered")
    org = Org(
        id=str(uuid.uuid4()),
        created_at=datetime.now(timezone.utc),
        **body.model_dump(),
    )
    repo.add(org)
    return org


@router.get("/{org_id}", response_model=Org)
def get_org(org_id: str):
    org = repo.get(org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="organisation not found")
    return org
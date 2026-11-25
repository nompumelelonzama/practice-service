import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response

import orgs
from orgs import router as orgs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the schema once the database is reachable (retry for up to 30s).
    if hasattr(orgs.repo, "ensure_schema"):
        last_error = None
        for _ in range(30):
            try:
                orgs.repo.ensure_schema()
                break
            except Exception as exc:
                last_error = exc
                time.sleep(1)
        else:
            raise RuntimeError("database not reachable at startup") from last_error
    yield


app = FastAPI(title="Identity Service (practice)", version="0.2.0", lifespan=lifespan)
app.include_router(orgs_router)


def database_ok() -> bool:
    if os.getenv("DB_AVAILABLE", "true").lower() == "false":
        return False
    url = os.getenv("DATABASE_URL")
    if not url:
        return True
    try:
        import psycopg

        with psycopg.connect(url, connect_timeout=2) as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False


@app.get("/healthz")
def healthz():
    """Liveness: is the process alive?"""
    return {"status": "ok"}


@app.get("/readyz")
def readyz(response: Response):
    """Readiness: can we serve traffic? Checks the database when one is configured."""
    if not database_ok():
        response.status_code = 503
        return {"status": "not ready", "reason": "database unreachable"}
    return {"status": "ready"}
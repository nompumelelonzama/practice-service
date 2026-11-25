import os

from fastapi import FastAPI, Response

from orgs import router as orgs_router

app = FastAPI(title="Identity Service (practice)", version="0.2.0")
app.include_router(orgs_router)


@app.get("/healthz")
def healthz():
    """Liveness: is the process alive?"""
    return {"status": "ok"}


@app.get("/readyz")
def readyz(response: Response):
    """Readiness: can we serve traffic? Simulates a database check."""
    if os.getenv("DB_AVAILABLE", "true").lower() == "false":
        response.status_code = 503
        return {"status": "not ready", "reason": "database unreachable"}
    return {"status": "ready"}
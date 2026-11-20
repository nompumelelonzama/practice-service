import os
from fastapi import FastAPI, Response

app = FastAPI(title="Identity Service (practice)", version="0.1.0")


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

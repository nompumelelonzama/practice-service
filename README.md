# Identity Service

A small identity service built as a practice exercise for a work-readiness programme:
health checks, a published API contract, organisation registration, a hardened container
image and a CI pipeline that gates every change. All data is synthetic, and nothing here
is a production system.

![CI](https://github.com/nompumelelonzama/practice-service/actions/workflows/ci.yml/badge.svg)

## What it does

| Capability | Status |
|---|---|
| `GET /healthz` liveness probe | Done |
| `GET /readyz` readiness probe (returns 503 when a dependency is down) | Done |
| Published OpenAPI contract (`openapi.json`), checked by a test | Done |
| `POST /orgs` and `GET /orgs/{id}`: register and fetch a business organisation | Done, in-memory storage |
| Persistent storage (PostgreSQL) | Not started |
| Login, tokens, roles and MFA | Not started |

## Run it locally

Requires Python 3.14.

```bash
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt     # Windows: .venv\Scripts\pip
.venv/bin/uvicorn main:app --port 8000            # Windows: .venv\Scripts\uvicorn
```

Then open http://localhost:8000/docs for the interactive API documentation.

## Run the tests

```bash
.venv/bin/python -m pytest -v
```

One test compares the committed `openapi.json` with what the app generates, so changing
an endpoint without re-exporting the contract fails the build. To re-export:

```bash
.venv/bin/python export_openapi.py
```

## Run it in a container

```bash
docker build -t identity-service .
docker run --rm -d -p 8080:8000 --name identity identity-service
curl http://localhost:8080/healthz
```

The image is multi-stage, runs as a non-root user (uid 10001), and contains no package
manager and no secrets. Configuration is passed at runtime, for example
`-e DB_AVAILABLE=false` makes `/readyz` return 503.

## API summary

| Method | Path | Success | Errors |
|---|---|---|---|
| GET | `/healthz` | 200 | none |
| GET | `/readyz` | 200 | 503 when the dependency is unavailable |
| POST | `/orgs` | 201 | 409 duplicate name, 422 invalid input or unsupported currency |
| GET | `/orgs/{id}` | 200 | 404 unknown organisation |

Supported billing currencies are ZAR, KES, NGN and GHS. Only the fields needed to register
an organisation are stored (data minimisation).

## CI

Every pull request runs two jobs: unit tests, then an image build followed by a Trivy
vulnerability scan that fails on fixable HIGH or CRITICAL findings. Merging requires both
to be green.

## Decisions and lessons

- [ADR 0001](docs/adr/0001-use-fastapi.md): why Python and FastAPI.
- The first image scan failed on five HIGH findings. Reading the scan per package showed
  none came from this service's dependencies: they were copies bundled inside `pip` in the
  base image. Removing `pip` from the runtime image cleared them, and it was verified by CI
  rather than by suppressing the scan.
- A pinned third-party action tag stopped resolving after a supply-chain incident in its
  upstream repository. It was replaced with a current release.

## Known limitations

- Organisations are stored in memory and are lost on restart.
- There is no authentication yet, so every endpoint is open.
- The CI pipeline builds the image but does not yet start it and probe `/healthz`.

## Project layout

| Path | Purpose |
|---|---|
| `main.py` | App, health endpoints |
| `orgs.py` | Organisation registration |
| `openapi.json` | Committed API contract |
| `docs/adr/` | Architecture decision records |
| `.github/workflows/ci.yml` | CI pipeline |
# ADR 0001: Use Python and FastAPI for the Identity service

Status: accepted
Date: 2026-11-25

## Context
The brief allows Node/TypeScript, Python/FastAPI or Go, one per squad. The Identity
service needs health endpoints, a published OpenAPI contract that other squads can code
against before logic exists, and token and permission logic.

## Decision
Use Python with FastAPI.

## Alternatives considered
- Node/TypeScript: strong ecosystem, but the OpenAPI document must be written or
  generated separately from the code.
- Go: small static binaries and fast startup, but slower for me to iterate on at this stage.

## Consequences
- Good: FastAPI generates the OpenAPI document from the code, so the contract cannot
  drift from the implementation.
- Good: Pydantic validates request bodies, which suits sign-up and login payloads.
- Bad: a larger runtime image than Go, so image patching and scanning matter more.
  This already happened: the base image's bundled pip carried five HIGH findings, which
  we cleared by removing pip from the runtime image.
- Bad: Python dependencies must stay pinned to keep builds reproducible.
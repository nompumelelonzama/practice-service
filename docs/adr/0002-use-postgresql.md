# ADR 0002: Use PostgreSQL for persistence

Status: accepted
Date: 2026-11-25

## Context
Organisations are currently held in memory (`InMemoryOrgRepo`) and are lost on restart.
Login, tokens and roles (ID-03 onwards) need durable users and organisations. The
project brief lists PostgreSQL as the data store, and /readyz currently fakes its
dependency check with an environment variable.

## Decision
Use PostgreSQL. Keep the repository interface that `orgs.py` already uses, and add a
PostgreSQL implementation behind it. Connection settings come from environment
variables at runtime and are never baked into the image.

## Alternatives considered
- SQLite: no extra container and simpler tests, but it does not match the project stack,
  differs from PostgreSQL in locking and type behaviour, and the swap later would be a
  migration project of its own.
-

$text = @'
# ADR 0002: Use PostgreSQL for persistence

Status: accepted
Date: 2026-11-25

## Context
Organisations are currently held in memory (`InMemoryOrgRepo`) and are lost on restart.
Login, tokens and roles (ID-03 onwards) need durable users and organisations. The
project brief lists PostgreSQL as the data store, and /readyz currently fakes its
dependency check with an environment variable.

## Decision
Use PostgreSQL. Keep the repository interface that `orgs.py` already uses, and add a
PostgreSQL implementation behind it. Connection settings come from environment
variables at runtime and are never baked into the image.

## Alternatives considered
- SQLite: no extra container and simpler tests, but it does not match the project stack,
  differs from PostgreSQL in locking and type behaviour, and the swap later would be a
  migration project of its own.
- Staying in memory: fine for a contract, but nothing survives a restart, so it cannot
  back authentication.

## Consequences
- Good: the same database runs locally, in CI and in the real platform, so behaviour
  that passes tests is closer to behaviour in staging.
- Good: /readyz can check a real connection instead of an environment flag.
- Bad: more moving parts. Local development needs a database container, CI needs a
  service container, and tests need setup and teardown of data.
- Bad: schema changes now need migrations, so a migration tool must be chosen and its
  files reviewed like code.
- Bad: credentials must be supplied securely. They come from environment variables now,
  and a secrets manager is a later concern.
- Follow-up: pin the PostgreSQL image to an exact version tag and scan it like any
  other image.
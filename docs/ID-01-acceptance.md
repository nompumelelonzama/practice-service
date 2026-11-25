# ID-01 Acceptance criteria

- [ ] GET /healthz returns 200 and {"status":"ok"} while the process is running
- [ ] GET /readyz returns 200 when dependencies are available
- [ ] GET /readyz returns 503 when a dependency is unavailable
- [ ] An openapi.json is committed and generated from the running app
- [ ] Automated tests cover both health endpoints, the 503 case and the contract
- [ ] The service runs from a container as a non-root user
- [ ] CI is green, including the image vulnerability scan
- [ ] An ADR records the language and framework choice (docs/adr/0001-use-fastapi.md)
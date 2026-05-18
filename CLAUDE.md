# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

This is **Fase 0** (scaffold only) of a DevOps coursework integrator (Prof. Lucas Bonanni). The repo currently contains empty package skeletons (`app/`, `tests/`) plus `requirements.txt`, `.env.example`, and `.dockerignore`. **The API code, Dockerfile, docker-compose, and GitHub Actions workflows do not exist yet** — they are the assignment.

The work is split across three team members. Their per-person briefs live in `tp-devops-contexto-claude-code/docs/` and are the source of truth for scope and acceptance criteria:

- **Persona A — Fase 1 (API + tests + DB):** `contexto-persona-A.md`
- **Persona B — Fase 2 (Dockerfile multi-stage + docker-compose):** `contexto-persona-B.md`
- **Persona C — Fases 3-5 (CI/CD + Docker Hub publish + Render deploy):** `contexto-persona-C.md`

Always read the relevant `contexto-persona-*.md` before implementing a fase — it contains the exact endpoints, justifications expected, and grading-relevant decisions (e.g. why `python:3.12-slim` over `alpine`, why SHA tagging, why API Key vs password).

## Grading rubric (central — drives scope decisions)

Bonanni does **not** evaluate API complexity. He evaluates that each DevOps stage is applied correctly and justified. Total = 10 pts:

| Item | Pts |
|---|---|
| Dockerfile (required) | 1 |
| Multi-stage | 1 |
| Docker buenas prácticas | 0,5 |
| Compose buenas prácticas | 0,5 |
| CI checks (build + unit test) | 0,5 |
| Flujo de mergeo (PRs + branch protection) | 1 |
| Publicación a Docker Hub | 2 |
| Deploy a Render | 1 |
| Monitoreo: Dashboard | 1,5 |
| Monitoreo: APM / Trazas | 1 |

Two consequences:
- **Do not add API features beyond what the persona briefs specify.** Extra endpoints/business logic do not score and dilute the layered-trace demo.
- Every Docker/compose "buena práctica" must include an inline comment citing its source (Python/Docker/FastAPI official docs). This is the evidence Bonanni grades.

## Stack

Python 3.12, FastAPI, SQLAlchemy 2.x, Pydantic v2, pytest + pytest-cov, httpx, New Relic agent. SQLite locally, Postgres in compose. Exact pinned versions in `requirements.txt`.

## Common commands

```bash
# Local dev setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Run API
uvicorn app.main:app --reload                  # http://localhost:8000  (docs at /docs)

# Tests
pytest --cov=app                               # full suite with coverage
pytest tests/test_items.py                     # single file
pytest tests/test_items.py::test_create_item   # single test
pytest -k "pokemon"                            # by keyword

# Docker (once Persona B's files exist)
docker build -t tp-devops .
docker compose up
```

## Architecture (target, not yet implemented)

Strict layered separation — this is what enables Fase 6 to show **chained traces** in New Relic, which is the whole point of the layering:

```
HTTP request
   -> app/routers/      (controller: parse request, call service, return response — NO business logic)
   -> app/services/     (business logic: items CRUD against DB, orchestrate external API calls)
   -> app/clients/      (httpx client to PokeAPI — external trace span)
   -> app/db/           (SQLAlchemy session + Item model)
app/models/             (Pydantic schemas: ItemCreate, ItemOut)
app/main.py             (FastAPI app, router includes, table creation on startup)
```

Endpoints required (per Persona A brief, not negotiable):
- `GET /health` — used by Docker HEALTHCHECK and Render
- `GET|POST|GET/{id}|DELETE /items` — DB-touching CRUD
- `GET /pokemon/{name}` — proxies via service+client to PokeAPI (the external-trace endpoint)
- `GET /error-test` — **intentionally raises** to demonstrate error visibility in monitoring

Configuration must come from env vars (`DATABASE_URL`, `POKEAPI_BASE_URL`, New Relic keys). Nothing hardcoded.

## Git workflow (graded — 1 pt for "flujo de mergeo")

Branch-per-feature with cross-review is part of the grade, not optional polish. Conventions in `GIT_WORKFLOW.md`:

- Branches: `feat/...`, `fix/...`, `chore/...`, `docs/...`, `ci/...`
- Conventional Commits (`feat:`, `fix:`, `ci:`, ...)
- `main` must be branch-protected and require CI checks (once `ci.yml` exists)
- A PR is reviewed/approved by a teammate who did **not** write it
- Aim for 3-4 real PRs with cross-review (evidence for the informe)

## Secrets

`.env` is gitignored; `.env.example` is the template. GitHub Actions secrets required for Fase 4-5:
- `DOCKER_USER`, `DOCKER_API_KEY` (API Key / Access Token, **not** the account password — Bonanni Clase 5)
- `RENDER_DEPLOY_HOOK`

The Render deploy step must pass the image as a query param to the hook so Render pulls the SHA-tagged image, not `latest`.

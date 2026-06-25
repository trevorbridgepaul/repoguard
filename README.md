# RepoGuard

RepoGuard is a backend platform tool that scans local code repositories for policy violations — repo hygiene, secrets, code quality, and dependency management — and returns a structured report.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the design decisions and tradeoffs behind how this is built.

## Problem

Engineering teams often need to make sure repositories meet minimum standards before being deployed or onboarded into a platform. RepoGuard automates those checks and produces a clear scan report instead of relying on manual review.

## Policies

| Policy | What it checks | Severity |
|---|---|---|
| `readme_exists` | README.md present at the repo root | MEDIUM |
| `gitignore_exists` | .gitignore present at the repo root | LOW |
| `codeowners_exists` | CODEOWNERS present at the repo root or in `.github/` | MEDIUM |
| `no_secrets` | AWS keys, `api_key=` assignments, PEM private key headers in any file | CRITICAL |
| `large_files` | Files over a configurable size threshold (default 1MB) | MEDIUM |
| `no_print_statements` | `print()` calls left in `.py` files | LOW |
| `license_header` | `.py` files missing a configured license header | LOW |
| `dependency_pinning` | Unpinned dependencies in `requirements.txt` | HIGH |

Every check, including `.gitignore` handling, runs against the real filesystem — no mocking in tests.

## API

- `POST /api/v1/auth/register` — create a user (`username`, `password`)
- `POST /api/v1/auth/login` — exchange `username`/`password` (form-encoded) for a JWT
- `POST /api/v1/scans` — **requires auth** (`Authorization: Bearer <token>`) — submit a `repo_path` (and optionally a subset of `policies`), runs synchronously, returns the completed scan
- `GET /api/v1/scans/{scan_id}` — **requires auth** — poll for a previously submitted scan's result. Scoped to the user who created it; a different user's `GET` on the same `scan_id` 404s exactly like an unknown id, so it can't be used to probe which scan_ids exist.
- `GET /api/v1/policies` — public, no auth — list every registered policy and its metadata
- `GET /healthz` — public, no auth, unversioned — actually queries the database; 503 if it's unreachable

Scan results are persisted in Postgres. `/docs` has a working "Authorize" button — register, log in, paste the token, and you can call the protected endpoints directly from there.

Application logs (scan start/finish, registration, login) are structured JSON on stdout — see `app/core/logging.py`. Uvicorn's own access/server logs are separate and stay in their default plain-text format.

## Running locally

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[test]"
docker compose up -d db
DATABASE_URL=postgresql+psycopg://repoguard:repoguard@localhost:5432/repoguard .venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload
```

Then visit `http://127.0.0.1:8000/docs` for interactive API docs.

## Running with Docker

```bash
docker compose up
```

This starts Postgres and the API together; migrations run automatically when the `app` container starts. The container only has its own code on disk by default — to scan a repo from the host, add a volume mount under the `app` service in `docker-compose.yml` (e.g. `- /path/to/your/repo:/scan-target:ro`) and pass that in-container path, e.g. `/scan-target`, as `repo_path` when calling `POST /api/v1/scans`.

## Tests

Storage and API tests need a real Postgres connection with migrations applied (`docker compose up -d db` then `alembic upgrade head`, as above) — policy and scanner tests don't touch the database at all.

```bash
.venv/bin/python -m pytest -q
```

## Tech Stack

- Python
- FastAPI / Pydantic
- SQLAlchemy / Alembic / Postgres
- PyJWT / bcrypt (auth)
- pathspec (`.gitignore` matching)
- pytest / httpx
- ruff / mypy (CI lint + type-check)

## Not yet implemented

- No refresh tokens / token revocation — access tokens just expire (`ACCESS_TOKEN_EXPIRE_MINUTES`, default 30)

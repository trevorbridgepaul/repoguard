# RepoGuard

RepoGuard is a backend platform tool that scans local code repositories for policy violations — repo hygiene, secrets, code quality, and dependency management — and returns a structured report.

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

- `POST /api/v1/scans` — submit a `repo_path` (and optionally a subset of `policies`), runs synchronously, returns the completed scan
- `GET /api/v1/scans/{scan_id}` — poll for a previously submitted scan's result
- `GET /api/v1/policies` — list every registered policy and its metadata

Scan results are held in memory for the life of the process — there's no database yet.

## Running locally

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[test]"
.venv/bin/uvicorn app.main:app --reload
```

Then visit `http://127.0.0.1:8000/docs` for interactive API docs.

## Tests

```bash
.venv/bin/python -m pytest -q
```

## Tech Stack

- Python
- FastAPI / Pydantic
- pathspec (`.gitignore` matching)
- pytest / httpx

## Not yet implemented

These were intentionally deferred to get the core scanning logic working first, not abandoned:

- A real database (currently an in-memory store, cleared on restart)
- Docker
- CI (GitHub Actions)
- Auth

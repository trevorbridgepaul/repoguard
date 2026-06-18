# repoguard
RepoGuard is a backend platform tool that scans software repositories for basic security, compliance, and engineering-readiness checks.

## Problem

Engineering teams often need to make sure repositories follow minimum standards before being deployed or onboarded into a platform. RepoGuard automates those checks and produces a clear scan report.

## Initial Checks

- README.md exists
- .gitignore exists
- CI workflow exists
- CODEOWNERS exists
- Dockerfile avoids running as root
- Dependency file exists
- Potential secrets are flagged

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Docker Compose
- pytest
- GitHub Actions

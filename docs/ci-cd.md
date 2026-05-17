# CI/CD and Automated Tests - ObRail

## 1) Pipeline scope

Workflow file: `.github/workflows/ci-cd.yml`

Executed on:
- `push` on `main`
- `pull_request` targeting `main`
- manual run via `workflow_dispatch`

Main jobs:
1. `backend-tests`: unit + integration + backend E2E tests.
2. `frontend-tests`: React unit tests + production build artifact (`admin-interface-build`).
3. `code-quality`: Flake8, ESLint, Prettier checks (non-blocking for now).
4. `docker-build`: automatic Docker image build (`front`, `api`, `etl`).
5. `deploy-testable-admin`: local CI deployment + smoke checks (`/health`, `/interne/HomePage`).
6. `docker-push`: GHCR image push on `push` to `main` only.

## 2) Environment variables and secrets

Reference file: `.env.example`

Runtime variables:
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `JWT_SECRET`
- `PROMETHEUS_URL`
- `GRAFANA_URL`
- `REACT_APP_API_URL`

CI expected secrets/values:
- `GITHUB_TOKEN` (provided automatically by GitHub Actions)
- `API_KEY` (if your deployment/integration uses it)
- `DB_URL` (if your deployment/integration uses it)

## 3) Local prerequisites

- Python `3.11+`
- Node.js `20+`
- Docker + Docker Compose v2

## 4) Local startup commands

### Full stack (Docker)
```bash
docker compose up --build
```

### Stop stack
```bash
docker compose down -v
```

## 5) Local test commands

### Backend
```bash
python -m pip install -r platform/server/requirements.txt
python -m pytest -q platform/server/test/unit
python -m pytest -q platform/server/test/integration/api_db
python -m pytest -q platform/server/test/E2E
```

### Frontend
```bash
cd platform/front/app
npm ci
CI=true npm test -- --watch=false --passWithNoTests
npm run build
```

### Local CI smoke (admin interface)
```bash
docker compose up -d db
docker compose up -d --no-deps api front
curl -f http://localhost:8000/health
curl -f http://localhost:3000/interne/HomePage
docker compose down -v
```

## 6) Notes on reliability and failures

- Backend test suites are executed in separate commands in CI to avoid fixture cross-contamination.
- Backend E2E tests use an isolated in-memory SQLite database and override FastAPI DB dependency safely per test.
- If smoke checks fail, inspect:
  - `docker compose ps`
  - `docker compose logs api --tail=80`
  - `docker compose logs front --tail=80`

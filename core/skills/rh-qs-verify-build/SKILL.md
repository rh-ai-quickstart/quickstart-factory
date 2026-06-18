---
name: rh-qs-verify-build
description: |
  Verify that the local build process and development workflow succeed. Checks the correctness of build tooling, container images, and key environment settings after implementation is complete.
---

# rh-qs-verify-build

**Category:** `implementation/`

---

## Trigger

When implementation vertical slice is complete and verified locally.

---

## Purpose

This skill verifies that the development and build processes for all code packages work as expected, both locally and in containers. It catches integration issues and ensures the application is ready for deployment.

---

## What it does

- Runs the local build using `make` targets or other repo build tooling.
- If a local build is not defined, runs individual container builds (e.g., via Docker/Podman Compose).
- Verifies that all referenced images exist and can be built without errors.
- Tests all development and production configurations (e.g., environment variables for both) to make sure no hardcoded secrets or values exist.

### Essential Checks

- [ ] All containers/images listed in `compose.yml` build successfully from the repo root.
- [ ] Any referenced build scripts (Makefile, pnpm, uv, etc) run without error.
- [ ] Each environment (dev/prod) is supported by build scripts and there are no hardcoded secrets/configs.
- [ ] Health endpoints respond when the stack is run locally (`make dev` or `docker compose up`).
- [ ] All default build/test commands (see Quality Gates) complete without errors.
- [ ] There are **no committed artifacts**: `venv/`, `node_modules/`, `__pycache__/`, or `.env`.
- [ ] No references to `"ai-quickstart-template"` remain in the source except for upstream links.

---

## Quality Gates

```bash
make lint
make test
```
*Or equivalent commands in your project.*

---

## Layer Requirements

### Backend
- Provide `/health` first, then core domain routes.
- Pydantic schemas in `src/schemas/`
- Async SQLAlchemy via `packages/db`
- `pytest` "happy-path" tests at minimum.

### Frontend
- Primary route calls API via `VITE_API_BASE_URL`
- All essential components/hook have Vitest tests.
- Proper error and loading states are present.

### Database
- Models live in `packages/db`
- Alembic migrations exist (if relevant).
- API package does not duplicate DB models.

### RAG Ingestion (if in design/PRD)
- Idempotent job or CLI in `packages/ingestion/`
- Pipeline: chunk → embed → write to pgvector

### CI/CD (if in design/PRD)
- Workflows from **`rh-qs-test-suite`** are green on a test PR
- Branch protection required checks match workflow job names

---

## Technology Defaults

| Layer         | Default stack                                                                                           |
| ------------- | ------------------------------------------------------------------------------------------------------ |
| Frontend      | React 19, TypeScript, Vite, TanStack Router/Query, Vitest, ESLint + Prettier                           |
| Backend       | Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2 async, pytest                                         |
| Database      | PostgreSQL (via `packages/db` + Alembic)                                                              |
| Vector DB     | pgvector — unless user specifies otherwise                                                             |
| LLM orchestration | Llama Stack (optional, chosen in architect phase)                                                  |
| Model serving | vLLM via llm-service chart (if on-cluster models needed)                                               |
| Monorepo      | Turborepo, pnpm (Node), uv (Python)                                                                   |
| Local runtime | compose.yml + podman-compose                                                                          |
| Containers    | Containerfile per package (multi-stage, non-root)                                                     |

---

## What *not* to include

- Storybook, demo CRUD, admin UIs, etc. unless specifically in PRD.
- Helm chart subchart wiring (that's for `rh-qs-deploy`).
- Real secrets or production credentials in code, configs, or .env files.

---

## Output

A working application that:
- Builds locally with `make lint && make test` (or project equivalents)
- Builds all containers from the repo root with no errors
- Passes quality gates for both dev and prod environments

---

## Next skill

When local vertical slice and build verification succeed → **`rh-qs-deploy`**

---

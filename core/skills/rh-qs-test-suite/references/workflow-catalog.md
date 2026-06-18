# Workflow catalog (it-self-service-agent pattern)

Reference repo: `it-self-service-agent/.github/workflows/`

Use this table to decide which files to copy or adapt for a new quickstart. Rename workflows to match the product; keep **one concern per file**.

## Pull request — fast feedback (`pull_request`)

| File | Workflow name | Jobs | Makefile / notes |
|------|---------------|------|------------------|
| `pr-checks.yml` | Pull Request - Quality Checks & Unit Tests | `code-quality-check`, `helm-export-validate`, `pull-request-tests` | `check-uv-version`, `check-lockfiles`, `check-requirements`, `deps-all`, flake8/black/isort/mypy or `make lint`, `helm-export-validate-demo`, `test-all` |
| `pr-pip-install-build.yml` | Pull Request - Build Test (pip install method) | `build-test-pip-install` | Same Kind path with `use_pip_install: "true"` on kind action |
| `pr-branch-check.yml` | Require dev branch for main PRs | `validate-pr-branch` | Inline bash: source must be `dev` or `dev-<hex>` from same repo |

**Triggers:** `pull_request` types `[opened, synchronize, reopened]`  
**Concurrency:** `${{ github.workflow }}-${{ github.event.pull_request.number }}`

## Pull request — secrets / heavy (`pull_request_target`)

Use when workflows need org secrets (LLM endpoints, Quay, prod cluster). Always checkout the PR head SHA:

```yaml
uses: actions/checkout@v5
with:
  ref: ${{ github.event.pull_request.head.sha }}
```

| File | Workflow name | Jobs | Notes |
|------|---------------|------|-------|
| `pr-e2e-tests.yml` | Pull Request - Integration + End to End Tests | `e2e-tests` | Validates `LLM_API_TOKEN_EVAL`; `prepare-runner` → `kind` → integration makes → `sync-evaluations` → short eval; daily cron `0 2 * * *` |
| `pr-evaluation-check.yml` | Pull Request - Evaluation Check | `evaluation-check` | `make check-known-bad-conversations` without full cluster |

## Push / release

| File | Trigger | Purpose |
|------|---------|---------|
| `build-and-push.yaml` | `push` to `main`, `dev` | `if: github.repository_owner == 'rh-ai-quickstart'`; version from `make version`; multi-tag push to `quay.io/rh-ai-quickstart` |
| `build-and-push-manual.yaml` | `workflow_dispatch` | Manual image build |
| `create-dev-to-main-pr.yaml` | `workflow_dispatch` | GitHub App token; version sync Makefile ↔ Chart.yaml ↔ values image tags; temp branch `dev-<short-sha>` |
| `create-dev-version-bump-pr.yml` | `workflow_dispatch` | Automated version bump on dev |

## Scheduled / nightly

Naming pattern: `nightly-e2e-<scope>-<branch-context>.yml`

| Pattern | Example | Environment |
|---------|---------|-------------|
| Kind + long eval | `nightly-e2e-long-dev.yml` | Checkout `dev`, Kind, `test-long-*` makes |
| Kind + scout prompts | `nightly-e2e-long-scout-prompt-dev.yml` | Variant eval datasets |
| Prod cluster | `nightly-e2e-prod-dev.yml` | `oc login` with `PROD_TOKEN`/`PROD_SERVER`; dedicated namespace; uninstall on success |
| Prod main | `nightly-e2e-prod-main.yml` | Same against `main` |

**Shared concurrency:** prod deploy workflows use a shared group (e.g. `prod-deploy-shared-namespace`) with `cancel-in-progress: false` to avoid namespace collisions.

## Quickstart mapping (typical)

| Design testing level | Workflows to add |
|---------------------|------------------|
| Unit + lint only | `pr-checks.yml` (or keep scaffold `ci.yaml`) |
| Helm render validation | `pr-checks.yml` → `helm-export-validate` job |
| API + DB integration on Kind | `pr-e2e-tests.yml` + `kind` action |
| LLM quality / RAG evals | `pr-e2e-tests.yml` + `pr-evaluation-check.yml` + eval artifact steps |
| Published images | `build-and-push.yaml` |
| dev/main git flow | `pr-branch-check.yml` + `create-dev-to-main-pr.yaml` |

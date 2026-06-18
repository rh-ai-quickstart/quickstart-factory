---
name: rh-qs-deploy
description: Deploy configuration for AI Quickstarts. Wires ai-architecture-charts Helm subcharts, compose.yml for local dev, Containerfiles, and Makefile deploy targets. Use when implementation works locally from rh-qs-implement.
---

# rh-qs-deploy

**Category:** `deployment/`

## Trigger

Implementation works locally from `rh-qs-implement` (`make dev`, `make test` pass)

## What it does

1. Wires **ai-architecture-charts** as Helm subchart dependencies based on the design document
2. Configures `Chart.yaml` with selected subcharts (llama-stack, llm-service, pgvector, minio, mcp-servers, etc.)
3. Sets up `values.yaml` with enablement flags and model configuration
4. Configures `compose.yml` for local development with **podman-compose**
5. Creates **Containerfiles** for each deployable package (multi-stage builds)
6. Adds Makefile targets: `make dev`, `make deploy`, `make undeploy`
7. Wires application environment variables to in-cluster services
8. Verifies: `helm lint`, `helm template` renders cleanly, local health checks pass

## Workflow

```
- [ ] 1. Wire Helm app chart (api, ui, db, routes, migration job)
- [ ] 2. Add ai-architecture-charts subchart dependencies
- [ ] 3. Configure values.yaml (models, secrets, resources, GPU)
- [ ] 4. Set up compose.yml for local dev
- [ ] 5. Build/update Containerfiles
- [ ] 6. Wire env vars to in-cluster services
- [ ] 7. Add Makefile deploy targets
- [ ] 8. Verify helm lint + template + local health
```

### Helm subcharts

Add dependencies from https://rh-ai-quickstart.github.io/ai-architecture-charts. Pin versions from design doc.

Detailed guides:

- [Llama Stack + llm-service + pgvector](./references/helm-llamastack.md)
- [MinIO object storage](./references/helm-minio.md)

### Environment wiring

| Variable | Source |
|----------|--------|
| `LLAMA_STACK_URL` | llama-stack subchart service |
| `DATABASE_URL` | app db or pgvector subchart |
| `S3_ENDPOINT` | minio subchart (if enabled) |

Document all variables in `.env.example`. **Never** commit real tokens or API keys.

### Makefile targets

```bash
make dev        # podman-compose local stack
make deploy     # helm upgrade --install to OpenShift (use oc)
make undeploy   # helm uninstall
make helm-lint
make helm-template
```

## Verification

```bash
make helm-lint
helm template deploy/helm/<slug>/ -f deploy/helm/<slug>/values.yaml
make dev && curl -f http://localhost:<port>/health
```

## Output

Complete deployment configuration: Helm chart, compose.yml, Containerfiles, and working Makefile targets.

## Next skill

When deploy configs render and health checks pass → **`rh-qs-test-suite`** (if design includes Kind/E2E/evals), then **`rh-qs-verify-build`** and **`rh-qs-document`**

## References

- [Helm: Llama Stack guide](./references/helm-llamastack.md)
- [Helm: MinIO guide](./references/helm-minio.md)
- [ai-architecture-charts](https://github.com/rh-ai-quickstart/ai-architecture-charts)
- Design doc: `data/designs/<slug>.md`

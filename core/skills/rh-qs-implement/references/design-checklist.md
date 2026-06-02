# Design checklist (pre-build)

Use after the description gate passes and before scaffolding.

## Scope

- [ ] One primary user journey is defined (start → outcome)
- [ ] Out of scope items are listed explicitly
- [ ] Success = demo works locally **and** Helm deploy path is defined

## Components

| Question | Yes → include |
|----------|----------------|
| Does the user interact in a browser? | `packages/ui` |
| Is there server-side logic or REST? | `packages/api` |
| Is data persisted between sessions? | `packages/db` |
| Are documents retrieved by embedding similarity? | pgvector + `packages/ingestion` |
| Is a hosted LLM required on cluster? | ai-architecture-charts (LLM subchart) |
| Is object storage needed for uploads? | MinIO subchart or documented external store |

## OpenShift AI alignment

- [ ] Inference approach named (OpenShift AI model endpoint, vLLM route, external API)
- [ ] GPU need stated or explicitly “CPU-only”
- [ ] Namespace / project assumptions documented for implementer
- [ ] No fabricated “tested on OpenShift AI x.y” version—leave for README skill after verification

## Security and data

- [ ] No real PII or licensed data in repo samples
- [ ] Secrets only via env / Helm values / OpenShift secrets
- [ ] Auth model decided (cluster SSO, API key, or open demo with warning)

## Deliverable quality

- [ ] Vertical slice: one path works before adding secondary features
- [ ] Tests cover API happy path (and ingestion idempotency if RAG)
- [ ] `make lint` and `make test` pass
- [ ] Rename from template slug complete

## README handoff

- [ ] Implementation stable enough for `rh-qs-document`
- [ ] Architecture diagram planned under `docs/images/` if README requires it

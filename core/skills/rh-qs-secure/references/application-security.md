# Application security checklist

Use during `rh-qs-architect`, `rh-qs-implement`, and `rh-qs-deploy`. Checks the **quickstart application**, not agent tooling.

## Secrets and credentials

- [ ] No passwords, tokens, or API keys in Git (including `.env`, `values.yaml`, README)
- [ ] `.env.example` lists variable **names** only; real values from OpenShift Secrets or External Secrets Operator
- [ ] Helm uses `existingSecret` or `Secret` templates with `stringData` populated at install time — not committed values
- [ ] Judge/guardian/LLM API keys injected via Secret mounts or CI secrets — never logged in Job output

## RBAC and identity

- [ ] Each workload uses its own **ServiceAccount** (not `default` unless justified)
- [ ] `Role`/`RoleBinding` scoped to the release namespace
- [ ] No `cluster-admin` for application pods
- [ ] MLflow or shared platform RBAC uses **workspace** scoping when using shared instances
- [ ] Document which OpenShift permissions the **end user** needs to install (typically `admin` or `edit` on one namespace)

## Network and transport

- [ ] In-cluster services use TLS where the platform provides it (e.g. MLflow `:8443`)
- [ ] `insecureSkipVerify` only when documented with a dev-only caveat
- [ ] Routes use appropriate TLS termination (edge vs passthrough)
- [ ] No unnecessary `ClusterIP` exposure of admin interfaces

## LLM, agent, and prompt safety

When the quickstart exposes LLM or agent endpoints:

- [ ] Input validation on API routes (size limits, schema validation)
- [ ] Llama Stack **safety** or guardrail providers configured when available
- [ ] System prompts do not embed secrets or PII
- [ ] User-supplied content is treated as untrusted in judge/guardian calls
- [ ] Rate limiting or resource limits on inference paths where feasible

## Supply chain

- [ ] Container images use pinned tags or digests in production values
- [ ] Helm subchart versions pinned in `Chart.yaml`
- [ ] Dependency bumps follow **`rh-qs-bump-versions`** and re-run `make lint && make test`

## Verification (via Makefile — no raw oc)

Add targets the human or CI runs after deploy:

```makefile
verify-deploy: ## Post-install smoke test (helm test or scripted health checks)
verify-secrets:  ## Fail if values.yaml or templates contain forbidden key patterns
```

Example checks:

```bash
make verify-deploy NAMESPACE=<ns>
make helm-template | grep -E 'password:|apiKey:' && exit 1 || true
```

## Design doc template snippet

```markdown
## Security considerations
### Secrets
- <how secrets are created and referenced>
### RBAC
- <ServiceAccounts and roles>
### LLM / agent safety
- <guardrails, if applicable>
### End-user permissions
- <minimum OpenShift role to install and run>
```

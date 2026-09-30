---
name: rhoai-genai-playground
description: Integrate quickstart resources with RHOAI Gen AI Studio Playground via the playground Helm chart. Use when registering MCP servers, custom model endpoints, or vector stores, or wiring the chart as a dependency.
---

# rhoai-genai-playground

**Category:** `deployment/`

## Trigger

A quickstart needs its deployed MCP servers, model endpoints, or vector stores visible in the RHOAI Gen AI Studio Playground UI.

## What it does

1. Wires the `playground` chart from **ai-architecture-charts** as a Helm subchart dependency
2. Registers MCP servers via ConfigMap in `redhat-ods-applications`
3. Registers custom OpenAI-compatible model endpoints (+ API key Secrets)
4. Optionally registers vector stores for the Playground Knowledge tab
5. Optionally configures `OdhDashboardConfig` feature flags
6. Optionally runs a post-install Job against Playground LlamaStack
7. Does **not** deploy Gen AI Studio or its LlamaStack — registration only

## Workflow

```
- [ ] 1. Add playground Chart.yaml dependency
- [ ] 2. Configure playground values (MCP / endpoints / vector stores)
- [ ] 3. Install via parent chart or helm upgrade
- [ ] 4. Create endpoint Secrets (endpoint-api-key-N) after deploy
- [ ] 5. Create Playground in UI (lsd-genai-playground-service)
- [ ] 6. Verify ConfigMaps + post-install Job (if enabled)
```

### Helm dependency

```yaml
dependencies:
  - name: playground
    version: 0.0.2
    repository: https://rh-ai-quickstart.github.io/ai-architecture-charts
    condition: playground.enabled
```

### Values wiring

```yaml
playground:
  enabled: true
  dashboardConfig:
    enabled: false
  mcpServers:
    enabled: true
    servers:
      - name: MCP-Example
        url: "http://mcp-example.{{ .Release.Namespace }}.svc:8000/mcp/"
        description: Example MCP server
  customEndpoints:
    enabled: true
    endpoints:
      - modelId: <id>
        displayName: <name>
        url: <openai-compatible-url>
        apiKey: ""                    # leave empty → create Secret manually after deploy
        providerType: remote::openai  # optional, default remote::openai
        modelType: llm               # llm | embedding
        # embeddingDimension: 768    # required when modelType is embedding
  vectorStores:
    enabled: false
```

The ConfigMap always references `endpoint-api-key-N` Secrets. Helm creates those Secrets only if `apiKey` is non-empty; leave it `""` and create the Secret manually after install to avoid committing credentials. Do not `--set` endpoint array fields (wipes siblings). **Never** commit real tokens or API keys.

### Install

```bash
make deploy NAMESPACE=<namespace>
```

Or standalone (without parent chart):

```bash
helm upgrade --install playground playground \
  --repo https://rh-ai-quickstart.github.io/ai-architecture-charts \
  --version 0.0.2 \
  -n <namespace>
```

## Verification

```bash
make verify-deploy NAMESPACE=<namespace>
```

The verify target checks:

- MCP ConfigMap exists in `redhat-ods-applications`
- Model endpoint ConfigMap exists in release namespace
- Vector store ConfigMap exists (if enabled)
- Post-install Job succeeded (if enabled — requires UI Playground first)

## Output

Playground registration resources: MCP ConfigMap, optional model endpoint ConfigMap/Secrets, optional vector-store ConfigMap, optional `OdhDashboardConfig`, optional post-install Job.

## Constraints

- **Playground LlamaStack:** `lsd-genai-playground-service:8321` appears only after a user creates a Playground in the UI. Post-install Jobs that wait on it will block until then.
- **Values nesting:** feature flags under chart `.Values.playground.*` need `playground.playground.<flag>` as a subchart when `dashboardConfig.enabled: true` (or fix the chart).
- **API keys:** create `endpoint-api-key-N` Secrets after deploy (ConfigMap already references them). Optional: supply via a values override file at install time. Never `--set` endpoint array fields.
- Requires RHOAI **3.4+** and cluster admin for `redhat-ods-applications`.

## References

- [Values and resources](./references/values-and-resources.md)
- [ai-architecture-charts](https://github.com/rh-ai-quickstart/ai-architecture-charts)
- Chart repo: [https://rh-ai-quickstart.github.io/ai-architecture-charts](https://rh-ai-quickstart.github.io/ai-architecture-charts)

# Values and resources

## Resources created

| Resource | Destination | Condition |
|----------|-------------|-----------|
| ConfigMap `gen-ai-aa-mcp-servers-<release-namespace>` | `redhat-ods-applications` | `mcpServers.enabled` + servers non-empty |
| ConfigMap `gen-ai-aa-custom-model-endpoints` | release namespace | `customEndpoints.enabled` + endpoints non-empty |
| Secret `endpoint-api-key-N` (per endpoint) | release namespace | `customEndpoints.enabled` + `apiKey` non-empty |
| ConfigMap `gen-ai-aa-vector-stores` | release namespace | `vectorStores.enabled` + stores non-empty |
| OdhDashboardConfig `odh-dashboard-config` | `redhat-ods-applications` | `dashboardConfig.enabled` |
| Job `<fullname>-post-install` | release namespace | `postInstall.enabled` + command non-empty (not a Helm hook) |

## Key values

| Key | Purpose |
|-----|---------|
| `enabled` | Parent-only condition for the subchart |
| `dashboardConfig.enabled` | Create `OdhDashboardConfig` in `redhat-ods-applications` |
| `mcpServers.enabled` / `.namespace` / `.servers[]` | MCP registration (`name`, tpl `url`, `description`); `enabled` defaults to `true` |
| `customEndpoints.enabled` / `.namespace` / `.endpoints[]` | External OpenAI-compatible models + `endpoint-api-key-N` Secrets (`modelId`, `displayName`, `url`, `apiKey`, `providerType`, `modelType`, `embeddingDimension`) |
| `vectorStores.enabled` / `.namespace` / `.stores[]` | Knowledge tab stores (`providerId`, `providerType`, `host`, `port`, `db`, `user`, `distanceMetric`, `credentialSecret`, `vectorStoreId`, `displayName`, `embeddingModel`, `embeddingDimension`) |
| `postInstall.enabled` / `.namespace` / `.image` / `.command` / `.env` / `.envFrom` / `.backoffLimit` / `.waitForLlamaStack.*` | Optional Job: runs after install/upgrade |
| `clusterDomains` | Custom endpoint allowlisting |

## Chart source

| Item | Value |
|------|-------|
| Repository | https://github.com/rh-ai-quickstart/ai-architecture-charts |
| Helm repo | https://rh-ai-quickstart.github.io/ai-architecture-charts |
| Chart | `playground` |
| Version | `0.0.2` |
| appVersion | `3.4` |

## Sibling charts

`llama-stack`, `llm-service`, `mcp-servers`, `pgvector` — related stack pieces in the same chart repository, not this registration chart.

# ai-architecture-charts mapping

Repository: https://github.com/rh-ai-quickstart/ai-architecture-charts  
Helm repo: https://rh-ai-quickstart.github.io/ai-architecture-charts

Use during `rh-qs-architect` to select subcharts; `rh-qs-deploy` wires them as Helm dependencies.

## Available charts

| Chart | When to use | PRD trigger |
|-------|-------------|-------------|
| llama-stack | Agent orchestration, multi-provider LLM, safety shields | agents, tool use, RAG orchestration, safety |
| llm-service | On-cluster model serving via vLLM | local model, GPU inference, no external API |
| pgvector | Vector embeddings and similarity search | RAG, semantic search, document retrieval |
| minio | S3-compatible object storage | document upload, file processing, data lake |
| mcp-servers | External tool access for AI agents | tool calling, external APIs, DB queries from agents |
| ingestion-pipeline | Document chunking, embedding, indexing | document ingestion, PDF processing, web scraping |
| configure-pipeline | Jupyter environment for RAG pipeline config | notebook-based configuration, interactive setup |
| model-registry | Model versioning and lifecycle | model versioning, A/B testing, model promotion |
| oracle-db | Enterprise DB with AI vector features | PRD explicitly requires Oracle (default is pgvector) |

## Red Hat OpenShift AI 3.4 feature mapping

| RHOAI feature | Maps to |
|---------------|---------|
| Model Serving (KServe / ModelMesh) | llm-service chart, vLLM runtime |
| Data Science Pipelines (Tekton) | configure-pipeline, ingestion-pipeline |
| Workbenches (JupyterLab) | configure-pipeline chart |
| Model Registry | model-registry chart |
| TrustyAI (bias/explainability) | Llama Stack safety shields |
| Distributed Workloads (Ray/Kueue) | Custom — not in charts yet |
| GPU autoscaling | llm-service tolerations + node selectors |

## Decision points to confirm with user

- Do you want Llama Stack?
- Local model (llm-service) or remote OpenAI-compatible endpoint?
- MinIO for document storage?
- MCP servers for external tool access?

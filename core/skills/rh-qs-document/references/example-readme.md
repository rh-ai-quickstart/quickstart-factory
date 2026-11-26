# Gold example README — ansible-log-analysis (the canary)

The canary repo's README, written to the CURRENT rules in
`template-structure.md` and `writing-style.md`. This is what the skill
should produce for this repo: same structure, house voice, and
evidence-gated facts, at overview altitude. Study its STRUCTURE and TONE
only — never copy its content into another repository's README.

---

# Accelerate Ansible troubleshooting with intelligent log analysis

Cut Ansible troubleshooting time with an AI agent that detects automation errors, routes them to the right experts, and generates guided remediation steps.

## Table of contents

1. [Detailed description](#detailed-description)
   - [The challenge](#the-challenge)
   - [Our solution](#our-solution)
   - [Architecture](#architecture)
2. [Usage](#usage)
   - [Expert UI](#expert-ui)
   - [Annotation and evaluation interface](#annotation-and-evaluation-interface)
3. [Requirements](#requirements)
   - [Minimum hardware requirements](#minimum-hardware-requirements)
   - [Minimum software requirements](#minimum-software-requirements)
   - [Required user permissions](#required-user-permissions)
4. [Deploy](#deploy)
   - [Quick Start - OpenShift Deployment](#quick-start---openshift-deployment)
   - [Quick Start - Local Development](#quick-start---local-development)
   - [Validating the deployment](#validating-the-deployment)
   - [Delete](#delete)
5. [Repository structure](#repository-structure)
6. [References](#references)
7. [Technical details](#technical-details)
8. [Tags](#tags)

## Detailed description

### The challenge

Teams running Ansible automation at scale troubleshoot failures by hand: an analyst searches the logs for errors, tracks down the one person authorized to fix each one (the AWS admin for provisioning failures, the programmer for playbook bugs), and waits for them to understand and solve the problem. Resolving more error logs this way requires more headcount, so cost grows with automation volume while mean time to resolution (MTTR) stays high.

### Our solution

Errors stop being found by hand: the system watches your Ansible logs, detects and categorizes each error as it happens, and routes it to the expert authorized to fix it — the AWS admin for provisioning failures, the playbook owner for bugs — with a contextual, step-by-step resolution attached. The analyst no longer searches logs or chases the right person, and the expert no longer starts from scratch. Your team resolves more failures with the headcount it already has, so mean time to resolution falls as automation grows instead of cost.

### Architecture

1. Alloy or Promtail ships logs from the Red Hat Ansible Automation Platform (AAP) clusters into Loki.
2. Grafana alerts on error logs, sending them to the agentic workflow.
3. The agentic workflow analyzes each error log, storing its suggestions in PostgreSQL.
4. The log analyst views the logs and suggested fixes in the UI, filtered by their authorization.

<img src="docs/images/high_level_architecture.png" alt="High-level architecture: AAP logs ingested into Loki, alerted on by Grafana, processed by an agentic workflow, and surfaced to analysts in a UI" style="width:70%;">

## Usage

The walkthrough below shows the deployed quickstart in action — for deployment itself, see [Deploy](#deploy).

### Expert UI

Each expert selects their role, depending on their authorization (Kubernetes/OpenShift cluster admins, DevOps/CI-CD engineers, networking/security engineers, system administrators, application developers, IAM engineers, and so on). The expert can filter alerts by labels (cluster_name, log_file_name, …); each log is listed as a summary, and clicking it shows the whole log, a step-by-step solution, timestamp, and labels.

<img src="docs/images/experts_option.png" alt="Expert role selection in the UI" style="width:40%;">

After selecting the authorization class "expert":

<img src="docs/images/ui_view.png" alt="Log summaries filtered by expert authorization" style="width:60%;">

<img src="docs/images/step-by-step.png" alt="Step-by-step solution for a selected log" style="width:60%;">

### Annotation and evaluation interface

To improve the agentic workflow and its supporting materials, the quickstart ships a data annotation interface for labeling the pipeline's outputs. Select from the log templates detected in your Ansible error logs, then have domain experts annotate errors and write the expected step-by-step solutions.

<img src="docs/images/annotation_part_1.png" alt="Selecting a detected log template for annotation" style="width:60%;">

Once annotation is complete (in this example, 43 logs), run the evaluation and use LLM-as-a-judge to compare the agent output against the expert-labeled golden output — the cases that score poorly point to where your prompts, data, or code need improvement.

<img src="docs/images/annotation_part_2.png" alt="Annotating a log with the expected step-by-step solution" style="width:60%;">

<img src="docs/images/annotation_part_3.png" alt="Evaluation results comparing agent output against expert labels" style="width:60%;">

## Requirements

### Minimum hardware requirements

CPU: 3-4 cores
Memory: 10Gi
Storage: 50Gi for the mock data; increase toward 200Gi for a large amount of logs
GPU: optional — model GPU requirements apply only if you deploy your own model on OpenShift AI (see [References](#references)); no GPU is required when using an external LLM endpoint

### Minimum software requirements

**OpenShift cluster deployment**
- **Red Hat OpenShift AI** 2.25.0 or later
- **Helm** 3.0.0 or later
- **oc CLI** — `TODO: version` (the repo does not pin one)

**External services and credentials**
- **LLM endpoint and API token** (credentials) — Red Hat OpenShift AI model serving (vLLM) recommended for enterprise deployments, or any OpenAI-compatible endpoint with its API key

**Local development**
- Podman and Podman Compose, or Docker and Docker Compose — `TODO: version`
- `uv` 0.9.x with Python 3.12+
- Make — `TODO: version`

### Required user permissions

**Local development**
- Permission to run containers via Docker or Podman
- Access to local ports: `3000`, `3100`, `5432`, `6006`, `7860`, `7861`, `8000`, `8080`, `8081`

**OpenShift cluster deployment**
- Authenticated to the OpenShift cluster (`oc login`)
- Permission to create or access a namespace/project — regular user / namespace admin is sufficient; no cluster-admin required

## Deploy

The Ansible Log Monitor can be deployed in **cluster** (production) or **local** (development and testing) mode.

**Prerequisites:** access to an OpenShift cluster with OpenShift AI installed and a namespace you can deploy into (see [Requirements](#requirements)); the `oc`, `helm`, and `make` CLI tools; credentials — `oc login` authentication plus your LLM endpoint API token; and network access from the cluster to your LLM endpoint.

This quickstart assumes a large language model is already deployed in your environment — see the model options below and [References](#references) for deployment guidance.

### Quick Start - OpenShift Deployment

```bash
# Install in your current namespace
make cluster/install

# Or specify a different namespace
make cluster/install NAMESPACE=ansible-logs-monitor
```

During installation, you'll be prompted to configure:
- API token
- LLM endpoint URL — Red Hat OpenShift AI model serving (vLLM) recommended; any OpenAI-compatible endpoint works
- Model name (e.g., the model deployed on your RHOAI model server)
- Temperature (optional — defaults are provided)

> **Note:** You can also create `.env` first (see step 2 of the local deployment below) and skip the prompting part.

**Model options:**
- **Option A — bring your own endpoint (no GPU required):** any OpenAI-compatible endpoint, with Red Hat OpenShift AI model serving (vLLM) recommended for its enterprise features. Test model access before deploying.
- **Option B — deploy your own model in-cluster:** the chart deploys no default model; hosting one on OpenShift AI model serving requires a GPU (see [References](#references)).

Additional commands:

```bash
# upgrade
make cluster/upgrade

# restart
make cluster/restart
```

### Quick Start - Local Development

1. **Clone and set up the repository:**

   ```bash
   git clone https://github.com/rh-ai-quickstart/ansible-log-analysis.git
   cd ansible-log-analysis
   ```

2. **Configure environment variables** — copy the template and edit it with your API keys and configuration:

   ```bash
   cp .env.example .env
   ```

   ```bash
   OPENAI_API_ENDPOINT: # LLM endpoint URL (RHOAI model serving or any OpenAI-compatible endpoint; some endpoints need /v1 suffix)
   OPENAI_API_TOKEN: # Your token to the endpoint (RHOAI service account token or API key)
   OPENAI_MODEL: # Model to use (e.g., the model deployed on your RHOAI vLLM server)
   LANGSMITH_API_KEY: # Optional, for LangSmith tracing
   ```

3. **Start all services and run the training pipeline:**

   ```bash
   # Launch all services in the background
   make local/install

   # Run the complete training pipeline (do it after local/install)
   make local/train

   # Perform status check to see which services are running
   make local/status

   # Uninstall all services when done
   make local/uninstall
   ```

### Validating the deployment

**OpenShift cluster deployment** — after installation, check the routes:

```bash
oc get routes -n <namespace>
```

**Local deployment** — verify services with `make local/status`, then open:
- User interface: `http://localhost:7861`
- Annotation interface and evaluation system: `http://localhost:7860`
- Phoenix tracing: `http://localhost:6006`

Once the deployment validates, walk the features in [Usage](#usage).

### Delete

```bash
# Remove from the current OpenShift project
make cluster/uninstall

# Or from a specific namespace
make cluster/uninstall NAMESPACE=ansible-logs-monitor

# Stop the local deployment
make local/uninstall
```

## Repository structure

```
├── deploy/
│   ├── helm/ansible-log-monitor/   # Helm chart — backend, UI, annotation-interface, clustering,
│   │                                #   RAG, TEI, Phoenix subcharts, plus Loki, Grafana, Alloy, MCP servers
│   └── local/                      # Podman/Docker Compose local deployment
├── services/
│   ├── aap-log-collector/          # collects logs from the AAP cluster
│   ├── alloy/                      # Alloy log shipping configuration
│   ├── clustering/                 # log embedding and template clustering
│   ├── rag/                        # RAG knowledge base and retrieval
│   ├── text-embeddings-inference/  # TEI embedding service
│   ├── annotation_interface/       # Gradio annotation and evaluation UI
│   └── ui/                         # Gradio expert dashboard
├── src/alm/                        # the agentic workflow — agents, pipeline, MCP tools, FastAPI routes
├── data/                           # mock logs, knowledge base, example queries
├── docs/images/                    # architecture diagrams and UI screenshots
├── examples/                       # example scripts against the running stack
├── tests/
├── Makefile                        # cluster/local install, train, status, uninstall targets
└── pyproject.toml
```

## References

- [How to deploy language models with Red Hat OpenShift AI](https://developers.redhat.com/articles/2025/09/10/how-deploy-language-models-red-hat-openshift-ai#)
- [Deploying models on the OpenShift AI model serving platform](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.0/html/deploying_models/deploying_models#deploying-models-on-the-model-serving-platform_rhoai-user)
- [Red Hat OpenShift AI documentation](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/)
- [Ansible Automation Platform documentation](https://docs.redhat.com/en/documentation/ansible_automation_platform/)
- [OpenShift route configuration](https://docs.openshift.com/container-platform/4.11/networking/routes/route-configuration.html) — linked from the chart's values files

## Technical details

Notable components of the stack:

- **Red Hat OpenShift AI — model serving** — serves the LLM (vLLM) that powers summarization, classification, and solution generation.
- **Red Hat OpenShift AI — data science pipelines** — run the training pipeline that fits the log-clustering model.
- **Red Hat OpenShift AI — workbenches** — notebook environment for developing and experimenting with the workflow.
- **Loki** — time-series log database for storing, aggregating, and querying Ansible logs.
- **Alloy / Promtail** — log collection agents ingesting from the AAP cluster.
- **LangGraph** — builds the agentic workflow.
- **MCP (Model Context Protocol)** — tool integration for Loki queries and Ansible code retrieval; uses an enhanced fork with additional query capabilities.
- **TEI (Text Embeddings Inference) + Sentence Transformers** — embeddings for log clustering by template similarity and RAG.
- **FAISS** — vector similarity search over the knowledge base.
- **[aws-compatible-storage](https://github.com/rh-ai-quickstart/ai-architecture-charts/tree/main/aws-compatible-storage) (S4)** — S3-compatible object storage for the RAG index and Loki chunks.
- **Phoenix + OpenTelemetry** — distributed tracing for LLM calls and pipeline monitoring.
- **Gradio** — the expert-facing dashboard and the annotation/evaluation interface.

The agentic workflow processes each alerted log in four steps:

<img src="docs/images/workflow.png" alt="Agentic workflow" style="width:70%">

1. **Embedding and clustering** — logs generated from the same template (e.g. `error: user id 10 already exists.` and `error: user id 15 already exists.`) are embedded and clustered into groups, so analysts can filter by template.
2. **Summary and expert classification** — each template gets a summary and an authorization classification; analysts see only the error summaries relevant to their authorization.
3. **Step-by-step solution generation** — a router decides whether the log alone suffices or more context is needed; if so, an agent accumulates context via the Loki MCP (querying the log database), RAG over a cheat sheet of already-solved questions, and the Ansible MCP (source code data).
4. **Storage** — a payload of the generated values for each log is stored in PostgreSQL.

The only difference between the training and inference stages is the clustering algorithm: training fits it to cluster logs by template; inference loads the trained model.

## Tags

**Title:** Accelerate Ansible troubleshooting with intelligent log analysis

**Description:** Cut Ansible troubleshooting time with an AI agent that detects automation errors, routes them to the right experts, and generates guided remediation steps.

**Industry:** Adopt and scale AI

**Product:** Red Hat OpenShift AI, Ansible Automation Platform

**Use case:** AI Operations, Log Analysis, Ansible Automation

**Contributor org:** Red Hat

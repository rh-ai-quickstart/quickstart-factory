---
name: rh-qs-minio-conversion
description: |
  Convert an existing AI Quickstart from the MinIO Helm subchart to S4 (Super Simple
  Storage Service) from rh-aiservices-bu/s4. Removes MinIO chart wiring, adds the S4
  Helm chart, updates app endpoints/credentials, and rewrites MinIO mentions in docs.
  Use when migrating a quickstart off ai-architecture-charts minio onto S4.
---

# rh-qs-minio-conversion

**Category:** `maintenance/`

## Trigger

- User asks to convert MinIO to **S4** / Super Simple Storage Service
- Quickstart currently depends on the [minio](https://github.com/rh-ai-quickstart/ai-architecture-charts/tree/main/minio) chart from **ai-architecture-charts**
- Target is the [rh-aiservices-bu/s4](https://github.com/rh-aiservices-bu/s4) Helm chart (`charts/s4`)

## Goal

Replace self-managed MinIO with **[S4](https://github.com/rh-aiservices-bu/s4)** — a lightweight S3-compatible store (Ceph RGW + web UI in one container) — while keeping the quickstart on the S3 API. Swap endpoints, credentials, Helm wiring, local compose, and docs.

## Where This Runs

Inside the quickstart repo — typically `.rhoai-qs/<slug>/` after scaffold, or a cloned `rh-ai-quickstart/<slug>` checkout. Resolve the slug before editing (Phase 0).

**Proven conversions (patterns to copy):**

| Quickstart | Chart path | Notes |
|------------|------------|--------|
| Fraud-Detection-data-versioning-with-lakeFS | `deploy/helm/fraud-detection` | lakeFS blockstore + DSPA + notebook PVC clone Jobs |
| Billing-extraction-with-GroundX | `helm/billing-workloads` | GroundX + notebook data connection; buckets `eyelevel`, `billing-artifacts` |

## What it does

1. Inventories every MinIO dependency (Helm, compose, app code, env, docs, CI, **PNG/Mermaid diagrams**)
2. Removes the MinIO package / subchart (and `configure-pipeline` MinIO path when that was the only reason for it)
3. Adds the **S4** Helm chart from [rh-aiservices-bu/s4](https://github.com/rh-aiservices-bu/s4) as a subchart
4. Rewires workloads to S4’s S3 API (`:7480`) and credential Secret
5. Adds a **bucket bootstrap Job** that does not depend on Docker Hub / `minio/mc`
6. Updates READMEs, `.env.example`, design notes, and MinIO mentions → S4
7. Verifies with `helm lint` / `helm template` and recommends **`rh-qs-verify-deploy`**

## Prerequisites

| Requirement | Notes |
|-------------|--------|
| Existing MinIO usage | Direct `minio` subchart **or** `configure-pipeline` with `pipelineStorage.deployMinio: true` |
| S3-compatible client code | boto3 / minio-py / AWS SDK — keep the S3 API; change endpoint + credentials |
| Cluster PVC support | S4 needs a PVC for RGW data (default `10Gi`) |
| S4 chart source | [github.com/rh-aiservices-bu/s4](https://github.com/rh-aiservices-bu/s4) → `charts/s4` (not in ai-architecture-charts) |
| Pullable Job images | Prefer Red Hat / in-cluster registries (see [Job images](#job-images--do-not-use-docker-hub-or-miniomc)) |

## MinIO → S4 mapping

| Concern | MinIO (ai-architecture-charts) | S4 ([rh-aiservices-bu/s4](https://github.com/rh-aiservices-bu/s4)) |
|---------|--------------------------------|---------------------------------------------------------------------|
| Chart | `minio` from ai-architecture-charts | `charts/s4` from s4 repo |
| Image | `quay.io/minio/minio` | `quay.io/rh-aiservices-bu/s4` (pin tag, e.g. `0.3.2`) |
| S3 API port | **9000** | **7480** |
| Web / console | **9090** (`minio-webui`) | **5000** (S4 UI Route by default) |
| In-cluster endpoint | `http://minio:9000` | `http://s4:7480` (with `fullnameOverride: s4`) |
| Credentials Secret | `minio` → `user` / `password` | `{fullname}-credentials` → `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` |
| Default access key | `minio_rag_user` (values) | `s4admin` |
| Default secret key | `minio_rag_password` (values) | `s4secret` |
| Readiness probe (wait Jobs) | `http://minio:9000/minio/health/live` | `http://s4:5000/api` (UI) or boto3 `list_buckets` on `:7480` |
| Sample / bucket bootstrap | subchart `sampleFileUpload` / `mc` | **Parent Job + boto3** on UBI Python (see below) — **not** `quay.io/minio/mc` |
| UI auth | MinIO console login | `auth.enabled` + `auth.username` / `auth.password` (required when auth on) |

## Hard-won rules (read before implementing)

These failures showed up on real OpenShift clusters during Fraud Detection and Billing conversions:

### 1. Helm `--wait` vs post-install hooks

Helm runs **`--wait` before post-install hooks**. If a consumer (e.g. OpenShift AI **DSPA**) stays unready until a bucket exists, and that bucket Job is a `post-install` hook, install hangs until timeout and hooks never run.

**Fix:** Make bucket (and lakeFS repo, if needed) creation a **regular Job** in the release resources — not a Helm hook — with wait loops for S4 readiness. Keep optional post-install hooks only for work that can run after the release is Ready (e.g. pipeline upload).

### 2. DSPA / external operators need FQDN

DSPA’s object-store probe often runs **outside** the release namespace. Host `s4` fails with `lookup s4 … no such host`.

**Fix:**

```yaml
dataSciencePipelines:
  objectStorage:
    host: s4.<namespace>.svc.cluster.local   # not bare "s4"
    port: "7480"
    scheme: http
```

In templates, default with `printf "s4.%s.svc.cluster.local" .Release.Namespace`. Keep in-cluster app env as `http://s4:7480` (same namespace).

### 3. Job images — do not use Docker Hub or minio/mc

| Avoid | Why |
|-------|-----|
| `quay.io/minio/mc:…` | Often **unauthorized** / not pullable |
| `curlimages/curl`, `busybox`, `python:3.11-slim`, `alpine/git` | Docker Hub **rate limits** → `ImagePullBackOff` |

**Prefer:**

```yaml
jobImages:
  cli: image-registry.openshift-image-registry.svc:5000/openshift/cli:latest   # curl + shell
  python: registry.redhat.io/ubi9/python-311:latest                            # boto3 bootstrap
  shell: registry.redhat.io/ubi9/ubi-minimal:latest                            # PVC wait
```

### 4. UBI Python + pip

`registry.redhat.io/ubi9/python-311` uses a venv where **`pip install --user` fails** (`User site-packages are not visible in this virtualenv`).

**Fix:** `pip install --no-cache-dir -q boto3` (no `--user`). Set `HOME=/tmp` for writable caches.

### 5. Credentials wiring

Prefer `secretKeyRef` → `s4-credentials` for `AWS_*` / `PIPELINE_ARTIFACTS_*`. Avoid inlining `s4admin`/`s4secret` in Notebook/Deployment env when the Secret exists. ODH data-connection Secrets (e.g. `pipeline-artifacts`) may still mirror keys for DSPA — keep them in sync with `s4.s3.*`.

### 6. Docs / diagrams

Inventory **PNG architecture images** as well as Markdown. A leftover MinIO box fails checklist item “docs describe S4”. Prefer replacing with **Mermaid** in the README when regenerating a PNG is awkward.

---

## Workflow

### Phase 0: Resolve quickstart

Resolve which quickstart this session is for before any edits. List sibling slugs under `.rhoai-qs/` (exclude `reports` and `blog-drafts`) and confirm the target when more than one exists. See [validation-skill-template.md](../../../docs/foundation/validation-skill-template.md).

### Phase 1: Inventory MinIO surface area

```
- [ ] 1. Chart.yaml — minio and/or configure-pipeline dependencies
- [ ] 2. values.yaml / values-*.yaml — minio.*, configure-pipeline.minio.*, pipelineStorage.deployMinio
- [ ] 3. Parent templates — bucket Jobs, hooks, Routes, Secrets referencing minio
- [ ] 4. App code — MINIO_*, AWS_* pointing at http://minio:9000, minio SDK clients
- [ ] 5. compose.yml / Containerfiles — local MinIO or minio/mc images
- [ ] 6. Makefile / CI — minio-console, health checks, sample-upload targets
- [ ] 7. Docs — README, design, Mermaid, **and PNG/SVG diagrams** labeled MinIO
- [ ] 8. DSPA / lakeFS / GroundX — anything that must be Ready before hooks run
```

Present a short inventory and confirm conversion scope (Helm-only vs Helm + app + docs).

### Phase 2: Spec the conversion (approve before edit)

Draft the mapping for this quickstart (service DNS name, bucket names, auth, PVC size, bootstrap Job vs hook, DSPA FQDN). Get user approval, then implement.

### Phase 3: Remove MinIO from Helm

```
- [ ] 1. Remove `minio` from Chart.yaml `dependencies` (or disable permanently and delete values)
- [ ] 2. If Path B was configure-pipeline solely for MinIO, disable `pipelineStorage.deployMinio` or remove that subchart if unused otherwise
- [ ] 3. Delete parent hooks/Jobs that assume Service `minio` or Secret `minio`
- [ ] 4. Drop `minio:` value blocks (secret, sampleFileUpload, volumeClaimTemplates, routes)
- [ ] 5. Run `helm dependency update` so charts/ no longer vendors minio
```

Reference for what you are removing: [rh-qs-deploy/references/helm-minio.md](../rh-qs-deploy/references/helm-minio.md).

### Phase 4: Add the S4 Helm chart

Upstream: [charts/s4](https://github.com/rh-aiservices-bu/s4/tree/main/charts/s4). S4 is **not** published on the ai-architecture-charts Helm repo — vendor or fetch from GitHub.

**Recommended: vendor as a subchart**

```bash
# From the quickstart Helm chart directory (e.g. deploy/helm/<slug>/)
mkdir -p charts
git clone --depth 1 https://github.com/rh-aiservices-bu/s4.git /tmp/s4
# Pin: record commit in Chart.yaml comments, e.g. @ 797911c
cp -R /tmp/s4/charts/s4 charts/s4
```

**Chart.yaml dependency (file path after vendoring):**

```yaml
dependencies:
  # S4 — vendored from rh-aiservices-bu/s4 @ <commit> (charts/s4 v0.1.0)
  - name: s4
    version: 0.1.0   # match charts/s4/Chart.yaml version
    repository: "file://charts/s4"
    condition: s4.enabled
```

Then:

```bash
helm dependency update
```

**Minimal values** (predictable DNS + OpenShift UI route):

```yaml
s4:
  enabled: true
  fullnameOverride: s4          # Service DNS → s4:<ports>
  image:
    repository: quay.io/rh-aiservices-bu/s4
    tag: "0.3.2"
    pullPolicy: IfNotPresent
  s3:
    accessKeyId: s4admin        # override per env; do not commit prod secrets
    secretAccessKey: s4secret
  auth:
    enabled: true
    username: admin             # required when auth.enabled=true
    password: changeme          # via overlay / --set, not Git
  route:
    enabled: true               # Web UI on OpenShift (port 5000)
    s3Api:
      enabled: false            # keep S3 API in-cluster only unless explicitly needed
  storage:
    data:
      size: 10Gi                # size to match prior MinIO PVC if needed

# Parent-owned bucket list for bootstrap Job (not passed into S4 chart logic)
s4Buckets:                      # or s4.bootstrap.buckets — keep parent template ownership clear
  create: true
  names:
    - pipeline-artifacts        # example — use this quickstart’s real bucket names
  serviceAccountName: demo-setup

jobImages:
  cli: image-registry.openshift-image-registry.svc:5000/openshift/cli:latest
  python: registry.redhat.io/ubi9/python-311:latest
  shell: registry.redhat.io/ubi9/ubi-minimal:latest
```

S4 creates Secret `s4-credentials` (when `fullnameOverride: s4` and no `existingSecret`) with `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.

### Phase 5: Rewire application and chart consumers

For each consumer (API, ingestion, notebooks, Jobs, DSPA, lakeFS, GroundX):

```
- [ ] 1. Endpoint: http://minio:9000 → http://s4:7480 (apps in same NS)
- [ ] 2. DSPA / cross-namespace probes: s4.<ns>.svc.cluster.local:7480
- [ ] 3. Credentials: Secret minio user/password → s4-credentials AWS_*
- [ ] 4. Prefer secretKeyRef; map legacy MINIO_* only if the app still requires them
- [ ] 5. Path-style addressing if the client defaults to virtual-hosted style
- [ ] 6. Region: us-east-1 (S4 default) unless the app already sets one
- [ ] 7. Bucket bootstrap Job (regular Job + boto3) — see Phase 5b
- [ ] 8. Update .env.example — S4 keys and ports; remove MinIO passwords from Git
- [ ] 9. lakeFS wait init: /minio/health/live → http://s4:5000/api
```

Example consumer env:

```yaml
env:
  - name: AWS_ACCESS_KEY_ID
    valueFrom:
      secretKeyRef:
        name: s4-credentials
        key: AWS_ACCESS_KEY_ID
  - name: AWS_SECRET_ACCESS_KEY
    valueFrom:
      secretKeyRef:
        name: s4-credentials
        key: AWS_SECRET_ACCESS_KEY
  - name: AWS_ENDPOINT_URL
    value: http://s4:7480
  - name: AWS_DEFAULT_REGION
    value: us-east-1
```

If the app still speaks `MINIO_*`:

```text
MINIO_ENDPOINT   ← s4:7480   (or http://s4:7480 — match prior scheme)
MINIO_ACCESSKEY  ← AWS_ACCESS_KEY_ID
MINIO_SECRETKEY  ← AWS_SECRET_ACCESS_KEY
MINIO_BUCKET     ← unchanged app bucket name (create via Job or S4 UI)
```

### Phase 5b: Bucket bootstrap Job (required pattern)

Do **not** use `mc` or Docker Hub images. Use a **regular Job** (not a post-install hook when DSPA/`--wait` depends on buckets):

```yaml
# Sketch — wait for S4 UI, then boto3 create_bucket for each name
initContainers:
  - name: wait-for-s4
    image: {{ .Values.jobImages.cli }}
    command: ["/bin/sh","-c"]
    args:
      - until curl -sf http://s4:5000/api; do sleep 5; done
containers:
  - name: create-buckets
    image: {{ .Values.jobImages.python }}
    env:
      - name: HOME
        value: /tmp
      - name: AWS_ACCESS_KEY_ID
        valueFrom:
          secretKeyRef:
            name: s4-credentials
            key: AWS_ACCESS_KEY_ID
      - name: AWS_SECRET_ACCESS_KEY
        valueFrom:
          secretKeyRef:
            name: s4-credentials
            key: AWS_SECRET_ACCESS_KEY
    command: ["/bin/bash","-ec"]
    args:
      - |
        pip install --no-cache-dir -q boto3
        python3 <<'PY'
        # list_buckets retry loop, then create_bucket for each name
        PY
```

Idempotent: treat “already exists” as success. Optional `ttlSecondsAfterFinished`.

### Phase 6: Local compose (optional)

Cluster path is S4. For laptop compose, prefer the same image:

```bash
podman run -d --name s4 \
  -p 5000:5000 -p 7480:7480 \
  -v s4-data:/var/lib/ceph/radosgw \
  quay.io/rh-aiservices-bu/s4:0.3.2
```

Wire compose services to `http://s4:7480` with `s4admin` / `s4secret` (dev only). Remove the MinIO compose service unless the user wants a temporary dual path.

### Phase 7: Docs, Makefile, verify

```
- [ ] 1. README — MinIO → S4; link https://github.com/rh-aiservices-bu/s4; document UI :5000 and S3 API :7480
- [ ] 2. Architecture diagram — MinIO node → S4 (Mermaid preferred; delete stale PNGs)
- [ ] 3. Makefile — drop minio-console / logs-minio; add logs-s4 (Makefile-wrapped, no raw oc in agent path)
- [ ] 4. verify-deploy — health against S4 S3 API / UI; DSPA ObjectStoreAvailable when applicable
- [ ] 5. Design / pipeline notes under .rhoai-qs/<slug>/ if present
```

### Phase 8: Quality gates

```bash
helm dependency update deploy/helm/<slug>/
helm lint deploy/helm/<slug>
helm template <release> deploy/helm/<slug> -f deploy/helm/<slug>/values.yaml \
  | grep -EIin 's4|minio|7480|9000|minio/mc|docker.io' || true
make lint test helm-lint helm-template   # when targets exist
```

Confirm rendered cluster manifests include S4 Deployment/Service and **no** MinIO StatefulSet / `quay.io/minio`. Recommend **`rh-qs-verify-deploy`**.

Optional: launch an explore subagent against the skill checklist (items 1–7) before calling the conversion done.

## Rules

- **Agents never run `oc`/`kubectl`** for routine work — Helm/Makefile only (`rh-qs-secure`). Cluster debug during an active user deploy may use Makefile targets the user already runs.
- **Never commit** real `auth.password`, S3 secret keys, or cluster Route hostnames
- **Do not** leave both MinIO and S4 enabled for the same workload unless the user explicitly wants dual stores
- Keep S3 API **in-cluster** (`route.s3Api.enabled: false`) unless the design requires external S3 access
- When `auth.enabled: true`, always set `auth.username` and `auth.password` (chart requires them)
- Pin S4 image tag / chart commit when possible; later bumps via **`rh-qs-bump-versions`**
- Prefer **podman** over docker in docs and local examples
- **Never** ship bootstrap Jobs on `quay.io/minio/mc` or unauthenticated Docker Hub images
- Bucket Jobs that unblock `helm --wait` must be **regular Jobs**, not post-install hooks

## Checklist

- [ ] MinIO dependency and values removed (or disabled with no render)
- [ ] S4 chart vendored / depended from [rh-aiservices-bu/s4](https://github.com/rh-aiservices-bu/s4); image tag pinned
- [ ] `fullnameOverride: s4` (or documented Service DNS) so clients use `http://s4:7480`
- [ ] All cluster consumers use S4 credentials Secret + port **7480**
- [ ] DSPA (if present) uses FQDN `s4.<ns>.svc.cluster.local`
- [ ] Bucket bootstrap is a regular Job + UBI Python/boto3 (no `minio/mc`, no Docker Hub)
- [ ] Sample-upload / repo bootstrap updated or documented via S4 UI
- [ ] README / diagram / `.env.example` describe S4, not MinIO (including PNGs)
- [ ] Job/init images use OpenShift CLI / UBI only
- [ ] `helm lint` + `helm template` clean; verify-deploy recommended

## Output

- Updated Helm chart (no MinIO subchart; S4 subchart wired)
- Updated app wiring and env examples
- Updated README / architecture mentions
- Short summary: endpoint/port change, Secret name, auth settings, bootstrap Job pattern, and any leftover `MINIO_*` aliases

## Related

- Upstream: [rh-aiservices-bu/s4](https://github.com/rh-aiservices-bu/s4) — [charts/s4](https://github.com/rh-aiservices-bu/s4/tree/main/charts/s4), [Deployment docs](https://github.com/rh-aiservices-bu/s4/tree/main/docs/deployment)
- Inverse (add MinIO): [rh-qs-deploy/references/helm-minio.md](../rh-qs-deploy/references/helm-minio.md)
- **`rh-qs-secure`** — no raw cluster commands
- **`rh-qs-verify-deploy`** — post-migration cluster check
- **`rh-qs-bump-versions`** — later dependency / image bumps

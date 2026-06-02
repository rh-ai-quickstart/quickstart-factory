---
name: rh-qs-discovery
description: Ideation and interview phase for new AI Quickstarts. Asks structured questions, accepts uploaded context, maps vague ideas to concrete requirements, and produces a PRD. Use when the user says hello to build from scratch, wants to build a quickstart, uploads ideas, or asks for gap analysis.
---

# rh-qs-discovery

**Category:** `inception/`

## Trigger

- User says **"hello"** (guided from scratch)
- **"I want to build X"**
- User uploads or pastes a document with ideas (design doc, meeting notes, issue text)

## What it does

1. Asks structured questions: use case, target user, data sources, AI capabilities needed, UI requirements
2. Accepts uploaded documents as context
3. Grills the user on gaps: RAG? Real-time inference or batch? How many concurrent users?
4. Maps vague ideas to concrete requirements (e.g. "chat with documents" → RAG + vector DB + ingestion), if there is no AI Concept in the quickstart or there exists another repo that is similar purpose the quickstart should be rejected.
5. Produces a PRD markdown document

## Interview questions

Ask until every PRD section can be filled:

| Topic | Question |
|-------|----------|
| Problem | What problem does this quickstart solve? (one sentence) |
| User | Who is the target user? (developer, data scientist, business analyst) |
| Flow | What's the primary user flow? (upload → process → display?) |
| UI | Does it need a UI or is API-only acceptable? |
| AI capability | What AI capability is central? (text generation, RAG, agents, classification, vision). This must be true, if not do not continue. |
| Data | What data does it work with? (documents, transactions, images, real-time streams) |
| Storage | Does it need persistent storage? What kind? |
| Models | Any specific model requirements? (size constraints, safety, multilingual) |
| Deploy | Deploy target: OpenShift AI only, or also local dev with podman? |
| Compliance | Any compliance/security considerations? |

**Gap questions (always ask when relevant):**

- Will this need RAG?
- Real-time inference or batch?
- How many concurrent users?

## Requirement mapping

| Vague idea | Concrete requirement |
|------------|---------------------|
| Chat with documents | RAG + pgvector + ingestion pipeline |
| Agent with tools | Llama Stack + optional MCP servers |
| PDF upload and processing | MinIO + extraction service |
| On-cluster LLM | llm-service chart + GPU |

## Workflow

```
- [ ] 1. Check backlog for duplicate ideas
- [ ] 2. Run structured interview (or parse uploaded doc)
- [ ] 3. Ask gap questions
- [ ] 4. Map requirements to concrete AI patterns
- [ ] 5. Write PRD to data/prds/<slug>.md
- [ ] 6. Confirm with user before rh-qs-architect
```

### Check backlog

```bash
python3 core/skills/rh-qs-gh-backlog-reader/scripts/read_backlog.py --search "<keywords>"
```

If a matching issue exists, link it and ask whether to extend or create a distinct PRD.

## Output

**`data/prds/<quickstart-slug>.md`** — structured PRD ready for `rh-qs-architect`

PRD template:

```markdown
# <Title>

## Use case summary
## User flows
## Data model
## AI touchpoints
## Deploy target
## Constraints and non-goals
## Open questions (if any)
```

Slug: lowercase, hyphenated (e.g. `mortgage-application-processor`).

## Gap analysis mode

When user asks to identify gaps (absorbs rh-qs-quickstart-identifier):

1. Fetch backlog with rh-qs-gh-backlog-reader
2. Read [references/industry-trends.md](./references/industry-trends.md)
3. Compare coverage by industry, technology, use case
4. Propose 3–5 new quickstart ideas with rationale
5. Save report to `data/reports/gap-analysis-<date>.md`

## Next skill

When PRD is approved → **`rh-qs-architect`**


---
name: gh-issue-creator
description: Create GitHub issues for quickstart suggestions, RFEs, or strategy items. Ask the user which destination repo to use before creating. Uses gh CLI.
---

# gh-issue-creator

## Purpose

Create backlog items in the destination the user chooses. Default is the AI Quickstarts contrib repo; RFE and strategy items may use OpenDataHub tooling instead.

## Ask first — issue destination

Before creating anything, ask:

> Where should this be tracked?
> 1. **Quickstart backlog** — `rh-ai-quickstart/ai-quickstart-contrib` (default)
> 2. **RFE** — [opendatahub-io/rfe-creator](https://github.com/opendatahub-io/rfe-creator) (OpenShift AI / platform enhancement)
> 3. **Strategy** — [opendatahub-io/strat-creator](https://github.com/opendatahub-io/strat-creator) (roadmap / strategic theme)

Partners may not have access to RFE or strat repos — offer the contrib backlog as fallback.

| Destination | Action |
|-------------|--------|
| Quickstart backlog | Run `create_issues.py` below (this skill) |
| RFE | Direct user to rfe-creator repo/process; do not force contrib issue |
| Strategy | Direct user to strat-creator repo/process |

## Quickstart backlog (default)

Create GitHub issues in `rh-ai-quickstart/ai-quickstart-contrib` following the `[Quickstart suggestion]` template. Uses `gh` CLI.

### Title Format

```
[Quickstart suggestion]: {name}
```

### Defaults

- **Repo:** `rh-ai-quickstart/ai-quickstart-contrib`
- **Label:** `quickstart_suggestion`

### Usage

```bash
python3 core/skills/gh-issue-creator/scripts/create_issues.py [options]
```

### Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--name` | Quickstart name (required) | `--name "GraphRAG"` |
| `--description` | Description of the quickstart | `--description "Graph-based RAG pipeline"` |
| `--owner` | Owner(s) | `--owner "Carlos Camacho"` |
| `--technology` | Technology tags | `--technology "Llama Stack, MCP"` |
| `--industry` | Target industry | `--industry "Financial Services"` |
| `--repo` | Override repo | `--repo org/repo` |
| `--label` | Override label | `--label my_label` |
| `--dry-run` | Preview without creating | `--dry-run` |

### Examples

```bash
# Preview what would be created
python3 core/skills/gh-issue-creator/scripts/create_issues.py --name "GraphRAG" --dry-run

# Create with full metadata
python3 core/skills/gh-issue-creator/scripts/create_issues.py \
  --name "Loan Origination" \
  --description "AI-powered loan processing pipeline" \
  --owner "Saurabh Agarwal" \
  --technology "Llama Stack" \
  --industry "Financial Services"
```

### Duplicate Detection

The script searches existing open issues for matching names. If a duplicate is found, it skips creation and reports it.

## Requirements

- `gh` CLI installed and authenticated

## Related skills

- **`rh-qs-discovery`** — asks destination during ideation
- **`pipeline-grooming`** — triages contrib backlog

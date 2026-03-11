---
name: gh-issue-creator
description: Create GitHub issues in rh-ai-quickstart/ai-quickstart-contrib. Use when adding new quickstart suggestions to the backlog.
---

# gh-issue-creator

## Purpose

Create GitHub issues in `rh-ai-quickstart/ai-quickstart-contrib` following the `[Quickstart suggestion]` template. Uses `gh` CLI.

## Title Format

```
[Quickstart suggestion]: {name}
```

## Defaults

- **Repo:** `rh-ai-quickstart/ai-quickstart-contrib`
- **Label:** `quickstart_suggestion`

## Usage

```bash
python3 projects/quickstart-pipeline/skills/gh-issue-creator/scripts/create_issues.py [options]
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
python3 scripts/create_issues.py --name "GraphRAG" --dry-run

# Create with full metadata
python3 scripts/create_issues.py \
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

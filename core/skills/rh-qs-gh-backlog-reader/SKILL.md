---
name: rh-qs-gh-backlog-reader
description: Read and display AI Quickstart backlog from GitHub issues. Use when viewing the backlog, filtering issues, generating summaries, or checking issue details.
---

# rh-qs-gh-backlog-reader

## Purpose

Read and display the AI Quickstart backlog directly from GitHub issues in `rh-ai-quickstart/ai-quickstart-contrib`. Supports filtering, summarization, detail view, and JSON export.

## Data Source

**GitHub Issues:** https://github.com/rh-ai-quickstart/ai-quickstart-contrib/issues

This is the single source of truth for the quickstart backlog.

## Usage

```bash
python3 core/skills/github/rh-qs-gh-backlog-reader/scripts/read_backlog.py [options]
```

### Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--issue` | View a single issue with comments and linked repos | `--issue 39` |
| `--label` | Filter by GitHub label | `--label quickstart_suggestion` |
| `--state` | Issue state: open, closed, all | `--state all` |
| `--assignee` | Filter by GitHub username | `--assignee ccamacho` |
| `--author` | Filter by issue author/creator | `--author ccamacho` |
| `--search` | Free-text search in titles/bodies | `--search "Financial"` |
| `--limit` | Max issues to fetch (default: 100) | `--limit 50` |
| `--summary` | Output summary stats (by label, assignee) | `--summary` |
| `--detail` | Show full issue details including body | `--detail` |
| `--json` | Output as JSON | `--json` |

### Examples

```bash
# All open issues (markdown table)
python3 core/skills/github/rh-qs-gh-backlog-reader/scripts/read_backlog.py

# View single issue with comments + linked repos
python3 core/skills/github/rh-qs-gh-backlog-reader/scripts/read_backlog.py --issue 39

# Summary stats
python3 core/skills/github/rh-qs-gh-backlog-reader/scripts/read_backlog.py --summary

# Filter by label
python3 core/skills/github/rh-qs-gh-backlog-reader/scripts/read_backlog.py --label quickstart_suggestion

# Issues by a specific author
python3 core/skills/github/rh-qs-gh-backlog-reader/scripts/read_backlog.py --author ccamacho

# Search for specific topics
python3 core/skills/github/rh-qs-gh-backlog-reader/scripts/read_backlog.py --search "Financial Services"

# Full details for a specific assignee
python3 core/skills/github/rh-qs-gh-backlog-reader/scripts/read_backlog.py --assignee ccamacho --detail

# All issues (open + closed) as JSON
python3 core/skills/github/rh-qs-gh-backlog-reader/scripts/read_backlog.py --state all --json
```

### Single-Issue View

When using `--issue <number>`, the output includes:
- Full issue description
- All comments (with author and date)
- **Linked Repositories** — automatically extracted from the issue body and comments

This is useful for identifying issues that have implementations in progress and are candidates for blog posts.

## Requirements

- `gh` CLI installed and authenticated (`gh auth status`)

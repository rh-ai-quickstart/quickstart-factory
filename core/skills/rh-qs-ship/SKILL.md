---
name: rh-qs-ship
description: Ship an AI Quickstart. Creates a pull request with structured summary, generates a blog post draft, and updates backlog status. Use when documentation is complete from rh-qs-document.
---

# rh-qs-ship

**Category:** `github/`  
**Replaces:** rh-qs-gh-pr-creator, rh-qs-blog-writer, rh-qs-release-management

## Trigger

Documentation is complete from `rh-qs-document`

## What it does

1. Creates a **pull request** with structured summary (what was built, how to test, architecture diagram)
2. Generates a **blog post draft** for announcing the quickstart (using messaging guidelines)
3. Updates the **quickstart backlog** (marks issue in-progress or done)
4. Provides the **PR URL** and next steps for human review

## Workflow

```
- [ ] 1. Verify git state (no secrets, no data/ committed)
- [ ] 2. Create pull request
- [ ] 3. Draft blog post
- [ ] 4. Update backlog issue
- [ ] 5. Return PR URL and review checklist
```

### Create pull request

Dry-run first:

```bash
python3 core/skills/github/rh-qs-ship/scripts/create_pr.py --dry-run
python3 core/skills/github/rh-qs-ship/scripts/create_pr.py --base main
```

| Mode | When |
|------|------|
| `branch` (default) | All commits on feature branch vs base |
| `last-commit` | Only latest commit |
| `working-tree` | Commit staged + unstaged, then PR |

**PR body template:**

```markdown
## Summary
- What was built and why
- Key components (from design doc)

## Architecture
- Link to diagram in docs/images/

## Test plan
- [ ] make lint
- [ ] make test
- [ ] make dev — health check
- [ ] helm lint / template
- [ ] Deploy to OpenShift (if tested)

## Related issue
- Closes rh-ai-quickstart/ai-quickstart-contrib#<N>
```

**Safety:** Never force-push to main. Never commit `.env`, credentials, or `data/`.

### Blog post draft

1. Fetch issue: `python3 core/skills/github/rh-qs-gh-backlog-reader/scripts/read_backlog.py --issue <N>`
2. Read repo README and architecture
3. Draft using [assets/blog-template.md](./assets/blog-template.md) and [references/messaging-guidelines.md](./references/messaging-guidelines.md)

**Required links:**

- Catalog: https://docs.redhat.com/en/learn/ai-quickstarts
- Implementation repo URL
- Contrib: https://github.com/rh-ai-quickstart/ai-quickstart-contrib

Save to **`data/blog-drafts/<slug>-YYYY-MM-DD.md`**. Drafts require human review before publication.

### Update backlog

Comment on or close the related contrib issue. Mark in-progress during review, closed when merged and catalog-ready.

## Standalone usage

| Request | Action |
|---------|--------|
| "Create PR" / "Open pull request" | PR workflow only |
| "Write blog draft" / "Announce quickstart" | Blog workflow only |

## Output

| Artifact | Path |
|----------|------|
| Pull request | GitHub URL |
| Blog draft | `data/blog-drafts/<slug>-<date>.md` |

## References

- [Blog template](./assets/blog-template.md)
- [Messaging guidelines](./references/messaging-guidelines.md)

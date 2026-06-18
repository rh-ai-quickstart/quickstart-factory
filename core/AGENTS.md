# Core

Contains the skills and sync script for the Quickstart Factory.

## Skills

All skills live in `core/skills/`. Each has a `SKILL.md` defining its purpose and usage.

Notable pipeline skills (see [docs/NEW_QUICKSTART_SKILLS.md](../../docs/NEW_QUICKSTART_SKILLS.md)):

| Skill | Role |
|-------|------|
| rh-qs-secure | Cluster + application security guardrails |
| rh-qs-verify-deploy | On-cluster verification before README |
| rh-qs-bump-versions | Dependency and chart version maintenance |

Suggestions backlog: [SUGGESTIONS.md](./skills/SUGGESTIONS.md)

## Sync

After adding or modifying skills, run:

```bash
bash core/scripts/sync-clients.sh
```

This creates symlinks in `.claude/`, `.codex/`, `.cursor/`, and `.gemini/` so AI clients can discover the skills.

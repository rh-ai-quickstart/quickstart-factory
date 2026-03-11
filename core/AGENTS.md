# Core

Contains the skills and sync script for the Quickstart Factory.

## Skills

All skills live in `core/skills/`. Each has a `SKILL.md` defining its purpose and usage.

## Sync

After adding or modifying skills, run:

```bash
bash core/scripts/sync-clients.sh
```

This creates symlinks in `.claude/`, `.codex/`, `.cursor/`, and `.gemini/` so AI clients can discover the skills.

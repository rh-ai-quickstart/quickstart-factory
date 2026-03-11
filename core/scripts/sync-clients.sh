#!/usr/bin/env bash
# sync-clients.sh — Sync core skills to AI client directories as symlinks.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILLS_DIR="$ROOT_DIR/core/skills"
CLIENTS=(.claude .codex .cursor .gemini)

for client in "${CLIENTS[@]}"; do
  target="$ROOT_DIR/$client/skills"
  mkdir -p "$target"

  # Clean old symlinks
  for link in "$target"/*; do
    [ -L "$link" ] && rm -f "$link"
  done

  # Link each skill
  for skill_dir in "$SKILLS_DIR"/*/; do
    [ -f "$skill_dir/SKILL.md" ] || continue
    name="$(basename "$skill_dir")"
    ln -s "$skill_dir" "$target/$name"
    echo "  ✓ $client/skills/$name"
  done
done

echo "✅ Sync complete."

#!/usr/bin/env python3
"""Create GitHub issues for AI Quickstart suggestions."""

import argparse
import json
import subprocess
import sys
import time

DEFAULT_REPO = "rh-ai-quickstart/ai-quickstart-contrib"
DEFAULT_LABEL = "quickstart_suggestion"
MAX_BATCH = 10
DELAY_SECONDS = 2


def search_existing_issues(repo: str, name: str) -> bool:
    """Check if an open issue with this quickstart name already exists."""
    try:
        result = subprocess.run(
            [
                "gh", "issue", "list", "-R", repo,
                "--state", "open",
                "--search", f'in:title "[Quickstart suggestion]: {name}"',
                "--json", "title",
            ],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            return False
        issues = json.loads(result.stdout or "[]")
        return any(name.lower() in t.get("title", "").lower() for t in issues)
    except Exception:
        return False


def create_issue(repo: str, title: str, body: str, label: str) -> bool:
    """Create one issue via gh CLI."""
    try:
        result = subprocess.run(
            ["gh", "issue", "create", "-R", repo, "--title", title, "--body", body, "--label", label],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            print(f"Error creating '{title}': {result.stderr.strip()}", file=sys.stderr)
            return False
        print(f"Created: {title}")
        url = result.stdout.strip()
        if url:
            print(f"  → {url}")
        return True
    except subprocess.TimeoutExpired:
        print(f"Timeout creating '{title}'", file=sys.stderr)
        return False


def build_body(name: str, description: str = "", owner: str = "", technology: str = "", industry: str = "") -> str:
    """Build issue body from arguments."""
    lines = ["## Quickstart suggestion", "", f"**Name:** {name}", ""]
    if description:
        lines.extend([f"**Description:** {description}", ""])
    if owner:
        lines.extend([f"**Owner(s):** {owner}", ""])
    if technology:
        lines.extend([f"**Technology:** {technology}", ""])
    if industry:
        lines.extend([f"**Industry:** {industry}", ""])
    lines.append("---")
    lines.append("_Created via gh-issue-creator_")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create GitHub issues for quickstart suggestions")
    parser.add_argument("--name", required=True, help="Quickstart name (used in title)")
    parser.add_argument("--description", default="", help="Quickstart description")
    parser.add_argument("--owner", default="", help="Owner(s)")
    parser.add_argument("--technology", default="", help="Technology tags (e.g. 'Llama Stack, MCP')")
    parser.add_argument("--industry", default="", help="Industry (e.g. 'Financial Services')")
    parser.add_argument("--repo", default=DEFAULT_REPO, help=f"GitHub repo (default: {DEFAULT_REPO})")
    parser.add_argument("--label", default=DEFAULT_LABEL, help=f"Issue label (default: {DEFAULT_LABEL})")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without creating")
    args = parser.parse_args()

    title = f"[Quickstart suggestion]: {args.name}"

    if search_existing_issues(args.repo, args.name):
        print(f"Skip (duplicate): issue already exists for '{args.name}'", file=sys.stderr)
        sys.exit(0)

    body = build_body(
        name=args.name,
        description=args.description,
        owner=args.owner,
        technology=args.technology,
        industry=args.industry,
    )

    if args.dry_run:
        print(f"Would create: {title}\n")
        print("--- Body preview ---")
        print(body)
        return

    if create_issue(args.repo, title, body, args.label):
        print("\nDone.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create a GitHub pull request from the current repository via gh CLI."""

from __future__ import annotations

import argparse
import subprocess
import sys
def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        print(f"Error: {' '.join(cmd)}\n{stderr}", file=sys.stderr)
        sys.exit(result.returncode)
    return result


def git(*args: str) -> str:
    return run(["git", *args]).stdout.strip()


def resolve_base(base: str | None) -> str:
    if base:
        return base
    for candidate in ("main", "master", "dev"):
        try:
            run(["git", "rev-parse", "--verify", candidate], check=True)
            return candidate
        except SystemExit:
            continue
    print("Error: could not detect base branch; pass --base", file=sys.stderr)
    sys.exit(1)


def commits_ahead(base: str) -> list[str]:
    log = run(["git", "log", f"{base}..HEAD", "--format=%H"], check=False)
    if log.returncode != 0:
        return []
    return [line for line in log.stdout.splitlines() if line]


def has_working_tree_changes() -> bool:
    status = git("status", "--porcelain")
    return bool(status)


def ensure_branch_pushed(branch: str, remote: str) -> None:
    upstream = run(["git", "rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}"], check=False)
    if upstream.returncode != 0:
        run(["git", "push", "-u", remote, "HEAD"])
        return
    counts = run(["git", "rev-list", "--left-right", "--count", f"{branch}@{{upstream}}...{branch}"], check=False)
    if counts.returncode == 0:
        parts = counts.stdout.split()
        if len(parts) == 2 and parts[0] != "0":
            run(["git", "push", remote, branch])


def prepare_last_commit_branch(base: str, remote: str) -> str:
    """Branch with only HEAD commit on top of base (for PR scope = last commit)."""
    head = git("rev-parse", "HEAD")
    ahead = commits_ahead(base)
    if len(ahead) <= 1:
        return git("branch", "--show-current")

    short = head[:7]
    branch = f"pr/last-commit-{short}"
    run(["git", "branch", "-f", branch, base])
    run(["git", "checkout", branch])
    cherry = run(["git", "cherry-pick", head], check=False)
    if cherry.returncode != 0:
        run(["git", "cherry-pick", "--abort"], check=False)
        run(["git", "checkout", "-"])
        print("Error: cherry-pick failed for last-commit mode", file=sys.stderr)
        sys.exit(1)
    run(["git", "push", "-u", remote, branch, "--force-with-lease"])
    return branch


def commit_working_tree(message: str, include_untracked: bool) -> None:
    if not has_working_tree_changes():
        print("No staged or unstaged changes to commit.")
        return
    cmd = ["git", "add", "-A"] if include_untracked else ["git", "add", "-u"]
    run(cmd)
    if run(["git", "diff", "--cached", "--quiet"], check=False).returncode != 0:
        run(["git", "commit", "-m", message])
    else:
        print("Nothing staged after git add; skipping commit.")


def default_title(base: str, mode: str) -> str:
    subject = run(["git", "log", "-1", "--format=%s"], check=False).stdout.strip()
    if mode == "working-tree" and has_working_tree_changes():
        return "WIP: local changes"
    if subject:
        return subject
    return f"Changes from {git('branch', '--show-current')}"


def build_body(base: str, mode: str) -> str:
    lines = [
        "## Summary",
        "",
        f"- Source: `{mode}` mode",
        f"- Base branch: `{base}`",
        f"- Head branch: `{git('branch', '--show-current')}`",
        "",
        "## Test plan",
        "",
        "- [ ] CI passes",
        "- [ ] Reviewed locally",
        "",
    ]
    if mode == "last-commit":
        lines.insert(4, f"- Includes only the latest commit: `{git('rev-parse', '--short', 'HEAD')}`")
        lines.insert(5, "")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a GitHub PR via gh CLI")
    parser.add_argument(
        "--mode",
        choices=("branch", "last-commit", "working-tree"),
        default="branch",
        help="branch: all commits on current branch vs base; last-commit: only HEAD; working-tree: commit staged+unstaged first",
    )
    parser.add_argument("--base", default=None, help="Base branch (default: main, master, or dev)")
    parser.add_argument("--title", default=None, help="PR title")
    parser.add_argument("--body", default=None, help="PR body (markdown)")
    parser.add_argument("--body-file", default=None, help="PR body from file")
    parser.add_argument("--commit-message", default=None, help="Commit message for working-tree mode")
    parser.add_argument("--remote", default="origin", help="Git remote to push")
    parser.add_argument("--draft", action="store_true", help="Open as draft PR")
    parser.add_argument("--no-untracked", action="store_true", help="working-tree: do not add untracked files")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without creating PR")
    args = parser.parse_args()

    run(["gh", "auth", "status"])
    inside = git("rev-parse", "--is-inside-work-tree")
    if inside != "true":
        print("Error: not inside a git repository", file=sys.stderr)
        sys.exit(1)

    base = resolve_base(args.base)
    original_branch = git("branch", "--show-current")
    remote = args.remote

    if args.mode == "working-tree":
        if not has_working_tree_changes():
            print("No unstaged or staged changes; use --mode branch or last-commit.")
            sys.exit(1)
        msg = args.commit_message or default_title(base, "working-tree")
        if args.dry_run:
            print(f"[dry-run] git add {'-A' if not args.no_untracked else '-u'}")
            print(f"[dry-run] git commit -m {msg!r}")
        else:
            commit_working_tree(msg, include_untracked=not args.no_untracked)

    pr_branch = original_branch
    if args.mode == "last-commit":
        if args.dry_run:
            ahead = commits_ahead(base)
            if len(ahead) > 1:
                print(f"[dry-run] Would create pr/last-commit-* from {base} with cherry-pick {ahead[0]}")
            else:
                print("[dry-run] Single commit ahead of base; use current branch")
        else:
            pr_branch = prepare_last_commit_branch(base, remote)
    else:
        if args.dry_run:
            print(f"[dry-run] git push -u {remote} {original_branch}")
        else:
            ensure_branch_pushed(original_branch, remote)

    ahead = commits_ahead(base)
    if not ahead and args.mode != "working-tree":
        print(f"No commits on {original_branch} ahead of {base}. Nothing to PR.")
        sys.exit(1)

    title = args.title or default_title(base, args.mode)
    body = args.body
    if args.body_file:
        with open(args.body_file, encoding="utf-8") as f:
            body = f.read()
    if body is None:
        body = build_body(base, args.mode)

    pr_args = [
        "gh", "pr", "create",
        "--base", base,
        "--head", pr_branch,
        "--title", title,
        "--body", body,
    ]
    if args.draft:
        pr_args.append("--draft")

    if args.dry_run:
        print("[dry-run]", " ".join(pr_args[:6]), "...")
        print("Title:", title)
        print("Body preview:\n", body[:500])
        return

    result = run(pr_args, check=False)
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        sys.exit(result.returncode)
    url = result.stdout.strip()
    print(url)


if __name__ == "__main__":
    main()

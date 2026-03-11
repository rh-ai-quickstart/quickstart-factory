#!/usr/bin/env python3
"""Read and display AI Quickstart backlog from GitHub issues."""

import argparse
import json
import re
import subprocess
import sys

DEFAULT_REPO = "rh-ai-quickstart/ai-quickstart-contrib"


def fetch_issues(
    repo: str,
    label: str | None = None,
    state: str = "open",
    assignee: str | None = None,
    author: str | None = None,
    search: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """Fetch issues from GitHub using gh CLI."""
    cmd = [
        "gh", "issue", "list",
        "-R", repo,
        "--state", state,
        "--limit", str(limit),
        "--json", "number,title,state,labels,assignees,author,createdAt,updatedAt,url,body",
    ]
    if label:
        cmd.extend(["--label", label])
    if assignee:
        cmd.extend(["--assignee", assignee])
    if author:
        cmd.extend(["--author", author])
    if search:
        cmd.extend(["--search", search])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"Error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout or "[]")


def fetch_single_issue(repo: str, number: int) -> dict:
    """Fetch a single issue with comments using gh issue view."""
    cmd = [
        "gh", "issue", "view", str(number),
        "-R", repo,
        "--json", "number,title,state,labels,assignees,author,createdAt,updatedAt,url,body,comments",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"Error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout or "{}")


def extract_links(text: str) -> list[str]:
    """Extract URLs from text."""
    return re.findall(r'https?://[^\s\)>\]]+', text or "")


def print_table(issues: list[dict]) -> None:
    """Print issues as markdown table."""
    if not issues:
        print("No issues found.")
        return
    print("| # | Title | Labels | Author | Assignees | Created |")
    print("|---|-------|--------|--------|-----------|---------|")
    for issue in issues:
        num = issue["number"]
        title = issue["title"]
        labels = ", ".join(lb["name"] for lb in issue.get("labels", []))
        author = issue.get("author", {}).get("login", "")
        assignees = ", ".join(a["login"] for a in issue.get("assignees", []))
        created = issue["createdAt"][:10]
        print(f"| #{num} | {title} | {labels} | @{author} | {assignees} | {created} |")


def print_summary(issues: list[dict]) -> None:
    """Print summary statistics."""
    print("## Backlog Summary\n")
    print(f"Total issues: {len(issues)}\n")

    label_counts: dict[str, int] = {}
    for issue in issues:
        for lb in issue.get("labels", []):
            name = lb["name"]
            label_counts[name] = label_counts.get(name, 0) + 1

    if label_counts:
        print("### By Label")
        for label, count in sorted(label_counts.items(), key=lambda x: -x[1]):
            print(f"- {label}: {count}")
        print()

    assignee_counts: dict[str, int] = {}
    unassigned = 0
    for issue in issues:
        assignees = issue.get("assignees", [])
        if not assignees:
            unassigned += 1
        for a in assignees:
            assignee_counts[a["login"]] = assignee_counts.get(a["login"], 0) + 1

    print("### By Assignee")
    if assignee_counts:
        for assignee, count in sorted(assignee_counts.items(), key=lambda x: -x[1]):
            print(f"- @{assignee}: {count}")
    if unassigned:
        print(f"- (unassigned): {unassigned}")


def print_detail(issues: list[dict]) -> None:
    """Print full issue details."""
    for issue in issues:
        num = issue["number"]
        title = issue["title"]
        labels = ", ".join(lb["name"] for lb in issue.get("labels", []))
        assignees = ", ".join(a["login"] for a in issue.get("assignees", []))
        created = issue["createdAt"][:10]
        url = issue.get("url", "")
        body = (issue.get("body") or "").strip()

        author = issue.get("author", {}).get("login", "")
        print(f"### #{num} — {title}")
        print(f"- **Author:** @{author}")
        print(f"- **Labels:** {labels or '(none)'}")
        print(f"- **Assignees:** {assignees or '(unassigned)'}")
        print(f"- **Created:** {created}")
        print(f"- **URL:** {url}")
        if body:
            print(f"\n{body}")
        print("\n---\n")


def print_issue_with_comments(issue: dict) -> None:
    """Print a single issue with its comments."""
    num = issue["number"]
    title = issue["title"]
    labels = ", ".join(lb["name"] for lb in issue.get("labels", []))
    assignees = ", ".join(a["login"] for a in issue.get("assignees", []))
    author = issue.get("author", {}).get("login", "")
    created = issue["createdAt"][:10]
    url = issue.get("url", "")
    body = (issue.get("body") or "").strip()
    comments = issue.get("comments", [])

    all_text = body + " ".join(c.get("body", "") for c in comments)
    links = extract_links(all_text)
    github_repos = [l for l in links if "github.com" in l and "/issues" not in l and "/pull" not in l]

    print(f"# #{num} — {title}\n")
    print(f"- **Author:** @{author}")
    print(f"- **Labels:** {labels or '(none)'}")
    print(f"- **Assignees:** {assignees or '(unassigned)'}")
    print(f"- **Created:** {created}")
    print(f"- **URL:** {url}")
    print(f"- **Comments:** {len(comments)}")

    if github_repos:
        print(f"\n### Linked Repositories")
        for repo_link in sorted(set(github_repos)):
            print(f"- {repo_link}")

    if body:
        print(f"\n### Description\n\n{body}")

    if comments:
        print(f"\n### Comments\n")
        for i, comment in enumerate(comments, 1):
            c_author = comment.get("author", {}).get("login", "unknown")
            c_created = comment.get("createdAt", "")[:10]
            c_body = (comment.get("body") or "").strip()
            print(f"**@{c_author}** ({c_created}):\n")
            print(f"{c_body}\n")
            if i < len(comments):
                print("---\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Read AI Quickstart backlog from GitHub issues")
    parser.add_argument("--repo", default=DEFAULT_REPO, help=f"GitHub repo (default: {DEFAULT_REPO})")
    parser.add_argument("--issue", type=int, help="View a single issue by number (includes comments)")
    parser.add_argument("--label", help="Filter by label (e.g. quickstart_suggestion)")
    parser.add_argument("--state", default="open", choices=["open", "closed", "all"], help="Issue state (default: open)")
    parser.add_argument("--assignee", help="Filter by assignee GitHub username")
    parser.add_argument("--author", help="Filter by issue author/creator GitHub username")
    parser.add_argument("--search", help="Free-text search in issue titles/bodies")
    parser.add_argument("--limit", type=int, default=100, help="Max issues to fetch (default: 100)")
    parser.add_argument("--summary", action="store_true", help="Show summary stats instead of table")
    parser.add_argument("--detail", action="store_true", help="Show full issue details including body")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.issue:
        issue = fetch_single_issue(args.repo, args.issue)
        if args.json:
            print(json.dumps(issue, indent=2))
        else:
            print_issue_with_comments(issue)
        return

    issues = fetch_issues(
        args.repo,
        label=args.label,
        state=args.state,
        assignee=args.assignee,
        author=args.author,
        search=args.search,
        limit=args.limit,
    )

    if args.json:
        print(json.dumps(issues, indent=2))
    elif args.summary:
        print_summary(issues)
    elif args.detail:
        print_detail(issues)
    else:
        print_table(issues)


if __name__ == "__main__":
    main()

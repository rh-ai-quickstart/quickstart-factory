---
name: blog-writer
description: Generate blog post drafts for completed AI Quickstarts. Use when announcing new quickstarts to Red Hat audience.
---

# blog-writer

## Purpose

Generate blog post drafts for completed AI Quickstarts. Outputs to `data/blog-drafts/`. Drafts require review before publication.

## Workflow

1. **Identify candidate:** Use `gh-backlog-reader --issue <N>` to view the issue, its comments, and linked repositories.
2. **Gather context:** If a linked implementation repo exists (auto-extracted from comments), browse the repo README and code to understand what the quickstart does, its architecture, and how to run it.
3. **Draft the blog post:** Use the format and template below.

Issues with an implementation repo linked in the comments are prime candidates for blog posts — the quickstart is being built or is already done.

## Blog Format Selection

Choose format based on quickstart type:
- **Standard announcement:** Use template (Hook, What It Does, How It Works, Get Started, What's Next, CTA)
- **Technical deep-dive:** Add architecture diagram, code snippets
- **Use case spotlight:** Emphasize industry and outcome

## Standard Links

Include in every blog post:
- **Catalog:** https://docs.redhat.com/en/learn/ai-quickstarts
- **Repository:** Link to the quickstart's implementation GitHub repo (from issue comments)
- **Contrib:** https://github.com/rh-ai-quickstart/ai-quickstart-contrib

## Output

- **Directory:** `data/blog-drafts/`
- **Naming:** `{quickstart-slug}-YYYY-MM-DD.md` (e.g. `vllm-cpu-2025-03-11.md`)

## References

- **Template:** [assets/blog-template.md](assets/blog-template.md)
- **Messaging:** [references/messaging-guidelines.md](references/messaging-guidelines.md)

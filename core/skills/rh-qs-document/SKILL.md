---
name: rh-qs-document
description: Generate README and catalog documentation for AI Quickstarts from the implementation. Creates or updates README.md with deploy steps, requirements, architecture diagram, and catalog metadata. Use when deployment works from rh-qs-deploy.
---

# rh-qs-document

**Category:** `documentation/'

## Trigger

Code is deployed and working from `rh-qs-deploy`; CI workflows from `rh-qs-test-suite` are in place when the design requires them

## What it does

1. Generates **README.md** from the implementation using standard quickstart catalog structure
2. Includes: title, description, requirements (hardware/software), deploy steps, delete/cleanup steps
3. References the **Mermaid architecture diagram** from the architect phase (saved in `docs/images/`)
4. Adds **catalog metadata/tags** for Red Hat documentation discovery
5. Documents all **environment variables** and their purpose
6. Optionally generates a **demo script outline** for video/presentation

## Workflow

```
- [ ] 1. Explore repository (code, Helm, Makefile, compose, docs/images/)
- [ ] 2. Read design doc for architecture diagram and component list
- [ ] 3. Gather user-facing facts (hardware, RHOAI version, permissions)
- [ ] 4. Draft or update README.md using ReadmeStructure
- [ ] 5. Validate every documented command exists in repo
- [ ] 6. Optional: write docs/demo-script.md
```

### README sections

Use [references/ReadmeStructure.md](./references/ReadmeStructure.md):

- Title and short description (catalog character limits)
- Workload-focused detailed description
- Requirements: specific GPU, tested OpenShift AI version, permissions
- Deploy and Delete steps (copy-pasteable; use `oc` and podman terminology)
- Architecture section with diagram from `docs/images/` or design doc
- Environment variables table
- Tags/metadata for catalog

### Demo script (optional)

Save to `docs/demo-script.md`:

- Setup (~2 min)
- Primary user journey demo (~5 min)
- Architecture callout (~2 min)
- Cleanup (~1 min)

## What not to include

- Line-by-line code walkthroughs
- Generic placeholders when repo pins specific versions
- Commands not present in Makefile or Helm

## Audience

Readers may have **limited OpenShift AI experience**. Use plain language, explicit prerequisites, ordered steps.

## Output

- `README.md` (create or replace)
- Optional `docs/demo-script.md`
- Updated `docs/images/` if diagram exported

## Next skill

When README is complete → **`rh-qs-ship`**

## References

- [README structure](./references/ReadmeStructure.md)
- Design doc: `data/designs/<slug>.md`

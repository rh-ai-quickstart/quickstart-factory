# Reasoning Guardrails Template

This document defines the standard format for `reasoning-guardrails.md` files. Every upgraded skill includes a guardrails file that ensures critical concerns are not overlooked during execution.

## What Guardrails Are (and Are Not)

**Guardrails ARE:**
- Concern areas the agent should reason about organically
- A mental framework for comprehensive coverage
- Prompts for self-reflection during complex reasoning
- Adaptive — irrelevant concerns are skipped, not forced

**Guardrails are NOT:**
- A checklist to mechanically fill out
- A step-by-step procedure
- A validation gate (that's what validators are for)
- A replacement for free thinking

The distinction matters. A checklist produces shallow, mechanical coverage. Guardrails produce deep, contextual reasoning — the agent thinks freely, then periodically checks whether it has overlooked a critical concern.

## Template Structure

Every `reasoning-guardrails.md` follows this structure:

```
1. Title and purpose (1 paragraph)
2. How to Use (4-step protocol)
3. Concern Areas (skill-specific, 3-10 areas)
4. Additional Concerns (conditional, context-specific)
5. Dynamic Reasoning Example (shows guardrails in action)
6. When to Stop Checking
7. Self-Check Before [Key Action]
```

## Template

Below is the generic template. Skill EPICs replace the placeholder concern areas with skill-specific ones from the ADR.

---

````markdown
# Reasoning Guardrails for rh-qs-<name>

This document defines the concern areas that should be investigated during <skill action>. These are **not** a checklist to mechanically fill out, but a mental framework to ensure critical aspects aren't overlooked while reasoning dynamically.

## Purpose

When <doing the skill's primary task>, questions should emerge organically from analysis. However, certain concerns are easy to miss without explicit attention. These guardrails ensure comprehensive coverage.

## How to Use

As you reason about <the task>:
1. Think freely — let questions emerge naturally from analysis
2. Periodically check: "Have I considered [concern area]?"
3. If not yet addressed, reason about it explicitly
4. Don't force irrelevant concerns

## Concern Areas

### 1. <Concern Area Name>
**What to consider:**
- <Aspect to think about>
- <Another aspect>
- <Another aspect>

**Key questions:**
- <Question the agent should ask itself>
- <Another question>
- <Another question>

**Where to look:**
- <Where in the project/codebase to find relevant information>
- <Another source>

---

### 2. <Concern Area Name>
**What to consider:**
- ...

**Key questions:**
- ...

**Where to look:**
- ...

---

<!-- Repeat for each concern area (typically 3-10 per skill) -->

## Additional Concerns (Context-Specific)

<!-- Concerns that only apply in specific situations.
     Use subsections without the full What/Questions/Where structure. -->

### <Conditional Concern>
- <Bullet points covering what to think about>
- <When this concern applies>

---

## Dynamic Reasoning Example

```
Analyzing <input>...
  ↓ Found: <something noteworthy in the input>

Question emerges: "<natural question from analysis>"
  ↓ <How the agent investigates>
  ↓ Answer: <what it finds>

Guardrail check: "Have I considered <concern area 1>?" ✓ Yes
Guardrail check: "Have I considered <concern area 2>?" ✓ Yes, <brief note>

Question emerges: "<follow-up question>"
  ↓ Check guardrails: <relevant area> ✓ <relevant area> ✓
  ↓ <Investigation>
  ↓ Answer: <finding>

Continue reasoning...
```

## When to Stop Checking Guardrails

Once you've reasoned about all applicable concerns:
- Concerns that don't apply to this <task> can be skipped
- If a concern was implicitly handled during reasoning, that counts
- Don't force concerns that are truly irrelevant

## Self-Check Before <Key Action>

Before <the skill's key output action>, quickly verify:
- [ ] All relevant guardrails considered
- [ ] Decisions documented (implicitly or explicitly)
- [ ] Edge cases identified
- [ ] User decision points identified

If any guardrail feels unaddressed, reason about it explicitly before proceeding.
````

---

## Adapting the Template for Each Skill

Each skill EPIC replaces the placeholders with skill-specific concern areas. The ADR defines the guardrails for each skill:

| Skill | Concern Areas |
|-------|---------------|
| rh-qs-discovery | Scope creep (don't invent requirements), technology bias (don't pre-decide stack), GPU assumptions |
| rh-qs-architect | Model sizing, GPU dependency, data residency, chart compatibility, scope creep |
| rh-qs-scaffold | Over-scaffolding, missing CI coverage, placeholder pollution, standards compliance |
| rh-qs-implement | Vertical slice (thinnest path), hardcoded values, error handling, async consistency, security |
| rh-qs-deploy | Chart version compatibility, secret exposure, GPU resource configuration, image registry accessibility |
| rh-qs-security | False positive filtering, compliance context (HIPAA/PCI if PRD specifies), GPU security contexts |
| rh-qs-debug-and-deploy | Namespace isolation, don't change application intent, dependency-order debugging, max 3 attempts per resource |
| rh-qs-document | Verbosity, accuracy (every command must work), completeness, audience (user-facing not developer-facing) |
| rh-qs-ship | PR description accuracy, blog post tone, no credentials in PR body, backlog cross-reference |
| rh-qs-update | Backward compatibility, semantic versioning awareness, test regression detection |
| rh-qs-handoff | Don't redo completed work, preserve existing code patterns, match codebase style conventions |
| rh-qs-extract-knowledge | No proprietary data in KB files, deduplicate before creating, preserve KB structure, validate frontmatter |

### How to expand ADR bullets into full concern areas

Each ADR bullet becomes a concern area with three sub-sections. Example — expanding "scope creep" for rh-qs-discovery:

**ADR says:** "Scope creep (don't invent requirements)"

**Becomes:**

```markdown
### 1. Scope Creep
**What to consider:**
- Requirements the user explicitly stated vs ones you inferred
- Features that sound useful but weren't requested
- Complexity escalation (simple request becoming an enterprise system)

**Key questions:**
- Did the user actually ask for this, or am I adding it?
- Would removing this feature change the user's stated problem?
- Am I designing for a scale the user didn't mention?

**Where to look:**
- The user's original input (exact words matter)
- PRD sections you've drafted — do they go beyond the conversation?
- Technology choices — are you picking complex stacks for simple problems?
```

### Concern area count guidelines

- **Minimum:** 3 concern areas (even simple skills have scope, quality, and security dimensions)
- **Typical:** 5-7 concern areas (covers the skill's primary risks)
- **Maximum:** 10 concern areas (beyond this, the guardrails become a checklist)

The blueprint kit's `bp-convert-to-rhoai` uses 10 core areas plus 3 conditional areas. Most quickstart factory skills will need 5-7.

## Relationship to Other Foundation Docs

- **[skill-directory-structure.md](skill-directory-structure.md)** — `reasoning-guardrails.md` is a required file in every skill directory
- **[spec-as-contract.md](spec-as-contract.md)** — guardrails are consulted during the Analyze phase, before spec generation
- **[acceptance-criteria.md](acceptance-criteria.md)** — guardrails inform what acceptance criteria to include in specs

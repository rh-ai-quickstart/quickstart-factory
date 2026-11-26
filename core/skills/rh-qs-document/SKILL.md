---
name: rh-qs-document
description: Generate a Red Hat AI Quickstart README.md for a repository — customer-facing highlights in the official ai-quickstart-template structure. Use when asked to write, regenerate, or improve the README of an AI quickstart repository (rh-ai-quickstart style).
---

# Red Hat AI Quickstart README generator

Write the front door of a Red Hat AI Quickstart: a `README.md` that sells
the use case to a customer and gets them deployed. Audience: a customer
deciding whether to deploy — never a contributor. A generated README
fails in one of four ways — **invented facts, wrong focus, unusable
deploy, wrong altitude** — every phase below exists to guard them.

Read before writing (each reference owns one concern; do not restate,
follow):
- `references/template-structure.md` — WHAT each section requires
  (sections, order, limits, TODO policy, Tags fields)
- `references/writing-style.md` — voice, narrative pattern, length budget
- `references/evidence-hunting.md` — HOW and WHERE to extract every
  section's content from the repository: search orders, grep patterns,
  decision rules, the claim ledger
- `references/drawio-svg-format.md` — HOW the generated architecture
  diagram's `.drawio.svg` is built and validated: two synchronized
  layers (visible SVG + escaped `content` model), the Red Hat logo at
  the bottom in both, the embed/validate script
- `references/example-readme.md` — gold example; study structure and tone
  only (exception: for that same repository, it is the real README — match
  it, including Tags values)
- `references/parallel-work.md` — WHEN and HOW to fan the independent
  subtasks out to subagents (extract lanes, diagram builder, grounding
  auditor); read it only when a subagent tool is available

## Process

`Classify → Survey → Extract → Draft → Verify and fix`. Every phase ends
in a gate; a failed gate routes work backward and is never waived. A
verify failure caused by **missing evidence** returns to Extract/Survey;
one of **wording, order, or altitude** returns to Draft. Never repair a
factual gap by inventing a fact. Assume nothing exists: no shape is the
default, and every search has an "if absent, try …" continuation.

1. **Classify** — record the repo's shape(s) and install entrypoints
   before reading deeply (`evidence-hunting.md` §1–2). Gate: 3–6 lines
   naming shape(s), entrypoints, and which signal rows below apply.
2. **Survey** — the cheap→expensive sweep; build an index plus recorded
   absences, not a summary (`evidence-hunting.md` §2–3). Gate: the
   working note names the interface class, the 1–3 headline features
   (entry point + evidence path each — each a core application feature
   the repo's own docs foreground, a journey with sub-steps folded in
   and its ordered screen list, one marked main for the
   architecture-diagram trunk), and the primary deploy path.
   The interface class, once named, is binding: it decides the Usage
   surface — a UI-reachable feature is walked in the UI (a screenshot or
   per-step capture TODO for every walked screen), never via an API/CLI
   the user does not touch
   (`evidence-hunting.md` §5).
3. **Extract** — in dependency order, not template order: narrative/use
   case → usage artifacts → deploy paths → requirements →
   architecture/solution stack → references/tree/Tags
   (`evidence-hunting.md` §4–9). Record every finding in the claim
   ledger (§0) and reconcile conflicts once, globally (§10). When a
   subagent tool is available, run this phase as the four parallel
   extract lanes in `references/parallel-work.md` (same recipes, same
   ledger, same gate — the fan-out changes who extracts, never what is
   claimed); without one, run the lanes yourself in dependency order.
   Gate: every required section has evidence or an explicit omit/TODO
   decision, every ledger row has a status, and every Usage artifact
   matches the Survey-recorded surface — a UI-reachable feature shown
   in the UI.
4. **Draft** — in `template-structure.md` order, only from the ledger
   plus references. If prose needs a fact not in the ledger, return to
   Extract — never draft from memory. You write every sentence of prose
   yourself; the one exception is the architecture diagram, which the
   Diagram Builder subagent may build concurrently with your drafting
   from the frozen ledger (`references/parallel-work.md`) — embed it
   only after re-validating it via `references/embed_drawio.py` and
   checking its labels agree with the Solution Stack. Gate: all
   required sections present; every factual claim maps to a ledger row.
5. **Verify and fix** — the final section below.

## Invariants (every repository; they outrank any score)

1. **Facts come from the repository.** Every version, GPU model, sizing
   figure, command, and URL traces to a repo file — never invented,
   guessed, derived, or imported from general knowledge. Requirements
   values are evidence-gated: each required item is listed, and its
   value is either repo-stated or an explicit `TODO: <what to fill in>`
   placeholder. Quote pins and figures exactly as stated — never
   loosened or reworded; a "tested with" pin is the stated requirement.
   When docs disagree, sweep every doc that states a floor and carry
   the strictest; scope path-specific floors to their path; carry
   ceilings as ceilings. *(Extract, Verify)*
2. **Use case first.** Title (≤64 chars), short description (≤160
   chars), Tags, and Challenge frame the end-user outcome the repo's
   runnable content delivers, not the platform or developer workflow
   it demonstrates; reuse the repo's own value framing rather than
   inventing a hotter narrative. Our solution answers the Challenge
   point-for-point: each pain it names gets its before → after
   improvement in plain user-facing terms, carrying only
   decision-relevant detail. The Solution Stack (under Technical
   details) names every component the repo's docs name, with deliberate
   defaults called out as the architecture decisions they are. The Usage
   walkthrough stays
   on the end-user surface: a UI-reachable feature is shown in the UI
   (a screenshot or per-step capture TODO for every walked screen), an
   API/CLI transcript at most as a
   labeled supplement. Each walkthrough is one end-to-end journey,
   walked step by step: every step that changes the screen carries its
   artifact, sub-features that are steps inside it appear as its steps,
   never as walkthroughs of their own; a second walkthrough is earned
   only by a headline feature outside the main journey, and the same
   journey exposed on two surfaces is walked once — the second surface
   gets a cross-reference. *(Classify, Draft)*
3. **Template order.** Required sections in template order; ToC matches
   the actual sections; no top-level sections the template doesn't
   define. The architecture diagram lives under `docs/images/` relative
   to the README, with alt text: reference a suitable diagram the repo
   ships when one exists; otherwise generate a draw.io-editable SVG
   saved as `architecture-overview.drawio.svg` (escaped model XML in
   its `content` attribute, Red Hat logo at the bottom of the canvas,
   per template-structure.md and `references/drawio-svg-format.md`).
   Size the canvas to the picture — canvas from the flow, one scale for
   boxes and type, nothing below 12px — so the diagram fills its frame
   instead of floating small on an oversized canvas.
   The picture is the application solution, not the deployment graph:
   headline-feature surfaces and engines in the center, a supporting
   tool only where a feature journey crosses it, mocks/install
   machinery/plumbing out, feature sub-labels repo-verbatim only.
   Never open binary files — describe repo images from filenames and
   documentation text — and write generated assets only under the
   README's own directory tree. *(Draft)*
4. **Every path the repo supports is presented.** Never flatten to one
   install path or serving option, or declare "no GPU required" while
   the repo also supports local model serving. *(Extract, Draft)*
5. **Cautions live where the user acts.** Operational cautions the repo
   states — components disabled by default (with the enabling flag),
   demo credentials, unauthenticated surfaces, ownership and
   upgrade/migration warnings, known limitations — appear in Deploy as
   visible call-outs, not buried clauses. Grep the docs for limitation
   / known-issue / do-not-mix / migration markers and surface each
   customer-visible hit. *(Extract, Draft)*
6. **Deploy is copy-pasteable.** The repo's real commands in fenced
   blocks, starting from `oc login` and cloning the repo. Each external
   integration's prerequisites (license keys, service tokens, bootstrap
   commands) appear in the step that needs them — repeated in every
   step that needs them. A command lifted from the docs never keeps an
   unsubstituted `$PLACEHOLDER`: supply the export step or rewrite as
   "your own …". Verify claims against what actually runs — a doc's
   summary or "e.g." list is examples, not shipped behavior; check the
   chart templates, values, notebook, or script first. *(Extract,
   Draft)*
7. **Right altitude.** The README is the overview, not the manual: deep
   material (per-component resource tables, configuration inventories,
   patch snippets, full file trees) is linked, not inlined. Count lines;
   stay within the budget in writing-style.md (~150–250, 300 ceiling);
   the cutting order is fixed — Technical-details depth goes first
   (link the repo's doc for it), walked journeys and their per-step
   artifacts last. A README at the ceiling that keeps per-replica
   resource rows or capacity tables while dropping a walked journey has
   the priority inverted. "Summarize" has a precise meaning:
   the few knobs or limitations that change what the deploy does or the
   user can do, plus a link — a bare link is under-coverage; a full
   copy is bloat. *(Draft, Verify)*
8. **Hardware floor up front.** Requirements leads with a floor row for
   the whole quickstart in cores / memory / storage (plus GPU when a
   model is served in-cluster). Quote the repo's stated floor; when the
   repo states none, the row still exists with a `TODO: <what to fill
   in>` per category — never derive, sum-with-headroom, or guess.
   "Not specified in this repository" prose is not a hardware answer.
   The items cover everything the install renders, including
   third-party platforms the Makefile deploys and defaults inside
   packaged subcharts. Skipping the row and guessing its values are
   both failures; TODOing it is not. *(Extract)*
9. **References mirror the repo.** Carry the external URLs the repo's
   own docs link — an equivalent-looking URL is still a substitution;
   never invent one. Every headline component named in the Solution
   Stack gets its product-doc or project page — a product-doc page
   beats a GitHub source mirror when the repo links both — and the
   stack and reference lists must agree. One addition: canonical Red
   Hat docs for every Red Hat platform or product the Solution Stack
   names (OpenShift, OpenShift AI, Dev Spaces, AAP, …). *(Extract,
   Draft)*
10. **Tags classify, never coin.** Industry is ONE catalog category
    (observed values: "Adopt and scale AI", "Media and IT services"),
    carried verbatim when the repo states its classification, and
    otherwise derived from the vertical the repo's own story serves
    (telecom operations, IT service desk, manufacturing supply chain →
    the matching catalog value) — "Adopt and scale AI" is the fallback
    only when no vertical is nameable; Use case phrases come from the
    repo's own capability nouns, never coined or padded; Product
    is the primary Red Hat product (a second only when load-bearing);
    Partner only for a named third-party partner. Title and Description
    match the H1 and short description character-for-character, written
    last. *(Extract, Draft)*

## Signals → obligations (apply when the repo has the shape)

| Signal | Obligation |
|---|---|
| Values overlays or install profiles | Read each; scope figures and defaults to the path that uses them, never flattening one overlay's default into a universal claim. |
| Subcharts vendored as packaged archives (`*.tgz`) | Inspect their defaults (unpack or read with `tar`) before claiming a component sets no resource requests; quote repo-stated figures scoped to their path, TODO the values nobody states. |
| A model is involved | Present every serving path per the template's Option A/B (external endpoint, no GPU; in-cluster serving, GPU), with exact GPU models for GPU-dependent components; the primary install command must work for the option it accompanies — parameterize model/endpoint values. |
| Repo ships mocks or demo modes | The numbered steps configure real integrations: the exact flags that disable each mock and where each real token is created. A mock path, if shown, is clearly labeled a development/evaluation alternative — never the default happy path. |
| Runnable demo content or a UI surface exists (notebook, demo script, sample conversation, deployed screens) | It carries the headline, and Usage walks the primary interaction end-to-end: expected outcome, state reset, one visibly different alternative, reconstructed from the repo's own material. The demo material supplies content, never the surface: the Survey interface class decides it — a UI-reachable feature is walked step by step, every screen of the journey carrying a repo `docs/images/` screenshot or its own per-step TODO (harvest the whole screenshot pool for the flow's screens; one artifact never stands in for a multi-step journey), and a demo script's `curl`/CLI transcript is at most a labeled supplement to those screens, never their replacement. The walkthrough is that one journey: sub-features that are steps in it appear as its steps, never as walkthroughs of their own. |
| A capability is documented in a dedicated guide | Summarize its main knobs, elements, and gotchas; a bare link is not enough. |
| Optional post-deploy journeys are wired to dedicated commands or env vars | Fold each into the walkthrough step where it occurs, or a short labeled note when it sits outside the journey. Either way the coverage carries the enabling command(s), the journey's main elements from the repo doc's own structure (named metrics or knobs, gotchas, worked examples as trimmed code blocks), and what the user sees — a one-line mention, a features-list bullet, or a bare link is a defect; neither is a second walkthrough for a journey the main one already crosses. |
| A troubleshooting guide exists | Link it from Deploy after validation and carry its top recovery paths. |
| Several of the repo's own guides | Close with a consolidated Documentation table folded into References; repo-linked demo videos or blog posts supplement the Usage walkthrough, they never replace it. |
| CI or version-check targets pin tool versions | Those pins are stated requirements, carried verbatim; list every client tool the install actually invokes, each with its repo-stated version or a `TODO: <version>`. |

## Parallel work (when subagents are available)

The Process above is the spec. When your runtime provides a subagent/Task
tool, the independent, mechanically checkable subtasks may fan out to
subagents; when it does not, run every phase yourself exactly as written —
the gates, ledger, and outputs are identical either way. Parallelism is an
acceleration, never a dependency: no gate may depend on a helper having run,
and a failed or empty lane is re-run inline, never drafted around.

You are the single author of the README. Subagents gather evidence, render
the diagram, and audit; they never write README prose, never edit the ledger,
never resolve a conflict, and never spawn subagents of their own. Only you
write `README.md`, the merged ledger, and the survey note.

| Phase | What may run concurrently |
|---|---|
| Classify, Survey | Nothing — the interface class, headline features, and primary deploy path are the binding contract every subagent receives. |
| Extract | Four extract lanes (one subagent each), launched together after the Survey gate: L1 narrative+Tags (§4), L2 usage (§5), L3 requirements+deploy (§6–7), L4 architecture+stack+references+tree (§8–9). Each writes one findings file of §0 ledger rows; none reads another lane's findings. |
| Ledger merge, reconciliation (§10) | Nothing — one brain resolves every CONFLICT once, globally. |
| Draft | You draft all prose; the Diagram Builder subagent may run concurrently from the frozen ledger. |
| Verify and fix | You run your grounding pass and `check.py`; the read-only Grounding Auditor may run concurrently as an independent second pass. |

Follow `references/parallel-work.md` for the lane map, the verbatim subagent
prompts (paste the Survey gate note into each, unchanged — a lane never
re-derives a binding decision), the merge protocol (union → dedupe → §10
reconcile → spot-check ≥3 STATED rows per lane against their cited
`path:line` before drafting), and the fallback rules. Its isolation
constraints mirror this factory's safeguards — never weaken them.


## Verify and fix (mandatory before returning)

A draft is not the deliverable until it passes the machine check. The
bundled `rh-qs-verify` verifier (this skill's `verify/` directory) turns
the template's restrictions into 32 scored rules (T01–T32, 0–10 each,
weighted overall); `check.py` is its deterministic, always-available
form.

0. **Grounding pass first** — walk every factual sentence back through
   the claim ledger: sentence → ledger row → source file. Any unmatched
   claim becomes a policy/capture TODO or is deleted. Re-check commands,
   unsubstituted placeholders, versions, URLs, paths, images (a
   generated `.drawio.svg` exists beside the README, re-validates via
   `references/embed_drawio.py`, and prints no `LAYOUT:` line), and Usage
   artifact types (a UI feature shown in the UI, not a `curl`
   transcript), walkthrough count (one journey per walkthrough — no
   sub-feature of a journey walked separately, no journey walked twice
   on two surfaces), and per-step coverage (every walked step carries
   its screen — no single TODO standing in for a multi-step journey).
   Two more grounding controls: a claim that characterizes an artifact
   ("the guide shows X", "the notebook builds Y") stands only after
   reading that artifact end-to-end — never from its filename or a
   doc's summary of it; and a list enumerated from code comes from the
   literal itself, honoring exclusion comments (a name commented out
   beside a tuple is not in the tuple).
   `check.py` cannot see the repository; this pass is the only control
   on factual grounding. When a subagent tool is available, launch the
   read-only Grounding Auditor from `references/parallel-work.md` now,
   concurrently with this pass and the checker: it repeats the walk from
   a fresh context. Its findings are pointers, not facts — re-open every
   source it disputes yourself; your own pass remains mandatory either
   way.

1. **Run the live checker** on the README you wrote:

   ```bash
   python3 <skill-dir>/verify/check.py <README-path> -o <README-dir>/verify-report.json
   ```

   `<skill-dir>` is the directory this SKILL.md lives in (you read the
   skill from there). If the README's directory is not writable, drop
   `-o` and read the JSON from stdout. The report has one entry per
   restriction: `score`, `evidence`, `rationale`, `applicable`.

2. **Fix every rejection.** An applicable restriction scoring below 8
   is a defect: read its `evidence` and `rationale`, look the
   restriction up in `<skill-dir>/verify/references/checklist.md` for its
   intent, and fix the README to genuinely satisfy it — the template
   rules in `references/template-structure.md` say how. Then re-run
   the checker on the updated README.

3. **Stop when** every applicable restriction scores ≥ 8 and the
   overall is ≥ 8.5, or after 3 fix iterations — whichever comes
   first. `applicable: false` entries are correct N/As: never add a
   section or content just to make a CONDITIONAL restriction apply.

4. **Never game the checker.** It measures form, not truth — it cannot
   see the repository, so Invariant 1 (facts come from the repository)
   is never machine-checked and must never be sacrificed for a score.
   A fix that would invent a fact, loosen a pin, or keyword-stuff a
   phrase to trip a heuristic is forbidden. When a low score can only
   be raised by violating an invariant, keep the README truthful,
   accept the score, and report the restriction and why in your final
   notes.

5. **Fallback** when `check.py` cannot run (no python3, or the script
   errors): follow the verifier's agent instructions instead — read
   `<skill-dir>/verify/SKILL.md` and score your README against its
   checklist — then apply steps 2–4 to that score.

The machine check cannot verify factual grounding — before returning,
re-read the Invariants above and confirm the README honors them; they
outrank any score.

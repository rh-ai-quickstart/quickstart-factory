# Parallel work — extract lanes, diagram builder, grounding auditor

Use this file only when the runtime provides a subagent/Task tool AND the
Survey gate has passed. Without such a tool, run each lane's charter yourself,
in dependency order, writing the same files and passing the same gates — the
sequential path is the reference implementation, not a degraded mode.

SKILL.md's "Parallel work" section says what may fan out. This file says how:
the work directory, the lane map, the verbatim subagent prompts, the merge
protocol, and the fallback rules. Build every Extractor prompt as the SHARED
EXTRACTOR PREAMBLE plus one LANE CHARTER; launch all four lanes in one
message so they run concurrently.

## Work directory and files

`<work-dir>` = `<README-dir>/.rh-qs-work/` — scratch beside the README
(inside the round directory in the factory), never referenced by the README,
deleted before returning unless the caller asks to keep it as an audit trail.

| File | Writer | Contents |
|---|---|---|
| `<work-dir>/survey.md` | lead, once | the Survey gate note verbatim (shapes, interface class, headline features with evidence paths and the one marked main, primary deploy path, applicable signal rows) |
| `<work-dir>/ledger-<lane>.md` | one per lane | §0 ledger rows for that lane only |
| `<work-dir>/ledger.md` | lead only | the merged, reconciled, frozen claim ledger |
| `<README-dir>/docs/images/architecture-overview.drawio.svg` | Diagram Builder | the one generated artifact |
| `<work-dir>/grounding-audit.md` | Grounding Auditor | claim-by-claim audit report |

One writer per file. Lanes never read each other's findings, the README
draft, or the merged ledger. The lead is the only writer of the README.

## Lane map

| Lane | Hunts | evidence-hunting.md | Output |
|---|---|---|---|
| L1 narrative | title/short-description framing, Challenge/Solution material, Tags values | §4 | `ledger-narrative.md` |
| L2 usage | walkthrough journeys, ordered screens, artifact pool, demo material, mock/demo flags | §5 | `ledger-usage.md` |
| L3 requirements+deploy | requirements items and values, hardware floor, deploy target graph, commands, cautions | §6–7 | `ledger-requirements-deploy.md` |
| L4 architecture+refs | solution stack, component wiring, external URLs, repository tree | §8–9 | `ledger-architecture-refs.md` |

The lanes cover §4–9 with no gaps and no overlap; §0 (ledger format) and
§10 (conflict reconciliation) are every lane's shared vocabulary and the
lead's private tool respectively.

## Shared Extractor preamble (paste into every lane prompt)

> You are an Extractor (lane `<lane>`) for a Red Hat AI Quickstart README.
> You fill ONE slice of the claim ledger; you never write README prose and
> never decide README structure.
>
> Repository: `<repo-root>`. Skill: `<skill-dir>`. Your output file:
> `<work-dir>/ledger-<lane>.md`.
>
> Binding Survey note (authoritative — never re-derive its interface class,
> headline features, ordered screen lists, or primary deploy path; if the
> repository contradicts it, record a CONFLICT row citing the source, never
> override it):
>
> `<paste the Survey gate note verbatim>`
>
> 1. Read `<skill-dir>/references/evidence-hunting.md` §0 (the claim ledger)
>    and ONLY your lane's sections: `<lane sections>`. Follow them exactly,
>    including the search order, decision rules, and every "if absent,
>    try …" continuation.
> 2. Hunt your lane's evidence in the repository. Every checkable fact
>    becomes a ledger row: `Section | Claim (verbatim value) | Source
>    path:locator | Scope | Status` with Status one of STATED / TODO / OMIT /
>    CONFLICT. A STATED row quotes the value exactly as a repo file prints
>    it and cites `path:line`. A required value the repo does not state is a
>    `TODO: <what a human must fill in>` — never derived, summed, rounded,
>    or guessed; "derived" is not a status. Sources that disagree become one
>    CONFLICT row carrying both values and both sources — never pick one.
> 3. Record what you searched and did not find; an absence is a finding, not
>    silence. Never open a binary image file — judge images by filename and
>    the docs text that references them.
> 4. Write your rows to `<work-dir>/ledger-<lane>.md` (create the directory
>    if needed). Rows are evidence, not prose — no narrative paragraphs.
>
> Hard constraints:
> - Work ONLY from local files under `<repo-root>` and `<skill-dir>`. No
>   network of any kind (no WebFetch/WebSearch, curl, git fetch, helm repo
>   add). Do not look for the repository's original README anywhere.
> - Do not read `.research/`, any other round's results, another lane's
>   findings, the README draft, or `references/example-readme.md` (the gold
>   example — never a source of facts).
> - Do not modify anything except your output file. Do not spawn subagents.
> - Do not execute repository code or Makefiles; reading them is enough.
>
> Return at most 10 lines: the output file path, row counts by status, each
> CONFLICT row on one line, and one line naming your lane's biggest absence.

## Lane charters (the `<lane sections>` and task text per lane)

**L1 — narrative** (`§4`): Hunt the use-case framing: H1 and short-description
candidate nouns (each with its source), the Challenge material (who does the
work today, the manual steps, the cost the repo states), the Solution
before → after material, and the Tags values (Industry, Product, Use case,
Partner) — repo-stated values carried verbatim; a value the repo does not
state is a TODO, never a coined one.

**L2 — usage** (`§5`): For each Survey headline feature, confirm the
interface class and enumerate the ordered journey steps. Every step that
changes what the user sees carries its artifact: the exact repo screenshot
path (verify with `ls` — a path that does not exist is a CONFLICT row, never
carried) or its per-step capture TODO. Record expected outcomes, state-reset
material, demo-content details, mock/demo flags and what they disable, and
optional post-deploy journeys. A UI-reachable feature never gets an API/CLI
transcript as its step artifact.

**L3 — requirements+deploy** (`§6–7`): Hunt the requirements items and values
— platform, operators, external services, every client tool the install
invokes, CPU/memory/storage/GPU categories and the whole-stack floor row —
each valued STATED or TODO, never summed with headroom. Build the deploy
target graph: entry targets, prerequisites, ordered state-changing steps,
real commands verbatim from `oc login`/clone onward, every supported path,
unsubstituted `$PLACEHOLDER`s with their export steps, validation and its
success signal, delete tiers, and operational cautions (limitation /
known-issue / do-not-mix / migration markers, disabled-by-default flags,
demo credentials). Scope overlay and subchart figures to their path; inspect
vendored `*.tgz` defaults with `tar`, never flattening one overlay's default
into a universal claim.

**L4 — architecture+refs** (`§8–9`): Hunt the deployment set and component
wiring (env vars, ports, topics, routes, external boundaries), the Solution
Stack components the repo's docs name, the external URLs the repo's own docs
link (carried byte-for-byte — an equivalent-looking URL is a substitution,
never invent one), the Documentation-table candidates, and the repository
tree (every printed path verified to exist). Record whether the repo ships a
suitable main-architecture diagram (per §8's reuse test) and, if not, the
box/edge/label facts a generated diagram would draw — each traceable to a
repo file.

## Merge protocol (lead only — never a subagent's)

1. After all four lanes return, concatenate their rows into
   `<work-dir>/ledger.md` and dedupe identical (Section, Claim, Source)
   rows.
2. Resolve every CONFLICT once, globally, with `evidence-hunting.md` §10
   precedence (artifact beats summary; strictest floor wins per path; scope,
   don't flatten; deployed beats documented). No CONFLICT row survives the
   merge unresolved — that is the Extract gate, not a hope.
3. Carry every recorded absence forward into the merged ledger; an absence
   is a finding.
4. **Spot-check before drafting**: pick at least 3 STATED rows per lane and
   open each cited `path:line` yourself; confirm the quoted value is there.
   A row that fails is demoted to TODO or deleted — never trusted on the
   lane's word. A lane that violated the binding interface class is re-run
   with its rows to redo; you do not patch its findings by hand.
5. Run the Extract gate (SKILL.md Process step 3) against the merged ledger
   and the survey note. Only then Draft — from the merged ledger only.

## Diagram Builder (launched after the ledger is frozen, concurrent with Draft)

> You are the Diagram Builder for a Red Hat AI Quickstart README. You build
> ONE artifact; you never write README prose and never edit the ledger.
>
> Inputs: the skill at `<skill-dir>`; the frozen claim ledger
> `<work-dir>/ledger.md`; the binding Survey note `<work-dir>/survey.md`
> (its headline feature marked main is the diagram trunk); the README's
> output directory `<README-dir>`; the repository at `<repo-root>`.
>
> 1. Read `<skill-dir>/references/drawio-svg-format.md` in full. If the
>    ledger records that the repository ships a suitable main-architecture
>    diagram (L4's reuse test), copy it to
>    `<README-dir>/docs/images/<original-name>` and stop — do not generate.
> 2. Otherwise generate `<README-dir>/docs/images/architecture-overview.drawio.svg`
>    exactly per the spec: two synchronized layers (visible SVG + escaped
>    model XML), the application solution picture (headline-feature surfaces
>    and engines centered, supporting tools only where a journey crosses
>    them, mocks/install machinery out), repo-verbatim component names,
>    canvas sized to the picture, nothing below 12px, the Red Hat logo from
>    `<skill-dir>/references/redhat-logo.svg` at the bottom of both layers.
> 3. Every box, sub-label, and arrow traces to a ledger row; a component
>    you cannot source is omitted, never guessed. Do not add versions,
>    ports, URLs, or config keys to the picture.
> 4. Validate: `python3 <skill-dir>/references/embed_drawio.py <file>` —
>    fix every error and every `LAYOUT:` line before returning. Never write
>    an invalid `.drawio.svg`.
>
> Hard constraints: work ONLY from local files under `<repo-root>` and
> `<skill-dir>`; no network; do not read `.research/`, other rounds'
> results, or `references/example-readme.md` as a fact source; never open
> binary image files; write only under `<README-dir>/docs/images/` (scratch
> in `/tmp`); do not edit the README, the ledger, or any lane file; do not
> spawn subagents.
>
> Return: the artifact path (or the copied reuse path), the validator's
> final output, a manifest mapping every box and every arrow
> (source → target) to its ledger row, and any component you deliberately
> left out with the reason.

## Grounding Auditor (launched in Verify step 0, read-only, fresh context)

> You are the Grounding Auditor for a Red Hat AI Quickstart README. You did
> not write it. You are read-only: you never edit the README, the ledger, or
> anything except your audit report. Do not trust the claim ledger — verify
> every claim against the repository yourself.
>
> Inputs: the README at `<readme-path>`; the repository at `<repo-root>`;
> the claim ledger `<work-dir>/ledger.md`; the skill at `<skill-dir>`; your
> output `<work-dir>/grounding-audit.md`.
>
> 1. Walk every factual sentence in the README — versions, GPU models,
>    sizing figures, commands, flags, env vars, URLs, paths, ports, named
>    components, Tags — and for each, find the ledger row, then open the
>    cited repo file at the cited locator and compare the value verbatim.
>    The ledger row is not evidence; the file is.
> 2. Run a token sweep over the README (`grep -noE` for semantic versions,
>    numbers with units, URLs, `$VARS`, `docs/images/` paths, and fenced
>    commands) and account for every token: it matches a sourced ledger row,
>    or it is a finding.
> 3. Verify: no value is derived, summed, rounded, loosened, or substituted;
>    overlay values are scoped to their path; every image path exists (`ls`
>    it — never open the image); every TODO names exactly what to fill in;
>    every command exists in the Makefile/script/chart that runs it; every
>    URL appears byte-for-byte in a repo file.
> 4. Write `<work-dir>/grounding-audit.md`, one line per checked claim:
>    `README line | claim | SUPPORTED|UNSUPPORTED|AMBIGUOUS | source
>    path:line you opened | exact fix`. For UNSUPPORTED, the fix is delete,
>    TODO, or the repo source the lead should use — never a replacement
>    value from memory. AMBIGUOUS names what a human must check.
>
> Hard constraints: no network; do not read `.research/` or other rounds'
> results; never open binary image files (`ls` for existence; the
> `.drawio.svg` is text and may be read as XML); do not modify anything
> except your audit report; do not spawn subagents.
>
> Return: the audit path, counts by verdict, and every UNSUPPORTED claim
> with its suggested fix — at most 20 lines.

Triage (lead): re-open the cited repository file for every UNSUPPORTED
finding before changing the README; a valid finding is fixed from evidence
(a new fact gets a new ledger row with its source), an invalid one is
recorded with why in the round notes. Findings are pointers, not facts.

## Fallback rules

- No subagent/Task tool: run the four lane charters yourself, in dependency
  order, writing the same `ledger-<lane>.md` files and keeping them separate
  until the merge; build the diagram yourself; perform the grounding pass
  yourself (Verify step 0 already requires this).
- A lane that returns nothing usable, writes a malformed file, or fails
  twice: run that lane's charter inline. A BLOCKED lane is never drafted
  around with invented facts — its required items get TODOs.
- The Diagram Builder failing or timing out: build the diagram yourself, or
  record the `TODO: <architecture diagram>` per Invariant 3 — never embed an
  invalid or unvalidated file.
- The Auditor is advisory everywhere: your own grounding pass and the
  check.py loop are unchanged and remain mandatory.

## Safeguards (do not weaken)

- Every subagent prompt above carries the isolation list (local files only,
  no network, no `.research/`, no original-README hunting, no other rounds)
  — the factory's testbed sanitization depends on it.
- No subagent ever writes README prose, the merged ledger, or another
  lane's file; the lead is the single author and the single reconciler.
- Invariant 1 is enforced twice: structurally (no ledger row without
  `path:line`) and behaviorally (the spot-check plus the grounding pass).
  A clean score never outranks a grounded fact.

# Evidence hunting — where each section's content comes from

`template-structure.md` says WHAT each section must contain;
`writing-style.md` says how it should read. This file says HOW to extract
the content from an arbitrary repository: which files to open, which
patterns to grep, and how to decide. SKILL.md's Process section says when
to run each pass. Ground rule throughout: **a fact enters the README only
from a file you opened** — never from memory, plausibility, or general
knowledge of the product category.

Read the repo as a search problem, not a manual: cheap signals first,
stop a pass when it has answered its question, and record an absence as
a finding. Never open binary image files — judge them by filename and
the docs text that references them. Never fetch a URL or run `helm repo
add` / `helm dependency update` — the network is off-limits and the
remote chart may differ from the vendored one.

## 0. The claim ledger (kept through every pass)

One private working list, one row per checkable fact — values, commands,
versions, URLs, paths, ports, named components. Prose assertions are not
facts and get no row.

`Section | Claim (verbatim value) | Source path:locator | Scope | Status`

- `STATED` — a repo file prints it. Quote pins and figures exactly as
  stated; never loosen ("2.25.0 or later" stays, not "2.x").
- `TODO` — required item, no repo value; record what a human must fill in.
- `OMIT` — no evidence and not required.
- `CONFLICT` — sources disagree; resolve once, globally (§10).

"Derived" is not a status — summing requests, adding headroom, or
inferring a plausible value is a defect, not a finding. Draft only from
the ledger; if a sentence needs a fact with no row, find it or TODO it.
The README never carries source annotations — the ledger stays in
scratch beside the draft.

Two legitimate TODO forms: a **policy TODO** (a value the repo does not
state) and a **capture TODO** (an artifact the repo does not ship). Both
name exactly what to fill in. A filled value the repo does not support is
worse than either.

## 1. Classify the repo shape (before reading deeply)

A repo is often several shapes at once; none is the default. Record 3–6
lines — shape(s), known/unknown install entrypoints, which SKILL.md
signal rows apply — before any deep reading:

- Helm chart(s) with values overlays / profile files
- compose / local-dev files alongside or instead of a chart
- operator / kustomize bundles, console plugins
- IaC (Terraform) or orchestration scripts
- per-service package manifests (a services/ or multi-project workspace)
- runnable demo content (notebooks, demo scripts, showcases)
- CI configs and version-check targets
- a Makefile or `scripts/` that is the only install surface — including
  installs that pull whole charts from OCI registries referenced only in
  the Makefile

Shape decides where the app can hide and which extraction branches
apply; it never decides facts. Every universal instruction below has an
"if absent, try …" continuation — never require a chart, Makefile,
`.env.example`, docs dir, or a single install command to exist.

## 2. Survey (build an index, not a summary)

Read cheap→expensive; stop as soon as every required evidence area has
a lead or a recorded absence:

1. **Tree** at depth 2–3 (skip `.git`, `node_modules`, vendored and
   generated dirs). Note component dirs, deploy surfaces, docs, data.
2. **Install entrypoints** — the Makefile first among files: the `help`
   target and `.PHONY` line are the author's own table of contents;
   journey-named targets (deploy, demo, validate) outrank CI plumbing.
   Then chart roots, compose files, operator manifests, deploy scripts.
3. **Chart values and image list** — `grep -rn "image:" <chart-dir>` is
   the authoritative list of deployed components; app code not in it is
   dev tooling, not the product. Read every `values*.yaml` overlay's
   top-level keys and `enabled`/`condition` flags: a component off by
   default is not a headline.
4. **Doc headings** (not bodies) across `docs/` and every sub-README;
   prefer domain-named docs over process docs (DEV_GUIDE, RELEASE,
   CONTRIBUTING — contributor material, skip unless a fact is missing).
5. **Demo artifacts** — demo scripts, showcases, notebooks, fixtures,
   seeded data; and image filenames under `docs/images/`, `assets/`.
6. **Configuration surfaces** — `.env.example` (its comments are the
   repo's own credential documentation), profile files.

The survey note (scratch, never pasted into the README) records: shapes,
entrypoints, deployed components, interface class, candidate headline
features with entry points and evidence paths (one marked main — that
mark only decides the architecture-diagram trunk; EVERY selected feature
is walked as a full Usage journey), each feature's ordered step list
(the screens its journey crosses — the walkthrough walks them all), demo
material, and — explicitly — what is absent. Do not draft until the note
names the interface, the 1–3 headline features (each a core application
feature the UI surfaces and the repo's own docs foreground — a journey
with sub-steps folded in, plus its ordered screen list), and the primary
deploy path.

## 3. Application, interface, headline features

**Finding the application.** The component that BOTH deploys (chart
image list, compose service) AND owns an interface is the application.
Everything else is infra (brokers, databases, observability backends,
gateways consumed only by other services), a pipeline stage (services
with only internal routes), a mock (anything named/structured `*-mock`,
`mock-*` — a Deploy caution, never the product), or install machinery
(Terraform, ArgoCD, operator subscriptions, CI, build/push targets).
**Platform-vs-product trap:** when the repo's own code is thin and the
deploy installs a platform (an IDE workspace, a third-party chart), the
product is what the user does inside it; the platform goes to
Requirements and Solution Stack, not the title.

**Classifying the interface** — grep for the signal, then confirm the
surface is deployed:

| Surface | Signals |
|---|---|
| Web UI | `package.json` with react/vue/svelte + `index.html`; `src/pages/`, `App.tsx`; `console-extensions.json` (console plugin — the console IS the surface) |
| Gradio/Streamlit | `gradio`, `gr.Blocks`, `demo.launch`; `streamlit`, `st.` |
| API | `FastAPI(`, `@app.get/post`, `APIRouter`, Flask routes, OpenAPI specs, MCP tool defs |
| CLI | `argparse`, `click`, `typer`, `console_scripts`, `[project.scripts]` |
| Notebook | `*.ipynb` with markdown stage headings; a chart shipping the notebook |
| Channel | Slack/Teams/webhook/email/ticket handlers, chat panels |

Precedence **UI > API > CLI** — binding, not a label: it decides the
artifact TYPE each Usage H3 shows (§5) before any search starts, and
evidence availability never reclassifies a feature. An internal REST
service behind a Slack/email/ticket agent or a dashboard's BFF is
plumbing — the conversation or the dashboard is the user surface — and
so is a documented REST API behind a UI: when a repo ships a real UI
and REST endpoints for the same feature, the UI is the surface, the
walkthrough shows the screen, and a transcript is at most a labeled
supplement. A demo script that drives a UI app via its REST API is
exercising plumbing, not choosing the surface. API or CLI is the
walkthrough artifact only for features no UI exposes. Multiple sibling
frontends: pick the one the repo's docs walk as the user's journey — a
demo script invoking an API is not walking a frontend. A UI gated off
or reachable on only one deploy path follows the surface the repo's
docs walk on the presented path (state the enabling flag only if the
user must set it). A repo with no first-party app code (charts, IaC,
tests only) has the deployed platform's UI / IDE / notebook as its
interface — classify it UI-like, source screenshots from the repo or
TODO them.

**Picking the 1–3 headline (core) features.** They are the application's
core features — the main things a user of the deployed quickstart does —
sourced where the authors
stated them, in trust order: sub-README feature lists and domain docs →
UI page/tab/nav structure (the screens the user reaches) → demo
scripts' stated flow → conversation/evaluation fixtures with expected
outcomes → CLI subcommands and route help text → chart values that
switch user-visible behavior (supporting evidence, rarely a feature
alone) — a demo script names the task, never the feature's endpoint. A feature must pass a
four-gate test before it enters the inventory:

1. **Implemented** — a shipped code/config path performs it, not prose.
2. **User-reachable entry point** — a UI page, exposed route, CLI
   command, notebook cell, or channel handler invokes it; a function
   only tests or internal services call fails here.
3. **On the primary path** — enabled by default in the main deploy, or
   explicitly part of the use case the repo demos. A surface reachable
   only through an optional integration profile or a non-default values
   overlay fails this gate: it becomes a labeled note with its enabling
   flag, never a Usage H3. Setup/configuration (e.g. connecting a model
   endpoint) counts as a feature when the repo's own docs walk it as a
   user journey.
4. **Demonstrable** — the repo ships an artifact of the type the
   classified interface demands (UI → a screenshot per walked step, or
   UI-source reconstruction; API → request+response; CLI →
   command+output), or the walkthrough carries that type's precise
   per-step TODOs (§5). An artifact of
   a different type — a `curl` transcript for a UI feature — does not
   satisfy this gate; it is a labeled supplement at most.

You must be able to state, in one sentence, who acts, what they do at a
named entry point, and what they get back. Rank by user value in journey
order; fold sub-steps of one workflow into one feature — a feature is a
journey with its own outcome, never a step inside another feature's
arc. What never
counts: capabilities only a developer or CI invokes; internal
architecture facts ("uses RAG"); doc-aspirational mentions; demo
scaffolding (`/demo/trigger` endpoints, demo-mode buttons, seeded
incidents); disabled-by-default add-ons (state the default and enabling
flag, or demote); platform features the quickstart merely configures; a
step of another feature's journey listed as its own feature;
anything beyond the third feature — completeness lives in Technical
details (features list, Solution Stack), not the walkthrough.

## 4. Narrative head and Tags — derive, don't invent

The head is a citation exercise: find the repo's own value framing and
compress it. Every headline noun must trace to a repo file.

**Search order** (stop when two independent sources agree on the use
case): user-facing docs (overview/architecture/guide intros — the first
~30 lines usually name role and outcome) → per-use-case `Chart.yaml`
`description:` lines → sub-READMEs of the user-facing component →
notebook markdown intros (read cells as JSON, never execute) → app
manifests and configs (a chat-app manifest's `long_description` is
written to sell the app to its users) → agent-instruction files
(`AGENTS.md`, `CLAUDE.md` openers — crisp one-liners, confirm against
the shipped charts) → demo scripts and agent/prompt configs → package
metadata, LAST and skeptically: a root `pyproject.toml` can describe
only the test tooling, not the product — prefer the sub-package
description that names the application. Trust order at the same tier: a
source naming the user's outcome beats one naming the architecture;
operational docs beat market-analysis prose.

**Two-source rule.** No use case goes in the H1 until two independent
places agree; a lone tagline can support a Solution sentence, never the
title. If sources never agree, describe the user action and output in
neutral verbs and stop. **End-user vs platform test:** if the sentence
only names components, rewrite it as action + result; a good head
sentence survives swapping the platform.

**Writing.** H1 (≤64 chars, count with `wc -m`): verb-led outcome using
the repo's domain noun — not a component name, not "Deploying…", not
"A quickstart for…". Short description (≤160 chars): one sentence —
outcome + application + 2–3 concrete capabilities, intelligible without
the repo. Challenge (2–4 sentences): who does the work today and how,
the cost the repo states (mechanism, not an invented number), why it
falls short; when the repo states only a solution, invert it — name the
manual steps its automation replaces, from its own docs/demo material.
Solution (2–4 sentences): the improvement for each pain the Challenge
named — before → after in the user's terms, only decision-relevant
detail, one-pass clear; no component inventory, no versions. Reuse the repo's verbs
and never upgrade them — "checks" is not "guarantees". Amplification
blacklist (unless repo-stated): percentages, time/cost/MTTR figures,
compliance guarantees, "enterprise-grade", "seamless", "revolutionary",
regulatory-threat narratives, coined domains.

**Tags gates.** Write the Tags block last, after the body settles, so
Title and Description are byte-identical copies of the final H1 and
short description — a reworded "match" is a mismatch; recount after
every late edit. **Industry:** exactly ONE catalog category; carry a
repo-stated classification verbatim only when it is an observed catalog
value — a sub-README's generic "Technology" and sectors appearing only
in example data or sizing tables are traps. Before defaulting, name the
vertical the repo's own narrative serves — the industry whose problem
the Challenge and the repo's docs name (telecom network operations, IT
service desk, manufacturing and logistics supply chain, healthcare
providers) — and map it to the closest catalog value (Telecom, "Media
and IT services", Manufacturing, Healthcare). Only when no vertical is
nameable, default to "Adopt and scale AI" and note the default; never
coin a sector or compound two. **Product:** "OpenShift AI" primary; add
a second Red Hat platform only when load-bearing — the repo's own
one-line value statement names it or it performs a core step of the use
case; an optional integration path is not load-bearing. **Partner:**
only a named third-party org the repo identifies as a partner or
co-star; integrated services (ticketing, chat, storage) are not
partners, and Red Hat is the vendor, never a partner. **Use case:**
2–4 short phrases from the repo's own capability nouns. **Contributor
org:** "Red Hat" by default; add an org only when the repo credits it.

## 5. Usage — find or reconstruct the walkthrough artifacts

Usage is organized by journey: one H3 per headline feature (§3), and a
sub-feature that is a step inside a journey appears as a step of that
walkthrough — never as its own H3. Each walkthrough is walked as a
step-by-step progression through the journey's screens: every step that
changes what the user sees carries a real artifact **of the type its
interface demands**; prose alone never counts, and one artifact standing
in for a multi-step journey is a defect — a step whose screen the repo
does not ship gets its own TODO and the walk continues. **The §3
interface class
fixes the type before any search begins** — UI → screen, API →
request+response, CLI → command+output, notebook → stored outputs,
channel → conversation. Record `feature | interface class | required
artifact type | journey steps (ordered screen list)` in the working note
first — enumerate the flow's steps BEFORE hunting images, so the hunt
maps screens to steps; any deployed, reachable UI
makes the feature type UI. The type, not the first artifact found,
governs the hunt: a `curl` pair found in a demo doc or test does not
satisfy a UI feature's hunt and never becomes its walkthrough artifact.
A UI action that calls an API is still UI — cite the screen; a
transcript supplements it only when it invokes the same backend action
the UI control performs, the repo captures the response, and it carries
the reconstruction label below. When demo material offers "dashboard or
curl", the dashboard is the walkthrough. Architecture diagrams
(`architecture*`, `diagram*`, `flow*`, `view*` filenames) belong in
Detailed description, not Usage.

**Search only the feature type's ordered path; for API/CLI/notebook/
channel features, stop at its first usable artifact — for UI features,
collect every walked step's screen, never just the first.** Demo docs
are richest for the type they demonstrate —
usually API/CLI; for a UI feature, one matching screenshot outranks
every transcript in them.

- **UI feature** — (1) the screenshot pool (`ls docs/images/`,
  `assets/`; filenames name the screens): list it whole, classify each
  image (screen vs diagram, from filename and doc text — never open the
  file), map every screen image to the journey step it shows, and use
  them in journey order; progression filename patterns (`_part_1/2/3`,
  a `-detail` variant of a list screen, before/after suffixes like
  `-no-guardrails` vs `-guardrails`) are explicit ordering signals. A
  filename matching a walked screen AND referenced by a doc naming that
  screen is used; an orphan matching a walked step's screen is usable
  when the flow's other screens are doc-referenced or page-matched;
  (2) UI source: the nav registry's order IS the journey order — read
  page components and their tests (component-test `defaultProps` carry
  real labels and option lists), grep literal UI strings (`label:`,
  `title:`, `placeholder=`, `choices=[...]`), quote them exactly inside
  quotation marks, and reconstruct the screen's states;
  (3) the exact per-step screenshot TODOs (Gates below). Fixtures, seeded/mock
  data, and tests supply concrete labels, options, and expected states
  as inputs to the reconstruction, never as a substitute artifact.
- **API feature** (no UI exposes it) — demo/showcase docs → tests
  (real request bodies, asserted outcomes) → conversation fixtures →
  OpenAPI specs. Stop at the first captured request+response.
- **CLI feature** (no UI or exposed API) — CLI example scripts and
  their docstrings → demo docs' command transcripts → outcome-asserting
  tests. Stop at the first real command+output.
- **Notebook feature** — stored cell outputs only (empty `outputs` is a
  script, not a transcript).
- **Channel feature** (Slack/email/ticket/web chat) — conversation and
  evaluation fixtures first (user turns quotable verbatim,
  `known_good*`, query-list files), then seeded data for concrete
  outcomes; the conversation is the artifact, the REST service behind
  the dispatcher is plumbing.

**Reconstruction rules.**
- From a demo script: lift the real command and its stated expected
  output verbatim; keep the script's ordering (it is the user's
  journey) and its reset step. **Placeholders stay placeholders** —
  `12.XXs`, `uuid`, `<namespace>`, `...`, alternations with `|` are not
  captured output; never normalize them into plausible values. "Expect
  stages like" is illustrative, not a transcript.
- From a conversation fixture: user turns are quotable verbatim; agent
  replies usually are NOT in the repo — narrate the arc from the
  fixture's expected-state metadata and take concrete outcomes from
  the seeded data. `known_bad` fixtures are negative evidence: a
  labeled alternative at most, never the happy path.
- From tests: a test asserts properties (`status == 200`, non-empty
  field), not a body — state the outcome in prose; do not synthesize a
  response the test never contained.
- From seeded/mock data: quote option names, labels, prices verbatim;
  separate input seed from generated output — a mock server generating
  random ticket IDs cannot supply a literal one; parameterize
  (`<ticket-id>`) or TODO the capture. State the seeded scope where it
  matters; never present the mock path as the production journey.
- Label every assembled transcript in one line above the block:
  "Reconstructed from `<repo path>`"; a literal documented
  request+response pair needs no label. A response schema with
  placeholder values is a contract, not a sample — the real sample
  stays a TODO.
- From UI source (tier 2 of the UI path above): the journey's screens
  walked as its numbered steps, each with its screenshot or TODO — not
  one H3 per screen, not the whole UI inventory; label the
  reconstruction like any other. This step-walking shape is the general
  walkthrough form (see the §5 intro), not a reconstruction-only
  special case.

**Gates.** Verify the exact path AND case AND extension of every image
before referencing it (`docs/img/` ≠ `docs/images/`; `.jpg` ≠ `.png`).
An existing image is not automatically usable: an orphan referenced by
no doc, matched by no page/component, and matching no walked step of a
flow whose other screens are matched gets the TODO, not a guess.
Never reference a remote image as a repo screenshot. Every fenced
request is runnable as written or carries only documented
substitutions; strip secrets. The TODO form is chosen by the feature's
type, never by which is easiest to fill — a UI feature never receives
an API or CLI TODO. TODOs are per-step: one placeholder per walked step
whose screen is missing, placed where that step's image belongs — a
single TODO standing in for a whole multi-screen journey is a defect.
Exact TODO wording:
- UI: `TODO: add a screenshot of <exactly what the step's screen shows>, saved as docs/images/<descriptive-name>.png`
- API: `TODO: capture the real response of <request>`
- CLI: `TODO: capture the real output of <command>`

Demo video/Arcade links supplement after the walkthrough, only when
the repo itself links them — never a replacement, never invented.

## 6. Requirements — the evidence hunt

Every required ITEM is listed; every VALUE is repo-stated or TODO.
Build the item/value/source table before writing.

**Hardware (CPU / memory / storage / GPU).** Aggregate floors live in
prose; per-component figures live in manifests; never confuse the two.
Search: dedicated requirements/sizing docs and per-path deploy-guide
READMEs (read them whole — a guide pointing at "the README's minimum
hardware" is pointing at the file you are writing, not a floor) → every
values overlay's `requests:`/`limits:`/`size:`/`storageClassName` (read
the templates that consume them too — a key is not proof it renders) →
packaged `*.tgz` subcharts: `find . -name '*.tgz'`, then
`tar -xzOf <tgz> <chart>/values.yaml` or unpack to a temp dir; they
nest, so recurse; a subchart shipping `resources: {}` states NO
resources — TODO, never "0" → compose `mem_limit`/`cpus` (local path
only) → ResourceQuotas (a stated ceiling the floor must fit under).

**Hard line — stated vs derived.** A whole-stack floor row is written
only when the repo states an aggregate; summing per-pod requests,
promoting one pod's request, headroom, or unit-rounding is forbidden
and a defect. Per-component figures may appear scoped in prose, not in
the floor row. A remote, non-vendored chart dependency is not evidence.

**Software versions.** Sweep: Makefile version variables and comments
(`OC_VERSION`, `*_CHART_VERSION`; a comment saying "must match CI"
makes the CI pin the requirement) and `check-*`/`validate-*` guard
targets whose error messages state prerequisites verbatim → CI configs
(`setup-python|uv|node|helm` `with: version`) → `.python-version`,
`.tool-versions`, `.nvmrc` → `requires-python` / `engines` (multi-project
workspaces have many manifests — read them ALL; scope test-only floors
out) → operator Subscriptions (`channel`, `startingCSV` — each names an
operator the install depends on, with its stated version) → `Chart.yaml`
`kubeVersion` (a floor; `appVersion` is a component version, NOT a
requirement). Carry the strictest stated minimum per presented path —
sweep every doc that states a floor; the strictest often sits in the
least-visible guide; "tested with" is a stated requirement. Keep
ceilings as ceilings; keep ranges as ranges; scope path-specific floors
to their path (one whole-stack floor; per-path rows when they differ).

**Client tools.** Token-grep the Makefile recipes, the scripts they
call, and CI: `grep -ohE '\b(oc|kubectl|helm|make|python3?|uv|jq|yq|podman|docker|git|terraform|node|npm)\b' Makefile scripts/ | sort | uniq -c`.
Confirm each hit is an invocation on the presented path, not prose or a
dev-only target; `git` counts only when invoked, not for the clone
step. A tool with no invocation site is dropped. Two refinements the
hit list alone gets wrong: **build-path tools count** — when the
install path builds images or frontend bundles, the tools it invokes
for that (container runtime, node/npm) are required, with their
CI-pinned versions as the stated values; and **the caller decides, not
the hit** — a token used only by a CI/service-account or contributor
script off the customer path (e.g. a GitHub Actions setup script) is
excluded even though the grep finds it.

**Permissions.** Decide from what the install CREATES:
`grep -rnE 'kind: (Namespace|ClusterRole|ClusterRoleBinding|CRD|OperatorGroup|Subscription|SecurityContextConstraints|DataScienceCluster|PersistentVolume)\b' --include='*.yaml' .`
— any hit the install creates (check `templates/` for templated ones)
means some step needs cluster-admin, said with its reason. A RoleBinding
that merely references an existing ClusterRole does not. Namespaced-only
releases need regular user / namespace admin. Scope per path; local
paths need container runtime permission and the compose file's ports.

**GPU.** Required only when an object on the presented path requests
`nvidia.com/gpu` (or `gpuCount`, GPU node selection); optional when an
external-endpoint path exists — state the trigger ("required only for
in-cluster model serving"). Name a GPU model only when the repo states
it; an instance type alone is not a model. Never say "no GPU required"
while an in-cluster serving path exists.

**TODO phrasing** — name exactly what a human verifies on a real
cluster: `CPU: TODO: minimum cores for the whole stack (repo states
none; per-service requests exist but are not summed)`; `oc CLI —
TODO: version (the repository does not pin one)`. "Not specified in
this repository" prose in place of a row value is not an answer.

## 7. Deploy — reconstruct from the target graph

Deploy is a transcript of what the repo actually runs. Build the
**target graph**: entry target → prerequisites → recipe → called
scripts/targets → what it creates, plus the inverse target that
removes it.

**Read order.** The root Makefile may be a router (`$(MAKE) -C
deploy/...`, `cluster/%`) — follow every delegation to the leaf file
holding the real `helm`/`oc`/`terraform` invocation, including
`scripts/*.sh`. The user-facing install target is the one whose
prerequisite chain composes the whole flow; guard targets in that
chain (`check-*`, `validate-*`, `pre-install-checks`) are the repo's
own prerequisite statements — their error messages name required
inputs verbatim. Then: every chart the install consumes (`Chart.yaml`
dependencies and `condition:` gates, `values.yaml`, every overlay —
note which the target passes with `-f` and in what order, last wins);
`.env.example` (key list + comments; note the loading convention —
some Makefiles `-include .env`, others require `source .env`, others
prompt — this changes step 1); route/ingress/HTTPRoute templates and
`NOTES.txt` (the chart author's post-install instructions); deploy
docs and per-path guides (to find the intended entry target — confirm
every command against the recipe); CI (reveals required overrides and
the non-interactive form of prompts, but is not the customer path).
Grep the Makefile and scripts for `helm install|upgrade`, `oci://`,
and `helm repo add` — charts installed only that way are real deployed
components absent from the local `Chart.yaml`.

**Turning the graph into steps.** One numbered step per node that
changes cluster state or requires user input, in execution order:
login+clone (the repo's stated clone URL) → set inputs (matching the
repo's env convention) → install in dependency order → post-install
initialization (bucket creation, minted credentials, demo data) →
validate → point to Usage → delete. Render each step as the repo's own
command — when the repo wraps helm in make, print the make invocation
(the conditional `--set` logic is the supported interface); do not
inline an expansion you will get wrong. Note interactive prompts in
prose and show the repo's `.env` alternative. `VAR ?=` defaults are
resolved, not shown as choices; `$(error ...)` guards and `[ -z ]`
checks mark user-supplied inputs, which get an export step and are
repeated at every step that consumes them. Hard prerequisites (guard
fails without them) go in Prerequisites; commented-out optional
overrides are configuration knobs, not prerequisites. When
`.env.example` or base values default a mock integration ON, the
numbered configure step writes the real-integration flags into its
printed env/command — mocks never ride the numbered path — and every
external-integration bootstrap target the repo ships (provisioning
scripts, `*-bootstrap` targets) appears as a numbered prerequisite with
its credential requirement. **Day-2 commands:** sweep the same `help`
output for operational targets beyond install/uninstall (logs,
restart, status helpers, port-forward); the customer-facing ones get a
short one-line-each list in Deploy, beside validation or delete.

**Optional post-deploy journeys.** A journey the repo's docs walk in a
dedicated section or guide — evaluation harnesses, session-level
observability, post-run audit/export, bring-your-own-data
customization, console integration menus — is deploy content, not a
Features bullet. Coverage is a labeled note or short subsection
carrying: the enabling command(s) (make target, env vars) exactly as
the repo prints them, the journey's main elements from the doc's own
structure (named metrics or thresholds, its gotchas, its worked
example as a trimmed code block), and what the user sees. A one-line
mention plus a link is under-coverage; the full doc copied is bloat.

**Validation** — from what the repo ships, in priority: its own
`status`/`verify`/`print-urls` target → the repo's own route-lookup
commands, with the real route name from the chart template
(`oc get route <name> -n <ns> -o jsonpath='{.spec.host}'`); if the
template sets no host, say it is auto-generated and show the lookup —
never write a plausible hostname → `NOTES.txt` → `helm test` only when
`templates/tests/` exists (a validation step naming a nonexistent
command is a defect) → port-forward targets for local access. State
what success looks like.

**Delete.** Read the uninstall target end-to-end, scripts included.
Present the tiers the repo defines — default uninstall often preserves
the namespace and data PVCs for a warm restart; the full-wipe path
(`DELETE_NAMESPACE=1`, a `teardown` target) is documented with its
data-loss consequence. Name the leftovers the recipe handles (PVCs,
secrets, cluster-scoped RBAC, CRDs, extra namespaces) and any
cluster-wide resource it deliberately keeps, with the removal command.

**Option A/B (model paths).** Detect from the machinery, not prose:
in-cluster serving when a chart deploys a serving component or values
carry `model.*`/`hf_token`/GPU resources; external when the target
accepts an `LLM_URL`/`OPENAI_*_ENDPOINT` plus token, or disables the
local service when the URL is set. Three shapes exist across repos:
external-only, either, or in-cluster-by-default — present every path
the repo supports with the exact flags that select it; the command
under each option must be the one that works for it. Never fabricate a
second option a single-path repo does not have.

**Multiple paths** (cluster/local, platform variants, topology, style)
enumerate from directories, overlays, and targets — one subsection per
path with its own commands and values files; shared first steps stated
once. Never average two paths or let the simplest stand in for the rest.

**Cautions.** Grep docs, values comments, `.env.example`, and Makefile
comments (not app source or prompts — noise) for:
`limitation|known issue|do not (run|use|mix)|disabled by default|deprecated|migration|unauthenticated|demo (value|password)`.
Each customer-visible hit becomes a call-out at the step where the
user hits it: default-on mocks with their disabling flags, disabled
routes with enabling flags, do-not-mix warnings, migration/upgrade
order, data preserved across uninstall. Keep the repo's wording.

**Gates.** Commands exist (target names verified); no unsubstituted
`$PLACEHOLDER` without its export step; env loading matches the
Makefile; vendored `charts/*.tgz` may be inspected but OCI/remote
charts only via the repo's flags and overlays; every supported path
present; every default named as a default.

## 8. Architecture diagram and solution stack

Two ledgers before drafting: **component/flow** (what deploys, what
talks to what, over which port/topic/route) and **stack** (notable
components + the OpenShift AI capabilities actually used). Draft from
the ledgers, never from what the product category "usually" includes.

**Enumerate the deployment set.** Read every `Chart.yaml` dependency
(`name`, `version`, `repository`, `condition`, `alias`): `file://`
entries recurse; packaged `charts/*.tgz` are vendored — read defaults
with `tar -xzOf` and never extract into the repository; a remote
repository is not fetched — its name/condition are evidence, its wiring
is in the parent's values. Read every template and record the kind and
name (Deployment, StatefulSet, Job, Knative Service/Broker/Trigger,
Kafka, and CRs like Notebook, InferenceService, LlamaStackDistribution,
HardwareProfile); open `_helpers.tpl` for real env blocks. Read
`values.yaml` `enabled`/`condition` defaults — a component default-off
is an optional alternative, not a main-path box; overlays can enable
what base values disable. Compose shapes: `services` keys with
`image`/`ports`/`environment`/`depends_on`. Then catch what the local
charts miss: Makefile/script `helm install` and `oci://` releases.
Cross-check against the repo's architecture docs — **when they
disagree, the chart/compose decides what deploys; the docs decide the
role and human-facing name.** Mermaid sources (`.mmd` files, fenced
`mermaid` blocks) are text — read them fully; they encode the flow the
authors consider main. Mocks deployed by default are deployed
components — list them, then place them per the mock rule.

**Wiring — the only valid arrow sources.** Env vars between services
(`*_HOST`, `*_URL`, `*_PORT`, `*_ENDPOINT`, `*_BOOTSTRAP`,
`DATABASE_URL`) — each consumer env var naming another service is an
edge; ports and their protocols; Kafka topic names and Knative
Trigger/Broker names (they literally spell the event flow); connection
strings; Route/Ingress/HTTPRoute path rules; Secret refs and outbound
URLs marking the external boundary (model endpoints, SaaS ticketing,
chat webhooks — external systems get boxes at the canvas edge). Code
alone is not proof: a gated-off template is not deployed behavior.

**Diagram — the application solution, not the deployment graph.**
Reuse a shipped image only when all three hold: it lives in the repo's
image dir with a main-architecture filename; repo text identifies it as
the main architecture; its components agree with the ledger — and it
shows the solution flow, not an install graph (a mock-laden or
infra-first shipped diagram is not suitable; generate instead).
Otherwise generate `docs/images/architecture-overview.drawio.svg` under
the README's own `docs/images/` per `template-structure.md` and
`references/drawio-svg-format.md`: a hand-authored, draw.io-editable
SVG (escaped model XML in the root's `content` attribute), with both
Red Hat logo `<path>` elements in a group at the bottom of the canvas
AND an image cell in the embedded model. Box color encodes the tier
grouping — application core strongest (red tint), architecture-bearing
tools lighter (blue tint), external systems neutral grey dashed,
optional alternatives dashed gold — same tier, same color, in both
layers, per the palette in `references/drawio-svg-format.md`. In one
line: draw the
end-user surfaces and application services that deliver the 1–3 core
(headline) features, plus only the architecture-bearing tools those
feature journeys cross and the external systems at the periphery. A
component earns a box only when it is deployed on the primary path (or
is an external boundary named by a primary-path wiring edge), sits on
a headline-feature journey, changes the customer's understanding of
the solution, is repo-named, and is not a mock, install tool, plumbing
item, platform box, or main-path default-off alternative. Boxes carry
the repo's names, never synonyms; shared infrastructure is drawn once;
a first-class alternative may appear as one detached box outside the
main flow, dashed, carrying the repo's name and enabling switch (max
two, never on a main arrow). The marked main feature's journey is the
trunk; each headline feature is visible at least once. A sub-label
under a box may name the end-user capability it delivers only when the
repo states it, verbatim from the §3 inventory — no quote, no label,
never invented. A box may carry the component's logo instead of its
bold title when the repo itself ships that logo — inlined as a data
URI in both layers, never fetched or invented (per
`references/drawio-svg-format.md`). Arrows remain wiring-ledger-only
and main-flow-only, in the user's data direction; one arrow per pair.
Only the main features earn space: target 5–10 content boxes (12 hard
ceiling only when every box sits on a headline-feature journey;
fewer only with a recorded justification), no orphans. The numbered
walkthrough below the image: 3–6 steps, one sentence each, actor →
mechanism → destination, starting at the end user and ending at the
outcome, naming components exactly as the picture does and never one
it omits; every step crosses a drawn arrow, every main-trunk arrow is
covered by a step.

**Solution stack.** Mine: every `pyproject.toml` in a multi-project
workspace (ignore `[dependency-groups]` dev blocks; for generated
requirements files take the project's own declared packages, not the
hashed transitive block) → `package.json` `dependencies` → chart
dependencies and vendored tgz → image repositories → Containerfile
`FROM` → names the repo's docs state. Apply the **household-name
filter**: drop what a working developer knows on sight (FastAPI,
uvicorn, pydantic, React, generic PostgreSQL, pytest); keep the
notable or architecture-bearing (agent frameworks, MCP, vector search,
embedding services, tracing/eval platforms, event buses, object
storage, guardrails, serving stacks, partner platforms). Test: would a
customer evaluating this quickstart learn something from the name?
One bullet per component — name plus a one-line role mined from the
repo's own docs, not general knowledge. 8–14 bullets: fewer means
under-mined manifests; more means the filter was skipped.

**OpenShift AI capabilities — the gate.** Grep for the signals
(`InferenceService`/`ServingRuntime`/KServe → model serving; a shipped
`Notebook` CR plus notebook content → workbenches;
`DataSciencePipelinesApplication`/pipeline CRs → data science
pipelines; `ModelRegistry` → model registry; `LlamaStackDistribution`
→ Llama Stack; TrustyAI; `modelsAsService`). A `DataScienceCluster`
entry with `managementState: Managed` proves the platform capability
is ENABLED, not that the quickstart USES it — require a project-owned
resource, a rendered workload, a shipped notebook, or an explicit repo
statement of use. Each capability that passes gets its own bullet;
OpenShift AI bullets lead the list, most core first; never a catch-all
"OpenShift AI" bullet. Docs claims alone ("designed for OpenShift AI")
never count.

## 9. References and Repository structure

**Harvest** (scoped away from lockfiles, CI, logs, tests, vendored
charts): inline markdown links in `docs/` and sub-README prose (highest
precision — the author chose label and target; a sub-README's
"Documentation/References" block is the repo's own curated list) →
`Chart.yaml` `home:`/`sources:`/dependency `repository:` → comment
links beside named settings in values/`NOTES.txt`/notebook markdown —
but `helm create` boilerplate (kubernetes.io concept links) appears in
nearly every chart and references nothing the quickstart integrates; a
comment link counts only when it documents a choice beyond Helm
defaults → code comments, last and skeptically.

```bash
grep -rhoE '\[[^]]{2,80}\]\(https?://[^)]+\)' --include='*.md' docs */README.md | sort -u
grep -rhoE 'https?://[^[:space:])"'"'"'<>`]+' docs guides */README.md | sort -u
```

**Drop** (each noise class recurs across repos): cluster-internal and
placeholder endpoints (`localhost`, `*.svc`, `.apps.<cluster>`,
`your-*`, `{{ }}`); registries, lockfiles, licenses, badges; download
mirrors; credential consoles and sign-up pages (keep the setup *guide*
an integration doc links, not the portal); issue trackers/PRs/CI;
self/fork links and the quickstart org's own clone URLs (they belong
in Deploy); runtime API examples (`api.*.com/v1`); third-party blogs
and pricing; live demo routes. **Keep:** product-doc domains
(`docs.<vendor>`, `<project>.io`), project org repos, vendor articles
the repo links, model cards for headline models. Carry URLs
byte-for-byte — an equivalent-looking URL is a substitution; the only
edit is trimming trailing punctuation.

**Stack ↔ References agreement.** After drafting Technical details,
map every headline external component → `COVERED <url>` or `MISSING`.
Dedupe to one link per component. Re-check the harvest before
declaring a gap; a genuinely doc-less headline component is a reported
gap or `TODO: <component> documentation link` — never an invented URL,
and never a truthful component silently dropped to game coverage. The
one allowed addition: versionless canonical Red Hat docs for every Red
Hat platform or product the Solution Stack names (OpenShift, OpenShift
AI, Dev Spaces, AAP landing pages), even when the repo links none —
nothing else enters from general knowledge. When the repo links both a
product-doc page and a GitHub source mirror for a component, carry the
product-doc page.

**Documentation table** (when the repo ships ≥3 substantive user-facing
guides): fold into References as a final two-column table, real
repo-relative links, one line per guide from its own title and intro.
Include deploy/config/integration/ops/architecture guides; exclude
CONTRIBUTING-adjacent material, ADRs, agent-instruction files, test
internals, demo scripts. Cap at 6–8 rows; merge near-duplicates. Order
References: platform docs first, then stack components in Solution
Stack order, then the table. **Related content:** grep the repo's docs
for demo-video and blog links the repo itself carries (loom.com,
youtube, redhat.com/en/blog, developers.redhat.com) and list them as a
short related-content line beside the table — repo-linked only, never
invented, and never a substitute for the walkthrough.

**Repository structure tree.** The tree maps the deploy and the app,
not an inventory: a path earns a line only if a customer deploying or
using the quickstart needs to know it exists. Include install
machinery, deployed app roots, user docs/data/demo dirs, and root
entry files (Makefile, `.env.example`, Containerfile, package
manifests); mocks the deploy uses, labeled as mocks. Exclude
contributor/CI paths, lockfiles, generated and run artifacts, and the
inside of any component directory — the component is one line. Budget
8–15 entries (4–8 for a tiny repo), depth 2–3, ordered as the deploy
story reads. Annotate each entry with its role in ≤12 words — never
restating the name ("helm directory") and never a bare pointer ("see
docs"). Verify every printed path exists; the tree is factual content.

## 10. Reconcile conflicts once, globally

Before drafting, dedupe the ledger and resolve every CONFLICT with
these precedence rules, then never revisit:

- **Artifact beats summary**: chart/compose/script that runs beats a
  doc's prose about it; a doc's "e.g." list is examples, not behavior.
- **Strictest floor wins** per presented path; ceilings stay ceilings.
- **Scope, don't flatten**: a figure stated in an overlay or per-path
  guide belongs to that path only.
- **Deployed beats documented**: what the install renders decides the
  architecture; docs decide role names.
- A remaining disagreement between two equally-authoritative sources is
  carried scoped, with both values — never averaged or silently picked.

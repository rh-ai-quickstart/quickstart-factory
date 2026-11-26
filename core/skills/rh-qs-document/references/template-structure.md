# ai-quickstart-template — distilled structure

Source: https://github.com/rh-ai-quickstart/ai-quickstart-template (README.md).
The template's contributor TODOs are hard rules. Legend: REQUIRED /
RECOMMENDED / OPTIONAL.

## Head

- **H1 title** — REQUIRED. Max 64 chars. Phrased as an industry use case,
  e.g. "Protect patient data with LLM guardrails". Extracted for publication.
- **Short description** — REQUIRED. Max 160 chars, between the H1 and the
  Table of Contents. Describes the INDUSTRY use case. Extracted for
  publication.
- **Table of Contents** — RECOMMENDED. Links must match the actual sections.

## Detailed description

Three-part structure, in this order:

- **Problem subsection** — REQUIRED. H3 titled "The challenge" / "The problem
  we're solving" / a similar repo-appropriate variant. A few sentences (2–4)
  on the current industry problem the quickstart solves: who hits it, what it
  costs, why existing approaches fall short. Use-case framing, not technology.
  Be very concise and to the point — every sentence must earn its place; no
  throat-clearing, no restating the title.
- **Solution subsection** — REQUIRED. H3 titled "Our solution" or similar. A
  few sentences (2–4) on the **improvement** the quickstart delivers for the
  challenge: for each pain the challenge names, state what changes for the
  user — the before → after in their terms (who does what, how much effort,
  with what result), not a feature list. Only the details that change the
  reader's decision to deploy; everything else lives in Usage, Deploy, or
  Technical details. Write for one-pass clarity: plain words, short
  sentences, one statement each — the reader must grasp the improvement
  without re-reading. No component inventories here — tools belong in the
  solution-stack list under Technical details.
- **Architecture diagrams** — REQUIRED, in this order:
  1. A basic diagram of the quickstart's core/main architecture — image in
     `docs/images/`, descriptive hyphenated filename, alt text. If the repo
     ships a suitable main-architecture diagram, reference it. If not,
     GENERATE one: a self-contained, hand-authored, draw.io-editable SVG —
     the root `<svg>` carries the diagram model XML-escaped in its
     `content` attribute; the visible shapes are ordinary SVG (rounded
     rects for components, arrows for the main data flow, white
     background, box colors encoding the grouping — application core,
     architecture-bearing tools, external systems, optional
     alternatives — per the tier palette in
     `references/drawio-svg-format.md`) describing the same diagram as
     the model — saved as
     `docs/images/architecture-overview.drawio.svg` relative to the
     README's location, built and validated per
     `references/drawio-svg-format.md`. The picture is the APPLICATION
     SOLUTION, not the deployment graph: the end-user surfaces and
     application services that deliver the 1–3 headline features sit in
     the center; an architecture-bearing tool earns a box only where a
     feature journey crosses it; external systems sit at the canvas edge
     outside the cluster boundary; mocks, install machinery, and generic
     plumbing stay out. Every box is a component the repo actually
     deploys or an external system its wiring names; every label is
     repo-sourced — never invented. A box may carry a one-line feature
     sub-label naming the end-user capability it delivers, only
     repo-verbatim from the headline-feature inventory — no evidence, no
     label. Place the Red Hat logo at the BOTTOM of the canvas
     (bottom-right, bottom-left only on collision), present in both the
     visible SVG and the embedded model, per
     `references/drawio-svg-format.md`. Size the canvas to the picture:
     it fills the frame (≥ 85% width, ≥ 70% height), boxes and type
     share one scale, no text below 12px — a sparse picture afloat on
     an oversized canvas is a defect, not a style choice.

     Concise by construction — important details only: the main
     components on the marked main feature's journey and the main flow
     between them, nothing finer. No versions, ports, protocols, URLs,
     namespaces, config keys, resource sizes, or minor plumbing
     anywhere in the picture; a detail earns a box, a label, or an
     arrow only if the main journey stops making sense without it —
     everything else belongs in Technical details or Deploy. Only the
     main features earn space: target 5–10 content boxes (12 hard
     ceiling only when every box sits on a headline-feature journey),
     one box per component — never a second box for a component
     already drawn; skip per-step detail diagrams (those belong in
     Technical details, if used).
  2. A brief explanation below the image: 3–6 numbered steps, in
     journey order, walking the diagram's main flow from where it
     enters the system (the end user, or the external source the
     journey starts from) to the customer-visible outcome. Each step
     is ONE short sentence stating ONE action — actor → mechanism →
     destination, subject–verb–object, plain everyday verbs (collects,
     sends, stores, shows), at most 25 words (target ≤ 20); the
     destination may be a short "to/into" phrase or a single
     participle ("sending them to …"), never a second full clause. No
     appositives explaining what a component is, no subordinate or
     "and"-chained second actions — if a step does two things, split
     it into two steps; a qualifier survives only when removing it
     changes the outcome (e.g. "filtered by authorization"). Name
     components exactly as the picture does and never one it omits;
     no install steps.
- Extra narrative subsections (e.g. current manual process, workflow steps)
  — OPTIONAL, between solution and architecture, only when the repo's own
  story needs them. Keep customer-facing.

## Usage

- **The feature walkthrough ("See it in action")** — REQUIRED. A top-level
  `## Usage` section, immediately after Detailed description (which ends
  with the architecture diagrams) and before Requirements — not nested
  under Deploy. It shows the DEPLOYED quickstart in action; deployment
  itself lives in Deploy, so link forward to it, and open the section
  with one sentence saying so ("The walkthrough below shows the deployed
  quickstart in action — for deployment itself, see Deploy"). Title the
  section "Usage" (or "See it in action"). Walk through the 1–3 MAIN
  features — the CORE features of the application, surfaced by the UI
  when the repo offers one (UI screens first, then API endpoints, then
  CLI commands) and foregrounded by the repo's own docs or navigation,
  not every capability. A surface reachable only through an optional
  integration profile or a non-default values overlay is not a MAIN
  feature — it gets a labeled note with its enabling flag, never a
  walkthrough subsection. A MAIN feature is a journey with its own
  outcome — never a step inside another feature's arc: sub-features the
  main journey crosses appear as steps of its walkthrough, each with its
  screen, and get NO subsection of their own. One H3 subsection per MAIN
  feature, ordered by the user's journey.
- **Each walkthrough is a step-by-step screen progression, not an
  illustrated summary.** Narrate the arc as the user lives it — what
  they do, what changes on screen, what they get back — and every step
  that changes what the user sees carries its artifact: a repo
  screenshot (or its TODO) for a UI step, a fenced request+response or
  command+output pair for an API/CLI step. Prose alone never counts, for
  a step or for the flow; one artifact standing in for a multi-step
  journey is a defect — a step whose screen the repo does not ship gets
  its own TODO, and the walk continues. The artifact type follows the
  FEATURE's user-facing interface, precedence **UI > API > CLI** — and
  evidence availability never changes it:
  1. **UI feature** — the repo's screenshots mapped to the journey's
     steps (usually under `docs/images/`): harvest the whole pool and
     use every image matching a walked screen, ordered by the journey —
     progression states are the norm (selection screen → resulting
     list → detail view; list → expanded → drill-down; before/after of
     a toggle), with one–two sentences of prose between images
     narrating each state change ("After selecting the authorization
     class 'expert':"). Verify every referenced file exists before
     referencing it; a referenced-but-missing image is a defect. Alt
     text is a full sentence naming the shown state. When a walked
     step's screen has no repo screenshot, leave an explicit
     placeholder where the image belongs — one per missing step, never
     one TODO covering the whole journey: `TODO: add a screenshot of
     <exactly what the step's screen shows>, saved as
     docs/images/<descriptive-name>.png` — never reference or invent an
     image that isn't in the repo.
  2. **API feature — no UI exists** (the criterion is whether the app
     ships a user interface, not whether a screenshot is available) —
     a fenced text demonstration: the
     real request plus its real sample response (e.g. a `curl` call and
     the JSON it returns), sourced from the repo's docs, demo scripts,
     tests, or sample data; label reconstructed transcripts as such.
     When the repo has no sample response, `TODO: capture the real
     response of <request>` — never invent one.
  3. **CLI feature** — the real command plus its real sample
     output, fenced, from the same repo-sourced material; the same TODO
     fallback applies.
  **UI-reachable means UI-demonstrated.** If the user can perform the
  action in a UI, artifact type 1 applies — a screenshot or its TODO,
  never an API/CLI transcript in its place. A repo that ships BOTH a UI
  and REST endpoints still walks the UI: a transcript for a
  UI-reachable feature is at most a supplement beside the screenshot,
  never the walkthrough. A missing screenshot is a TODO, not a
  demotion to the easier-to-build curl demo.
  **Walk each journey once.** The same journey exposed on two surfaces
  (a web UI and a chat channel, an API and a ticketing integration) is
  walked on the primary surface with its images; the second surface
  gets a one-line cross-reference, never a second walkthrough of the
  same arc.
  Same evidence-gated policy as requirements values: every artifact is
  real and repo-sourced, or an explicit TODO naming what to capture.
  Repo demo links (Arcade, video) supplement the walkthrough; they
  never replace it. Keep the narration tight — one–two sentences per
  step, a walkthrough targeting ≤ ~25 lines per flow including image
  embeds — so the README's length budget holds.

## Requirements

- **Minimum hardware requirements** — REQUIRED. The floor needed to RUN
  the whole quickstart:
  - One line per category: CPU (cores), memory (GiB), storage (GiB), GPU
    (exact model — or "optional" + the condition that triggers it).
  - Scope the floor as the repo does ("on top of an existing OpenShift
    cluster", "Production: …"); say what drives the biggest number (e.g.
    model cache); keep a named storage class.
  - If the quickstart self-hosts a model, list its resource requirements
    separately; an external model endpoint (MaaS) needs no GPU — mark
    GPU-dependent extras "optional" with their trigger.
  - Every value comes from the repo itself or is `TODO: <what to fill
    in>` — never invented; node counts and "recommended" figures don't
    replace the rows.
- **Minimum software requirements** — REQUIRED. Only what the user MUST
  have to run the install — no nice-to-haves — each entry carrying the
  version the repo states (floor "4.20+", range "3.12–3.13", or exact pin,
  carried verbatim) or `TODO: <version>`. Three groups:
  1. **Red Hat platform**: OpenShift always; OpenShift AI when the solution
     uses it; other operators only when the install depends on them (GPU
     Operator, Serverless, AAP, …). Never "requires OpenShift AI" alone.
  2. **External services and credentials** it can't run without: model
     endpoint or hosted model, API tokens, licenses.
  3. **Client tools the install invokes**: `oc`, `helm`, `make`, plus
     `python` / `git` / `podman` / `jq` / `yq` / `uv` only when the
     Makefile or scripts call them.
  - Scope mode- or path-specific items to their mode (e.g. "Production:
    OpenShift 4.17+"); common items once, per-path additions scoped.
  - Omit dev conveniences and optional integrations (Slack, email, …).
- **Required user permissions** — REQUIRED and clear. Prefer regular user /
  namespace admin; cluster-admin only if absolutely necessary, with an
  explanation why.

## Deploy

- **Prerequisites** — access to platforms/clusters, CLI tools with version
  requirements, authentication/credentials, network access requirements.
- **Installation** — numbered, copy-pasteable steps, each explained. If a
  model is involved, offer: **Option A** bring your own endpoint (MaaS) via
  `--set model.name/endpoint/api_key`; **Option B** default model deployed by
  the chart (requires GPU). When using MaaS, test model access before
  deploying.
- **Validating the deployment** — check pod status, get the application
  route/URL, verify functionality, `helm test` if available. Once the
  deployment validates, walk the features in the Usage section.
- **Delete** — `helm uninstall` / repo's uninstall targets, optional project
  deletion, manual cleanup of secrets/PVCs. Users must be able to return to
  pre-deployment state.

## Repository structure

- Concise file tree of important directories and key files (`chart/`,
  `docs/`, application code). Don't list every file.

## References — RECOMMENDED, optional

Official documentation, blog posts, related quickstarts, partner docs.
Cover the stack: each headline external component in the solution stack
gets its product-doc or official project page, plus Red Hat platform docs
for the cluster / OpenShift AI the quickstart deploys onto. Remove the
section entirely if there is nothing to add.


## Technical details

- **Solution stack** — REQUIRED. Bullet list of the notable / lesser-known
  libraries and tools the quickstart uses — skip household names (e.g.
  FastAPI, PostgreSQL); each bullet: component name + one-line description
  of its role; never invent a component — every name comes from the repo.
  Every OpenShift AI component / capability the quickstart actually uses
  gets its OWN bullet (e.g. model serving, data science pipelines,
  workbenches, model registry); merge into one bullet only when very
  similar. The OpenShift AI bullets LEAD the list, most core first.
- **Features** — OPTIONAL. A bold-led bullet list of the end-user
  benefits the deployed quickstart delivers — one capability per bullet,
  each traceable to a pain named in the Challenge; a feature with no
  pain is cut, a pain with no feature means the Challenge oversold. Not
  a component inventory (Solution stack's job) and not a walkthrough
  (Usage's job). Include only when the repo surfaces benefits the Usage
  walkthrough doesn't already show; omit the subsection otherwise.
- **Technical depth** — OPTIONAL. How components work together,
  implementation details, model details (size, quantization, context
  window), API endpoints, performance characteristics. Technical depth
  lives here, not in the earlier sections.

## Tags — REQUIRED for publication

Bold-labeled block at the end:

- **Title:** must match the H1, ≤ 64 chars
- **Description:** must match the short description, ≤ 160 chars
- **Industry:** ONE catalog category, carried verbatim when the repo
  states its classification — observed values: "Adopt and scale AI",
  "Media and IT services"; don't coin a near-synonym
- **Product:** primary Red Hat product — "OpenShift AI" in every real
  quickstart; a second Red Hat platform only when load-bearing (e.g.
  "Ansible Automation Platform")
- **Use case:** optional; short comma-separated phrases, not sentences
  (e.g. "AI Operations, Observability, Monitoring")
- **Partner:** optional; a named third-party partner only (e.g. DagsHub)
- **Contributor org:** optional; the contributing organization(s), e.g.
  "Red Hat" or "Red Hat, DagsHub" default is "Red Hat"

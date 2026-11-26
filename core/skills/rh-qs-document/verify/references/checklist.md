# Verification checklist — every restriction from the template

Source of truth: the ai-quickstart-template rules as distilled in
`../../references/template-structure.md` (the rh-qs-document skill's
copy — identical rules). Every restriction below is scored 0–10 (one decimal allowed)
using the anchors in SKILL.md. Classes: REQUIRED (hard rule, weight 1.0),
CONDITIONAL (REQUIRED when its applicability rule fires, weight 1.0),
RECOMMENDED (weight 0.5), OPTIONAL (weight 0.25). Absence is N/A only
where the template source marks the section optional: all OPTIONAL
restrictions, plus the RECOMMENDED entry T23 (References). Every other
RECOMMENDED restriction (T05, T22) is scored 0 when absent. T08 is
REQUIRED by spec change: the official template marks "See it in action"
optional, but every real quickstart demonstrates usage, so the feature
walkthrough is mandatory (same tightening precedent as the
evidence-gated T11/T12/T14 requirements policy).

Judged from the README alone — no repository access, no network.

## Head

### T01 — H1 title present, ≤ 64 chars · REQUIRED
The document starts with a single H1 (`# `). Measure its length.
- 10: exactly one H1, ≤ 64 chars.
- ≤ 4 (hard-limit violation): H1 longer than 64 chars, or multiple H1s.
- 0: no H1.

### T02 — H1 phrased as an industry use case · REQUIRED
The H1 is a value-proposition sentence about an industry problem
(e.g. "Protect patient data with LLM guardrails"), not a product or
component name dump.
- 10: clear industry use case, verb-led or outcome-led.
- 7–8.9: use case identifiable but partially tech-named.
- 4–6.9: mostly component/product names with a hint of use case.
- ≤ 3: pure product/tech name(s).

### T03 — Short description present, ≤ 160 chars, positioned correctly · REQUIRED
A plain-text paragraph between the H1 and the ToC / first section.
Measure its length.
- 10: present, ≤ 160 chars, correctly positioned.
- ≤ 4: present but > 160 chars, or misplaced (after ToC, inside a
  section, or formatted as a heading/list).
- 0: absent.

### T04 — Short description describes the industry use case · REQUIRED
The short description is about the business/industry problem and
outcome, not a technology inventory.
- 10: industry use case + outcome.
- 7–8.9: use case with tech emphasis.
- 4–6.9: mostly stack description.
- ≤ 3: pure tech description or marketing filler.

### T05 — Table of Contents present · RECOMMENDED
- 10: ToC near the top (after the short description).
- 4–6.9: ToC present but deep in the document or malformed.
- 0: absent.

### T06 — ToC links match actual sections · RECOMMENDED
Every ToC entry resolves to a heading that exists; every major section
appears in the ToC. Verify mechanically (grep each anchor).
- 10: all links live, all major sections listed.
- 7–8.9: 1–2 dead/missing entries.
- 4–6.9: several dead or missing entries.
- ≤ 3: ToC bears little relation to the document.

## Detailed description

### T07 — Detailed description: 2–3 use-case paragraphs · REQUIRED
A "Detailed description" (or equivalent top-level narrative) section of
roughly 2–3 paragraphs expanding the USE CASE: business problem, how the
quickstart addresses it, key capabilities, real-world scenarios.
- 10: present, substantive, use-case-focused, multi-paragraph.
- 7–8.9: present and substantive but tech-heavy or poorly scoped.
- 4–6.9: present but thin (single paragraph or bullet list only).
- ≤ 3: absent or a stub.

### T08 — Usage / See it in action — feature walkthrough · REQUIRED
The "Usage" (or "See it in action") subsection, normally inside Deploy
after validation. A walkthrough of the 1–3 main features — UI screens,
CLI commands, API endpoints — each demonstrated by a real artifact: an
embedded screenshot with meaningful alt text, or a fenced
command/request plus its sample output. When the repo provides neither,
an explicit TODO placeholder naming exactly what to capture is
compliant (evidence-gated, same policy as requirements values). Prose
alone does not demonstrate. Demo links (Arcade, video) supplement; they
never satisfy this restriction by themselves.
- 10: every main feature has a real artifact (screenshot with alt text,
  or command/request + output pair) or a specific TODO placeholder
  naming the screenshot/output to add.
- 7–8.9: a feature has neither artifact nor placeholder, the
  placeholder is vague (doesn't say what to capture), or artifacts lack
  alt text.
- 4–6.9: usage content present but features described in prose only —
  no artifacts and no placeholders.
- ≤ 3: heading only; 0 if no Usage / See-it-in-action content at all.

### T09 — Architecture diagram present with alt text · REQUIRED
A markdown image (`![alt](path)`) in the Detailed description area.
- 10: image with meaningful alt text, descriptive filename, path under
  a docs/images-style directory (judge the path string; the file itself
  is not checkable).
- 7–8.9: image present; weak alt text or a vague filename/path.
- 4–6.9: image present, no alt text; or diagram referenced but not
  embedded.
- 0: no architecture diagram at all.

### T10 — Diagram explanation · OPTIONAL
N/A if absent. If present: a brief explanation below the image.
- 10: present and describes the flow/components. ≤ 4: stub.

## Requirements

### T11 — Minimum hardware requirements: present, structured, evidence-gated · REQUIRED
A "Minimum hardware requirements" subsection listing the categories CPU
cores, memory in GiB, GPU (model), and storage — each category carrying
either a concrete value or an explicit `TODO` placeholder (an unfilled
template row a human verifies on a real cluster). A vague statement that
is neither ("adequate resources") does not count.
- 10: all relevant categories present, every one valued or TODO'd, no
  vague filler.
- 7–8.9: one category missing, or one vague (non-TODO, non-value) entry.
- 4–6.9: only node counts, or "adequate resources" style statements with
  no category rows.
- ≤ 3: section absent, or a disclaimer instead of requirements.

### T12 — Whole-stack floor stated up front · REQUIRED
The floor row for the WHOLE quickstart (all charts combined) is stated in
the categories above, up front — not only a per-component table. Its
values may be concrete or TODO placeholders; the row must exist.
- 10: explicit whole-stack floor (valued or TODO'd).
- 7–8.9: floor derivable with slight ambiguity.
- 4–6.9: only per-component/per-chart numbers, no combined floor row.
- 0: no floor row at all.

### T13 — Model resource requirements / MaaS GPU note · CONDITIONAL
Applicability (deploy-path tiebreaker — the judgment rule is IDENTICAL
for T13 and T19): applicable only when the quickstart's DEPLOY path
itself serves or configures a model — a model or model-serving component
deployed by the chart (e.g. a vLLM/llm-d-style serving chart), or a MaaS
endpoint configured at deploy time (`--set model.*`-style values, an LLM
API key consumed by the deployed application). Educational or tutorial
usage of external LLM services — tutorial notebooks, optional workbench
content, post-deploy UI configuration — does NOT count: N/A. Judge from
the README's own deploy instructions, not from its background material.
- If a model is deployed by the quickstart: 10 when the model's
  resource requirements are listed separately from the platform floor;
  4–6.9 when merged into the general table only; ≤ 3 when absent.
- If MaaS (external endpoint): 10 when the README states no GPU is
  required (and lists optional GPU-dependent components if any);
  4–6.9 when the GPU situation is merely implicit; ≤ 3 when it
  wrongly implies a GPU is needed.

### T14 — Minimum software requirements: present, complete, evidence-gated · REQUIRED
A "Minimum software requirements" subsection listing the required items:
OpenShift and OpenShift AI, operators/platform dependencies, and client
tools (`oc`, `helm`, plus any others the install invokes). Every entry
carries either a SPECIFIC version or an explicit `TODO` placeholder —
a bare name with neither is the failure mode (an unfilled row is
correct output; a guessed version is not).
Mechanical count required in the evidence: N entries version-pinned or
TODO'd vs M bare names (neither version nor TODO), and the core items
(OpenShift, OpenShift AI, `oc`, `helm`) present — count the list, never
eyeball it.
- 9–10: M = 0 and all core items listed.
- 7–8.9: M = 1, or one core item missing.
- 5–6.9: M = 2–3.
- ≤ 4.9: M ≥ 4.
- ≤ 3: section absent, or "requires OpenShift AI" with no item rows.
A bare `oc` or `helm` entry counts as two bare entries (the template
names these tools explicitly).

### T15 — Version discipline: floors and ceilings as stated · REQUIRED
Where the README states version bounds, they are well-formed: ranges
kept as ranges (e.g. "3.12–3.13", not loosened to "3.12+"), mode-scoped
floors labeled with their mode (e.g. "Production mode: OpenShift 4.17+"),
no loosening of a "tested with" pin. Entries left as TODO placeholders
are correct treatment for values the repo doesn't state and do not
lower this score.
- 10: all stated bounds well-formed and scoped (a fully TODO'd list with
  no stated bounds also scores 10 — nothing stated, nothing mis-stated).
- 7–8.9: one loose or unscoped bound.
- 4–6.9: several loosened/unscoped bounds.
- 0: no version bounds stated anywhere (if T14 scored ≥ 7, this cannot
  be 0 — rescore).

### T16 — Required user permissions · REQUIRED
A "Required user permissions" subsection. Prefers regular user /
namespace admin; cluster-admin only with an explanation of why.
- 10: present, specific role, correct preference.
- 7–8.9: present, role named, minor gaps.
- 4–6.9: present but vague ("appropriate permissions").
- ≤ 3: absent.

## Deploy

### T17 — Prerequisites · REQUIRED
A prerequisites block: platform/cluster access, CLI tools with
versions, authentication/credentials, network access requirements.
- 10: all four covered.
- 7–8.9: three covered.
- 4–6.9: one or two only.
- ≤ 3: absent.

### T18 — Installation steps: numbered and copy-pasteable · REQUIRED
Numbered, copy-pasteable steps, each with a short explanation — not a
bare wall of commands and not prose without commands.
- 10: numbered steps + commands + per-step explanation.
- 7–8.9: steps present, explanation sparse.
- 4–6.9: commands present but unstructured/unexplained.
- ≤ 3: no real installation instructions.

### T19 — Model options A/B · CONDITIONAL
Applicability: IDENTICAL rule to T13 (deploy-path tiebreaker) — applies
only when the DEPLOY path itself serves or configures a model
(chart-deployed model/serving component, or a MaaS endpoint set at
deploy time via `--set model.*` or an LLM API key consumed by the
deployed application); tutorial/educational use of external LLM services
with no deploy-time model decision → N/A.
- 10: both paths offered — Option A bring-your-own endpoint (MaaS) via
  `--set model.name/endpoint/api_key`-style values, Option B default
  model deployed by the chart (GPU noted) — and the README says to test
  model access before deploying when using MaaS.
- 7–8.9: both paths offered, MaaS pre-test missing.
- 4–6.9: only one path offered.
- ≤ 3: neither offered despite a model being involved.

### T20 — Validating the deployment · REQUIRED
A validation section: pod status checks, retrieving the route/URL,
verifying functionality, `helm test` where available.
- 10: all relevant checks with commands.
- 7–8.9: most checks.
- 4–6.9: minimal validation (route only).
- ≤ 3: absent.

### T21 — Delete / cleanup · REQUIRED
Uninstall commands (`helm uninstall` or repo targets), optional project
deletion, and manual cleanup of secrets/PVCs — the user can return to
pre-deployment state.
- 10: uninstall + PVC/secret cleanup covered.
- 7–8.9: uninstall covered, cleanup partial.
- 4–6.9: uninstall command only.
- ≤ 3: absent.

## Structure and optional sections

### T22 — Repository structure · RECOMMENDED
Absent → scored 0 (same treatment as T05: the template source does not
mark this section optional or removable). If present:
- 10: concise tree of key directories/files, not exhaustive.
- 7–8.9: slightly over- or under-detailed.
- 4–6.9: exhaustive file dump or near-empty.
- ≤ 3: heading only.

### T23 — References cover the stack · RECOMMENDED
N/A if the section is entirely absent (allowed — the template source
says "Remove the section entirely if there is nothing to add"). If
present, score by a mechanical coverage count: N_named = headline stack
components the README itself names in its stack/architecture; N_cov =
how many of those carry an official product/project doc link.
- 9–10: N_cov/N_named ≥ 80% and Red Hat platform docs (OpenShift /
  OpenShift AI) present — 10 only when both are complete.
- 7–8.9: about half of the named components covered.
- 4–6.9: few covered — platform docs only, or 1–2 component links.
- ≤ 3.9: repo-internal or generic links only (N_cov = 0 and no platform
  docs), or filler links unrelated to the stack.

### T24 — Technical details · OPTIONAL
N/A if absent. If present: model details (size, quantization, context
window), API endpoints, performance characteristics — and the deep
technical content lives HERE rather than in the earlier sections.
- 10: present, substantive, correctly placed.
- 7–8.9: present but thin, or some deep detail leaked into earlier
  sections.
- 4–6.9: heading-level only.

### T25 — Section order follows the template · REQUIRED
(Class derives from rubric D1 — "Required sections present, in template
order" — and the template README's fixed layout; template-structure.md
states it implicitly.)
Order: Head → Detailed description → Requirements → Deploy →
Repository structure → References → Technical details → Tags.
- 10: exact order.
- 7–8.9: minor deviation (e.g. one optional section out of place, or
  auxiliary subsections like Usage nested under Deploy).
- 4–6.9: major reordering (e.g. Deploy before Requirements).
- ≤ 3: no recognizable template order.

### T26 — No invented top-level sections · REQUIRED
(Class derives from rubric D1 — "no invented top-level sections" — and
the template README's fixed section set.)
No top-level sections outside the template set. Commonly accepted
auxiliary sections (Usage, Troubleshooting, License, Contributing,
Security) are tolerated at a minor cost; sections that displace template
content (standalone "Documentation", "FAQ", marketing blurbs) are
violations.
- 10: only template sections (+ tolerated auxiliaries).
- 7–8.9: one tolerated-but-nonstandard auxiliary section.
- 4–6.9: off-template sections that duplicate/displace template
  content.
- ≤ 3: document structure dominated by non-template sections.

## Tags

### T27 — Tags block present, bold-labeled, at the end · REQUIRED
A bold-labeled block (`**Title:** …`) at the end of the document.
- 10: present, bold labels, at the end.
- 7–8.9: present but not last, or labels not bold.
- 4–6.9: present but malformed (plain list, table).
- 0: absent.

### T28 — Tags Title matches the H1, ≤ 64 chars · REQUIRED
Measure both; compare verbatim (case and punctuation included).
- 10: exact match (or trivially identical), within limit.
- ≤ 4 (hard-rule violation): mismatch in wording, or over 64 chars.
- 0: Tags Title missing.

### T29 — Tags Description matches the short description, ≤ 160 chars · REQUIRED
Measure both; compare verbatim.
- 10: match (identical or trivially identical), within limit.
- ≤ 4: mismatch or over 160 chars.
- 0: Tags Description missing.

### T30 — Tags Industry: one value · REQUIRED
Score FORM only: `**Industry:**` present, exactly one value. Do NOT
judge whether a value "is an industry" — the template's controlled
vocabulary lives in CONTRIBUTING.md, outside your evidence universe
(README-only, no network). Values the published catalog itself uses are
acceptable, e.g. "Adopt and scale AI", "Media and IT services",
Healthcare, Retail, Financial Services, Technology,
Telecom/Telecommunications, IT (Services/Operations).
- 10: present, exactly one value (including known catalog values).
- 7–8.9: a single value that reads as a non-industry descriptor — minor
  deduction only; a single present value never scores below 7.
- 4–6.9: multiple values, or a compound of two sectors that is not a
  known catalog value.
- ≤ 3: the Industry label missing entirely.

### T31 — Tags Product: primary Red Hat product · REQUIRED
- 10: one primary Red Hat product (e.g. OpenShift AI); a second Red Hat
  platform only when it is load-bearing in the README's own solution
  stack.
- 7–8.9: two Red Hat platforms where the second is peripheral.
- 4–6.9: product list that includes non-Red-Hat items as "Product".
- ≤ 3: missing.

### T32 — Tags Use case / Partner used correctly · OPTIONAL
N/A if both absent. If present:
- 10: Use case is a short descriptor; Partner names a genuine
  third-party partner (Red Hat alone is the vendor, not a Partner).
- 4–6.9: one of them misused.
- ≤ 3: Partner set to Red Hat / a non-partner, or labels invented
  beyond the template set and the published-quickstart conventions
  (`Contributor org` / `Contributing org` are accepted house labels —
  real published quickstarts carry them; genuinely coined labels, e.g.
  "Author", are invented). "≤ 3" is a hard
  ceiling: at most 3.0 — a 3.5 is never valid when an invented label is
  present.

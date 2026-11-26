---
name: rh-qs-verify
description: Score a Red Hat AI Quickstart README.md against every template restriction — one 0-10 score per restriction plus a weighted overall score. Use when verifying or checking a quickstart README's template compliance.
---

# rh-qs-verify — quickstart README template verifier

You are a template-compliance verifier for Red Hat AI Quickstart READMEs.
Input: ONE `README.md`, judged as a standalone artifact. Output: a JSON
report with a 0–10 score for every template restriction and a weighted
overall score.

## Scope — what you verify

The restrictions are enumerated in `references/checklist.md` (in this
directory, beside this file — the verifier is bundled inside the
rh-qs-document skill at `verify/`). Every restriction has an ID (T01…T32), a class
(REQUIRED / RECOMMENDED / OPTIONAL / CONDITIONAL), an applicability rule,
and scoring guidance. You score ALL of them; where the rule says N/A you
set `applicable: false` instead of a score.

You verify TEMPLATE COMPLIANCE ONLY: structure, presence, specificity,
hard limits, and internal consistency (ToC vs actual headings, Tags block
vs H1 / short description). You do NOT verify factual claims against a
repository — never open repository source, charts, or docs, and never use
the network. The README is the entire universe of evidence.

## Procedure

1. Read `references/checklist.md` completely before scoring anything.
2. Read the target README once, fully.
3. Run the mechanical measurements (below) with Bash. Never eyeball a
   countable property — record the measured number in the evidence.
4. Score each restriction 0–10 (one decimal allowed) per the anchors.
   Every score requires verbatim evidence: a quoted line (with its
   heading context) or a measurement. A score without quoted evidence is
   invalid — rescore it.
5. Compute the overall score with the python3 one-liner under
   "Mechanical measurements" (never in your head) and write the JSON
   report to the output path given in your invocation.

## Mechanical measurements (mandatory, via Bash)

- H1: the first `# ` line. Measure its character count
  (`awk '/^# /{print length($0)-2; exit}' FILE`).
- Short description: the paragraph between the H1 and the next heading.
  Measure its character count.
- ToC → heading match: list every `## `/`### ` heading; for each ToC
  link target, check the heading exists; report dead targets and major
  headings missing from the ToC.
- Tags Title vs H1, Tags Description vs short description: compare them
  character by character and report any differences.
- Top-level section list: all `## ` headings, in order.
- Overall score: computed with python3, never mental math. After
  drafting the report JSON, run this against it and paste the printed
  number into `overall`:

  ```
  python3 -c "import json,sys; d=json.load(open(sys.argv[1])); rs=[r for r in d['restrictions'] if r['applicable']]; w={'REQUIRED':1.0,'CONDITIONAL':1.0,'RECOMMENDED':0.5,'OPTIONAL':0.25}; print(round(sum(r['score']*w[r['class']] for r in rs)/sum(w[r['class']] for r in rs),1))" REPORT.json
  ```

  A ~30-term weighted mean is a countable property — never eyeball it.
  Re-run the command after ANY score change: an adjusted score
  invalidates the previously computed overall.

## Scoring anchors (apply to every restriction)

| Score | Meaning |
|---|---|
| 9–10 | Fully compliant; evidence is exact |
| 7–8.9 | Compliant with a minor issue |
| 4–6.9 | Present but materially deficient |
| 1–3.9 | Token / stub presence only |
| 0–0.9 | Absent, or violates a hard rule |

Hard numeric limits (H1 ≤ 64 chars, short description ≤ 160 chars, Tags
Title matching the H1, Tags Description matching the short description)
are pass/fail: any violation caps that restriction at 4.

## Applicability

- OPTIONAL restrictions that are simply absent → `applicable: false`
  (absence is allowed). If present, they are scored normally —
  present-but-bad may score lower than an absent N/A; that is correct.
- RECOMMENDED restrictions: absent → N/A only where the checklist entry
  says the template source marks the section optional (T08 "See it in
  action", T23 References). Otherwise (T05 ToC, T22 Repository
  structure) absence is a deviation and scores 0.
- CONDITIONAL restrictions → apply the checklist's applicability rule,
  judged from the README alone, and record the judgment in `rationale`.
- Never mark a REQUIRED restriction N/A because "this repo probably
  doesn't need it" — the template's REQUIRED items are hard rules.

## Overall score

Weighted mean over applicable restrictions only:

- REQUIRED — weight 1.0
- CONDITIONAL (applicable) — weight 1.0
- RECOMMENDED — weight 0.5
- OPTIONAL (present and scored) — weight 0.25

Round to one decimal. `applicable: false` restrictions are excluded
entirely.

## Report format

Write valid JSON (no trailing commas) to the output path:

```json
{
  "file": "<README path as given in the invocation>",
  "restrictions": [
    {
      "id": "T01",
      "name": "H1 title present, ≤ 64 chars",
      "class": "REQUIRED",
      "applicable": true,
      "score": 10,
      "evidence": "H1 = \"Protect patient data with LLM guardrails\" — 38 chars (measured)",
      "rationale": "Within the 64-char hard limit."
    },
    {
      "id": "T08",
      "name": "Usage / See it in action — feature walkthrough",
      "class": "REQUIRED",
      "applicable": true,
      "score": 10,
      "evidence": "'### Usage' with 2 feature subsections; each has an embedded screenshot with alt text or a fenced command+output pair.",
      "rationale": "2–3 main features, each demonstrated by a real artifact."
    }
  ],
  "overall": 8.4,
  "verdict": "One line: the biggest compliance gaps."
}
```

Rules:

- `score` is `null` exactly when `applicable` is `false`.
- Quote evidence verbatim — do not paraphrase. For measurements, give
  the number.
- Do NOT trust the Table of Contents as evidence that a section exists;
  the section body itself must be present in the document.
- One report per README. Do not modify any file except your output JSON.

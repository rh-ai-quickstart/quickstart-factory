# Writing style — Red Hat AI Quickstart house voice

This file owns three things: how the prose sounds (voice), how the README
unfolds (narrative pattern), and how long it runs (length budget). What
each section contains is `template-structure.md`; where every fact comes
from is `evidence-hunting.md` and the SKILL.md invariants — where a rule
here touches their ground, they win. The house voice in action:
`example-readme.md` — match its tone, never copy its content.

## Core principle

Write so a busy customer can decide and deploy on one read. Every
sentence either helps them decide — which pain this removes, what it
costs, what it delivers — or helps them act — the exact next command.
A sentence that does neither is cut.

## Voice — one expert talking to one customer

The reader is a customer deciding whether to deploy, never a contributor.

- Address them as "you"; present tense; active voice with a named actor.
  Reserve "the user" for the people the deployed product serves.
- Concrete outcomes over adjectives. "The agent routes each error to the
  expert authorized to fix it, cutting mean time to resolution (MTTR)"
  earns its line; "dramatically improves operational efficiency" does
  not. If a rival quickstart could print the same sentence, rewrite it.
- Never amplify the repo's claims. State the problem in the repository's
  own terms; do not upgrade a workflow annoyance into regulatory threat,
  penalty, or lost revenue the repo never mentions. A technical buyer
  reads inflation as sales talk; restraint is the house style.
- Plain words: "use" over "utilize", "build" over "orchestrate". Write
  the real name — command, component, screen label — never a synonym,
  and one name per concept: never rotate "the agent / the assistant /
  the bot".
- No marketing filler: "seamless", "powerful", "cutting-edge", "robust",
  "simply", "easy", "leverage", "unlock", "empower". No throat-clearing:
  open each section on its point, never restating the title or the
  previous paragraph.

## Sentence craft

- One statement per sentence; split anything past ~20 words in an
  instruction, ~25 in prose. Action in a verb: "classifies each error",
  not "performs classification of each error".
- Conditions before the step they guard, and say what the reader gets
  back. Before: "Run `oc get routes`." After: "Run `oc get routes` to
  get the URL of the running application."
- Warnings precede the step they guard, as their own line — never a
  trailing clause the reader meets too late.
- Vary sentence length; let a short sentence land the point. Bullets are
  parallel: same grammatical form, one idea each.

## Narrative pattern — the persuasion arc

The Detailed description is one argument in three movements; each answers
the one before it, so the reader wants the outcome before being asked to
install anything.

1. **Challenge** — who feels the problem and what it costs them today
   (hours, headcount, errors, delay), in operational terms. Two to four
   sentences; make the reader recognize their own week.
2. **Manual process** — today's steps walked one at a time, present
   tense, in the order a person performs them, so the reader feels the
   toil instead of being told about it. Use it only when the repo tells
   a manual-workflow story; never invent one.
3. **Our solution** — the improvement, point for point: each pain the
   Challenge named gets its before → after in the user's terms — what
   they stop doing by hand, what gets done for them, what they get back.
   Outcome first; components only as far as they explain the mechanism.
   Only decision-relevant detail, plain short sentences; a sentence that
   does not state an improvement the reader can feel is cut.

Close the arc with the machine: the architecture explanation is a
numbered data-flow walkthrough — each step names the component and what
it does with the data, in the order the data moves. Start at the end
user, not at the install, and end at the customer-visible outcome; the
steps narrate the same edges the picture draws, never a component the
picture omits. Feature labels name capabilities; the steps explain
flow — do not repeat one as the other. No Features list in
the narrative: the bold-led features bullets live under Technical
details (template-structure.md), never between Our solution and the
architecture.

## Show, don't summarize

- Walk the primary interaction end-to-end with the repo's real nouns —
  the actual options offered, the actual input, the artifact produced.
  "You can also configure various settings" is a summary; "select the
  cluster-admin role, then filter alerts by `cluster_name`" is a
  demonstration.
- In a UI walkthrough, the screenshots carry the cadence: one–two
  sentences of prose between images narrate the state change ("After
  selecting the authorization class 'expert':") — never a caption
  restating the previous image, never filler between two resting
  screens. Alt text is a full sentence naming the shown state ("Log
  summaries filtered by expert authorization"), not a label
  ("screenshot"); a caption a rival quickstart could print under its
  own screenshot is cut.
- A second scenario earns its lines only by producing a visibly
  different outcome and sitting outside the main journey — re-walking a
  step of it is not a scenario; the same scenario reworded is padding.
  The same journey on a second surface is a cross-reference, not a
  second walkthrough.

Each later section keeps a distinct job and tone. Usage is the promise
made real: one end-to-end journey from the customer's point of view —
sub-features along the journey are covered as its steps, never
re-walked as separate scenarios.
Deploy is the trust test: procedural, calm, no selling, every step's
success visible.

## Length budget

- Target 150–250 lines; ~300 is the ceiling. Count the draft's lines
  before finishing — over budget is a defect, not a style choice.
- The gold example demonstrates the voice, not a length to imitate.
- When over budget, the fix is referral, not compression of substance:
  cut the deepest material first (per-component resource tables,
  configuration inventories, patch snippets, full file trees), keep the
  line that changes the deploy outcome, and link the repo's own guide.
- Usage walkthroughs are budgeted like everything else: one–two
  narration sentences per step with the image embeds included, a flow
  targeting ≤ ~25 lines. When over budget, trim walkthrough steps
  (fewer, more decisive screens) — never collapse a flow to prose-only,
  which trades a demonstrated journey for a summary.

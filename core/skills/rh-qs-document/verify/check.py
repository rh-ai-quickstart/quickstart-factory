#!/usr/bin/env python3
"""rh-qs-verify live checker — deterministic code implementation of the
rh-qs-verify skill (core/skills/rh-qs-document/verify/SKILL.md +
references/checklist.md).

Scores a Red Hat AI Quickstart README against the 32 template restrictions
(T01–T32), 0–10 each, and computes the weighted overall with the same
weights as the skill: REQUIRED/CONDITIONAL 1.0, RECOMMENDED 0.5,
OPTIONAL 0.25; N/A excluded. Output JSON matches the skill's schema.

Countable restrictions (character limits, ToC anchors, Tags matching,
section order) are exact. Judgment-band restrictions use deterministic
heuristics calibrated against the validated round-2 agent reports.

Usage:
    python3 check.py README.md                 # prints JSON to stdout
    python3 check.py README.md -o report.json  # writes JSON to a file
    python3 check.py --selftest                # synthetic-README sanity tests
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

WEIGHTS = {"REQUIRED": 1.0, "CONDITIONAL": 1.0, "RECOMMENDED": 0.5, "OPTIONAL": 0.25}

TEMPLATE_ORDER = [
    "detailed description", "requirements", "deploy",
    "repository structure", "references", "technical details", "tags",
]
ALLOWED_TOP_LEVEL = set(TEMPLATE_ORDER) | {
    "table of contents", "contents", "overview", "see it in action",
    "usage", "troubleshooting", "license", "contributing", "security",
    "architecture", "architecture diagrams", "next steps", "conclusion",
    "summary", "what you have accomplished", "glossary",
}

MODEL_DEPLOY_KEYS = [
    "--set model", "model.name", "model endpoint", "model serving", "vllm",
    "modelmesh", "maas", "openai-compatible", "openai compatible",
    "inference endpoint", "deployed model", "serving runtime", "model runtime",
    "llm-d", "kserve", "default model", "hf_token", "inferenceservice",
]
# subsections under Deploy whose content is usage/tutorial, not deployment
USAGE_SUBSECTION = re.compile(r"usage|tutorial|walkthrough|demo|troubleshoot|"
                              r"next steps|what you|see it|delete|uninstall|"
                              r"clean ?up|teardown|validat", re.I)
NON_TOOL_HINTS = [
    "access", "account", "credential", "subscription", "network",
    "cluster with", "permission", "role", "login", "sign",
]
BUSINESS_WORDS = [
    "help", "team", "organization", "organisation", "business", "reduce",
    "accelerate", "improve", "faster", "efficiency", "productivity",
    "scale", "protect", "troubleshoot", "resolve", "monitor", "analyze",
    "analyse", "identify", "action", "workflow", "process",
]
VERB_WORDS = [
    "protect", "accelerate", "automate", "analyze", "analyse", "monitor",
    "troubleshoot", "summarize", "summarise", "detect", "resolve",
    "simplify", "scale", "build", "create", "deploy", "improve",
    "streamline", "empower", "enable", "deliver", "gain", "boost",
]


# ---------------------------------------------------------------- parsing


def github_anchor(text: str) -> str:
    """GitHub-style heading anchor."""
    a = text.strip().lower()
    a = re.sub(r"[^\w\s-]", "", a)
    return re.sub(r"\s", "-", a)


class Doc:
    def __init__(self, text: str):
        self.lines = text.splitlines()
        self.text = text

        # fenced-code-block line indices (headings inside fences are prose)
        self.in_fence = set()
        fence = False
        for i, ln in enumerate(self.lines):
            if ln.lstrip().startswith("```"):
                fence = not fence
                self.in_fence.add(i)
            elif fence:
                self.in_fence.add(i)

        self.h1 = None            # (text, line_idx)
        self.h1_count = 0
        self.headings = []        # (level, text, line_idx)
        for i, ln in enumerate(self.lines):
            if i in self.in_fence:
                continue
            m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", ln)
            if m:
                level, t = len(m.group(1)), m.group(2).strip()
                self.headings.append((level, t, i))
                if level == 1:
                    self.h1_count += 1
                    if self.h1 is None:
                        self.h1 = (t, i)

        # top-level sections: "## name" -> body text (ALL lines until the
        # next heading of any level, including sub-heading lines)
        self.sections = {}        # lower name -> (title, body, line_idx)
        self.section_order = []   # lower names in document order
        cur = None
        buf = []
        for i, ln in enumerate(self.lines):
            if i in self.in_fence:
                if cur is not None:
                    buf.append(ln)
                continue
            m = re.match(r"^(#{1,6})\s+", ln)
            if m and len(m.group(1)) == 2:
                if cur is not None:
                    title, _, idx = self.sections[cur]
                    self.sections[cur] = (title, "\n".join(buf), idx)
                title = re.sub(r"^##\s+", "", ln).strip()
                cur = title.lower()
                self.section_order.append(cur)
                self.sections[cur] = (title, "", i)
                buf = []
            elif cur is not None:
                buf.append(ln)
        if cur is not None:
            title, _, idx = self.sections[cur]
            self.sections[cur] = (title, "\n".join(buf), idx)

        self.short_desc = self._short_description()

    def _short_description(self) -> str:
        if self.h1 is None:
            return ""
        start = self.h1[1] + 1
        end = None
        for level, t, i in self.headings:
            if i > start:
                end = i
                break
        chunk = self.lines[start:end]
        paras, cur = [], []
        for ln in chunk:
            if ln.strip():
                cur.append(ln.strip())
            elif cur:
                paras.append(" ".join(cur))
                cur = []
        if cur:
            paras.append(" ".join(cur))
        return paras[0] if paras else ""

    def find_section(self, *keywords) -> tuple[str, str] | None:
        """First '##' section whose name contains any keyword; falls back to
        the first '###'/'####' subsection heading matching a keyword."""
        for name in self.section_order:
            if any(k in name for k in keywords):
                return self.sections[name]
        for level, t, i in self.headings:
            if level in (3, 4) and any(k in t.lower() for k in keywords):
                nxt = next((i2 for l2, t2, i2 in self.headings if i2 > i), len(self.lines))
                body = "\n".join(self.lines[i + 1:nxt])
                return t, body
        return None

    def toc_block(self) -> str:
        sec = self.find_section("table of content", "contents")
        return sec[1] if sec else ""

    def images(self) -> list[tuple[str, str]]:
        """(alt, path) for markdown and HTML images in the document."""
        out = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", self.text)
        for tag in re.findall(r"<img\s[^>]*>", self.text):
            src = re.search(r'src="([^"]+)"', tag)
            alt = re.search(r'alt="([^"]*)"', tag)
            if src:
                out.append((alt.group(1) if alt else "", src.group(1)))
        return out


# ---------------------------------------------------------------- helpers


def clamp(x: float) -> float:
    return round(max(0.0, min(10.0, x)), 1)


def list_items(body: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^\s*(?:[-*]|\d+[.)])\s+(.+)$", body, re.M)]


def count_links(body: str) -> int:
    return len(re.findall(r"\[[^\]]+\]\((https?://[^)]+)\)", body))


class Checker:
    def __init__(self, path: str):
        self.path = path
        self.doc = Doc(Path(path).read_text(encoding="utf-8", errors="replace"))
        self.results = []

    def add(self, tid, name, cls, applicable, score, evidence, rationale):
        self.results.append({
            "id": tid, "name": name, "class": cls,
            "applicable": applicable,
            "score": None if not applicable else clamp(score),
            "evidence": evidence, "rationale": rationale,
        })

    # ---- applicability shared by T13/T19: does the DEPLOY path serve a model?
    def model_in_deploy(self) -> tuple[bool, str]:
        # Scope: the whole Deploy body minus usage/tutorial subsections
        # (option-style install subsections must stay in scope) + hardware.
        scopes = []
        deploy = self.doc.find_section("deploy", "installation", "install", "quick start", "getting started")
        if deploy:
            idx = None
            for name in self.doc.section_order:
                if self.doc.sections[name][0] == deploy[0]:
                    idx = self.doc.sections[name][2]
                    break
            end = next((i2 for l2, t2, i2 in self.doc.headings if l2 == 2 and i2 > (idx or 0)),
                       len(self.doc.lines))
            subs = [(t, i) for l, t, i in self.doc.headings
                    if l >= 3 and idx is not None and idx < i < end]
            body_lines = self.doc.lines[idx + 1:end] if idx is not None else deploy[1].splitlines()
            if subs:
                drop = set()
                for t, i in subs:
                    if USAGE_SUBSECTION.search(t):
                        nxt = next((i2 for l2, t2, i2 in self.doc.headings if i2 > i), end)
                        drop.update(range(i + 1, nxt))
                body_lines = [ln for j, ln in enumerate(self.doc.lines[idx + 1:end], start=idx + 1)
                              if j not in drop]
            scopes.append("\n".join(body_lines))
        hw = self.doc.find_section("hardware")
        if hw:
            scopes.append(hw[1])
        # tutorial/notebook lines are NOT deploy-time model configuration
        keep = [ln for sc in scopes for ln in sc.splitlines()
                if not re.search(r"tutorial|notebook|walkthrough|stage \d", ln, re.I)]
        blob = "\n".join(keep).lower()
        hits = [k for k in MODEL_DEPLOY_KEYS if k in blob]
        llm_anywhere = bool(re.search(r"\bllm\b|large language model", self.doc.text, re.I))
        # Model involved at deploy time only if deploy/hardware sections carry
        # model-configuration keys (tutorial/usage-only LLM mentions do not count).
        applicable = bool(hits)
        ev = f"deploy/hardware model keys (usage/tutorial excluded): {hits or 'none'}; LLM mentioned anywhere: {llm_anywhere}"
        return applicable, ev

    # ------------------------------------------------------------ checks

    def t01(self):
        if self.doc.h1 is None:
            self.add("T01", "H1 title present, ≤ 64 chars", "REQUIRED", True, 0, "No H1 heading found.", "Absent.")
            return
        n = len(self.doc.h1[0])
        ev = f"H1 = \"{self.doc.h1[0]}\" — {n} chars (measured)"
        if n <= 64 and self.doc.h1_count == 1:
            self.add("T01", "H1 title present, ≤ 64 chars", "REQUIRED", True, 10, ev, "Single H1, within the 64-char hard limit.")
        else:
            why = "over the 64-char hard limit" if n > 64 else f"{self.doc.h1_count} H1 headings"
            self.add("T01", "H1 title present, ≤ 64 chars", "REQUIRED", True, 3, ev, f"{why} — hard-limit violation caps at 4.")

    def t02(self):
        if self.doc.h1 is None:
            self.add("T02", "H1 phrased as an industry use case", "REQUIRED", True, 0, "No H1.", "Absent.")
            return
        h = self.doc.h1[0].lower()
        verb = any(re.search(rf"\b{v}\b", h) for v in VERB_WORDS)
        prep = bool(re.search(r"\b(with|for|in|across|using)\b", h))
        techish = bool(re.search(r"^(a |an |the )?[a-z0-9 .+-]+$", h)) and not verb and not prep
        score = 10 if (verb or prep) else (7.5 if not techish else 5)
        ev = f"H1 = \"{self.doc.h1[0]}\""
        self.add("T02", "H1 phrased as an industry use case", "REQUIRED", True, score, ev,
                 "Verb/outcome-led phrasing." if score >= 9 else "Partially tech-named; use case identifiable." if score >= 7 else "Mostly component names.")

    def t03(self):
        sd = self.doc.short_desc
        n = len(sd)
        if not sd:
            self.add("T03", "Short description present, ≤ 160 chars, positioned correctly", "REQUIRED", True, 0, "No paragraph between H1 and the first heading.", "Absent.")
            return
        ev = f"Short description ({n} chars, measured): \"{sd[:80]}{'…' if n > 80 else ''}\""
        if n <= 160:
            self.add("T03", "Short description present, ≤ 160 chars, positioned correctly", "REQUIRED", True, 10, ev, "Present, within the 160-char limit, correctly positioned.")
        else:
            self.add("T03", "Short description present, ≤ 160 chars, positioned correctly", "REQUIRED", True, 3, ev, f"{n} chars — over the 160-char hard limit, capped at 4.")

    def t04(self):
        sd = self.doc.short_desc.lower()
        if not sd:
            self.add("T04", "Short description describes the industry use case", "REQUIRED", True, 0, "No short description.", "Absent.")
            return
        hits = [w for w in BUSINESS_WORDS if w in sd]
        n = len(self.doc.short_desc)
        if hits:
            score = 10
        elif n >= 90:
            score = 9
        elif n >= 50:
            score = 7.5
        else:
            score = 6
        ev = f"outcome vocabulary in short description: {hits[:6] or 'none'}; {n} chars"
        self.add("T04", "Short description describes the industry use case", "REQUIRED", True, score, ev,
                 "Outcome-focused." if score >= 9 else "Tech-focused; use case implicit.")

    def t05(self):
        toc = self.doc.toc_block()
        has = bool(self.doc.find_section("table of content", "contents"))
        ev = "Table of Contents heading present near the top." if has else "No Table of Contents section."
        self.add("T05", "Table of Contents present", "RECOMMENDED", True, 10 if has else 0, ev,
                 "Present." if has else "Absent — RECOMMENDED, scored 0.")

    def t06(self):
        toc = self.doc.toc_block()
        if not toc:
            self.add("T06", "ToC links match actual sections", "RECOMMENDED", True, 0, "No ToC to check.", "Absent.")
            return
        targets = re.findall(r"\]\(#([^)]+)\)", toc)
        anchors = {github_anchor(t) for _, t, _ in self.doc.headings}
        dead = [t for t in targets if t not in anchors]
        major = [n for n in TEMPLATE_ORDER if n not in self.doc.sections and any(n in s for s in self.doc.sections)]
        missing_major = [n for n in ("detailed description", "requirements", "deploy", "tags")
                         if not any(n in s for s in self.doc.section_order)]
        ratio_dead = len(dead) / max(1, len(targets))
        if not dead and not missing_major:
            score = 10
        elif ratio_dead <= 0.15 and len(dead) <= 2:
            score = 8
        elif ratio_dead <= 0.4:
            score = 6
        else:
            score = 3
        ev = f"{len(targets)} ToC links, {len(dead)} dead{f': {dead[:4]}' if dead else ''}; major sections missing from doc: {missing_major or 'none'}"
        self.add("T06", "ToC links match actual sections", "RECOMMENDED", True, score, ev,
                 "All links live." if score >= 9 else f"{len(dead)} dead/missing entries.")

    def t07(self):
        sec = self.doc.find_section("detailed description", "description", "overview")
        if not sec:
            self.add("T07", "Detailed description: 2–3 use-case paragraphs", "REQUIRED", True, 0, "No detailed-description section.", "Absent.")
            return
        body = sec[1]
        paras = [p for p in re.split(r"\n\s*\n", body) if p.strip() and not re.match(r"^\s*(!\[|<|```)", p)]
        chars = len(re.sub(r"\s", "", body))
        if len(paras) >= 2 and chars >= 400:
            score = 10
        elif len(paras) >= 2:
            score = 8.5
        elif len(paras) == 1 and chars >= 200:
            score = 7
        else:
            score = 5
        ev = f"\"{sec[0]}\" section: {len(paras)} paragraphs, {chars} non-space chars"
        self.add("T07", "Detailed description: 2–3 use-case paragraphs", "REQUIRED", True, score, ev,
                 "Substantive multi-paragraph narrative." if score >= 9 else "Present but thin or list-only.")

    def t08(self):
        # feature walkthrough — "Usage" / "See it in action", normally in
        # Deploy after validation. Judged standalone: screenshots count by
        # their embed + alt text (file existence is a generator-side
        # check, unverifiable here), text demos by fenced input/output.
        name = "Usage / See it in action — feature walkthrough"
        hit = None
        for level, t, i in self.doc.headings:
            lt = t.lower()
            if (lt == "usage" or "see it in action" in lt or
                    "walkthrough" in lt or lt.startswith("interact with") or
                    "try it" in lt):
                hit = (level, t, i)
                break
        if not hit:
            self.add("T08", name, "REQUIRED", True, 0,
                     "No Usage / 'See it in action' walkthrough section.",
                     "Feature walkthrough absent.")
            return
        level, title, i = hit
        end = len(self.doc.lines)
        for l2, t2, i2 in self.doc.headings:
            if i2 > i and l2 <= level:
                end = i2
                break
        body_lines = self.doc.lines[i + 1:end]
        body = "\n".join(body_lines)
        # a flat "Usage" label sitting among sibling subsections (matched
        # heading's direct body is a stub) — widen the scope to the
        # sibling container, up to the next strictly higher-level heading
        if level > 3 and len(body.strip()) < 100:
            end_w = len(self.doc.lines)
            for l2, t2, i2 in self.doc.headings:
                if i2 > i and l2 < level:
                    end_w = i2
                    break
            body_lines = self.doc.lines[i + 1:end_w]
            body = "\n".join(body_lines)
        # screenshots in the section (markdown or HTML); alt-text quality
        imgs = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", body)
        for tag in re.findall(r"<img\s[^>]*>", body):
            src = re.search(r'src="([^"]+)"', tag)
            alt = re.search(r'alt="([^"]*)"', tag)
            if src:
                imgs.append((alt.group(1) if alt else "", src.group(1)))
        good_imgs = [a for a, _ in imgs if len(a.strip()) >= 10]
        # fenced blocks: (gap_before, lines). A block demonstrates I/O
        # when it has >= 2 content lines (transcript) or directly follows
        # another block with only a short gap (input -> output pair).
        items, fence, cur, gap = [], False, [], []
        for ln in body_lines:
            if ln.lstrip().startswith("```"):
                if fence:
                    items.append(("\n".join(gap), cur))
                    gap = []
                fence = not fence
                cur = []
            elif fence:
                cur.append(ln)
            else:
                gap.append(ln)
        content = [(g, b) for g, b in items if any(x.strip() for x in b)]
        io_blocks = 0
        for j, (g, b) in enumerate(content):
            if sum(1 for x in b if x.strip()) >= 2 or (j > 0 and len(g.strip()) <= 80):
                io_blocks += 1
        # explicit capture placeholders (evidence-gated: repo has no
        # screenshot/output material) — a specific one names what to add
        todos = [ln for ln in body_lines
                 if re.search(r"todo", ln, re.I)
                 and re.search(r"screenshot|image|capture|photo|recording|output", ln, re.I)
                 and len(ln.strip()) >= 30]
        subsecs = sum(1 for l2, t2, i2 in self.doc.headings
                      if i2 > i and i2 < end and l2 > level)
        feats = max(subsecs, 1)
        artifacts = len(good_imgs) + io_blocks + len(todos)
        ev = (f"walkthrough '{title}' (H{level}): {len(imgs)} images "
              f"({len(good_imgs)} with real alt text), {io_blocks} I/O blocks, "
              f"{len(todos)} TODO placeholders, {subsecs} feature subsections")
        if artifacts >= max(feats, 2):
            score, why = 10, "Main features each demonstrated by a real artifact or a specific TODO placeholder."
        elif artifacts >= 1:
            score, why = 7.5, "Walkthrough present; not every feature demonstrated."
        elif imgs:
            score, why = 7, "Screenshots present but alt text weak."
        elif len(body.strip()) >= 100:
            score, why = 5, "Features described in prose only; no artifacts or placeholders."
        else:
            score, why = 3, "Heading only."
        self.add("T08", name, "REQUIRED", True, score, ev, why)

    def t09(self):
        imgs = self.doc.images()
        if not imgs:
            self.add("T09", "Architecture diagram present with alt text", "REQUIRED", True, 0, "No markdown images anywhere in the document.", "No architecture diagram.")
            return
        alt, path = imgs[0]
        good_alt = len(alt.strip()) >= 10
        good_path = bool(re.search(r"(docs/)?images?/|assets?/", path, re.I))
        good_name = bool(re.search(r"[-_]", Path(path).stem)) and len(Path(path).stem) > 8
        score = 10 if (good_alt and good_path and good_name) else (8 if good_alt else (5 if alt is not None else 5))
        ev = f"First image: alt=\"{alt[:40]}\" path={path}"
        self.add("T09", "Architecture diagram present with alt text", "REQUIRED", True, score, ev,
                 "Alt text + descriptive filename + images path." if score >= 9 else "Image present; alt text or filename weak.")

    def t10(self):
        imgs = self.doc.images()
        if not imgs:
            self.add("T10", "Diagram explanation", "OPTIONAL", False, None, "No image to explain.", "Optional, absent — allowed.")
            return
        after = self.doc.text.split(f"]({imgs[0][1]})", 1)[-1][:400]
        explained = len(re.sub(r"\s|!\[.*?\]\(.*?\)", "", after).strip()) > 60
        self.add("T10", "Diagram explanation", "OPTIONAL", True, 10 if explained else 8,
                 f"text after first image: {len(after.strip())} chars", "Explanation follows the diagram." if explained else "Little explanation below the image.")

    def _hw_software_sections(self):
        """Bodies of the hardware/software ### subsections under Requirements."""
        req = self.doc.find_section("requirement")
        hw = sw = None
        if req:
            start = req[2]
            end = next((i2 for l2, t2, i2 in self.doc.headings if i2 > start and l2 == 2), len(self.doc.lines))
            for level, t, i in self.doc.headings:
                if level == 3 and start < i < end:
                    tl = t.lower()
                    if "hardware" in tl and hw is None:
                        hw = self._sub_body(i)
                    if "software" in tl and sw is None:
                        sw = self._sub_body(i)
        return hw, sw

    def _sub_body(self, line_idx):
        buf = []
        for ln in self.doc.lines[line_idx + 1:]:
            if re.match(r"^#{1,3}\s", ln):
                break
            buf.append(ln)
        return "\n".join(buf)

    def _hw_body(self) -> str:
        hw, _ = self._hw_software_sections()
        if hw is None:
            hw = ""
            for name in self.doc.section_order:
                if "hardware" in name:
                    hw = self.doc.sections[name][1]
        return hw

    def _sw_body(self) -> str:
        _, sw = self._hw_software_sections()
        if sw is None:
            sw = ""
            for name in self.doc.section_order:
                if "software" in name:
                    sw = self.doc.sections[name][1]
        return sw

    def t11(self):
        hw = self._hw_body()
        if not hw.strip():
            self.add("T11", "Minimum hardware requirements: present, structured, evidence-gated", "REQUIRED", True, 0, "No hardware requirements subsection.", "Absent.")
            return
        lines = [l for l in hw.splitlines() if l.strip()]
        cats = {
            "CPU": r"core|vcpu|\bcpu\b",
            "memory": r"memory|\bram\b|\bgi[b]?\b|\bgb\b",
            "GPU": r"\bgpu\b|nvidia|a100|l40s|h100|\ba10\b|\bt4\b",
            "storage": r"storage|\bpvc\b|disk|\bssd\b",
        }
        ok, vague = [], []
        for name, pat in cats.items():
            matched = [l for l in lines if re.search(pat, l, re.I)]
            if not matched:
                continue
            # a category is satisfied when some matching row carries a value
            # or an explicit TODO placeholder; per the template, GPU "None"
            # and "optional" (+ its trigger) are values, not vague mentions
            valued = re.compile(r"\b(none|optional|not required|no gpu)\b", re.I)
            if any(("todo" in l.lower()) or re.search(r"\d", l) or valued.search(l) for l in matched):
                ok.append(name)
            else:
                vague.append(name)
        n_ok, n_vague = len(ok), len(vague)
        if n_ok >= 3 and n_vague == 0:
            score = 10
        elif n_ok >= 3:
            score = 8.5
        elif n_ok == 2:
            score = 7
        else:
            score = 5
        ev = f"hardware categories valued-or-TODO: {ok or 'none'}; vague (no value, no TODO): {vague or 'none'}"
        self.add("T11", "Minimum hardware requirements: present, structured, evidence-gated", "REQUIRED", True, score, ev,
                 "All categories present, valued or TODO'd." if score >= 9 else "Categories missing or vague.")

    def t12(self):
        hw = self._hw_body()
        if not hw.strip():
            self.add("T12", "Whole-stack floor stated up front", "REQUIRED", True, 0, "No hardware requirements subsection.", "Absent.")
            return
        low = hw.lower()
        total = bool(re.search(r"\b(total|combined|overall|entire|whole|sums to|across all|"
                               r"all (charts|components|deployed)|full stack|footprint|sizing|"
                               r"and its dependencies)\b", low))
        sizing = bool(re.search(r"\d+\s*(worker\s+)?nodes?\b", low)) and \
            bool(re.search(r"\d+\s*[-–]?\d*\s*gi\b|\b\d+\s*gib\b|\d+\s*gb\b", low))
        # flat un-attributed CPU/Memory/Storage statements read as a
        # whole-stack floor; "(from values.yaml)"-style attribution means
        # per-component numbers instead
        keys = sum(bool(re.search(p, low, re.I | re.M)) for p in
                   (r"^\s*[-*]?\s*\**cpu\**\s*:", r"^\s*[-*]?\s*\**memory\**\s*:",
                    r"^\s*[-*]?\s*\**storage\**\s*:", r"^\s*[-*]?\s*\**gpu\**\s*:"))
        attributed = bool(re.search(r"\(from|values\.ya?ml|per[- ]chart|per[- ]component", low))
        flat_floor = keys >= 3 and not attributed
        rows = len(list_items(hw))
        if total or sizing or flat_floor:
            score = 10
        elif rows >= 3:
            score = 5
        else:
            score = 4
        ev = (f"whole-stack keywords: {total}; node+GiB sizing: {sizing}; "
              f"flat resource floor: {flat_floor} (keys={keys}, attributed={attributed}); "
              f"TODO-valued floor accepted: {'todo' in hw.lower()}; {rows} rows")
        self.add("T12", "Whole-stack floor stated up front", "REQUIRED", True, score, ev,
                 "Explicit combined floor." if score >= 9 else "Per-component numbers only, no combined floor.")

    def t13(self):
        applicable, ev = self.model_in_deploy()
        if not applicable:
            self.add("T13", "Model resource requirements / MaaS GPU note", "CONDITIONAL", False, None, ev,
                     "Deploy path does not serve/configure a model — N/A per the deploy-path tiebreaker.")
            return
        hw = self._hw_body().lower()
        low_all = self.doc.text.lower()
        maas = bool(re.search(r"maas|external (model|endpoint)|bring.your.own|no gpu", low_all))
        separate = bool(re.search(r"model[^\n]{0,60}(requirement|resource|gpu|vram|memory)|for the model\b", hw))
        if maas and not re.search(r"nvidia|gpu", hw):
            score = 10 if "no gpu" in low_all or "not required" in low_all else 7
            why = "MaaS path: GPU situation stated."
        elif separate:
            score, why = 10, "Model resource requirements listed separately."
        elif re.search(r"gpu|vram", hw):
            score, why = 6, "Model resources merged into the general table only."
        else:
            score, why = 4, "No model resource requirements stated."
        self.add("T13", "Model resource requirements / MaaS GPU note", "CONDITIONAL", True, score,
                 ev + f"; separate model row in hardware: {separate}", why)

    def t14(self):
        sw = self._sw_body()
        if not sw.strip():
            self.add("T14", "Minimum software requirements: present, complete, evidence-gated", "REQUIRED", True, 2.5, "No software requirements subsection.", "Absent → ≤3 band.")
            return
        items = list_items(sw)
        low = sw.lower()
        versioned, todo, bare = 0, 0, 0
        tool_items = []
        for it in items:
            if any(h in it.lower() for h in NON_TOOL_HINTS):
                continue
            if not re.search(r"[a-zA-Z]{2}", it):
                continue
            tool_items.append(it)
            # count individual backticked tools inside the item (a single CLI
            # line can bundle oc, helm, jq, aws... — each counts separately)
            tokens = re.findall(r"`([A-Za-z][\w.-]{1,20})`", it)
            if len(tokens) >= 2:
                for tok in tokens:
                    pos = it.find(f"`{tok}`")
                    window = it[pos:pos + len(tok) + 30]
                    if re.search(rf"\d+\.\d+|v\d+\b|≥\s*\d+|>=\s*\d+", window):
                        versioned += 1
                    elif "todo" in window.lower():
                        todo += 1
                    else:
                        bare += 1
            elif "todo" in it.lower():
                todo += 1
            elif re.search(r"\d+\.\d+|v\d+\b|\d+\.\d+\.\d+", it):
                versioned += 1
            else:
                bare += 1
        # core items the template names explicitly must be listed at all
        core = {
            "OpenShift": "openshift" in low,
            "OpenShift AI": "openshift ai" in low,
            "oc": bool(re.search(r"\boc\b", low)),
            "helm": "helm" in low,
        }
        core_missing = [k for k, v in core.items() if not v]
        if not tool_items:
            score = 6
        elif bare == 0:
            score = 9.5 if not core_missing else 8
        elif bare == 1:
            score = 8
        elif bare <= 3:
            score = 6
        else:
            score = 4.5
        ev = (f"software-requirements list: {versioned} versioned, {todo} TODO, {bare} bare "
              f"(of {len(tool_items)} entries, backticked tools counted individually); "
              f"core items missing: {core_missing or 'none'}")
        self.add("T14", "Minimum software requirements: present, complete, evidence-gated", "REQUIRED", True, score, ev,
                 "Every entry version-pinned or TODO'd; core items present." if score >= 9 else f"{bare} bare names — banded by mechanical count.")

    def t15(self):
        sw = self._sw_body()
        if not sw.strip():
            self.add("T15", "Version discipline: floors and ceilings as stated", "REQUIRED", True, 6, "No software requirements to check.", "No stated bounds.")
            return
        versioned = len(re.findall(r"\d+\.\d+", sw))
        todo_n = len(re.findall(r"todo", sw, re.I))
        tested = bool(re.search(r"tested with", sw, re.I))
        # TODO placeholders are correct treatment for unstated values —
        # nothing stated, nothing mis-stated
        score = 10 if (versioned >= 1 or todo_n >= 1) else (8 if tested else 6)
        ev = f"{versioned} version bounds, {todo_n} TODO entries in software requirements; 'tested with' pin: {tested}"
        self.add("T15", "Version discipline: floors and ceilings as stated", "REQUIRED", True, score, ev,
                 "Bounds well-formed and scoped (TODO'd entries acceptable)." if score >= 9 else "Few or no stated bounds.")

    def t16(self):
        sec = self.doc.find_section("permission")
        if not sec:
            self.add("T16", "Required user permissions", "REQUIRED", True, 0, "No permissions subsection.", "Absent.")
            return
        low = sec[1].lower()
        good = bool(re.search(r"cluster-admin|cluster admin|namespace admin|regular user|project admin", low))
        vague = bool(re.search(r"appropriate|sufficient|adequate", low))
        score = 10 if good else (6 if vague else 7.5)
        ev = f"permission role statements in '{sec[0]}': cluster-admin/namespace-admin/regular-user present: {good}"
        self.add("T16", "Required user permissions", "REQUIRED", True, score, ev,
                 "Specific role named." if good else "Role vague or missing.")

    def t17(self):
        deploy = self.doc.find_section("deploy", "installation", "install", "quick start", "getting started")
        prereq = self.doc.find_section("prerequisit")
        scope = (prereq[1] if prereq else "") + "\n" + (deploy[1][:1500] if deploy else "")
        low = scope.lower()
        kinds = {
            "platform access": bool(re.search(r"access to (an? |the )?(openshift|cluster|platform)|cluster access|account", low)),
            "CLI tools": bool(re.search(r"\boc\b|helm|kubectl|cli", low)),
            "credentials": bool(re.search(r"credential|log ?in|token|api key|password|kubeconfig", low)),
            "network": bool(re.search(r"network|egress|firewall|dns|internet", low)),
        }
        n = sum(kinds.values())
        score = 10 if n >= 4 else (8.5 if n == 3 else (7 if n == 2 else 5.5))
        if not scope.strip():
            score = 0
        ev = f"prerequisite kinds covered: {[k for k, v in kinds.items() if v]}"
        self.add("T17", "Prerequisites", "REQUIRED", True, score, ev,
                 "All four kinds covered." if score >= 9 else f"{n}/4 kinds covered.")

    def t18(self):
        sec = self.doc.find_section("installation", "install", "deploy", "quick start")
        if not sec:
            self.add("T18", "Installation steps: numbered and copy-pasteable", "REQUIRED", True, 0, "No installation/deploy section.", "Absent.")
            return
        body = sec[1]
        numbered = len(re.findall(r"^\s*\d+[.)]\s", body, re.M))
        code = len(re.findall(r"```", body)) // 2
        prose = len([p for p in re.split(r"\n\s*\n", body) if p.strip() and not re.match(r"^\s*(```|!\[|\d+[.)])", p)])
        if numbered >= 3 and code >= 2 and prose >= 2:
            score = 10
        elif numbered >= 3 and code >= 1:
            score = 8
        elif code >= 1:
            score = 6
        else:
            score = 3
        ev = f"installation section: {numbered} numbered steps, {code} code blocks, {prose} explanation paragraphs"
        self.add("T18", "Installation steps: numbered and copy-pasteable", "REQUIRED", True, score, ev,
                 "Numbered steps + commands + explanations." if score >= 9 else "Commands present but structure/explanation sparse.")

    def t19(self):
        applicable, ev = self.model_in_deploy()
        if not applicable:
            self.add("T19", "Model options A/B", "CONDITIONAL", False, None, ev,
                     "Deploy path does not serve/configure a model — N/A per the deploy-path tiebreaker.")
            return
        low = self.doc.text.lower()
        opt_a = bool(re.search(r"--set model|model\.(name|endpoint|api)|bring.your.own|external (model|endpoint)|openai-compatible|maas", low))
        opt_b = bool(re.search(r"default model|deploy(ed)? (by|with) the chart|chart.deploy|pre-?loaded model|in.cluster model", low))
        pretest = bool(re.search(r"(test|verify).{0,60}(model|endpoint|connection).{0,40}(before|prior|first)|before deploying.{0,40}(test|verify)", low))
        if opt_a and opt_b:
            score = 10 if pretest else 8
        elif opt_a or opt_b:
            score = 5
        else:
            score = 3
        self.add("T19", "Model options A/B", "CONDITIONAL", True, score,
                 ev + f"; option A (external endpoint): {opt_a}; option B (chart model): {opt_b}; pre-deploy test: {pretest}",
                 "Both paths offered." if score >= 8 else "Only one model path offered.")

    def t20(self):
        sec = self.doc.find_section("validat", "verification", "verify")
        scope = sec[1] if sec else ""
        low = scope.lower()
        if not scope.strip():
            # validation may live inside Deploy
            deploy = self.doc.find_section("deploy")
            low = (deploy[1] if deploy else "").lower()
            scope = deploy[1] if deploy else ""
        checks = {
            "pod status": bool(re.search(r"get pods|pod status|oc get pod", low)),
            "route/URL": bool(re.search(r"route|url|endpoint", low)),
            "functionality": bool(re.search(r"verify|check|test|curl|expected", low)),
            "helm test": bool(re.search(r"helm test", low)),
        }
        n = sum(checks.values())
        if not scope.strip():
            score = 0
        else:
            score = 10 if n >= 3 else (8.5 if n == 2 else (7 if n == 1 else 5))
        ev = f"validation checks present: {[k for k, v in checks.items() if v] or 'none'}"
        self.add("T20", "Validating the deployment", "REQUIRED", True, score, ev,
                 "All relevant checks with commands." if score >= 9 else "Minimal validation.")

    def t21(self):
        sec = self.doc.find_section("delete", "uninstall", "cleanup", "clean up", "teardown")
        low = (sec[1] if sec else "").lower()
        if not sec:
            self.add("T21", "Delete / cleanup", "REQUIRED", True, 0, "No delete/uninstall section.", "Absent.")
            return
        uninstall = bool(re.search(r"uninstall|make .*(clean|uninstall)|delete", low))
        pvc = bool(re.search(r"\bpvc\b|persistentvolume|secret|namespace|project", low))
        score = 10 if uninstall and pvc else (8 if uninstall else 4)
        ev = f"uninstall commands: {uninstall}; PVC/secret/project cleanup: {pvc}"
        self.add("T21", "Delete / cleanup", "REQUIRED", True, score, ev,
                 "Uninstall + residual cleanup covered." if score >= 9 else "Uninstall only.")

    def t22(self):
        sec = self.doc.find_section("repository structure", "repo structure", "project structure", "repository layout")
        if not sec:
            self.add("T22", "Repository structure", "RECOMMENDED", True, 0, "No repository-structure section.", "Absent — RECOMMENDED, scores 0.")
            return
        tree = bool(re.search(r"[├└│]|^\s{2,}\S+/\s*$", sec[1], re.M))
        files = len(re.findall(r"\.(py|yaml|json|sh|toml|md|tf)\b", sec[1]))
        score = 10 if tree and files <= 25 else (8 if tree else 6)
        ev = f"'{sec[0]}' section: tree-like={tree}, ~{files} file entries"
        self.add("T22", "Repository structure", "RECOMMENDED", True, score, ev,
                 "Concise tree of key directories." if score >= 9 else "Over- or under-detailed.")

    def t23(self):
        sec = self.doc.find_section("reference", "learn more", "further reading", "going deeper", "component documentation")
        if not sec:
            self.add("T23", "References cover the stack", "RECOMMENDED", False, None, "No References section.", "Absent — allowed ('remove entirely if nothing to add').")
            return
        links = re.findall(r"\[[^\]]+\]\((https?://[^)]+)\)", sec[1])
        # github links to the quickstart's own org are repo-internal; other
        # github links are project pages but weaker than product docs
        internal = [u for u in links if "github.com/rh-ai-quickstart" in u]
        github = [u for u in links if "github.com" in u and u not in internal]
        official = [u for u in links if "github.com" not in u]
        redhat = any("redhat.com" in u for u in official)
        if len(official) >= 4 and redhat:
            score = 9
        elif len(official) >= 4:
            score = 8
        elif len(official) + len(github) >= 2:
            score = 7 if redhat else 6
        elif links:
            score = 4
        else:
            score = 3
        ev = (f"References: {len(links)} links ({len(official)} non-github official, "
              f"{len(github)} project-github, {len(internal)} repo-internal); Red Hat platform docs: {redhat}")
        self.add("T23", "References cover the stack", "RECOMMENDED", True, score, ev,
                 "Official docs for most stack components." if score >= 8 else "Partial coverage of the named stack.")

    def t24(self):
        sec = self.doc.find_section("technical details", "technical detail")
        if not sec:
            self.add("T24", "Technical details", "OPTIONAL", False, None, "No Technical details section.", "Optional, absent — allowed.")
            return
        chars = len(re.sub(r"\s", "", sec[1]))
        score = 10 if chars >= 300 else 8
        ev = f"'{sec[0]}' section: {chars} non-space chars"
        self.add("T24", "Technical details", "OPTIONAL", True, score, ev, "Substantive technical depth, correctly placed.")

    def t25(self):
        present = [n for n in TEMPLATE_ORDER if any(n in s for s in self.doc.section_order)]
        idx = {n: self.doc.section_order.index(next(s for s in self.doc.section_order if n in s)) for n in present}
        inversions = sum(1 for i, a in enumerate(present) for b in present[i + 1:] if idx[a] > idx[b])
        aux = [s for s in self.doc.section_order if s not in ALLOWED_TOP_LEVEL]
        if inversions == 0:
            score = 10 if not aux else 8
        elif inversions == 1:
            score = 7
        else:
            score = 5
        ev = f"template sections in doc order: {present}; inversions: {inversions}"
        self.add("T25", "Section order follows the template", "REQUIRED", True, score, ev,
                 "Exact template order." if score >= 9 else f"{inversions} ordering deviations.")

    def t26(self):
        invented = [s for s in self.doc.section_order if s not in ALLOWED_TOP_LEVEL]
        score = 10 if not invented else (7 if len(invented) == 1 else 5)
        ev = f"top-level sections outside the template set: {invented or 'none'}"
        self.add("T26", "No invented top-level sections", "REQUIRED", True, score, ev,
                 "Only template (+ tolerated auxiliary) sections." if not invented else f"{len(invented)} off-template sections.")

    def _tags_block(self):
        """(bold_labels dict, plain_labels dict, invented_labels list, is_last)."""
        tags_names = [s for s in self.doc.section_order if "tags" in s]
        if not tags_names:
            return {}, {}, [], False
        body = self.doc.sections[tags_names[0]][1]
        known = ("title", "description", "industry", "product", "use case", "partner",
                 "contributor org", "contributing org")
        bold, plain, invented = {}, {}, []
        for m in re.finditer(r"\*\*([^:*]+)\s*:\*\*\s*(.+)", body):
            k, v = m.group(1).strip().lower(), m.group(2).strip()
            if k in known:
                bold.setdefault(k, v)
            elif k not in invented:
                invented.append(k)
        for m in re.finditer(r"^\s*[-*]\s+\*?\*?([^:*]+?)\s*:\s*\*?\*?\s*(.+)$", body, re.M):
            k, v = m.group(1).strip().lower().strip("*"), m.group(2).strip()
            if k in bold:
                continue
            if k in known:
                plain.setdefault(k, v)
            elif k not in invented:
                invented.append(k)
        last = self.doc.section_order[-1] in tags_names
        return bold, plain, invented, last

    def t27(self):
        bold, plain, invented, last = self._tags_block()
        if not bold and not plain and not invented:
            self.add("T27", "Tags block present, bold-labeled, at the end", "REQUIRED", True, 0, "No Tags section or label lines.", "Absent.")
            return
        if bold and last:
            score = 10
        elif bold:
            score = 8.5
        elif plain:
            score = 5
        else:
            score = 4
        ev = f"tags labels: bold={list(bold)}, plain={list(plain)}, invented={invented}; last section: {last}"
        self.add("T27", "Tags block present, bold-labeled, at the end", "REQUIRED", True, score, ev,
                 "Bold-labeled block at the end." if score >= 9 else "Present but malformed (plain list / not bold / not last).")

    def t28(self):
        bold, plain, invented, _ = self._tags_block()
        h1 = self.doc.h1[0] if self.doc.h1 else ""
        title = bold.get("title") or plain.get("title")
        if title is None:
            self.add("T28", "Tags Title matches the H1, ≤ 64 chars", "REQUIRED", True, 0, "No Tags Title line.", "Missing.")
            return
        same = title.strip().strip('"') == h1.strip()
        n = len(title)
        score = 10 if (same and n <= 64) else 3
        ev = f"H1 = \"{h1}\" ({len(h1)} chars) vs Tags Title = \"{title}\" ({n} chars) — measured"
        self.add("T28", "Tags Title matches the H1, ≤ 64 chars", "REQUIRED", True, score, ev,
                 "Verbatim match, within limit." if score >= 9 else "Mismatch or over limit — hard-rule violation caps at 4.")

    def t29(self):
        bold, plain, _, _ = self._tags_block()
        desc = bold.get("description") or plain.get("description")
        sd = self.doc.short_desc
        if desc is None:
            self.add("T29", "Tags Description matches the short description, ≤ 160 chars", "REQUIRED", True, 0, "No Tags Description line.", "Missing.")
            return
        same = desc.strip().strip('"') == sd.strip()
        n = len(desc)
        score = 10 if (same and n <= 160) else 3
        ev = f"short description ({len(sd)} chars) vs Tags Description ({n} chars) — measured, identical: {same}"
        self.add("T29", "Tags Description matches the short description, ≤ 160 chars", "REQUIRED", True, score, ev,
                 "Verbatim match, within limit." if score >= 9 else "Mismatch or over limit — hard-rule violation caps at 4.")

    def t30(self):
        bold, plain, invented, _ = self._tags_block()
        val = bold.get("industry") or plain.get("industry")
        if val is None:
            if any("industry" in i for i in invented):
                self.add("T30", "Tags Industry: one value", "REQUIRED", True, 0, "Industry label missing/invented.", "Missing label.")
            else:
                self.add("T30", "Tags Industry: one value", "REQUIRED", True, 0, "No Tags Industry line.", "Missing label → ≤3 band.")
            return
        # multiple values only when comma-separated (" and " occurs inside
        # single catalog values like "Media and IT services")
        multi = "," in val
        score = 10 if not multi else 5
        ev = f"Industry = \"{val}\""
        self.add("T30", "Tags Industry: one value", "REQUIRED", True, score, ev,
                 "Exactly one value (form-only scoring)." if score >= 9 else "Multiple/compound values.")

    def t31(self):
        bold, plain, _, _ = self._tags_block()
        val = bold.get("product") or plain.get("product")
        if val is None:
            self.add("T31", "Tags Product: primary Red Hat product", "REQUIRED", True, 0, "No Tags Product line.", "Missing.")
            return
        vals = [v.strip() for v in re.split(r",| and ", val) if v.strip()]
        rh = all(re.search(r"red hat|openshift|ansible|rhel|amq|jboss", v, re.I) for v in vals)
        if len(vals) == 1 and rh:
            score = 10
        elif len(vals) == 2 and rh:
            score = 8.5
        elif rh:
            score = 6
        else:
            score = 4
        ev = f"Product = \"{val}\" ({len(vals)} values)"
        self.add("T31", "Tags Product: primary Red Hat product", "REQUIRED", True, score, ev,
                 "One primary Red Hat product." if score >= 9 else "Multiple/non-Red-Hat product values.")

    def t32(self):
        bold, plain, invented, _ = self._tags_block()
        use_case = bold.get("use case") or plain.get("use case")
        partner = bold.get("partner") or plain.get("partner")
        if use_case is None and partner is None and not invented:
            self.add("T32", "Tags Use case / Partner used correctly", "OPTIONAL", False, None, "No Use case or Partner lines.", "Optional, absent — allowed.")
            return
        problems = []
        if partner and re.fullmatch(r"red hat(\s+hat)?", partner.strip(), re.I):
            problems.append(f"Partner set to the vendor: \"{partner}\"")
        if invented:
            problems.append(f"invented labels: {invented}")
        score = 3.0 if problems else 10
        ev = f"Use case: {use_case!r}; Partner: {partner!r}; invented: {invented}"
        self.add("T32", "Tags Use case / Partner used correctly", "OPTIONAL", True, score, ev,
                 "Both used correctly." if not problems else "; ".join(problems) + " — ≤3.0 hard ceiling.")

    # ------------------------------------------------------------ run

    def run(self):
        for t in (self.t01, self.t02, self.t03, self.t04, self.t05, self.t06, self.t07,
                  self.t08, self.t09, self.t10, self.t11, self.t12, self.t13, self.t14,
                  self.t15, self.t16, self.t17, self.t18, self.t19, self.t20, self.t21,
                  self.t22, self.t23, self.t24, self.t25, self.t26, self.t27, self.t28,
                  self.t29, self.t30, self.t31, self.t32):
            t()
        num = sum(r["score"] * WEIGHTS[r["class"]] for r in self.results
                  if r["applicable"] and r["score"] is not None)
        den = sum(WEIGHTS[r["class"]] for r in self.results
                  if r["applicable"] and r["score"] is not None)
        overall = round(num / den, 1) if den else 0.0
        lows = [r for r in self.results if r["applicable"] and r["score"] is not None and r["score"] < 7]
        verdict = ("Template-compliant." if not lows else
                   "Biggest gaps: " + "; ".join(f"{r['id']} {r['name']} ({r['score']})" for r in lows[:4]))
        return {
            "file": self.path,
            "restrictions": self.results,
            "overall": overall,
            "verdict": verdict,
            "generator": "check.py (live code)",
        }


# ---------------------------------------------------------------- selftest

GOOD_README = """# Protect patient data with LLM guardrails

Healthcare teams use this quickstart to screen prompts and responses for PHI before they reach patients, reducing compliance risk.

## Table of contents

- [Detailed description](#detailed-description)
- [Requirements](#requirements)
- [Deploy](#deploy)
- [Tags](#tags)

## Detailed description

Organizations handling patient communications must prevent protected health information from leaking through AI assistants. This quickstart deploys a guardrails service that inspects traffic in real time.

Teams in compliance roles can enforce policies without rebuilding their applications. The solution integrates with existing OpenShift AI serving paths.

![Architecture diagram](docs/images/guardrails-traffic-flow.svg)

Traffic flows from the application through the guardrails service to the model server.

## Requirements

### Minimum hardware requirements

- CPU: 4 cores
- Memory: 16 GiB
- GPU: NVIDIA L40S (not required when using MaaS)
- Storage: 50 Gi

Total for the whole quickstart: 4 CPU / 16 GiB / 1 GPU.

### Minimum software requirements

- Red Hat OpenShift AI 2.22
- OpenShift 4.14+
- Helm 3.14
- oc CLI 4.14

### Required user permissions

Namespace admin (regular user); cluster-admin only if installing the operator.

## Deploy

### Prerequisites

- Access to an OpenShift 4.14+ cluster
- oc CLI 4.14, Helm 3.14
- Login credentials for the cluster
- Network egress to the model endpoint

### Installation

1. Clone the repository.
2. Create the namespace.

```bash
oc new-project guardrails
```

3. Install the chart.

```bash
helm install guardrails chart/guardrails
```

### Validating the deployment

```bash
oc get pods
oc get route guardrails
helm test guardrails
```

### Usage

#### Screen a prompt

Send a screening request and inspect the verdict:

```bash
curl -s $ROUTE/v1/screen -d '{"prompt": "patient follow-up notes"}'
```

```json
{"verdict": "blocked", "policy": "PHI-screening", "matches": 1}
```

#### Review flagged traffic

![Flagged requests in the guardrails dashboard](docs/images/guardrails-flagged-traffic.png)

The dashboard lists blocked prompts with the matched policy for review.

### Delete

```bash
helm uninstall guardrails
oc delete project guardrails
```

PVCs and secrets are removed with the project.

## References

- [OpenShift AI docs](https://docs.redhat.com/documentation/red_hat_openshift_ai)
- [Helm docs](https://helm.sh/docs)
- [vLLM docs](https://docs.vllm.ai)

## Tags

**Title:** Protect patient data with LLM guardrails

**Description:** Healthcare teams use this quickstart to screen prompts and responses for PHI before they reach patients, reducing compliance risk.

**Industry:** Healthcare

**Product:** Red Hat OpenShift AI
"""

BAD_README = """# My Cool Project

Some repo about a cool project, see our links.

## Setup

Install stuff.

## Tags

* Industry: Tech, and Media
* Product: Kubernetes, Docker
* Partner: Red Hat
* Contributor org: Red Hat
"""


TODO_README = GOOD_README.replace(
    """- CPU: 4 cores
- Memory: 16 GiB
- GPU: NVIDIA L40S (not required when using MaaS)
- Storage: 50 Gi

Total for the whole quickstart: 4 CPU / 16 GiB / 1 GPU.""",
    """- CPU: TODO: verify cores needed for the whole stack
- Memory: TODO: verify GiB needed
- GPU: TODO: tested GPU model (not required when using MaaS)
- Storage: TODO: verify storage

Total for the whole quickstart: TODO — verify on a cluster."""
).replace(
    """- Red Hat OpenShift AI 2.22
- OpenShift 4.14+
- Helm 3.14
- oc CLI 4.14""",
    """- Red Hat OpenShift AI: TODO tested version
- OpenShift: TODO minimum version
- Helm: TODO tested version
- oc CLI: TODO tested version""")


def selftest():
    good = Path(_tmp_write(GOOD_README))
    bad = Path(_tmp_write(BAD_README))
    todo = Path(_tmp_write(TODO_README))
    ok = True
    g = Checker(str(good)).run()
    b = Checker(str(bad)).run()
    t = Checker(str(todo)).run()
    print(f"good README overall: {g['overall']} (expect >= 8.5)")
    print(f"bad README overall: {b['overall']} (expect <= 4.5)")
    print(f"TODO README overall: {t['overall']} (expect >= 8.5)")
    ok &= g["overall"] >= 8.5
    ok &= b["overall"] <= 4.5
    ok &= t["overall"] >= 8.5
    # spot mechanical expectations
    gs = {r["id"]: r for r in g["restrictions"]}
    bs = {r["id"]: r for r in b["restrictions"]}
    ts = {r["id"]: r for r in t["restrictions"]}
    for tid, expect in [("T01", 10), ("T03", 10), ("T08", 10), ("T28", 10), ("T29", 10), ("T30", 10)]:
        got = gs[tid]["score"]
        print(f"good {tid}: {got} (expect {expect})")
        ok &= got == expect
    for tid, expect in [("T01", 10), ("T08", 0), ("T28", 0), ("T30", 5), ("T31", 4), ("T32", 3)]:
        got = bs[tid]["score"]
        print(f"bad  {tid}: {got} (expect {expect})")
        ok &= got == expect
    # TODO-template requirements score as high as fully valued ones
    for tid, expect in [("T11", 10), ("T12", 10), ("T14", 9.5), ("T15", 10)]:
        got = ts[tid]["score"]
        print(f"todo {tid}: {got} (expect {expect})")
        ok &= got == expect
    good.unlink()
    bad.unlink()
    todo.unlink()
    print("SELFTEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def _tmp_write(content: str) -> str:
    import tempfile
    f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
    f.write(content)
    f.close()
    return f.name


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("readme", nargs="?", help="path to the README to verify")
    ap.add_argument("-o", "--json", help="write the JSON report to this path")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if not args.readme:
        ap.error("README path required (or --selftest)")
    report = Checker(args.readme).run()
    out = json.dumps(report, indent=2)
    if args.json:
        Path(args.json).write_text(out + "\n")
        print(f"overall: {report['overall']} -> {args.json}")
    else:
        print(out)


if __name__ == "__main__":
    main()

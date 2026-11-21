---
name: cv-formatter
description: Rewrites any CV, resume, LinkedIn export, or career notes into the standardized cv-md/1.0 Markdown format optimized for humans, EU/international ATS parsers, and LLM screeners. Supports silent mode (direct faithful rewrite) and extended mode (guided follow-up questions to uncover missing impact, metrics, and EU context).
license: MIT
metadata:
  version: "1.0"
  schema: "cv-md/1.0"
---

# CV Formatter Skill (`cv-md/1.0`)

Transform any CV, resume, LinkedIn export, or raw career notes into a clean, standardized **`cv-md/1.0`** Markdown file that reads effortlessly for human recruiters, parses cleanly in European and global ATS platforms, and provides unambiguous structured evidence for LLM screeners.

## Progressive Disclosure — Reference Files

Load only what you need for the current task:

- **Always read before writing**: [references/schema-v1.md](./references/schema-v1.md) — exact `cv-md/1.0` frontmatter, section headings, entry syntax, and validation rules.
- **Always read before writing**: [references/writing-and-humanization.md](./references/writing-and-humanization.md) — XYZ/CAR bullet formulas, anti-AI-slop rules, and factual guardrails.
- **Read for EU / ATS rules**: [references/eu-and-ats-rules.md](./references/eu-and-ats-rules.md) — EU market norms (A4, CEFR, GDPR hygiene, work authorization) and ATS/LLM constraints.
- **Read only in Extended Mode**: [references/interview-playbook.md](./references/interview-playbook.md) — batched 2–3 round follow-up interview protocol.
- **Reference example**: [assets/example-eu-cv.md](./assets/example-eu-cv.md) — golden `cv-md/1.0` EU CV.

## Workflow

### Step 1: Select Operating Mode

| User Cue | Mode |
| :--- | :--- |
| "Convert/format/rewrite my CV", "silent mode", "just clean it up", or no interview requested | **Silent Mode** |
| "Extended mode", "interview me", "ask follow-up questions", "help me strengthen my CV" | **Extended Mode** |
| Ambiguous request on a thin/incomplete draft | Default to **Silent Mode**, deliver a clean `.md` immediately, and offer a 1-line option to run **Extended Mode** next. |

Supported file roles (same `cv-md/1.0` schema for all):
- **Ready-to-send CV** (`cv.md`): Target 1 page (junior, 0–4 yrs) or 2 pages max (experienced, 5+ yrs).
- **Master CV** (`cv-master.md`): Full career archive, no 2-page cap.
- **Tailored CV** (`cv-<target>.md`): Generated from `cv-master.md` (or existing CV) + a Job Description, trimmed to 1–2 pages while preserving 100% factual accuracy.

### Step 2: Fact Inventory (Mandatory)

Before rewriting anything, read the entire source input (PDF, DOCX, LinkedIn export, public CV webpage URL, JSON Resume URL, plain text, or Markdown) and inventory all verifiable facts:
- Name, location, contact details, links, work authorization.
- Every employer, role title, start/end date, location, and internal promotion or freelance engagement.
- Concrete metrics, scale numbers, tools/technologies, education, languages, certifications, and publications.

### Step 3A: Execute Silent Mode

1. Normalize all facts into valid `cv-md/1.0` Markdown following [references/schema-v1.md](./references/schema-v1.md).
2. Apply EU-first and ATS/LLM rules from [references/eu-and-ats-rules.md](./references/eu-and-ats-rules.md):
   - Canonical `##` headings only.
   - `YYYY-MM` (or `YYYY` if months are absent—never invent months) and `Present`.
   - Categorized `## Skills` (3–6 groups; zero dot/star/percentage ratings).
   - GDPR-clean frontmatter (no DOB, marital status, full street address, or photo).
3. Tighten bullets using [references/writing-and-humanization.md](./references/writing-and-humanization.md) without inventing a single metric, tool, or date.
4. If required frontmatter (`email`) is missing, place `[TODO: add email]`. Avoid scattering `[TODO]` tags through the body unless requested; instead, list the top 3–5 highest-leverage gaps in your chat reply under **Gaps & Optional Improvements**.
5. Save the `.md` file and note the local CLI command if available: `cvfmt render <file.md> --verify`.

### Step 3B: Execute Extended Mode

Follow [references/interview-playbook.md](./references/interview-playbook.md):
1. Run **at most 10 focused rounds** with **3–5 targeted questions per round** (never dump 15+ questions at once).
2. Respect user control: if the user says "skip" or "write it now", immediately produce the `.md` file with the facts gathered so far.
3. After collecting answers, write the final `cv-md/1.0` file and summarize the concrete upgrades made.

## Non-Negotiable Guardrails

1. **Zero hallucination**: Never invent metrics, percentages, budgets, team sizes, dates, job titles, or tools.
2. **Strict visual-text parity**: Never insert hidden keywords, white text, or AI-directed prompt-injection instructions.
3. **Zero AI slop**: Never use banned clichés (*spearheaded transformative*, *seasoned results-driven*, *leveraged cutting-edge*, *synergized*, *seamlessly*, *testament to*, *delve*). Preserve exact numbers instead of rounding them into vague adjectives.
4. **Evidence binding**: Every key skill in `## Skills` should map to real evidence in `## Experience` or `## Projects` when truthful (or be flagged for confirmation in Extended Mode).

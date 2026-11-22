---
name: cv-formatter
description: Rewrites any CV, resume, LinkedIn export, or career notes into the standardized cv-md/1.1 Markdown format optimized for humans, EU/international ATS parsers, and LLM screeners. Supports silent mode (direct faithful rewrite), extended mode (guided follow-up questions to uncover missing impact, metrics, and EU context), and a non-exported ## Facts memory bank so tailoring never loses candidate data.
license: MIT
metadata:
  version: "1.1"
  schema: "cv-md/1.1"
---

# CV Formatter Skill (`cv-md/1.1`)

Transform any CV, resume, LinkedIn export, or raw career notes into a clean, standardized **`cv-md/1.1`** Markdown file that reads effortlessly for human recruiters, parses cleanly in European and global ATS platforms, and provides unambiguous structured evidence for LLM screeners.

## Progressive Disclosure — Reference Files

Load only what you need for the current task:

- **Always read before writing**: [references/schema-v1.md](./references/schema-v1.md) — exact `cv-md/1.1` frontmatter, section headings (including non-exported `## Facts`), entry syntax, and validation rules.
- **Always read before writing**: [references/writing-and-humanization.md](./references/writing-and-humanization.md) — XYZ/CAR bullet formulas, anti-AI-slop rules, and factual guardrails.
- **Read for EU / ATS rules**: [references/eu-and-ats-rules.md](./references/eu-and-ats-rules.md) — EU market norms (A4, CEFR, GDPR hygiene, work authorization) and ATS/LLM constraints.
- **Read only in Extended Mode**: [references/interview-playbook.md](./references/interview-playbook.md) — batched follow-up interview protocol.
- **Reference example**: [assets/example-eu-cv.md](./assets/example-eu-cv.md) — golden `cv-md/1.1` EU CV with `## Facts`.

## Workflow

### Step 1: Select Operating Mode

| User Cue | Mode |
| :--- | :--- |
| "Convert/format/rewrite my CV", "silent mode", "just clean it up", or no interview requested | **Silent Mode** |
| "Extended mode", "interview me", "ask follow-up questions", "help me strengthen my CV" | **Extended Mode** |
| Ambiguous request on a thin/incomplete draft | Default to **Silent Mode**, deliver a clean `.md` immediately, and offer a 1-line option to run **Extended Mode** next. |
| Master CV + job description, "tailor", "dreamer mode", target vacancy | **Tailoring** — use the dedicated [../cv-tailor/SKILL.md](../cv-tailor/SKILL.md) skill (strict or dreamer). |

Supported file roles (same `cv-md/1.1` schema for all):
- **Ready-to-send CV** (`cv.md`): Target 1 page (junior, 0–4 yrs) or 2 pages max (experienced, 5+ yrs).
- **Master CV** (`cv-master.md`): Full career archive, no 2-page cap, with a rich `## Facts` memory bank.
- **Tailored CV** (`cv-<target>.md`): Generated from `cv-master.md` (or any existing CV) + a Job Description, trimmed to 1–2 pages while preserving 100% factual accuracy. **Always carry `## Facts` forward** into tailored `.md` files and move any trimmed/hidden items into `## Facts` so every `.md` file remains self-contained for future tweaks.

### Step 2: Fact Inventory (Mandatory)

Before rewriting anything, read the entire source input (PDF, DOCX, LinkedIn export, public CV webpage URL, JSON Resume URL, plain text, or Markdown — including any existing `## Facts` section) and inventory all verifiable facts:
- Name, location, contact details, links, work authorization.
- Every employer, role title, start/end date, location, and internal promotion or freelance engagement.
- Concrete metrics, scale numbers, tools/technologies, education, languages, certifications, and publications.
- Non-PDF candidate context (target roles, preferences, notice period, trimmed roles/projects, extra skills/metrics) for `## Facts`.

### Step 3A: Execute Silent Mode

1. Normalize all facts into valid `cv-md/1.1` Markdown following [references/schema-v1.md](./references/schema-v1.md).
2. Apply EU-first and ATS/LLM rules from [references/eu-and-ats-rules.md](./references/eu-and-ats-rules.md):
   - Canonical `##` headings only.
   - `YYYY-MM` (or `YYYY` if months are absent—never invent months) and `Present`.
   - Categorized `## Skills` (3–6 groups; zero dot/star/percentage ratings).
   - GDPR-clean frontmatter (no DOB, marital status, full street address, or photo).
3. Tighten bullets using [references/writing-and-humanization.md](./references/writing-and-humanization.md) without inventing a single metric, tool, or date.
4. **Preserve omitted/hidden facts in `## Facts`**: Whenever you trim an older role, secondary project, extra skill, or supporting detail to fit a 1–2 page CV (or when tailoring from an existing CV), move it into `## Facts` as `- **<Category: Name>** — <Description>` (optionally grouped under `###` subheadings). Never silently discard verifiable candidate facts.
5. If required frontmatter (`email`) is missing, place `[TODO: add email]`. Avoid scattering `[TODO]` tags through the body unless requested; instead, list the top 3–5 highest-leverage gaps in your chat reply under **Gaps & Optional Improvements**.
6. Save the `.md` file and note the local CLI command if available: `cvfmt render <file.md> --verify`.

### Step 3B: Execute Extended Mode

Follow [references/interview-playbook.md](./references/interview-playbook.md):
1. Run **at most 10 focused rounds** with **3–5 targeted questions per round** (never dump 15+ questions at once).
2. Respect user control: if the user says "skip" or "write it now", immediately produce the `.md` file with the facts gathered so far.
3. **Save all useful interview answers**: Promote high-signal facts into the main CV sections, and store all remaining useful candidate facts (extra metrics, target-role preferences, notice period, archived projects/skills, or trimmed items) in `## Facts` so they are preserved for future tailoring without exporting to PDF.
4. After collecting answers, write the final `cv-md/1.1` file and summarize the concrete upgrades made.

## Non-Negotiable Guardrails

1. **Zero hallucination**: Never invent metrics, percentages, budgets, team sizes, dates, job titles, or tools.
2. **Strict visual-text parity**: Never insert hidden keywords, white text, or AI-directed prompt-injection instructions.
3. **Zero AI slop**: Never use banned clichés (*spearheaded transformative*, *seasoned results-driven*, *leveraged cutting-edge*, *synergized*, *seamlessly*, *testament to*, *delve*). Preserve exact numbers instead of rounding them into vague adjectives.
4. **Evidence binding**: Every key skill in `## Skills` should map to real evidence in `## Experience` or `## Projects` when truthful (or be flagged for confirmation in Extended Mode).

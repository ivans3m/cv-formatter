# Specification: Agent Skills (`skills/cv-formatter` & `skills/cv-tailor`)

**Status:** v1.1 *(shipped in `v0.2.0`)*  
**Standard:** Open Agent Skills Specification ([agentskills.io](https://agentskills.io/specification))  
**Data-Model Contract:** Operates exclusively on valid `cv-md/1.1` Markdown files defined in [spec-cv-markdown.md](./spec-cv-markdown.md) (backward-compatible with `cv-md/1.0`).

> **Positioning:** These skills are optional, portable agent workflows built *on top of* the `cv-md/1.1` data model. Because all state lives inside the plain-text `.md` file (including the non-exported `## Facts` memory bank), any LLM harness can run these playbooks without proprietary state or vendor lock-in.

---

## 1. Packaging & Progressive Disclosure

Both skills follow the portable `agentskills.io` directory layout so they work across Antigravity, Claude Code, Codex, Cursor, and other compatible harnesses:

```text
skills/
├── cv-formatter/
│   ├── SKILL.md                          # Frontmatter + Silent/Extended router + guardrails
│   ├── references/
│   │   ├── schema-v1.md                  # Concise reference copy of cv-md/1.1 rules
│   │   ├── eu-and-ats-rules.md           # EU conventions, CEFR, GDPR, ATS constraints
│   │   ├── writing-and-humanization.md   # XYZ/CAR formulas, banned AI clichés, tone rules
│   │   └── interview-playbook.md         # Question prioritization for Extended Mode
│   └── assets/
│       └── example-eu-cv.md              # Golden cv-md/1.1 reference example with ## Facts
└── cv-tailor/
    ├── SKILL.md                          # Frontmatter + Strict/Dreamer tailoring router
    ├── references/
    │   ├── tailoring-playbook.md         # Strict JD alignment workflow
    │   ├── dreamer-playbook.md           # Autonomous reach-role gap analysis + markers
    │   └── strict-vs-dreamer.md          # Mode selection guide
    └── assets/
        └── example-tailored-cv.md        # Golden tailored cv-md/1.1 example
```

### `cv-formatter` Frontmatter
```yaml
---
name: cv-formatter
description: Rewrites any CV, resume, LinkedIn export, or career notes into the standardized cv-md/1.1 Markdown format optimized for humans, EU/international ATS parsers, and LLM screeners. Supports silent mode (direct faithful rewrite), extended mode (guided follow-up questions to uncover missing impact, metrics, and EU context), and a non-exported ## Facts memory bank so tailoring never loses candidate data.
license: MIT
metadata:
  version: "1.1"
  schema: "cv-md/1.1"
---
```

---

## 2. Supported Inputs & Lifecycle Workflows

All three file roles use the exact same `cv-md/1.1` schema:

1. **Conversion / Cleanup (`cv-formatter`)**: Existing PDF, DOCX, TXT, HTML, LaTeX, LinkedIn export, or unstructured notes → `cv.md`.
2. **Master CV Creation (`cv-formatter`)**: Full career history → `cv-master.md` (same `cv-md/1.1` schema, uncapped length, rich `## Facts` memory bank).
3. **Role Tailoring (`cv-tailor`)**: `cv-master.md` (or any existing `cv.md`) + target Job Description → tight 1–2 page `cv-<target>.md`. **Always carries `## Facts` forward**, promotes relevant verified facts from `## Facts` when truthful, and parks trimmed items under `## Facts` → `### Archived for <tailor_target>` so every `.md` file remains lossless.

---

## 3. Mode Selection Contract

| User Intent / Cue | Skill & Mode Activated |
| :--- | :--- |
| "Convert/format/rewrite my CV", "silent mode", "just clean it up", no interview requested | `cv-formatter` — **Silent Mode** |
| "Extended mode", "interview me", "help me improve/strengthen my CV", "ask follow-up questions" | `cv-formatter` — **Extended Mode** |
| Ambiguous request on a thin/incomplete draft | Default to **Silent Mode**, deliver a clean `.md` immediately, and offer a concise 1-line option to run **Extended Mode**. |
| Master CV + job description, "tailor", "match this JD", ready to apply | `cv-tailor` — **Strict Mode** (`tailor_mode: strict`) |
| "Dreamer mode", "imagine the strongest CV", reach-role gap analysis | `cv-tailor` — **Dreamer Mode** (`tailor_mode: dreamer`) |

---

## 4. `cv-formatter`: Silent Mode Contract

1. **Fact Inventory**: Read the entire input (including any existing `## Facts`) and extract all verifiable facts (roles, companies, dates, locations, tools, numbers, education, languages, links, preferences).
2. **Schema Normalization**:
   - Map all sections to canonical `##` headings (or recognized `nl`/`de`/`fr` EU equivalents).
   - Normalize dates to `YYYY-MM` (or `YYYY` if months are absent—never fabricate months).
   - Group flat skill lists into 3–6 logical categories; remove numeric/star/percentage self-ratings.
   - Strip GDPR-unnecessary PII (DOB, marital status, full street address, photo references) unless explicitly requested.
3. **Prose Tightening**:
   - Convert passive duties into crisp, active statements.
   - Keep bullets to 1–2 lines, preserving exact numbers, tools, and domain vocabulary.
   - Enforce all anti-AI-slop rules (Section 7).
4. **Lossless Archiving (`## Facts`)**:
   - Never silently drop verifiable roles, projects, or metrics when trimming for length; move them into `## Facts` as `- **<Category: Name>** — <Description>`.
5. **Zero-Hallucination Rule**:
   - Never invent metrics, percentages, team sizes, revenue, dates, or skills.
   - If required frontmatter (`email`) is missing, insert `[TODO: add email]`.
   - Avoid scattering `[TODO]` tags through the body unless asked; list the top 3–5 concrete additions under **Gaps & Optional Improvements** in the chat reply.
6. **Write Output**: Save the standardized `cv-md/1.1` file and optionally note the supporting `cvfmt render <file.md> --verify` command.

---

## 5. `cv-formatter`: Extended Mode Contract (Guided Interview)

Extended Mode runs **batched rounds of 3–5 high-leverage questions** (typically 2–3 rounds; capped at 10 rounds max—never an overwhelming 20-question dump). The user can say "skip" or "enough, write it now" at any point.

- **Round 1 — Target, EU Context & Logistics:** Target role/seniority, target market/work authorization, CEFR language levels, availability/notice period, and target page length.
- **Round 2 — Impact & Evidence Mining (Top 2–3 Roles):** Concrete role-specific questions for scale, outcomes, promotion boundaries, and ungrounded `## Skills` claims.
- **Round 3 — Pruning & Finalization:** Propose trims to fit 1–2 pages; promote high-signal answers into the public CV and preserve all remaining useful context inside `## Facts`.

---

## 6. `cv-tailor`: Strict vs. Dreamer Tailoring Contract

- **Strict Mode (`tailor_mode: strict`, `tailor_target: "<label>"`):**
  - Rewrites `headline` and `## Summary` using JD vocabulary backed strictly by existing evidence.
  - Reorders and tightens `## Experience`, `## Projects`, and `## Skills` for JD alignment.
  - Demotes low-signal items into `## Facts` → `### Archived for <tailor_target>` (never deletes).
  - Forbids any `**(Aspirational)**` markers.
- **Dreamer Mode (`tailor_mode: dreamer`, `tailor_target: "<label>"`):**
  - Identifies concrete gaps between the candidate's verified history and the target JD without running a long questionnaire.
  - Drafts plausible gap-fill bullets explicitly prefixed with `**(Aspirational)** ` in renderable sections and logs the gap rationale under `## Facts` → `### Dreamer rationale`.
  - Summarizes **Verified vs. Aspirational** items in chat so the user reviews every speculative line before ever exporting a real application.

---

## 7. Editorial & Anti-AI-Slop Guardrails

- **Banned clichés:** Never output *"spearheaded transformative"*, *"seasoned results-driven"*, *"leveraged cutting-edge"*, *"orchestrated seamless"*, *"synergy"*, *"delve"*, *"testament to"*, *"passionate self-starter"*, *"dynamic fast-paced environment"*.
- **Preserve numbers:** Never replace concrete numbers with vague adjectives.
- **Concrete verbs:** Prefer plain, accurate verbs (*built, reduced, migrated, led, shipped, designed, cut, automated, launched, scaled, audited*).
- **Evidence binding:** Every major skill in `## Skills` should map to real evidence in `## Experience` or `## Projects` when truthful.
- **Strict visual-text parity:** Never insert hidden keywords, white text, or AI-directed prompt-injection phrases.

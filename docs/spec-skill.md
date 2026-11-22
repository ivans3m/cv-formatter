# Specification: CV-Rewriting Agent Skill (`skills/cv-formatter`)

**Status:** Draft v1.1  
**Standard:** Open Agent Skills Specification ([agentskills.io](https://agentskills.io/specification))  
**Output Contract:** Produces valid `cv-md/1.1` Markdown files defined in [spec-cv-markdown.md](./spec-cv-markdown.md) (backward-compatible with `cv-md/1.0`).

---

## 1. Packaging & Progressive Disclosure

The skill follows the portable `agentskills.io` directory layout so it works across Antigravity, Claude Code, Codex, Cursor, and other compatible harnesses:

```text
skills/cv-formatter/
├── SKILL.md                          # Frontmatter + workflow router + core guardrails
├── references/
│   ├── schema-v1.md                  # Concise reference copy of cv-md/1.0 rules
│   ├── eu-and-ats-rules.md           # EU conventions, CEFR, GDPR, ATS constraints
│   ├── writing-and-humanization.md   # XYZ/CAR formulas, banned AI clichés, tone rules
│   └── interview-playbook.md         # Question prioritization for Extended Mode
└── assets/
    └── example-eu-cv.md              # Golden cv-md/1.0 reference example
```

### `SKILL.md` Frontmatter
```yaml
---
name: cv-formatter
description: Rewrites any CV, resume, LinkedIn export, or career notes into the standardized cv-md/1.0 Markdown format optimized for humans, EU/international ATS parsers, and LLM screeners. Supports silent mode (direct faithful rewrite) and extended mode (guided follow-up questions to uncover missing impact, metrics, and EU context).
license: MIT
metadata:
  version: "1.0"
  schema: "cv-md/1.0"
---
```

---

## 2. Supported Inputs & Workflows

1. **Conversion / Cleanup**: Existing PDF, DOCX, TXT, HTML, LaTeX, LinkedIn PDF export, or unstructured notes → `cv.md`.
2. **Master CV Creation**: Full career history → `cv-master.md` (same `cv-md/1.1` schema, no 2-page cap, with a `## Facts` memory bank).
3. **Role Tailoring**: `cv-master.md` (or existing `cv.md`) + target Job Description → tight 1–2 page `cv-<target>.md` preserving 100% factual honesty while prioritizing relevant achievements and exact target terminology. **Always carry `## Facts` forward** into tailored `.md` files, promote relevant facts from `## Facts` when truthful, and move trimmed/hidden items into `## Facts` so no candidate data is lost.

---

## 3. Mode Selection Contract

| User Intent / Cue | Mode Activated |
| :--- | :--- |
| "Convert/format/rewrite my CV", "silent mode", "just clean it up", no interview requested | **Silent Mode** |
| "Extended mode", "interview me", "help me improve/strengthen my CV", "ask follow-up questions" | **Extended Mode** |
| Ambiguous request on a very thin/incomplete draft | Default to **Silent Mode**, deliver a clean draft immediately, and offer a concise 1-line option to run **Extended Mode** for missing metrics/context. |

---

## 4. Silent Mode Execution Contract

1. **Fact Inventory**: Read the entire input and extract all verifiable facts (roles, companies, dates, locations, tools, numbers, education, languages, links).
2. **Schema Normalization**:
   - Map all sections to canonical `##` headings (`Summary`, `Experience`, `Projects`, `Skills`, `Education`, `Languages`, `Certifications`, `Publications`).
   - Normalize dates to `YYYY-MM` (or `YYYY` if months are absent in the source—never fabricate months).
   - Group flat skill lists into 3–6 logical categories; remove numeric/star/percentage self-ratings.
   - Strip GDPR-unnecessary PII (DOB, marital status, full street address, photo references) unless explicitly requested by the user.
3. **Prose Tightening**:
   - Convert passive duties into crisp, active statements.
   - Keep bullets to 1–2 lines, preserving exact numbers, tools, and domain vocabulary.
   - Enforce all anti-AI-slop rules (Section 6).
4. **Zero-Hallucination Rule**:
   - Never invent metrics, percentages, team sizes, revenue, dates, or skills.
   - If required frontmatter (`email`) is missing from the input, insert `[TODO: add email]`.
   - Do **not** pollute the body with dozens of `[TODO]` tags unless asked; instead, output a brief **Gaps & Optional Improvements** section in the chat reply listing the top 3–5 concrete additions that would strengthen the CV (e.g., CEFR levels, work authorization, specific metrics for the top role).
5. **Write Output**: Save the standardized `.md` file and, if the local CLI is available, note the command to validate and render it to PDF.

---

## 5. Extended Mode Execution Contract (Guided Interview)

Extended Mode runs **at most 3 focused rounds**, with **3–5 high-leverage questions per round** (never an overwhelming 20-question dump). The user can say "skip" or "enough, write it now" at any point.

### Round 1: Target, EU Context & Logistics
- Target role title(s) and seniority level?
- Target market/geography (e.g., Netherlands, DACH, UK, remote EU) and work authorization note (if any)?
- Languages and CEFR levels (`A1–C2` / `Native`)?
- Target length (1 page vs. 2 pages) and optional job description to tailor against?

### Round 2: Impact & Evidence Mining (Top 2–3 Roles)
Ask concrete, role-specific questions targeting weak or vague bullets found in the source:
- **Scale**: How many users, requests/sec, clients, markets, or team members?
- **Outcome**: What changed (latency, revenue, cost, hours saved, conversion, reliability, delivery speed)?
- **Clarifications**: Resolve overlapping dates (freelance vs. full-time), internal promotions, or key skills listed in `Skills` that have no evidence in `Experience`.

### Round 3: Pruning & Finalization
- Propose specific trims for low-signal or >10-year-old items to fit cleanly within 1–2 pages.
- Once confirmed (or if no pruning is needed, skip Round 3), write the final `cv-md/1.0` file and summarize the key upgrades made.

---

## 6. Editorial & Anti-AI-Slop Guardrails

- **Banned clichés**: Never output *"spearheaded transformative"*, *"seasoned results-driven"*, *"leveraged cutting-edge"*, *"orchestrated seamless"*, *"synergy"*, *"delve"*, *"testament to"*, *"passionate self-starter"*, *"dynamic fast-paced environment"*.
- **Preserve numbers**: Never replace concrete numbers with vague adjectives.
- **Concrete verbs**: Prefer plain, accurate verbs (*built, reduced, migrated, led, shipped, designed, cut, automated, launched, scaled, audited*).
- **Evidence binding**: Every major technology/skill in `## Skills` should appear in at least one `Experience` or `Projects` bullet when truthful.
- **Strict visual-text parity**: Never insert hidden keywords, white text, or AI-directed prompt-injection phrases.

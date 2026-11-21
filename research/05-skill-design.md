# Research 05: Agent Skill Architecture (Open Standard `SKILL.md`)

## Executive Summary

The CV-rewriting skill will be authored using the open **`agentskills.io` `SKILL.md` standard**, making it portable across Antigravity, Claude Code, Codex, Cursor, and other compatible agent harnesses. Using **progressive disclosure**, the skill keeps its top-level `SKILL.md` crisp and focused on workflow orchestration, while delegating detailed domain rules (EU conventions, ATS rules, anti-AI-slop rules, and the Markdown schema spec) into `references/` files loaded on demand.

---

## 1. Open Standard Packaging (`agentskills.io`)

```text
skills/cv-formatter/
├── SKILL.md                          # Core workflow, mode selection, guardrails
├── references/
│   ├── schema-v1.md                  # Exact canonical Markdown CV specification
│   ├── eu-and-ats-rules.md           # EU market norms, CEFR, GDPR, ATS constraints
│   ├── writing-and-humanization.md   # XYZ/CAR formulas, banned AI clichés, tone rules
│   └── interview-playbook.md         # Question bank & prioritization for Extended Mode
└── assets/
    └── example-eu-cv.md              # Golden reference example
```

### Frontmatter Contract
- `name: cv-formatter` (lowercase, hyphenated, matches directory name).
- `description`: Clear trigger description explaining *what* the skill does (rewrites any CV into standardized human- and LLM-readable Markdown in silent or extended mode, tailored for EU & international hiring) and *when* to activate it.

---

## 2. Input Ingestion Strategy

Users will supply messy, heterogeneous inputs:
- Existing PDFs or DOCX files (potentially multi-column or broken).
- LinkedIn PDF exports or pasted profile text.
- Raw career notes, older Markdown/LaTeX CVs, or a `cv-master.md` + target job description.

**Ingestion Guardrail**: Before rewriting, the skill must extract and inventory all verifiable facts (roles, companies, dates, locations, tools, numbers, education, languages) so nothing is silently dropped or hallucinated during restructuring.

---

## 3. Two Operating Modes

### Mode A: Silent Mode (Fast, Zero-Friction Rewrite)
*When to use*: User asks to "convert/format/clean up this CV" without requesting an interview, or passes `--silent` / "just rewrite it".

**Behavior**:
1. Parse and normalize all source facts into the canonical Markdown schema (`schema: cv-md/1.0`).
2. Fix ATS & LLM failure modes: standardize section headings, normalize dates to `YYYY-MM`, group skills by category, remove visual-only ratings, strip unnecessary PII (DOB, marital status, full street address).
3. Tighten prose: replace passive duties (*"Responsible for..."*) with active, crisp phrasing while keeping **100% factual fidelity**.
4. **Strict Anti-Hallucination Contract**:
   - **Never invent metrics, team sizes, revenue figures, or tools** not present in the source.
   - Where high-value information is missing (e.g., CEFR language levels, work authorization, or unquantified impact on a recent role), leave clean inline comments or a short **Gaps & Suggestions** summary *outside* the final `.md` file (or `[TODO: ...]` markers if the user explicitly wants an editable draft) so the candidate knows what to fill in.
5. Output the finished `.md` file ready for the PDF CLI.

### Mode B: Extended Mode (Guided Career Interview)
*When to use*: User asks for "extended mode", "deep rewrite", "ask me questions", or wants to significantly strengthen a weak/outdated CV (or tailor from a master CV to a specific job description).

**Behavior**:
Instead of dumping 25 overwhelming questions at once, the skill runs a **structured, batched interview (2–3 focused rounds max, 3–5 high-leverage questions per round)**:

- **Round 1 — Targeting & EU Context**:
  - Target role title(s) and seniority level?
  - Target market/geography (e.g., NL, DACH, UK, remote EU) and work authorization status to display?
  - Languages & CEFR levels (`A1–C2` / `Native`)?
  - Target length (1 page vs. 2 pages) and whether a specific job description is being targeted?
- **Round 2 — Impact & Evidence Mining (Most Recent 2–3 Roles)**:
  - Targeted questions on vague bullets: *"At Acme, you 'improved API performance'—do you recall approximate latency/throughput gains, user scale, or cost savings?"*
  - Scope questions: team size, budget, users, customers, or business outcome.
  - Clarifying promotions, overlapping consulting engagements, or ungrounded skills in the Skills section.
- **Round 3 — Pruning, Positioning & Confirmation**:
  - Propose what to trim (older roles >10 years, irrelevant coursework, low-signal bullets) to hit the 1–2 page target cleanly.
  - Write the standardized `.md` file and summarize exact improvements made.

---

## 4. Editorial & Anti-AI-Slop Guardrails

To ensure the rewritten CV passes both human skepticism and LLM rubric evaluation:

1. **Banned cliché list**: Strictly forbid hollow AIisms (*"spearheaded transformative"*, *"seasoned professional"*, *"leveraged cutting-edge"*, *"synergized"*, *"delved"*, *"testament to"*, *"seamlessly"*, *"passionate results-driven"*).
2. **Fact preservation**: Never round concrete numbers into adjectives (*"99.95% uptime"* must never become *"high reliability"*).
3. **Varied, concrete verbs**: Use plain, accurate engineering/product/business verbs (*built, reduced, migrated, led, designed, shipped, cut, automated, negotiated*).
4. **Evidence alignment**: Every major skill in `## Skills` should map to concrete usage in `## Experience` or `## Projects` (or be flagged for confirmation in Extended Mode).
5. **Zero hidden tricks**: Never insert invisible text, keyword stuffing blocks, or LLM prompt-injection strings.

---

## References

- [Agent Skills Open Standard Specification](https://agentskills.io/specification)

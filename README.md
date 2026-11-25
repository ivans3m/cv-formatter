# CV Formatter (`cv-md/1.1`)

**A plain-text Markdown data model for career history, designed for AI-driven workflows, human readability, and deterministic ATS/PDF output.**

Most CV tools start from layout templates and leave your career data trapped inside PDFs, DOCX files, or brittle JSON blobs. **CV Formatter** flips that around: the core product is **`cv-md/1.1`**, a strict yet human-readable YAML + CommonMark data model that makes your career history lossless, diffable, and natively operable by any LLM or agent.

The repository also ships optional reference tooling built on top of the format: open-standard agent skills (`skills/cv-formatter/`, `skills/cv-tailor/`) and a zero-dependency local Python + Typst CLI (`cvfmt`) for validation, importing, tailoring, and minimalist PDF rendering.

**Repository:** [github.com/ivans3m/cv-formatter](https://github.com/ivans3m/cv-formatter) · **License:** [MIT](LICENSE) · [![CI](https://github.com/ivans3m/cv-formatter/actions/workflows/ci.yml/badge.svg)](https://github.com/ivans3m/cv-formatter/actions/workflows/ci.yml) · **Version:** `v0.2.0` (`cv-md/1.1`, backward-compatible with `cv-md/1.0`)

---

## The Data Model (`cv-md/1.1`)

A `cv-md/1.1` file is a single UTF-8 Markdown document divided into **three semantic layers**:

1. **Structured YAML frontmatter** — Typed identity, contact, EU compliance (`location`, `work_authorization`, `availability`), locale/paper metadata (`lang`, `paper`, `accent`), and tailoring state (`tailor_mode`, `tailor_target`). GDPR-unnecessary PII (date of birth, street address, marital status, photo) is omitted by default.
2. **Canonical CommonMark body (public view)** — Strictly typed `##` sections (with built-in English, Dutch `nl`, German `de`, and French `fr` aliases), unambiguous `### Role — Company` and `#### Sub-role` hierarchies, ISO dates (`YYYY-MM – Present`), categorized `## Skills`, CEFR `## Languages`, and verifiable `## Certifications`. Everything here renders 1:1 to PDF.
3. **`## Facts` memory bank (private, Markdown-only)** — An optional non-exported section inside the same `.md` file that holds trimmed roles, archived projects, extra metrics, interview notes, and preferences. It **never** exports to PDF, making every CV file lossless and re-tailorable.

```markdown
---
schema: cv-md/1.1
name: Lukas Müller
headline: Senior Backend Engineer
location: Amsterdam, Netherlands
work_authorization: EU Citizen
availability: 1 month notice
email: lukas.mueller@example.eu
links:
  - label: GitHub
    url: https://github.com/lukasmueller
paper: a4
lang: en
tailor_mode: strict
tailor_target: Staff Backend @ Acme
---

## Summary

Backend engineer with 7 years of experience building high-throughput payment and data platforms in Go and Python across European fintech teams.

## Experience

### Acme Payments
*2021-03 – Present | Amsterdam, Netherlands (Hybrid)*

#### Senior Backend Engineer *(2023-04 – Present)*
- Reduced p95 checkout API latency from 420ms to 110ms across 12 Go services handling 40K req/s.
- Led zero-downtime migration of a €180M/month SEPA settlement pipeline to event-driven Kafka workers.

## Skills

- **Languages:** Go, Python, SQL
- **Infrastructure:** PostgreSQL, Redis, Kafka, Kubernetes, Terraform

## Languages

- **German:** Native
- **English:** C2 (Proficient / Working Language)
- **Dutch:** B1 (Intermediate)

## Facts

### Archived for Staff Backend @ Acme
- **Project: Legacy Billing CLI** — Maintained internal Python invoicing scripts (2020); cut to keep PDF at 1 page.
- **Preference: Notice Period** — 1 month; open to remote EU or hybrid Amsterdam.
```

See the full contract, all 14 canonical sections, localized EU headings, and validation rules in [docs/spec-cv-markdown.md](docs/spec-cv-markdown.md).

---

## Why This Data Model Works for AI-Driven Workflows

- **Native to both humans and LLMs:** JSON is painful to write and review; raw YAML traps prose in escaped strings; PDF/DOCX scramble layout and text order. Canonical CommonMark gives LLMs clean structural boundaries while remaining effortless to read, edit, and `git diff`.
- **One schema across the entire career lifecycle:** No proprietary template tags or conditional macros. A 6-page `cv-master.md` archive and a tight 2-page `cv-acme.md` application obey the exact same grammar.
- **Lossless tailoring via `## Facts`:** Compressing a career into two pages is usually destructive. Because `## Facts` travels inside every `.md` file and never leaks into the PDF, agents park cut bullets there during tailoring and promote them back when another role calls for them.
- **Explicit honesty boundaries (`strict` vs. `dreamer`):** Agents tend to quietly embellish unless constrained by the format. `tailor_mode: strict` forbids unverified claims; `tailor_mode: dreamer` allows reach-role gap exploration only when explicitly prefixed with `**(Aspirational)**` — which validators flag and the PDF renderer strips by default.
- **Deterministic entity binding & evidence grounding:** Predictable `###` / `####` / `*YYYY-MM – Present | Location*` syntax binds dates, promotions, and impact bullets to the right employer, letting both linters and AI screeners verify that every skill in `## Skills` is backed by real evidence in `## Experience` or `## Projects`.
- **Strict visual-text parity:** Zero hidden keywords, zero multi-column interleaving, zero icon-only ratings. What a hiring manager reads is 100% identical to what an ATS parser or LLM rubric extracts.

---

## Supporting Bonus: Agent Skills & Local CLI

Everything below is optional reference tooling built around `cv-md/1.1`. You can use the format with any editor or LLM on its own, or drop in these tools to automate ingestion, tailoring, validation, and PDF export.

### Open-Standard Agent Skills (`skills/`)

Both skills follow the portable [agentskills.io](https://agentskills.io/specification) `SKILL.md` standard (Antigravity, Claude Code, Codex, Cursor, and compatible agents):

- **[`skills/cv-formatter/`](skills/cv-formatter/)** — Converts any messy CV, LinkedIn export, or career notes into canonical `cv-md/1.1`:
  - **Silent Mode:** Faithful restructuring with zero invented metrics; trimmed items move safely to `## Facts`.
  - **Extended Mode:** Focused, batched follow-up interview rounds to uncover missing scope, numbers, and EU context.
- **[`skills/cv-tailor/`](skills/cv-tailor/)** — Tailors a master or existing `cv-md/1.1` file to a target job description while carrying `## Facts` forward:
  - **Strict Mode:** Verified evidence only, aligned with target terminology.
  - **Dreamer Mode:** Autonomous reach-role gap analysis with explicit `**(Aspirational)**` markers and gap rationales logged under `## Facts`.

### Local Utility CLI (`cvfmt`)

A lightweight Python + bundled Typst CLI (no TeX Live, Cairo, or browser binary required) that validates `cv-md/1.1`, imports LinkedIn/URLs, runs deterministic strict tailoring, and compiles a Warm Editorial Tagged PDF (`PDF/UA-1`, IBM Plex Sans, A4 default) with dual-parser text-layer verification.

```bash
git clone https://github.com/ivans3m/cv-formatter.git
cd cv-formatter
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"

# Scaffold & validate a cv-md/1.1 file (schema, ATS headings, CEFR, evidence rules)
.venv/bin/cvfmt init cv.md
.venv/bin/cvfmt validate cv.md

# Render to minimalist A4 PDF (IBM Plex Sans, Tagged PDF/UA-1) and verify text layer + ## Facts isolation
.venv/bin/cvfmt render cv.md --verify
.venv/bin/cvfmt render cv.md --accent "#0F766E" --paper letter -o cv-us.pdf --verify

# Deterministic strict tailoring (archives trimmed items into ## Facts) or dreamer prep bundle
.venv/bin/cvfmt tailor job.txt --base cv-master.md -o cv-acme.md --mode strict --target-title "Senior Backend Engineer"
.venv/bin/cvfmt tailor job.txt --base cv-master.md --mode dreamer --prepare ./tailor-bundle/

# Optional importers: LinkedIn PDF/GDPR export or public CV URL → cv-md/1.1 (+ optional PDF)
.venv/bin/cvfmt linkedin Profile.pdf --pdf -o cv.pdf --verify
.venv/bin/cvfmt from-url https://ivan.diuldia.com/cv/ --pdf -o cv.pdf --verify
```

### Verification & Tests

```bash
.venv/bin/pytest -v
```

The test suite (**39 tests**) covers schema validation, writer round-trips, strict tailoring, aspirational guards, localized `nl`/`de`/`fr` headings, LinkedIn/URL importers, and dual-parser (`pypdf` + `pdfplumber`) PDF round-trips across EU golden fixtures—including Unicode/diacritic stress cases (`Łukasz Żółć-François`, `Zürich`, `München`, `Straße`, `€`) and `## Facts` anti-leak checks.

An optional blind LLM extraction benchmark lives in [`benchmarks/llm_extraction.py`](benchmarks/llm_extraction.py) to verify that models recover 100% of entities from rendered PDF text layers:

```bash
.venv/bin/python benchmarks/llm_extraction.py prepare --out /tmp/cvfmt-bench
# … run your model on the prepared prompts …
.venv/bin/python benchmarks/llm_extraction.py grade --bench-dir /tmp/cvfmt-bench --predictions /path/to/predictions.json
```

---

## Documentation

| Document | Focus |
| --- | --- |
| **[docs/spec-cv-markdown.md](docs/spec-cv-markdown.md)** | **Core data model (`cv-md/1.1`)** — schema, `## Facts`, localized EU headings, epistemic markers, validation rules, golden example |
| [docs/spec-skill.md](docs/spec-skill.md) | Supporting agent skill contracts (`cv-formatter` and `cv-tailor`) |
| [docs/spec-pdf-renderer.md](docs/spec-pdf-renderer.md) | Supporting `cvfmt` CLI, Typst pipeline, Warm Editorial typography, and verification gates |
| [docs/README.md](docs/README.md) | Documentation index and repository layout |
| [docs/TODO.md](docs/TODO.md) | Completed milestones and backlog |

## Project Structure

```text
.
├── docs/                      # Core data-model spec (cv-md/1.1), tool specs, backlog
├── research/                  # Domain research (ATS parsing, LLM screening, schema design)
├── skills/
│   ├── cv-formatter/          # Open-standard SKILL.md (Silent & Extended modes)
│   └── cv-tailor/             # Open-standard SKILL.md (Strict & Dreamer tailoring)
├── src/cvfmt/                 # Reference Python + Typst CLI + bundled IBM Plex Sans fonts
├── tests/                     # Golden EU fixtures + 39-test pytest suite
├── benchmarks/                # Optional blind LLM PDF extraction benchmark
└── .agents/                   # Local only (gitignored): agent rules and notes
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for local setup, design guardrails, and PR guidelines. Read [docs/spec-cv-markdown.md](docs/spec-cv-markdown.md) before changing schema or validation behavior.

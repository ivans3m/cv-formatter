# Project TODO & Backlog

Living task tracker for **CV Formatter** (`cv-md/1.0` format, open-standard rewriting skill, and Python + Typst local CLI).

---

## Completed

- [x] **Project setup & git repo** — Created `docs/`, `research/`, `.gitignore`, `README.md`, and initial commit (`ee40291`).
- [x] **Phase 1–3 Research** (`research/01`–`07`) — Completed research on EU ATS parsing, LLM screening & EU AI Act, human recruiter UX, Markdown schema design, `agentskills.io` skill architecture, Typst vs. WeasyPrint/Playwright/LaTeX, and evaluation benchmarks.
- [x] **Formal v1 Specifications** (`docs/spec-*.md`) — Locked in `cv-md/1.0`, `agentskills.io` skill contract, and `cvfmt` Python + Typst + IBM Plex Sans CLI spec.
- [x] **Open-Standard CV-Rewriting Skill (`skills/cv-formatter/`)**:
  - [x] `SKILL.md` (frontmatter, Silent & Extended Mode router, zero-hallucination & anti-AI-slop guardrails).
  - [x] Progressive-disclosure references (`schema-v1.md`, `eu-and-ats-rules.md`, `writing-and-humanization.md`, `interview-playbook.md`).
  - [x] Golden example `assets/example-eu-cv.md`.
- [x] **Local Markdown-to-PDF CLI (`cvfmt`)**:
  - [x] Python package (`pyproject.toml`, `.venv`, `typst 0.15.2` wheel, `pydantic`, `typer`, `pypdf`, `pdfplumber`, `pytest`).
  - [x] Bundled official **IBM Plex Sans** TTF weights (`Regular`, `Medium`, `SemiBold`, `Bold`, `Italic`) + OFL license.
  - [x] `cv-md/1.0` parser, validator, and ATS/LLM linter (`cvfmt validate`).
  - [x] Minimalist Typst generator (`A4` default + `letter`, single-column, contact info in body flow, `sticky: true` headings, `ligatures: false`, Tagged PDF / `PDF/UA-1`).
  - [x] `cvfmt render` (`-o`, `--paper`, `--allow-todos`, `--strict`, `--verify`) and `cvfmt init`.
- [x] **Verification & Golden Benchmarks**:
  - [x] 4 anonymized EU golden fixtures (`junior-eu-1page.md`, `senior-eu-2page.md`, `consultant-multirole.md`, `diacritics-stress.md`).
  - [x] Automated `pytest` suite (10/10 passing in <1s) verifying schema rules, `pypdf` + `pdfplumber` round-trip reading order, EU diacritics (`ü`, `ö`, `ä`, `ß`, `é`, `ł`, `ø`, `€`), `fi`/`fl` ligature integrity, contact visibility, and clickable URI annotations.
  - [x] Visual PNG review of rendered golden PDFs + Warm Editorial redesign (default `#71717A` light-grey accent, `--accent` hex CLI flag, fixed list interline spacing).
  - [x] **LLM Structured Extraction Benchmark** (`benchmarks/llm_extraction.py`) — Blind LLM extraction on raw `pdfplumber` text of all 4 rendered EU golden PDFs achieved **100% accuracy** on identity, roles/companies (including nested promotions), dates, CEFR languages, education, and quantified metrics.
- [x] **LinkedIn-to-PDF Export (`cvfmt linkedin`)**:
  - [x] Supports both LinkedIn's official GDPR Data Export (`.zip` / CSV folder) and 2-column "Save to PDF" (`Profile.pdf`) using column-aware `pdfplumber` cropping.
  - [x] Auto-groups consecutive roles at the same company into `####` sub-roles, maps LinkedIn language labels to EU CEFR levels, and supports one-shot `--pdf --accent --verify`.
- [x] **Public URL Import (`cvfmt from-url`)**:
  - [x] Supports public HTML CV pages, JSON Resume (`.json`) URLs, and raw `cv-md/1.0` URLs with optional `--pdf --accent --verify`.
  - [x] Detects gated `linkedin.com/in/` URLs and prints the 2-step `Save to PDF -> cvfmt linkedin` instructions.

---

## Up Next

- [ ] **Test the `skills/cv-formatter` skill on a real CV** (both Silent Mode and Extended Mode) and refine edge cases.

---

## Backlog

- [ ] **Direct LinkedIn profile URL import (without manual export)**
  - *Comment*: LinkedIn blocks direct unauthenticated HTTP fetches (HTTP 999 / authwall). Explore ToS-compliant approaches later (e.g., official OAuth / user-authenticated browser extension or BYO compliant enrichment API key).
- [ ] **Polish PDF design**
  - *Comment*: Further refine the Warm Editorial layout's visual craft—micro-typography, long role/company title wrapping (avoiding awkward `. Company` line breaks), page-2 balance/density, and optional modern theme presets (`--theme editorial|neon|swiss`) while preserving 100% single-column ATS/LLM readability.
- [ ] **Optional `Inter` typeface theme flag** (`--font ibm-plex|inter`) once IBM Plex Sans v1 is solid.
- [ ] **Localized EU canonical section heading presets** (e.g., `de`, `nl`, `fr`) for non-English EU applications.
- [ ] **Optional DACH photo toggle** (strictly opt-in, off by default, keeping linear text order intact).

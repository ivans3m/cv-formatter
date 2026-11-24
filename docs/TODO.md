# Project TODO & Backlog

Living task tracker for **CV Formatter** (`cv-md/1.0` format, open-standard rewriting skill, and Python + Typst local CLI).

**Repo:** [github.com/ivans3m/cv-formatter](https://github.com/ivans3m/cv-formatter) · **Branch:** `main` · **License:** MIT

---

## Completed

- [x] **Project setup & git repo** — Created `docs/`, `research/`, `.gitignore`, `README.md`, and initial history (`ee40291` …).
- [x] **GitHub publication (v0.1.0 source)** — `origin` → [ivans3m/cv-formatter](https://github.com/ivans3m/cv-formatter); root `LICENSE` (MIT); `pyproject.toml` `license-files`; merged remote initial commit; `main` tracking `origin/main`.
- [x] **Repository hygiene & local-only paths** — `.gitignore` covers `.agents/` and `docs/blog/`; `tests/` (fixtures + pytest) tracked on GitHub again for clone-and-verify workflows.
- [x] **Phase 1–3 Research** (`research/01`–`07`) — Completed research on EU ATS parsing, LLM screening & EU AI Act, human recruiter UX, Markdown schema design, `agentskills.io` skill architecture, Typst vs. WeasyPrint/Playwright/LaTeX, and evaluation benchmarks.
- [x] **Formal v1 Specifications** (`docs/spec-*.md`) — Locked in `cv-md/1.0`, `agentskills.io` skill contract, and `cvfmt` Python + Typst + IBM Plex Sans CLI spec.
- [x] **Open-Standard CV-Rewriting Skill (`skills/cv-formatter/`)**:
  - [x] `SKILL.md` (frontmatter, Silent & Extended Mode router, zero-hallucination & anti-AI-slop guardrails).
  - [x] Progressive-disclosure references (`references/schema-v1.md`, `references/eu-and-ats-rules.md`, `references/writing-and-humanization.md`, `references/interview-playbook.md`).
  - [x] Golden example `assets/example-eu-cv.md`.
- [x] **Local Markdown-to-PDF CLI (`cvfmt`)**:
  - [x] Python package (`pyproject.toml`, `.venv`, `typst 0.15.2` wheel, `pydantic`, `typer`, `pypdf`, `pdfplumber`, `pytest`).
  - [x] Bundled official **IBM Plex Sans** TTF weights (`Regular`, `Medium`, `SemiBold`, `Bold`, `Italic`) + OFL license.
  - [x] `cv-md/1.0` parser, validator, and ATS/LLM linter (`cvfmt validate`).
  - [x] Minimalist Typst generator (`A4` default + `letter`, single-column, contact info in body flow, `sticky: true` headings, `ligatures: false`, Tagged PDF / `PDF/UA-1`).
  - [x] `cvfmt render` (`-o`, `--paper`, `--allow-todos`, `--strict`, `--verify`) and `cvfmt init`.
- [x] **Verification & Golden Benchmarks**:
  - [x] 4 anonymized EU golden fixtures (`junior-eu-1page.md`, `senior-eu-2page.md`, `consultant-multirole.md`, `diacritics-stress.md`).
  - [x] Automated local `pytest` suite (**22/22** passing in ~1s) verifying schema rules, `pypdf` + `pdfplumber` round-trip reading order, EU diacritics (`ü`, `ö`, `ä`, `ß`, `é`, `ł`, `ø`, `€`), `fi`/`fl` ligature integrity, contact visibility, clickable URI annotations, LinkedIn/URL importers, and CLI error paths.
  - [x] Visual PNG review of rendered golden PDFs + Warm Editorial redesign (default `#71717A` light-grey accent, `--accent` hex CLI flag, fixed list interline spacing).
  - [x] **LLM Structured Extraction Benchmark** (`benchmarks/llm_extraction.py`) — Blind LLM extraction on raw `pdfplumber` text of all 4 rendered EU golden PDFs achieved **100% accuracy** on identity, roles/companies (including nested promotions), dates, CEFR languages, education, and quantified metrics.
- [x] **LinkedIn-to-PDF Export (`cvfmt linkedin`)**:
  - [x] Supports both LinkedIn's official GDPR Data Export (`.zip` / CSV folder) and 2-column "Save to PDF" (`Profile.pdf`) using column-aware `pdfplumber` cropping.
  - [x] Auto-groups consecutive roles at the same company into `####` sub-roles, maps LinkedIn language labels to EU CEFR levels, and supports one-shot `--pdf --accent --verify`.
- [x] **Public URL Import (`cvfmt from-url`)**:
  - [x] Supports public HTML CV pages, JSON Resume (`.json`) URLs, and raw `cv-md/1.0` URLs with optional `--pdf --accent --verify`.
  - [x] Detects gated `linkedin.com/in/` URLs and prints the 2-step `Save to PDF -> cvfmt linkedin` instructions.

- [x] **End-to-end Extended Mode Skill Test** — Tested `skills/cv-formatter` 2-round guided interview on Ivan's real CV (`ivan.diuldia.com/cv/`) tailored for a Netherlands Fractional CMO role, producing a validated, verified 2-page Warm Editorial PDF.
- [x] **Code Review & Hardening Pass** — Fixed LinkedIn `Profile.pdf` overwrite guard, capped `fetch_url` at 5 MB, added clean YAML/Pydantic CLI error handling, narrowed Typst font fallback, fixed `YYYY-MM` HTML date splitting, fixed `UNRESOLVED_TODO` line numbers and `[TODO]` email allowance, deduplicated `cli.py`, prevented orphan splits on compact `Skills`/`Languages` sections, and eliminated pytest warnings.
- [x] **Documentation sync (post-GitHub)** — Root and `docs/` README indexes updated for public repo layout, MIT license, tracked `tests/`, local-only `.agents/`, CLI quickstart, and 22-test verification story.
- [x] **Sync `spec-pdf-renderer.md` with v0.1.0 CLI** — Documented `linkedin`, `from-url`, `version`, importer flags, exit codes, URL fetch limits; fixed research/spec cross-links (`../research/…`, relative `docs/` paths; removed `file://` URLs).
- [x] **GitHub Actions CI** — Added `.github/workflows/ci.yml` running `pytest -v` and CLI smoke checks (`cvfmt version`, `validate`, `render --verify`) on `main` and PRs across Python 3.11–3.13.
- [x] **Public contributor docs** — Added `CONTRIBUTING.md` and `.github/ISSUE_TEMPLATE/` (`bug_report.yml`, `feature_request.yml`, `config.yml`), linked from `README.md`.
- [x] **Schema `cv-md/1.1` & non-exported `## Facts` section** — Added `## Facts` as an optional canonical Markdown-only memory bank (`Name — Description` bullets + optional `###` subheadings), omitted from PDF rendering and verified anti-leak in `cvfmt render --verify`, with backward-compatible `cv-md/1.0` support and updated skill instructions.
- [x] **Tailoring skill, dreamer mode, and `cvfmt tailor` (v0.2.0)** — `skills/cv-tailor/`, aspirational validation/render guards, strict deterministic pipeline, dreamer coverage + `--prepare` bundle, writer round-trip, pytest + CI smoke.
- [x] **Expanded `cv-md/1.1` schema & localized EU headings (`nl`, `de`, `fr`)** — Full `## Certifications` contract (expiry, credential ID, verification link), new optional canonical sections (`Awards`, `Speaking`, `Volunteering`, `Courses`, `Interests`), optional `availability` frontmatter field, documented 1-line company context & Career Break patterns, localized `nl`/`de`/`fr` heading aliases across validator/renderer/verifier/tailor, and upgraded LinkedIn/JSON Resume importers.

---

## Up Next

- *(Pick the next milestone from Backlog below — e.g. web app or PDF polish.)*

---

## Backlog

- [x] **Role / Job Description tailoring skill** — `skills/cv-tailor/` with strict playbook, dreamer playbook, and golden example; cross-linked from `skills/cv-formatter`.
- [x] **Dreamer mode (autonomous enhanced CV generation)** — Skill contract + `**(Aspirational)**` markers, validator/render guards, `cvfmt tailor --mode dreamer --prepare`.
- [x] **CLI `cvfmt tailor`** — `--base`, `--mode strict|dreamer`, `-o`, `--prepare`, optional `--pdf`; deterministic strict pipeline in `src/cvfmt/tailor/`.
- [ ] **Big Update: Simple Web App (CV → `cv-md/1.0` & PDF)**
  - *Comment*: Lightweight web app where users upload or paste a CV (or URL), parse/rewrite it using deterministic algorithmic parsing or free-tier AI model APIs (e.g., NVIDIA NIM / Groq), and download a clean `cv-md/1.0` Markdown file and/or rendered Warm Editorial PDF.
- [ ] **Direct LinkedIn profile URL import (without manual export)**
  - *Comment*: LinkedIn blocks direct unauthenticated HTTP fetches (HTTP 999 / authwall). Explore ToS-compliant approaches later (e.g., official OAuth / user-authenticated browser extension or BYO compliant enrichment API key).
- [ ] **Polish PDF design**
  - *Comment*: Further refine the Warm Editorial layout's visual craft—micro-typography, long role/company title wrapping (avoiding awkward `. Company` line breaks), page-2 balance/density, and optional modern theme presets (`--theme editorial|neon|swiss`) while preserving 100% single-column ATS/LLM readability.
- [ ] **Optional `Inter` typeface theme flag** (`--font ibm-plex|inter`) once IBM Plex Sans v1 is solid.
- [x] **Localized EU canonical section heading presets** (`nl`, `de`, `fr`) for non-English EU applications.
- [ ] **Optional DACH photo toggle** (strictly opt-in, off by default, keeping linear text order intact).

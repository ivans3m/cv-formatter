# Contributing to CV Formatter

Thanks for your interest in contributing to **CV Formatter**.

## Before You Start

The **`cv-md/1.1` data model** is the core contract of this project; agent skills and the `cvfmt` CLI are built around it. Read the relevant specification under `docs/` before changing schema rules, skill behavior, or rendering:

- [`docs/spec-cv-markdown.md`](docs/spec-cv-markdown.md) — Core `cv-md/1.1` data model, `## Facts`, localized EU headings, and validation rules
- [`docs/spec-skill.md`](docs/spec-skill.md) — Open-standard agent skill contracts (`cv-formatter` and `cv-tailor`)
- [`docs/spec-pdf-renderer.md`](docs/spec-pdf-renderer.md) — Reference `cvfmt` CLI, importers, and Typst rendering pipeline
- [`docs/TODO.md`](docs/TODO.md) — Current backlog and planned features

If you plan a large change or new backlog feature, open an issue first to align on design before writing code.

## Local Development Setup

Requires Python **3.11+**. Typst and IBM Plex Sans are bundled inside the package dependencies, so no external TeX or browser install is needed.

```bash
git clone https://github.com/ivans3m/cv-formatter.git
cd cv-formatter
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

Run the full test suite:

```bash
.venv/bin/pytest -v
```

Quick CLI verification:

```bash
.venv/bin/cvfmt validate tests/fixtures/senior-eu-2page.md
.venv/bin/cvfmt render tests/fixtures/senior-eu-2page.md -o /tmp/test.pdf --verify
```

## Guidelines by Area

### Data Model, Validator, Writer & Renderer (`src/cvfmt/`)
- **Protect backward compatibility:** Keep `cv-md/1.0` files valid alongside `cv-md/1.1`, and never export `## Facts` to PDF.
- **Preserve machine readability:** Rendered PDFs must remain single-column, keep contact details in normal body flow (not running headers/footers), disable problematic ligatures (`fi`/`fl`), and pass `pypdf` + `pdfplumber` round-trip verification (`--verify`).
- **Keep fixtures anonymized:** Never commit real personal CVs, emails, phone numbers, or LinkedIn exports in `tests/fixtures/`.
- **Add tests:** Every bug fix or feature should include unit/integration tests under `tests/`.

### Agent Skills (`skills/cv-formatter/` & `skills/cv-tailor/`)
- Follow the [agentskills.io](https://agentskills.io/specification) `SKILL.md` format and keep detailed rules in each skill's `references/` directory (progressive disclosure).
- Never weaken the zero-hallucination, `## Facts` preservation, or `**(Aspirational)**` labeling guardrails.

### Specifications & Docs (`docs/`)
- Keep specs in sync when schema fields, validation codes, skill contracts, or CLI flags change.

## Pull Request Checklist

- [ ] `.venv/bin/pytest -v` passes locally with no new warnings.
- [ ] New or updated behavior is covered by tests in `tests/`.
- [ ] Relevant `docs/spec-*.md` and `README.md` sections are updated if public behavior changed.
- [ ] All test fixtures and examples use anonymized/fictional data.

## Reporting Bugs & Requesting Features

Use the GitHub [issue templates](.github/ISSUE_TEMPLATE/) to report bugs or propose new features. For schema, parser, or rendering bugs, please include a minimal anonymized `cv-md/1.1` snippet that reproduces the issue.

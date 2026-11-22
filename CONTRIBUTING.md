# Contributing to CV Formatter

Thanks for your interest in contributing to **CV Formatter**.

## Before You Start

Read the relevant specification under `docs/` before changing schema rules, skill behavior, or PDF rendering:

- [`docs/spec-cv-markdown.md`](docs/spec-cv-markdown.md) — `cv-md/1.0` schema and validation rules
- [`docs/spec-skill.md`](docs/spec-skill.md) — Open-standard agent skill contract (Silent & Extended modes)
- [`docs/spec-pdf-renderer.md`](docs/spec-pdf-renderer.md) — `cvfmt` CLI, importers, and Typst rendering pipeline
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

### CLI, Parser, Validator & Renderer (`src/cvfmt/`)
- **Preserve machine readability:** Rendered PDFs must remain single-column, keep contact details in normal body flow (not running headers/footers), disable problematic ligatures (`fi`/`fl`), and pass `pypdf` + `pdfplumber` round-trip verification (`--verify`).
- **Keep fixtures anonymized:** Never commit real personal CVs, emails, phone numbers, or LinkedIn exports in `tests/fixtures/`.
- **Add tests:** Every bug fix or feature should include unit/integration tests under `tests/`.

### Agent Skill (`skills/cv-formatter/`)
- Follow the [agentskills.io](https://agentskills.io/specification) `SKILL.md` format and keep detailed rules in `skills/cv-formatter/references/` (progressive disclosure).
- Never weaken the zero-hallucination or evidence-grounding guardrails in Silent/Extended modes.

### Specifications & Docs (`docs/`)
- Keep specs in sync when CLI flags, exit codes, validation codes, or schema fields change.

## Pull Request Checklist

- [ ] `.venv/bin/pytest -v` passes locally with no new warnings.
- [ ] New or updated behavior is covered by tests in `tests/`.
- [ ] Relevant `docs/spec-*.md` and `README.md` sections are updated if public behavior changed.
- [ ] All test fixtures and examples use anonymized/fictional data.

## Reporting Bugs & Requesting Features

Use the GitHub [issue templates](.github/ISSUE_TEMPLATE/) to report bugs or propose new features. For rendering or parser bugs, please include a minimal anonymized `cv-md/1.0` snippet that reproduces the issue.

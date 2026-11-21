# Documentation

Formal specifications and design documents consolidated from our [research phase](../research/research-plan.md).

**Public source:** [github.com/ivans3m/cv-formatter](https://github.com/ivans3m/cv-formatter) (MIT — see [LICENSE](../LICENSE)).

## Project Tracking

- **[TODO.md](./TODO.md)** — Completed milestones, active notes, and feature backlog (tailoring skill, web app, PDF polish, and more).

## What is in Git vs. local-only

| Path | In public repo | Notes |
| --- | --- | --- |
| `src/`, `skills/`, `docs/`, `research/`, `benchmarks/` | Yes | Core format, CLI, skill, specs, research |
| `tests/` | Yes | Golden fixtures + pytest (`pip install -e ".[dev]"` then `pytest -v`) |
| `.agents/` | No | Agent-specific rules and workflows |
| `docs/blog/` | No | Personal blog drafts |

## Specifications

- **[spec-cv-markdown.md](./spec-cv-markdown.md)** — Canonical Markdown CV format (`cv-md/1.0`): YAML frontmatter, canonical sections, experience/promotion/freelance syntax, CEFR languages, validation rules, and golden example.
- **[spec-skill.md](./spec-skill.md)** — Open-standard (`agentskills.io`) CV-rewriting skill design: progressive disclosure layout, Silent Mode vs. Extended Mode interview contract, and anti-AI-slop guardrails.
- **[spec-pdf-renderer.md](./spec-pdf-renderer.md)** — Local Python + Typst CLI (`cvfmt`) specification: commands, compilation pipeline, IBM Plex Sans minimalist A4 typography, PDF/UA-1 tagging, and verification gates.

## CLI command map (implemented in v0.1.0)

| Command | Purpose |
| --- | --- |
| `cvfmt init` | Scaffold a starter `cv-md/1.0` Markdown file |
| `cvfmt validate` | Schema, ATS headings, CEFR, evidence/TODO linting |
| `cvfmt render` | Typst → PDF (`--paper`, `--accent`, `--verify`, …) |
| `cvfmt linkedin` | Import LinkedIn export ZIP or `Profile.pdf` |
| `cvfmt from-url` | Import HTML CV, JSON Resume, or raw `cv-md/1.0` URL |
| `cvfmt version` | Print installed package version |

Full flag tables and importer behavior: [spec-pdf-renderer.md](./spec-pdf-renderer.md).
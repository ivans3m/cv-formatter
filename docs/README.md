# Documentation

Specifications and design documents for **CV Formatter**, centered on the **`cv-md/1.1` career data model** and its supporting skills and local CLI tooling (synthesized from our [research phase](../research/research-plan.md)).

**Public source:** [github.com/ivans3m/cv-formatter](https://github.com/ivans3m/cv-formatter) (MIT — see [LICENSE](../LICENSE)).

## Core Data Model

- **[spec-cv-markdown.md](./spec-cv-markdown.md)** — **The primary contract (`cv-md/1.1`, backward-compatible with `cv-md/1.0`).** Defines the three-layer plain-text data model (typed YAML frontmatter, canonical CommonMark body, non-exported `## Facts` memory bank), AI-workflow design rationale, localized EU headings (`nl`, `de`, `fr`), epistemic tailoring markers (`strict` / `dreamer`), validation rules, and a complete golden example.

## Supporting Tooling Specifications

- **[spec-skill.md](./spec-skill.md)** — Open-standard (`agentskills.io`) agent skills built on `cv-md/1.1`: [`skills/cv-formatter/`](../skills/cv-formatter/) (Silent & Extended interview modes) and [`skills/cv-tailor/`](../skills/cv-tailor/) (Strict & Dreamer JD tailoring).
- **[spec-pdf-renderer.md](./spec-pdf-renderer.md)** — Reference local Python + Typst CLI (`cvfmt`): schema validation, deterministic tailoring, LinkedIn/URL import, Warm Editorial A4 PDF rendering (IBM Plex Sans, Tagged PDF/UA-1), and dual-parser verification gates.

## Project Tracking

- **[TODO.md](./TODO.md)** — Completed milestones, implementation notes, and feature backlog.

## Reference CLI Command Map (`v0.2.0`)

| Command | Purpose |
| --- | --- |
| `cvfmt init` | Scaffold a starter `cv-md/1.1` Markdown file |
| `cvfmt validate` | Validate schema, ATS headings, CEFR levels, aspirational markers, and skill evidence |
| `cvfmt render` | Compile public sections to Tagged PDF (`--paper`, `--accent`, `--verify`, …), omitting `## Facts` |
| `cvfmt tailor` | Deterministic strict reorder/trim (archiving cuts to `## Facts`) or dreamer prep bundle |
| `cvfmt linkedin` | Import LinkedIn GDPR export (`.zip` / CSV) or `Profile.pdf` into `cv-md/1.1` |
| `cvfmt from-url` | Import public HTML CV, JSON Resume, or raw `cv-md` URL into `cv-md/1.1` |
| `cvfmt version` | Print installed package version |

Full flag tables and importer behavior: [spec-pdf-renderer.md](./spec-pdf-renderer.md).

## What Is in Git vs. Local-Only

| Path | In public repo | Notes |
| --- | --- | --- |
| `docs/`, `research/`, `skills/`, `src/`, `benchmarks/` | Yes | Data-model spec, research, agent skills, reference CLI |
| `tests/` | Yes | Golden EU fixtures + 39-test pytest suite (`pip install -e ".[dev]"` then `pytest -v`) |
| `.agents/` | No | Local agent rules and workflows |
| `docs/blog/` | No | Personal blog drafts |

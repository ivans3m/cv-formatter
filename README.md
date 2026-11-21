# CV Formatter

A standardized, human- and LLM-readable Markdown CV format (`cv-md/1.0`), an open-standard agent skill to rewrite any CV into that format (silently or via guided follow-up questions), and a local Python + Typst CLI to render it into a clean, minimalist, machine-parseable PDF.

## Project Status

**Stage: Research & Specifications Complete** — Ready for implementation once approved.

## Project Structure

```text
.
├── docs/
│   ├── README.md
│   ├── spec-cv-markdown.md   # Canonical cv-md/1.0 format specification
│   ├── spec-skill.md         # Open-standard SKILL.md rewriting skill spec
│   └── spec-pdf-renderer.md  # Python + Typst + IBM Plex Sans CLI spec
├── research/
│   ├── research-plan.md
│   ├── 01-ats-parsing.md
│   ├── 02-llm-screening.md
│   ├── 03-human-cv-best-practices.md
│   ├── 04-markdown-schema-design.md
│   ├── 05-skill-design.md
│   ├── 06-pdf-rendering-and-design.md
│   └── 07-evaluation-framework.md
├── .gitignore
└── README.md
```

## Core Design Decisions

- **EU-First Defaults**: A4 paper (`210 × 297 mm`), 1–2 page target, CEFR language levels, GDPR-clean personal details (no DOB, full address, or photo by default), optional work authorization.
- **Format**: YAML frontmatter + strict canonical CommonMark (`cv-md/1.0`). One clean schema for both ready-to-send CVs (`cv.md`) and optional master archives (`cv-master.md`).
- **Skill**: Portable `agentskills.io` `SKILL.md` with progressive disclosure (`references/`) supporting **Silent Mode** and **Extended Mode**.
- **PDF CLI**: Python 3.11+ with the bundled `typst` compiler wheel, Tagged PDF (`PDF/UA-1`), **IBM Plex Sans**, and built-in `--verify` text-layer round-trip checks.

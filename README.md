# CV Formatter

A standardized, human- and LLM-readable Markdown CV format (`cv-md/1.0`), an open-standard agent skill to rewrite any CV into that format (silently or via guided follow-up questions), and a local Python + Typst CLI (`cvfmt`) to render it into a clean, minimalist, machine-parseable PDF.

## Project Status

**v0.1.0 Implemented & Verified** — Open-standard skill (`skills/cv-formatter/`), Python + Typst + IBM Plex Sans CLI (`cvfmt`), and automated PDF text-layer round-trip tests are working.

## Quickstart (`cvfmt` CLI)

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"

# Create a starter EU cv-md/1.0 file
.venv/bin/cvfmt init cv.md

# Validate schema, ATS headings, EU CEFR languages, and LLM evidence rules
.venv/bin/cvfmt validate cv.md

# Render to minimalist A4 PDF (Warm Editorial, IBM Plex Sans, Tagged PDF/UA-1) and verify text layer
.venv/bin/cvfmt render cv.md --verify

# Optional custom accent color (6-digit hex, default: #71717A light grey) or US Letter override
.venv/bin/cvfmt render cv.md --accent "#0F766E" -o cv-teal.pdf --verify
.venv/bin/cvfmt render cv.md --paper letter -o cv-us.pdf --verify

# Import LinkedIn Data Export (.zip / CSV folder) or 'Save to PDF' (Profile.pdf) directly to cv-md/1.0 + PDF
.venv/bin/cvfmt linkedin Profile.pdf --pdf -o cv.pdf --verify
.venv/bin/cvfmt linkedin linkedin-export.zip --pdf --accent "#0F766E" --verify
```

Run tests:

```bash
.venv/bin/pytest -v
```

## Using the Agent Skill (`skills/cv-formatter/`)

`skills/cv-formatter/` follows the open [agentskills.io](https://agentskills.io/specification) `SKILL.md` standard and can be mounted in Antigravity, Claude Code, Codex, Cursor, or other compatible agents:

- **Silent Mode**: *"Rewrite my CV into cv-md/1.0 format."* — Faithful restructuring with zero invented metrics.
- **Extended Mode**: *"Use extended mode to interview me and strengthen my CV."* — 2–3 focused rounds of follow-up questions to uncover missing impact, scope, and EU context.

## Project Structure

```text
.
├── docs/                     # Formal v1 specs and TODO/backlog
├── research/                 # 7 domain research reports
├── skills/cv-formatter/      # Open-standard SKILL.md + progressive-disclosure references
├── src/cvfmt/                # Python + Typst CLI + bundled IBM Plex Sans fonts
└── tests/                    # 4 EU golden fixtures + automated round-trip test suite
```

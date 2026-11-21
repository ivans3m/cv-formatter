# CV Formatter

A standardized, human- and LLM-readable Markdown CV format (`cv-md/1.0`), an open-standard agent skill to rewrite any CV into that format (silently or via guided follow-up questions), and a local Python + Typst CLI (`cvfmt`) to render it into a clean, minimalist, machine-parseable PDF.

**Repository:** [github.com/ivans3m/cv-formatter](https://github.com/ivans3m/cv-formatter) · **License:** [MIT](LICENSE)

## Project Status

**v0.1.0 implemented and verified** — Open-standard skill ([`skills/cv-formatter/`](skills/cv-formatter/)), Python + Typst + IBM Plex Sans CLI (`cvfmt`), LinkedIn and public-URL importers, and a local pytest suite (22 tests) with PDF text-layer round-trips are working.

## Quickstart (`cvfmt` CLI)

```bash
git clone https://github.com/ivans3m/cv-formatter.git
cd cv-formatter
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

# Import a public CV webpage, JSON Resume URL, or raw cv-md/1.0 URL directly to cv-md/1.0 + PDF
.venv/bin/cvfmt from-url https://ivan.diuldia.com/cv/ --pdf -o cv.pdf --verify
```

### Local development & tests

The public Git repository intentionally omits `tests/` and `.agents/` (see [`.gitignore`](.gitignore)). After `git clone`, those directories are absent unless you restore them from a maintainer checkout. If you have the local `tests/` tree, run:

```bash
.venv/bin/pytest -v
```

Golden fixtures under `tests/fixtures/` cover junior/senior EU layouts, multi-role consulting, and Unicode/diacritic stress cases. See [`docs/TODO.md`](docs/TODO.md) for what is shipped vs. kept local.

Optional LLM extraction benchmark (requires local `tests/fixtures/` and your own LLM for the grading step):

```bash
.venv/bin/python benchmarks/llm_extraction.py prepare --out /tmp/cvfmt-bench
# … run your model on the prepared prompts …
.venv/bin/python benchmarks/llm_extraction.py grade --bench-dir /tmp/cvfmt-bench --predictions /path/to/predictions.json
```

## Using the Agent Skill (`skills/cv-formatter/`)

[`skills/cv-formatter/`](skills/cv-formatter/) follows the open [agentskills.io](https://agentskills.io/specification) `SKILL.md` standard and can be mounted in Antigravity, Claude Code, Codex, Cursor, or other compatible agents:

- **Silent Mode:** *"Rewrite my CV into cv-md/1.0 format."* — Faithful restructuring with zero invented metrics.
- **Extended Mode:** *"Use extended mode to interview me and strengthen my CV."* — 2–3 focused rounds of follow-up questions to uncover missing impact, scope, and EU context.

## Project Structure

```text
.
├── LICENSE                   # MIT
├── docs/                     # Formal v1 specs, TODO/backlog (see docs/README.md)
├── research/                 # Seven domain research reports
├── benchmarks/               # Optional LLM PDF extraction benchmark script
├── skills/cv-formatter/      # Open-standard SKILL.md + progressive-disclosure references
├── src/cvfmt/                # Python + Typst CLI + bundled IBM Plex Sans fonts
├── tests/                    # Not on GitHub; maintainer-only golden fixtures + pytest
└── .agents/                  # Not on GitHub; maintainer-only agent rules and notes
```

## Documentation

| Document | Description |
| --- | --- |
| [docs/README.md](docs/README.md) | Index of specs and project tracking |
| [docs/TODO.md](docs/TODO.md) | Completed work, backlog, and implementation notes |
| [docs/spec-cv-markdown.md](docs/spec-cv-markdown.md) | `cv-md/1.0` schema and validation rules |
| [docs/spec-skill.md](docs/spec-skill.md) | Agent skill contract (Silent / Extended modes) |
| [docs/spec-pdf-renderer.md](docs/spec-pdf-renderer.md) | `cvfmt` CLI and Typst rendering pipeline |

## Contributing

This is an early-stage open project. Read the specs under `docs/` before changing schema or validation behavior. Open issues or pull requests on GitHub for bugs and feature ideas listed in the backlog.
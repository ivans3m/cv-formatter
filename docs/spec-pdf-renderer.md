# Specification: Reference Local CLI & PDF Renderer (`cvfmt`)

**Status:** Implemented v1.1 (shipped in package version `0.2.0`)  
**Role:** Supporting local utility for the [`cv-md/1.1`](./spec-cv-markdown.md) data model  
**Stack:** Python 3.11+ + bundled `typst` compiler (`typst` PyPI wheel)  
**Default Typography:** IBM Plex Sans (open-source, bundled with the CLI package)  
**Default Page Size:** A4 (`210 × 297 mm`), optional US Letter (`letter`)  
**Install:** `pip install -e ".[dev]"` from the project root (see [README.md](../README.md))

---

## 1. Goals & Non-Goals

### Goals
- Validate any `cv-md/1.1` (or `cv-md/1.0`) file against the data-model contract (schema, ATS headings, EU CEFR levels, aspirational guards, and skill evidence).
- Convert the public sections of a `cv-md/1.1` file into a clean, minimalist Warm Editorial PDF in <1 second locally, completely omitting non-exported sections (`## Facts`).
- Guarantee **100% linear, ATS- and LLM-readable PDF text extraction** (exact reading order, `ligatures: false`, full EU Unicode/diacritic fidelity, Tagged PDF / PDF/UA-1, and anti-leak verification for `## Facts`).
- Provide zero-dependency local helpers for importing LinkedIn exports / public URLs into `cv-md/1.1` and running deterministic strict tailoring.

### Non-Goals (v1)
- Multi-column or graphic-heavy templates.
- Web UI / SaaS hosting (local CLI first).
- Photo embedding by default.

---

## 2. CLI Interface

Command name: `cvfmt` (console script from `pyproject.toml`; invocable after `pip install -e .` or via `python -m cvfmt.cli`).

### Commands (`v0.2.0`)

```bash
# Validate a cv-md/1.1 file (schema + ATS/LLM lint checks)
cvfmt validate cv.md [--allow-todos] [--allow-aspirational] [--strict]

# Render cv.md to PDF (validates before compile; omits ## Facts)
cvfmt render cv.md [-o output.pdf] [--paper a4|letter] [--accent #RRGGBB] [--allow-todos] [--allow-aspirational] [--strict] [--verify]

# Tailor master CV to job description (strict deterministic or dreamer prep)
cvfmt tailor job.txt --base cv-master.md -o cv-target.md --mode strict [--target-title "Role"] [--pages 1|2] [--pdf] [--verify]
cvfmt tailor job.txt --base cv-master.md --mode dreamer --prepare ./bundle/

# Scaffold a starter EU cv-md/1.1 file
cvfmt init [path] [--force]

# Import LinkedIn "Save to PDF", GDPR export (.zip), or CSV folder → cv-md/1.1 (optional PDF)
cvfmt linkedin Profile.pdf [-o cv.md] [--pdf] [-o cv.pdf] [--paper a4|letter] [--accent #RRGGBB] [--verify]
cvfmt linkedin linkedin-export.zip --pdf -o cv.pdf --verify

# Import public HTML CV page, JSON Resume URL, or raw cv-md URL → cv-md/1.1 (optional PDF)
cvfmt from-url https://example.com/cv/ [-o cv.md] [--pdf] [-o cv.pdf] [--paper a4|letter] [--accent #RRGGBB] [--verify]

# Print installed version
cvfmt version
```

### `validate`

| Flag | Description |
| :--- | :--- |
| `--allow-todos` | Permit `[TODO: ...]` placeholders without hard errors. |
| `--allow-aspirational` | Allow `**(Aspirational)**` dreamer bullets (warnings only). |
| `--strict` | Treat lint warnings as errors (exit `1`). |

### `render`

| Flag | Description |
| :--- | :--- |
| `-o`, `--output` | Output PDF path (default: `<stem>.pdf` next to input). |
| `--paper a4\|letter` | Overrides YAML `paper` frontmatter. |
| `--accent #RRGGBB` | Warm Editorial accent (default `#71717A`; 6-digit hex with or without `#`; also settable via frontmatter `accent`). |
| `--allow-todos` | Allow rendering with `[TODO: ...]` markers. |
| `--allow-aspirational` | Include `**(Aspirational)**` bullets in PDF (internal gap-analysis only; default off). |
| `--strict` | Treat warnings as errors before compile. |
| `--verify` | After PDF generation, run dual-parser text-layer round-trip check (`pypdf` + `pdfplumber`) including `## Facts` anti-leak verification. |

### `tailor`

| Flag | Description |
| :--- | :--- |
| `JOB` | Job description plain-text or Markdown file. |
| `--base` | Master `cv-md` input (required). |
| `-o` | Output tailored `.md` (required for `--mode strict`). |
| `--mode strict\|dreamer` | Deterministic strict pipeline or dreamer coverage/prepare bundle. |
| `--target-title` | Override `headline` (strict). |
| `--pages` | Soft character budget for `1` or `2` pages (strict). |
| `--prepare DIR` | Write dreamer LLM bundle (`jd.txt`, `base.md`, `prompt.md`). |
| `--pdf` / `--verify` | Render and verify tailored output after strict mode. |

### `init`

| Flag | Description |
| :--- | :--- |
| `--force` | Overwrite an existing starter file. |

### `linkedin`

Accepts LinkedIn **Save to PDF** (`Profile.pdf`), official **Data Export** (`.zip`), or a folder of GDPR CSV exports. Writes `cv-md/1.1` Markdown; with `--pdf`, also renders Warm Editorial PDF.

| Flag | Description |
| :--- | :--- |
| `-o`, `--output` | Output `.md` path, or `.pdf` when `--pdf` is set. Defaults derived from source name (`Profile.pdf` → `Profile-cv.pdf` + sidecar `.md`). |
| `--pdf` | Compile PDF after import (validates imported MD first). |
| `--paper`, `--accent`, `--verify` | Same semantics as `render` when `--pdf` is used. |

**Guards:** Refuses to overwrite the input `.pdf` when output would collide with the source path.

### `from-url`

Fetches a public URL (max **5 MB** response) and converts:

- Raw `cv-md/1.1` or `cv-md/1.0` Markdown URLs
- [JSON Resume](https://jsonresume.org/) `.json` documents
- Simple HTML CV pages (heuristic extraction)

LinkedIn profile URLs that hit an auth wall exit `1` with instructions to use `cvfmt linkedin` on a saved PDF/export instead.

| Flag | Description |
| :--- | :--- |
| `-o`, `--output` | Output path (default `cv-imported.md` or `cv-imported.pdf` when `--pdf`). |
| `--pdf` | Compile PDF after import. |
| `--paper`, `--accent`, `--verify` | Same as `linkedin --pdf`. |

### Exit Codes (All Commands)

| Code | Meaning |
| :--- | :--- |
| `0` | Success. |
| `1` | Validation/schema/import error, or `--strict` warnings on `validate`. |
| `2` | Typst compilation failure or `--verify` text-layer check failure. |

---

## 3. Rendering Pipeline Architecture

```text
cv.md (cv-md/1.1)
  │
  ▼
[1. Frontmatter + CommonMark AST Parser (Python)]
  │  Extracts structured CVDocument (Pydantic Frontmatter + typed Section/Entry/SubRole tree)
  ▼
[2. Validator & Linter]
  │  Hard errors (schema, dates, required fields, TODOs, ASPIRATIONAL_IN_STRICT)
  │  Soft warnings (ATS headings, ungrounded skills, CEFR levels, aspirational bullets)
  ▼
[3. Warm Editorial Typst Generator]
  │  Emits deterministic .typ for renderable_sections only (omits ## Facts)
  │  Escapes Markdown/Unicode safely; maps YYYY-MM → MMM YYYY; strips aspirational bullets by default
  ▼
[4. Typst Compiler (Python `typst` wheel, bundled binary)]
  │  Compiles with Tagged PDF / PDF/UA-1 support & bundled IBM Plex Sans fonts
  ▼
[5. Optional `--verify` Text-Layer Check]
  │  Dual-parser (pypdf + pdfplumber) check: reading order, EU diacritics, contact presence,
  │  clickable URIs, page count, and zero ## Facts leakage
  ▼
cv.pdf
```

---

## 4. Warm Editorial Typography & Layout Specification

### 4.1 Page Geometry
- **A4 (default):** `210mm × 297mm`, margins `17mm` top, `16mm` bottom, `18mm` left/right.
- **US Letter:** `8.5in × 11in`, margins `0.66in` top, `0.62in` bottom, `0.70in` left/right.
- **Single-column strictly:** All content flows linearly top-to-bottom.
- **Contact block:** Rendered inside the main body flow at the top of page 1 (never inside Typst's `page(header: ...)` margin zone so ATS parsers never strip contact details).
- **Page footer:** Omitted on 1-page CVs. On 2+ page CVs, subtle muted `Page 1 of 2` (`8pt`, `#A1A1AA`) right-aligned in the bottom margin.

### 4.2 Typeface: IBM Plex Sans
- Bundled TTF weights: **Regular (400)**, **Medium (500)**, **SemiBold (600)**, **Bold (700)**, **Italic (400i)**.
- Full Latin Extended coverage for European names, cities, and currency (`ü`, `ö`, `ä`, `ß`, `é`, `è`, `ł`, `ż`, `ø`, `å`, `€`).
- **Ligature safety:** Explicitly compiled with `ligatures: false` so `fi`/`fl` words extract cleanly across all PDF parsers.
- **Zero letter-spaced uppercase headings:** Avoids wide tracking on headings so text extractors never split letters.

### 4.3 Visual Hierarchy & Color Tokens

Default accent color is `#71717A` (Zinc 500), overridable via frontmatter `accent` or `--accent #RRGGBB`.

| Element | Font Size | Weight | Color | Layout & Spacing |
| :--- | :--- | :--- | :--- | :--- |
| **Name (`=`)** | `24 pt` | SemiBold (600) | `#18181B` | Tracking `-0.02em`, `3 pt` below |
| **Headline** | `10.5 pt` | Regular (400) | `#71717A` | `5 pt` below |
| **Contact & Links** | `8.6 pt` | Regular (400) | `#71717A` | Single flow separated by `·` (`#D4D4D8`), `4 pt` below |
| **Summary Callout** | `9.3 pt` | Regular (400) | `#27272A` | `#FAFAF9` fill, `2 pt` left accent border, `10 pt`/`8 pt`/`7 pt` inset |
| **Section Heading (`##`)** | `10 pt` | SemiBold (600) | `accent` | `15 pt` above, `6 pt` below, inline `0.5 pt` hairline (`#E4E4E7`) |
| **Entry Header (`###`)** | `9.8 pt` | SemiBold (600) | `#18181B` | Secondary part `9.5 pt` `#71717A` (`·`), `11 pt` above, `5 pt` below |
| **Sub-role (`####`)** | `9.4 pt` | Medium (500) | `#18181B` | `8 pt` above, `5 pt` below |
| **Dates & Location** | `8.5 pt` | Regular (400) | `#71717A` | Right-aligned on same visual row via `grid(1fr, auto)` preserving linear text order |
| **Body & Bullets** | `9.3 pt` | Regular (400) | `#27272A` | Leading `0.56em`, en-dash marker (`#A1A1AA`), `7.5 pt` spacing (`6.5 pt` compact) |
| **Links** | Inherit | Regular (400) | `accent` | Clickable PDF URI annotation |

### 4.4 Pagination & Flow Rules
- `##` headings use `sticky: true` so a section heading is never orphaned at the bottom of a page.
- Each `###` / `####` entry header stays attached to its metadata line and optional 1-line company context (`sticky: true, breakable: false`).
- Compact bullet-only sections (≤5 bullets, such as `Skills`, `Languages`, `Certifications`) are kept together in an unbreakable block.
- Long roles split gracefully between bullets across page 1 and page 2.

---

## 5. Verification & Quality Gates

Acceptance uses the three-layer framework in [07-evaluation-framework.md](../research/07-evaluation-framework.md). The **39-test** `pytest` suite and **4 golden EU fixtures** live under `tests/`. Criteria:
1. Zero schema/lint errors on valid fixtures; expected errors (`SCHEMA_VERSION`, `INVALID_DATE`, `UNRESOLVED_TODO`, `ASPIRATIONAL_IN_STRICT`) caught on invalid fixtures.
2. `pypdf` and `pdfplumber` extract 100% of characters (including EU diacritics and `fi`/`fl` words) in exact top-to-bottom reading order, with zero `## Facts` leakage.
3. Contact details (name, email, phone, URLs) appear in body text and links are clickable PDF URI annotations.
4. Blind LLM extraction round-trip from raw PDF text recovers 100% of roles, companies, dates, CEFR languages, degrees, and core metrics.
5. Visual PNG inspection confirms balanced whitespace, crisp IBM Plex Sans hierarchy, and zero orphan headings or awkward page spills.

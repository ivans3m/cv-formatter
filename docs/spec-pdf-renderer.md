# Specification: Markdown-to-PDF Local CLI (`cvfmt`)

**Status:** Implemented v1.1 (shipped in package version `0.2.0`)  
**Stack:** Python 3.11+ + bundled `typst` compiler (`typst` PyPI wheel)  
**Default Typography:** IBM Plex Sans (open-source, bundled with the CLI package)  
**Default Page Size:** A4 (`210 × 297 mm`), optional US Letter (`letter`)  
**Install:** `pip install -e ".[dev]"` from the project root (see [README.md](../README.md))

---

## 1. Goals & Non-Goals

### Goals
- Convert any valid `cv-md/1.1` (or `cv-md/1.0`) Markdown file into a clean, modern, minimalist PDF in <1 second locally, while omitting non-exported sections (`## Facts`).
- Guarantee **100% linear, ATS- and LLM-readable PDF text extraction** (exact reading order, zero ligature drops, full EU Unicode/diacritic fidelity, Tagged PDF / PDF/UA-1, and anti-leak verification for `## Facts`).
- Zero manual system dependencies (no TeX Live, no Cairo/Pango, no Chromium download).

### Non-Goals (v1)
- Multi-column or graphic-heavy templates.
- Web UI / SaaS hosting (local CLI first).
- Photo embedding by default.

---

## 2. CLI Interface

Command name: `cvfmt` (console script from `pyproject.toml`; invocable after `pip install -e .` or via `python -m cvfmt.cli`).

### Commands (v0.2.0)

```bash
# Validate a cv-md/1.0 file (schema + ATS/LLM lint checks)
cvfmt validate cv.md [--allow-todos] [--allow-aspirational] [--strict]

# Render cv.md to PDF (validates before compile)
cvfmt render cv.md [-o output.pdf] [--paper a4|letter] [--accent #RRGGBB] [--allow-todos] [--allow-aspirational] [--strict] [--verify]

# Tailor master CV to job description (strict deterministic or dreamer prep)
cvfmt tailor job.txt --base cv-master.md -o cv-target.md --mode strict [--target-title "Role"] [--pdf] [--verify]
cvfmt tailor job.txt --base cv-master.md --mode dreamer --prepare ./bundle/

# Scaffold a starter EU cv-md/1.0 file
cvfmt init [path] [--force]

# Import LinkedIn "Save to PDF", GDPR export (.zip), or CSV folder → cv-md/1.0 (optional PDF)
cvfmt linkedin Profile.pdf [-o cv.md] [--pdf] [-o cv.pdf] [--paper a4|letter] [--accent #RRGGBB] [--verify]
cvfmt linkedin linkedin-export.zip --pdf -o cv.pdf --verify

# Import public HTML CV page, JSON Resume URL, or raw cv-md/1.0 URL → cv-md/1.0 (optional PDF)
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
| `--allow-aspirational` | Include `**(Aspirational)**` bullets in PDF (gap-analysis only; default off). |
| `--strict` | Treat warnings as errors before compile. |
| `--verify` | After PDF generation, run text-layer round-trip check (`pypdf` / `pdfplumber`). |

### `tailor`

| Flag | Description |
| :--- | :--- |
| `JOB` | Job description plain-text or Markdown file. |
| `--base` | Master `cv-md` input (required). |
| `-o` | Output tailored `.md` (required for `--mode strict`). |
| `--mode strict\|dreamer` | Strict pipeline or dreamer coverage/prepare. |
| `--target-title` | Override `headline` (strict). |
| `--pages` | Soft budget `1` or `2` (strict). |
| `--prepare DIR` | Write dreamer LLM bundle (`jd.txt`, `base.md`, `prompt.md`). |
| `--pdf` / `--verify` | Render tailored output after strict mode. |

### `init`

| Flag | Description |
| :--- | :--- |
| `--force` | Overwrite an existing starter file. |

### `linkedin`

Accepts LinkedIn **Save to PDF** (`Profile.pdf`), official **Data Export** (`.zip`), or a folder of GDPR CSV exports. Writes `cv-md/1.0` Markdown; with `--pdf`, also renders Warm Editorial PDF.

| Flag | Description |
| :--- | :--- |
| `-o`, `--output` | Output `.md` path, or `.pdf` when `--pdf` is set. Defaults derived from source name (`Profile.pdf` → `Profile-cv.pdf` + sidecar `.md`). |
| `--pdf` | Compile PDF after import (validates imported MD first). |
| `--paper`, `--accent`, `--verify` | Same semantics as `render` when `--pdf` is used. |

**Guards:** Refuses to overwrite the input `.pdf` when output would collide with the source path.

### `from-url`

Fetches a public URL (max **5 MB** response) and converts:

- Raw `cv-md/1.0` Markdown URLs
- [JSON Resume](https://jsonresume.org/) `.json` documents
- Simple HTML CV pages (heuristic extraction)

LinkedIn profile URLs that hit an auth wall exit `1` with instructions to use `cvfmt linkedin` on a saved PDF/export instead.

| Flag | Description |
| :--- | :--- |
| `-o`, `--output` | Output path (default `cv-imported.md` or `cv-imported.pdf` when `--pdf`). |
| `--pdf` | Compile PDF after import. |
| `--paper`, `--accent`, `--verify` | Same as `linkedin --pdf`. |

HTTP client identifies as `cvfmt/0.1 (+https://github.com/ivans3m/cv-formatter)`.

### Exit codes (all commands)

| Code | Meaning |
| :--- | :--- |
| `0` | Success. |
| `1` | Validation/schema/import error, or `--strict` warnings on `validate`. |
| `2` | Typst compilation failure or `--verify` text-layer check failure. |

---

## 3. Rendering Pipeline Architecture

```text
cv.md
  │
  ▼
[1. Frontmatter + CommonMark AST Parser (Python)]
  │  Extracts structured CV model (Pydantic / dataclasses)
  ▼
[2. Validator & Linter]
  │  Hard errors (schema, dates, required fields, TODOs)
  │  Soft warnings (ATS headings, ungrounded skills, EU language hint)
  ▼
[3. Typst Generator]
  │  Emits clean, deterministic .typ document using built-in minimalist template
  │  Escapes all Markdown/Unicode safely; maps YYYY-MM → MMM YYYY
  ▼
[4. Typst Compiler (Python `typst` wheel, bundled binary)]
  │  Compiles with Tagged PDF / PDF/UA-1 support & bundled IBM Plex Sans fonts
  ▼
[5. Optional `--verify` Text-Layer Check]
  │  Extracts text stream, verifies reading order, EU diacritics, contact presence, page count
  ▼
cv.pdf
```

---

## 4. Minimalist Typography & Layout Specification

### 4.1 Page Geometry
- **A4 (default)**: `210mm × 297mm`, margins `16mm` top/bottom, `17mm` left/right.
- **US Letter**: `8.5in × 11in`, margins `0.62in` top/bottom, `0.65in` left/right.
- **Single-column strictly**: All content flows linearly top-to-bottom.
- **Contact block**: Rendered inside the main body flow at the top of page 1 (never inside Typst's `page(header: ...)` margin zone so ATS parsers never strip contact details).
- **Page footer**: Omitted on 1-page CVs. On 2+ page CVs, subtle muted `Page 1 of 2` right-aligned in the bottom margin (marked as a pagination artifact by Typst).

### 4.2 Typeface: IBM Plex Sans
- Bundled TTF/OTF weights: **Regular (400)**, **Medium (500)**, **SemiBold (600)**, **Bold (700)**, **Italic (400i)**.
- Full Latin Extended coverage for European names, cities, and currency (`ü`, `ö`, `ä`, `ß`, `é`, `è`, `ł`, `ż`, `ø`, `å`, `€`).
- **Ligature safety**: Verify `fi`/`fl` extraction in `pdftotext` & `pdfplumber`; set `#set text(ligatures: false)` if any extractor fails to decompose standard ligatures cleanly.
- **Zero letter-spaced uppercase headings**: Avoid wide tracking on headings so text extractors never split letters.

### 4.3 Visual Hierarchy & Color Tokens

| Element | Font Size | Weight | Color | Spacing |
| :--- | :--- | :--- | :--- | :--- |
| **Name** | `19.5 pt` | Bold (700) | `#111827` | `2 pt` below |
| **Headline** | `10.5 pt` | Medium (500) | `#374151` | `5 pt` below |
| **Contact & Links** | `8.8 pt` | Regular (400) | `#4B5563` | `9 pt` below + `0.5 pt` rule (`#E5E7EB`) |
| **Section Heading (`##`)** | `10.5 pt` | SemiBold (600) | `#111827` | `11 pt` above, `4 pt` below + `0.5 pt` rule (`#E5E7EB`) |
| **Entry Header (`###`)** | `9.8 pt` | SemiBold (600) | `#111827` | `7 pt` above, `1.5 pt` below |
| **Sub-role (`####`)** | `9.5 pt` | Medium (500) | `#1F2937` | `5 pt` above, `1.5 pt` below |
| **Dates & Location** | `8.8 pt` | Regular (400) | `#6B7280` | Right-aligned on same visual row via Typst `grid` / `#h(1fr)` preserving linear reading order |
| **Body & Bullets** | `9.5 pt` | Regular (400) | `#1F2937` | Line height `1.28`, `2.5 pt` between bullets |
| **Links** | Inherit | Regular (400) | `#1E3A5F` | Subtle underline or clean dark-slate tint; clickable PDF URI annotation |

### 4.4 Pagination & Flow Rules
- `##` headings use `sticky: true` so a section heading is never orphaned at the bottom of a page.
- Each `###` / `####` entry header stays attached to its metadata line and at least its first bullet.
- Long roles split gracefully between bullets across page 1 and page 2 (avoiding giant blank gaps).

---

## 5. Verification & Quality Gates (v1 Acceptance Criteria)

v1 acceptance uses the three-layer framework in [07-evaluation-framework.md](../research/07-evaluation-framework.md). The **22-test** `pytest` suite and **4 golden EU fixtures** live under `tests/` in the repository. Criteria:
1. Zero schema/lint errors on valid fixtures; expected errors caught on invalid fixtures.
2. `pdftotext` and `pdfplumber` extract 100% of characters (including EU diacritics and `fi`/`fl` words) in exact top-to-bottom reading order.
3. Contact details (name, email, phone, URLs) appear in body text and links are clickable PDF annotations.
4. LLM extraction round-trip from PDF text recovers 100% of roles, companies, dates, languages, and core metrics.
5. Visual PNG inspection confirms clean whitespace, crisp IBM Plex Sans hierarchy, and zero orphan headings or awkward page spills.

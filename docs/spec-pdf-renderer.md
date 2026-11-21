# Specification: Markdown-to-PDF Local CLI (`cvfmt`)

**Status:** Draft v1.0  
**Stack:** Python 3.11+ + bundled `typst` compiler (`typst` PyPI wheel)  
**Default Typography:** IBM Plex Sans (open-source, bundled with the CLI package)  
**Default Page Size:** A4 (`210 × 297 mm`), optional US Letter (`letter`)

---

## 1. Goals & Non-Goals

### Goals
- Convert any valid `cv-md/1.0` Markdown file into a clean, modern, minimalist PDF in <1 second locally.
- Guarantee **100% linear, ATS- and LLM-readable PDF text extraction** (exact reading order, zero ligature drops, full EU Unicode/diacritic fidelity, Tagged PDF / PDF/UA-1).
- Zero manual system dependencies (no TeX Live, no Cairo/Pango, no Chromium download).

### Non-Goals (v1)
- Multi-column or graphic-heavy templates.
- Web UI / SaaS hosting (local CLI first).
- Photo embedding by default.

---

## 2. CLI Interface

Proposed command name: `cvfmt` (invocable via `uv run cvfmt` or installed via `uv tool install` / `pipx`).

### Commands

```bash
# Validate a cv-md/1.0 file (schema + ATS/LLM lint checks)
cvfmt validate cv.md

# Render cv.md to cv.pdf (validates first by default)
cvfmt render cv.md [-o output.pdf] [--paper a4|letter] [--accent #RRGGBB] [--allow-todos] [--verify]

# Scaffold a starter EU cv-md/1.0 file
cvfmt init [path]
```

### Flags & Exit Codes
- `--paper a4|letter`: Overrides the `paper` frontmatter value.
- `--accent #RRGGBB`: Overrides the Warm Editorial accent color (default `#71717A` light grey; accepts 6-digit hex with or without `#`, also configurable via `accent` in frontmatter).
- `--verify`: After generating the PDF, automatically runs the text-layer round-trip check (`pypdf`/`pdfplumber` or `pdftotext`) and reports any extraction anomalies, page count, and link count.
- `--allow-todos`: Allows rendering even if `[TODO: ...]` markers exist (useful for draft previews).
- `--strict`: Treats lint warnings (non-canonical headings, >2 pages, ungrounded skills) as non-zero exit errors.
- **Exit codes**: `0` = success, `1` = validation/schema error, `2` = compilation or verification failure.

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

Before v1 is considered complete, the CLI must pass all checks from [07-evaluation-framework.md](file:///Users/s3m/Projects/CV%20formatter/research/07-evaluation-framework.md) across all 4 golden EU fixtures:
1. Zero schema/lint errors on valid fixtures; expected errors caught on invalid fixtures.
2. `pdftotext` and `pdfplumber` extract 100% of characters (including EU diacritics and `fi`/`fl` words) in exact top-to-bottom reading order.
3. Contact details (name, email, phone, URLs) appear in body text and links are clickable PDF annotations.
4. LLM extraction round-trip from PDF text recovers 100% of roles, companies, dates, languages, and core metrics.
5. Visual PNG inspection confirms clean whitespace, crisp IBM Plex Sans hierarchy, and zero orphan headings or awkward page spills.

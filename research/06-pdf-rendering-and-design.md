# Research 06: Markdown-to-PDF Pipeline & Minimalist Typography

## Executive Summary

For a **local CLI** that must produce both **modern minimalist typography** and a **pristine, ATS- and LLM-readable PDF text layer**, **Typst** is the clear winner over WeasyPrint, Chromium/Playwright, and Pandoc/LaTeX.

Starting with Typst 0.14, Typst compiles in milliseconds from a single binary, produces clean linear text streams, natively emits **Tagged PDF / PDF/UA-1** accessibility trees, and handles European Unicode/diacritics and open-source typography cleanly without browser engines or heavy TeX distributions.

---

## 1. Rendering Engine Comparison

| Criterion | **Typst** (Recommended) | WeasyPrint | Chromium / Playwright | Pandoc + LaTeX |
| :--- | :--- | :--- | :--- | :--- |
| **Install footprint** | Single fast binary (~30 MB) | Python + Cairo/Pango/GObject native libs (frequent macOS/Linux friction) | Node/Python + ~300 MB Chromium binary | Multi-GB TeX Live installation |
| **Compile speed** | < 100 ms | ~0.5–2 s | ~1–3 s | ~2–5 s |
| **PDF text extraction** | **Pristine** (exact logical stream) | Good (if semantic HTML + simple CSS) | Good (occasional spacing quirks) | Good, but ligature/CMap pitfalls if misconfigured |
| **Tagged PDF / PDF/UA** | **Native (`--pdf-standard ua-1`)** | Supported (`--pdf-tags`), can need tuning | Weak / limited | Experimental / complex |
| **Typography & pagination** | **Excellent** (widow/orphan control, clean flex/grid spacing, crisp margins) | Good (`@page` CSS Paged Media) | Medium (`break-inside` quirks across pages) | Excellent, steep template maintenance |
| **Local CLI ergonomics** | **Best** | Medium | Heavy | Heavy |

### Recommended CLI Architecture
```text
cv.md  ──▶  CLI (Parse Frontmatter + CommonMark AST + Validate)
              ──▶  Generate clean intermediate .typ from built-in minimalist template
              ──▶  Compile via `typst compile` (with PDF/UA tagging)
              ──▶  Optional `--verify` pass via `pdftotext` text-layer check
              ──▶  cv.pdf
```

*Implementation language note (for the future coding stage)*: Either **Python** (e.g., `uv`/`typer` + `typst` PyPI package, which bundles the Typst compiler binary directly so users don't even have to install Typst separately!) or **TypeScript/Node** calling the `typst` binary. Bundling Typst via the official Python `typst` wheel or shipping a thin wrapper gives a near-zero-friction local install.

---

## 2. Minimalist Typography & Layout Specification (EU A4 Default)

Design goal: **Quiet, architectural, modern minimalism**—zero visual noise, effortless 7.4-second F-pattern scanning, and 100% linear text extraction.

### Page Geometry
- **Default page size**: **A4** (`210 × 297 mm`); optional `paper: letter` (`8.5 × 11 in`).
- **Margins**: `16mm` top/bottom, `17mm` left/right (generous breathing room without wasting space).
- **Columns**: **Strictly single-column**.
- **Page numbers**: Subtle, muted footer (`Page 1 of 2`) *only* on multi-page CVs, marked as a PDF pagination artifact so ATS parsers ignore it.

### Typeface Selection (Open-Source, Embedded, Full EU Diacritic Support)
- **Primary recommendation**: **Inter** ([rsms.me/inter](https://rsms.me/inter/)) — neutral, crisp, high x-height, superb legibility at 9.5–10.5 pt, full Latin Extended coverage for European names/cities.
- **Alternative (editorial/technical option)**: **IBM Plex Sans** ([ibm.com/plex](https://www.ibm.com/plex/)) — slightly more engineered personality, equally clean in print and on screen.
- **Font safety rules**:
  - Embed fonts in the PDF.
  - Disable discretionary ligatures (and verify standard `fi`/`fl` ligatures extract cleanly as ASCII `f`+`i`, `f`+`l` in `pdftotext`—if any extractor stumbles, set `#set text(ligatures: false)`).
  - Avoid letter-spaced uppercase headings (or keep tracking subtle and verify `pdftotext` doesn't insert spaces between letters like `E X P E R I E N C E`).

### Type Scale & Vertical Rhythm
| Element | Size | Weight | Color | Spacing |
| :--- | :--- | :--- | :--- | :--- |
| **Candidate Name** | `19–20 pt` | Bold (700) | Near-black (`#111827`) | `2pt` below |
| **Headline / Title** | `11 pt` | Medium (500) | Slate (`#374151`) | `6pt` below |
| **Contact & Links Line** | `9 pt` | Regular (400) | Muted (`#4B5563`) | `10pt` below + subtle `0.5pt` divider |
| **Section Heading (`##`)** | `10.5–11 pt` | Semi-Bold (600) | Near-black (`#111827`) | `12pt` above, `4pt` below + hairline rule (`#E5E7EB`) |
| **Role & Company (`###`)** | `10 pt` | Semi-Bold (600) | Near-black (`#111827`) | `7pt` above, `1.5pt` below |
| **Date & Location** | `9 pt` | Regular (400) | Muted (`#6B7280`) | Right-aligned on same visual row (using Typst grid/horizontal space that preserves linear reading order) |
| **Body / Bullets** | `9.5–10 pt` | Regular (400) | Charcoal (`#1F2937`) | Line height `1.28`, `2.5pt` between bullets |

### Color Palette
- **Monochrome + one restrained slate accent** (`#111827` primary text, `#4B5563` metadata, `#E5E7EB` hairline rules, subtle link underline or dark slate `#1E3A5F` for clickable URLs).
- Prints cleanly in black-and-white with zero loss of contrast.

### Pagination Rules
- Keep every section heading attached to its first entry (`sticky: true` on headings).
- Keep an entry's Role/Company + Date/Location line attached to at least its first bullet (never orphan a job header at the bottom of page 1).
- Allow long roles to split cleanly between bullets across pages 1 and 2 rather than leaving a giant blank gap at the bottom of page 1.

---

## References

- [Typst](https://typst.app/) — Modern markup-based typesetting system with native Tagged PDF / PDF/UA-1 support.
- [WeasyPrint](https://weasyprint.org/) — Python HTML/CSS Paged Media PDF renderer.
- [Playwright](https://playwright.dev/) — Browser automation & Chromium PDF rendering.
- [Inter Typeface](https://rsms.me/inter/) — Open-source UI & document sans-serif font.
- [IBM Plex](https://www.ibm.com/plex/) — Open-source corporate/technical typeface family.

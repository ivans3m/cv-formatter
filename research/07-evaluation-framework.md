# Research 07: Verification & Quality Benchmarks

## Executive Summary

Claiming a CV is "human- and LLM-readable" is meaningless without an automated way to prove it. Before shipping v1 of the skill and CLI, we need a repeatable **three-layer evaluation framework** that tests: (1) schema correctness, (2) PDF text-layer & ATS round-trip fidelity, and (3) LLM structured extraction accuracy + human visual quality.

---

## 1. Golden Test Fixtures (EU-Focused Edge Cases)

We should maintain 4 anonymized test CVs in Markdown to stress-test both the schema and PDF renderer:

1. **`junior-eu-1page.md`**: Early-career engineer in Amsterdam (0–2 years, 1 page, Education + Projects prominent, CEFR languages).
2. **`senior-eu-2page.md`**: Senior/Staff professional in Berlin (8+ years, 2 pages, internal promotions at one company, categorized skills, quantified XYZ bullets).
3. **`consultant-multirole.md`**: Independent/agency specialist with overlapping client engagements, speaking/publications, and EU remote work authorization.
4. **`diacritics-stress.md`**: Heavy European Unicode stress test (`Łukasz Żółć`, `München`, `Zürich`, `Malmö`, `François`, `€1.2M`, `—`, `fi`/`fl` ligature words like *profile*, *workflow*, *offline*, long GitHub/LinkedIn URLs).

---

## 2. Automated Verification Layers

### Layer 1: Schema & Content Linting (Pre-Render)
- Valid YAML frontmatter (`schema`, `name`, `email`, valid `paper`).
- All dates match `YYYY-MM`, `YYYY`, or `Present`.
- All `##` section headers belong to the canonical set (or trigger explicit ATS warning).
- Zero unresolved `[TODO: ...]` markers.
- Zero banned AI clichés (optional lint warning).

### Layer 2: PDF Text-Layer & ATS Round-Trip Checks (Post-Render)
Run standard open-source extractors (`pdftotext`, `pdfplumber`, `pypdf`) on every generated PDF and assert:
- **Reading order fidelity**: Every job title appears immediately before its own bullets, and never interleaved with another section.
- **Unicode & ligature integrity**: All EU diacritics (`ü`, `ö`, `ä`, `é`, `ł`, `ø`, `ß`, `€`) and ligature-prone words (`profile`, `workflow`, `efficient`, `offline`) extract with 100% character accuracy.
- **Contact visibility**: Name, email, phone, and links appear in the extracted body text (proving nothing was trapped in a stripped header/footer artifact).
- **Zero visual-text discrepancy**: No invisible/hidden text; extracted text matches the rendered visible content.
- **Clickable link annotations**: All URLs in frontmatter/body exist as valid PDF URI annotations.
- **Page count sanity**: 1-page fixture stays 1 page; 2-page fixture stays 2 pages with no 3-line overflow onto page 3.

### Layer 3: LLM Structured Extraction Benchmark
Feed *only* the raw text extracted from the generated PDF (via `pdftotext`) into an LLM with a strict JSON extraction schema (simulating a real AI recruiter pipeline) and compare against the ground-truth Markdown source:
- **100% exact match** on: candidate name, email, location, work authorization, languages + CEFR levels.
- **100% exact match** on: list of employers, job titles, start/end dates, and total calculated years of experience.
- **≥95% recall** on: key quantified metrics and technical skills mapped to the correct employer.

---

## 3. Human Visual Review Rubric

Render each golden fixture's PDF pages to PNGs and inspect against a fixed checklist:
- **7.4-second F-pattern test**: Can you identify name, target role, location, last 2 job titles, companies, and dates in under 8 seconds?
- **Whitespace & rhythm**: Margins balanced (16–18mm), no cramped bullet walls, clear separation between roles and sections.
- **Pagination hygiene**: No orphaned headings at the bottom of page 1; no awkward 2-line spill onto an extra page.
- **Print test**: Legible and high-contrast in grayscale/black-and-white.

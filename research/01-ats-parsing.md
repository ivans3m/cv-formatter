# Research 01: ATS & Automated HR Parsing Systems (EU Priority)

## Executive Summary

Most online advice about "beating the ATS" is fear-driven folklore. Modern ATS platforms widely used in Europe—**Greenhouse, Lever, Ashby, Teamtailor, Recruitee, Personio**, and enterprise suites like **Workday**—almost never auto-reject candidates solely because of a missing keyword or a layout quirk. Instead, they act as **structured databases and search engines** backed by document parsers (such as **Textkernel**, built-in ML parsers, or LLM extractors).

The real danger of a badly formatted CV is not "instant robot rejection"—it is **silent data corruption**: scrambled job timelines, missing contact details, unindexed skills, and broken years-of-experience calculations that make a candidate invisible when recruiters filter or search.

---

## 1. The European ATS Landscape

| Platform | Origin / Footprint | Typical Employers | Parsing & Screening Behavior |
| :--- | :--- | :--- | :--- |
| **Teamtailor** | Sweden (Nordics, UK, NL, DACH) | SMBs & mid-market, brand-focused teams | Drag-and-drop CV parsing into structured profiles; strong GDPR workflows. |
| **Recruitee (Tellent)** | Netherlands (Western EU) | Tech scale-ups, collaborative SMBs | Automatic CV parsing into candidate cards; keyword search & filtering. |
| **Personio** | Germany (DACH + expanding EU) | European SMEs (all-in-one HR + recruiting) | Parses emailed/uploaded CVs into candidate profiles; simpler recruiting filters. |
| **Greenhouse** | US (heavy EU tech adoption) | Venture-backed tech, international hubs | Strict section-heading expectations; structured scorecards; split-screen PDF + parsed profile view. |
| **Ashby / Lever** | US (growing EU tech adoption) | High-growth tech & AI startups | Modern parsing + AI criteria-evidence highlighting; final decisions remain human. |
| **Workday** | US (global enterprise standard) | Multinationals, banks, Fortune 500 in EU | Rigid parser; notorious for scrambling multi-column layouts and tables during auto-fill. |
| **Textkernel / Sovren** | Netherlands (underlying parser API) | Embedded inside many EU ATS & staffing CRMs | Multilingual European parsing engine; relies on linear reading order and canonical section taxonomy. |

### European-Specific Parsing Factors
- **Multilingual & Unicode names/places**: European CVs routinely include diacritics (`ü`, `ö`, `ä`, `é`, `ł`, `ø`, `ß`) and mixed-language entities (e.g., an English CV with a German company or university name). PDFs **must** embed proper Unicode `ToUnicode` CMap tables so text extraction never turns accented characters into mojibake.
- **GDPR & Compliance**: EU-native ATS tools enforce strict data retention and consent rules. Minimizing unnecessary PII (date of birth, full street address, marital status, nationality) is both a privacy best practice and cleaner for parsing.

---

## 2. Myths vs. Reality

- **Myth**: *"ATS bots auto-reject 75% of resumes for missing keywords."*
  - **Reality**: Modern ATS platforms do not auto-reject on keyword scores. Automated disqualifications come almost exclusively from **explicit knockout questions** on the application form (e.g., work authorization in the EU, required language level, relocation eligibility, minimum years of experience).
- **Myth**: *"Recruiters never see the PDF."*
  - **Reality**: Recruiters typically view a **split-screen** showing the parsed structured profile alongside the original PDF. However, **search, filtering, and auto-fill** depend entirely on the parsed text layer.
- **Reality that actually hurts candidates**:
  1. **Search invisibility**: Recruiters search their ATS like Google (`"TypeScript" AND "Kubernetes" AND "Amsterdam"`). If a skill or standard job title is missing, trapped in an image/SVG, or split by weird hyphenation, the candidate never surfaces.
  2. **Broken auto-fill (Workday, Taleo, legacy portals)**: Corrupted reading order forces candidates to manually re-type their entire career or leaves broken date/title mappings in the recruiter's summary table.

---

## 3. What Actually Breaks ATS Parsers

1. **Multi-column layouts & sidebars**: Linear text extractors sweep left-to-right across the page coordinate plane, interleaving sidebar skills/contact details right into the middle of job descriptions.
2. **Tables & floating text boxes**: Parsers read table cells out of logical order, frequently detaching employment dates from their job titles or companies.
3. **Contact info in PDF headers/footers**: Many parsers treat page header/footer zones as repeated artifacts (like page numbers) and strip them—silently dropping email, phone, or LinkedIn URLs.
4. **Creative / non-standard section headings**: Headings like *"My Journey"*, *"Toolkit"*, or *"Superpowers"* confuse taxonomy classifiers (especially Greenhouse and Workday), causing work history or skills to be dumped into "Other/Summary" or dropped.
5. **Graphics, icons, skill bars, and flattened PDFs**: Rating bars (4/5 dots for Python), SVG icons replacing labels, or image-only PDFs are invisible to text parsers.
6. **Ambiguous date formats**: European (`DD/MM/YYYY`) vs. US (`MM/DD/YYYY`) numeric dates create ambiguity. Unambiguous `YYYY-MM` or `Mon YYYY` (e.g., `2023-04` or `Apr 2023 – Present`) parses cleanly everywhere.
7. **Broken ligatures & custom font encodings**: Some PDF generators emit ligatures (`fi`, `fl`) or custom glyph subsets without proper Unicode mapping, turning `"Profile"` into `"Prole"` in `pdftotext`.

---

## 4. Actionable Design Constraints for CV Formatter

| Constraint | Applies To | Requirement |
| :--- | :--- | :--- |
| **Single-column linear flow** | PDF Renderer | Strictly single-column body layout; visual reading order must equal PDF text-stream order. |
| **No contact info in page margins** | PDF Renderer | Name, location, email, phone, and links live in the main body flow at the top of page 1, never in PDF header/footer regions. |
| **No layout tables for experience** | PDF Renderer | Align dates using flex/grid/inline layout primitives that preserve linear text order (`Role — Company — Dates`), never `<table>` grids that split rows/columns in text extraction. |
| **Canonical section headings** | Schema & Skill | Use universally recognized headings: `Summary`, `Experience`, `Education`, `Skills`, `Projects`, `Languages`, `Certifications`. |
| **Unambiguous dates** | Schema & Skill | Store ISO-like `YYYY-MM` (or `YYYY`) in Markdown; render cleanly as `MMM YYYY – MMM YYYY` (or `Present`). |
| **Zero visual-only information** | Schema & PDF | No skill progress bars, star ratings, or icon-only labels. Every piece of information must exist as plain Unicode text. |
| **Clean Unicode text layer** | PDF Renderer | Verify every rendered PDF with `pdftotext` and `pdfplumber` to guarantee zero ligature corruption, zero mojibake on EU diacritics, and exact reading order. |

---

## References

- [Greenhouse](https://www.greenhouse.com/) — Structured hiring ATS widely used in EU tech.
- [Teamtailor](https://www.teamtailor.com/) — European ATS focused on employer branding and GDPR-native hiring.
- [Recruitee](https://recruitee.com/) — Dutch-born collaborative ATS across Western Europe.
- [Personio](https://www.personio.com/) — German all-in-one HR and recruiting platform for EU SMEs.
- [Textkernel](https://www.textkernel.com/) — Multilingual CV parsing engine powering many European HR systems.

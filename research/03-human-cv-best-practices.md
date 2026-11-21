# Research 03: Human CV Best Practices & Recruiter UX (EU Market Priority)

## Executive Summary

Even when a CV sails through ATS parsing and LLM summarization, a human recruiter or hiring manager makes the actual interview decision—and they form their initial impression in **~7.4 seconds** (Ladders eye-tracking study, 2018). A great CV for the European market combines **instant visual scannability**, **evidence-backed impact bullets**, **EU-native conventions** (A4 format, 1–2 pages, CEFR language levels, GDPR-clean personal details), and **authentic human prose** stripped of AI clichés.

---

## 1. How Humans Actually Scan a CV

Eye-tracking research (Ladders, 2012 & 2018) established clear behavioral patterns during initial screening:

- **The 7.4-second triage**: Recruiters do not read top-to-bottom on first pass. They triage whether to invest another 60 seconds.
- **F-pattern / E-pattern scanning**: Eyes start at the top left (name, headline/title, summary), sweep down the **left margin** checking job titles and companies, and flick right to verify **dates** and scan opening words of bullet points.
- **Top-third real estate**: The top third of page 1 must immediately answer three questions:
  1. *Who are you and what role do you do?* (Name + clear target title/headline)
  2. *Where are you based and can you work here?* (City, Country + optional work authorization / remote status)
  3. *What is your core value proposition?* (Tight 2–4 line summary or high-signal skills + top recent role)
- **What kills readability**: Dense walls of text (>4-line paragraphs), cramped margins, inconsistent date alignment, multi-column clutter that breaks the left-margin anchor, and weak typographic hierarchy.

---

## 2. European Market Conventions (EU Priority)

While Europe is not monolithic, pan-European tech, product, engineering, and international business hiring has converged on clear modern norms:

### Paper Size & Length
- **Paper size**: **A4** (`210 × 297 mm`) as the default, with clean support for US Letter (`8.5 × 11 in`) when applying to US companies.
- **Length**:
  - **1 page**: Junior/early-career (0–4 years) or tightly focused roles.
  - **2 pages**: Standard and expected for mid-to-senior professionals (5+ years), staff/principal ICs, managers, and consultants.
  - **Hard cap**: Avoid spilling 3–4 orphan lines onto page 3.

### Europass: Know When *Not* to Use It
- **Do not use Europass** for private-sector companies, startups, scale-ups, or international tech firms. It is verbose (often 3–5 pages), visually dated, and its multi-column templates can hurt ATS parsing.
- Only use Europass when explicitly mandated (EU institutions/EPSO, certain public tenders, or academic grants).

### Personal Details & GDPR Hygiene
- **Include**: Full name, City & Country (e.g., `Haarlem, Netherlands` or `Berlin, Germany`), Email, Phone (with country code, e.g., `+31 ...`), LinkedIn, GitHub / Portfolio / Personal Website.
- **Optional (high value in EU)**: Work authorization / visa status if relevant (e.g., `EU work permit` / `EU citizen` / `No sponsorship required`)—prevents unnecessary recruiter hesitation in cross-border EU hiring.
- **Omit by default**: Date of birth, age, marital status, nationality, full street address, ID numbers.
- **Photos**:
  - **NL, UK, Ireland, Nordics, international tech/remote**: **No photo** (actively discouraged to reduce unconscious bias).
  - **DACH (DE/AT/CH), Spain, Italy (traditional/non-tech)**: Still seen in traditional industries, though declining fast in tech.
  - **Default for our tool**: **No photo by default** (keeps the format minimalist, bias-resistant, and cleanly linear).

### Languages (CEFR Standard)
- European employers expect the **CEFR scale** (`A1`, `A2`, `B1`, `B2`, `C1`, `C2`, plus `Native`) rather than vague labels like *"Good"* or *"Conversational"*.
- Example: `English (C2 / Fluent), Dutch (B1), Ukrainian (Native)`.

---

## 3. Writing High-Signal Content (Without AI Slop)

### Bullet Point Frameworks
- **Google XYZ Formula**: *"Accomplished [X], as measured by [Y], by doing [Z]."*
- **CAR (Challenge → Action → Result)**: Useful for senior/architectural work where context matters.
- **Front-load impact**: Put the strong action verb and outcome near the start of the bullet so F-pattern scanners catch it immediately.
- **Honest quantification**: Quantify with real numbers wherever possible—revenue, cost saved, latency reduced, team size, users served, frequency, or delivery speed. **Never fabricate metrics.** When exact numbers are unavailable or confidential, use honest scope indicators (e.g., *"for 14 enterprise clients"*, *"across a 6-engineer team"*, *"cut weekly manual reporting from ~4 hours to 15 minutes"*).
- **Length discipline**: 1–2 lines per bullet; 3–5 bullets for recent/core roles, 1–3 for older roles, and brief 1-line summaries for roles >10 years old.

### Categorized Skills (Not a Keyword Cloud)
- Group skills into 3–6 logical categories (e.g., `Languages`, `Frameworks`, `Infrastructure`, `Data`, `Product & Methods`) rather than a 35-item comma-separated wall.
- Never use self-assessed ratings (`Python: 4/5`, `90% bar`)—they are meaningless to humans and unreadable to machines.

### Anti-AI-Slop Voice Rules
Recruiters immediately recognize and distrust raw LLM-rewritten CVs. The skill must strictly avoid:
- Hollow buzzwords and AI clichés: *"spearheaded transformative initiatives"*, *"seasoned results-driven professional"*, *"leveraged cutting-edge solutions"*, *"passionate self-starter"*, *"orchestrated seamless cross-functional synergy"*.
- Rounding concrete facts into vague superlatives (e.g., turning *"cut deploy time from 40 min to 6 min"* into *"dramatically enhanced deployment efficiency"*).
- Repetitive sentence cadence (every bullet starting with the same verb or identical 22-word rhythm).

---

## 4. Actionable Design Constraints for CV Formatter

| Constraint | Applies To | Requirement |
| :--- | :--- | :--- |
| **A4 default, Letter option** | PDF Renderer | Default page size is A4 (`210 × 297 mm`), configurable via CLI flag or frontmatter (`paper: a4 \| letter`). |
| **F-pattern visual hierarchy** | PDF Renderer | Strong left-aligned anchors for section headers, bold job titles, clear company names, right-aligned dates, generous whitespace (15–20 mm margins). |
| **GDPR-clean header** | Schema & Skill | Default contact block includes Name, Headline, City/Country, Email, Phone, Links, and optional Work Authorization—never DOB, full address, or photo by default. |
| **CEFR language format** | Schema & Skill | Dedicated `Languages` section using CEFR levels (`A1–C2` / `Native`). |
| **Categorized skills** | Schema & Skill | Key-value skill groups (`Category: Skill A, Skill B, Skill C`) instead of flat lists or visual rating bars. |
| **Anti-slop editorial guardrails** | Skill | Explicit negative list of AI clichés; preserve exact numbers, tools, and domain terminology; never invent metrics. |
| **Smart length budget** | Skill & PDF | Guide content toward 1 page (junior) or 2 pages (experienced), avoiding awkward page breaks or 2-line page-3 overflow. |

---

## References

- Ladders (2018). *Eye-Tracking Study: How Recruiters Read Resumes* (7.4-second scan & F-pattern findings).
- Bock, L. (2015). *Work Rules!* — Origin of the Google XYZ accomplishment bullet formula.
- Europass — [Common European Framework of Reference for Languages (CEFR) Self-Assessment](https://europass.europa.eu/en/common-european-framework-reference-language-skills)

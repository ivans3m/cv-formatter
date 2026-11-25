# Specification: Canonical Markdown CV Data Model (`cv-md/1.1`)

**Status:** v1.1 *(shipped in `v0.2.0`; backward-compatible with `cv-md/1.0`)*  
**Scope:** Single source-of-truth plain-text career data model designed for AI-driven workflows, human readability, ATS parsing, and deterministic PDF rendering.  
**Default Target:** European market (A4, CEFR languages, GDPR-clean personal metadata).

---

## 1. Design Principles & AI-Workflow Rationale

Most career documents fail in AI-driven workflows because they treat a CV as a **visual layout** (PDF/DOCX) rather than **structured data**. When an agent edits a PDF export or free-form prose, every tailoring pass drops history, blurs dates and promotions, or quietly introduces unverified claims. `cv-md/1.1` is designed as a lightweight data model first; linters, skills, and PDF renderers are secondary consumers of the file.

### Core Principles

1. **Readable as plain text, strict as a schema:** Valid UTF-8 CommonMark Markdown with zero custom template tags or conditional macros. Any human can edit and `git diff` it directly; any LLM or deterministic parser can read its AST unambiguously.
2. **Three-layer single-file architecture:**
   - **Typed YAML frontmatter** for structured identity, contact, EU work-right/availability metadata, locale settings, and tailoring state—never career prose.
   - **Canonical CommonMark body** for the public, renderable CV (`## Summary` through `## Interests`).
   - **Non-exported `## Facts` memory bank** for private candidate context, preferences, interview notes, and archived items trimmed during tailoring.
3. **Unambiguous entity binding:** Roles, nested promotions, ISO dates, locations, optional company context, and impact bullets follow a strict heading/metadata hierarchy so neither ATS parsers nor LLMs misattribute tenure, scope, or achievements.
4. **One schema across the entire lifecycle:** A 6-page `cv-master.md` career archive and a tight 2-page tailored `cv-<target>.md` obey the exact same grammar. Because `## Facts` travels with the file, compressing a CV for one vacancy is **lossless**—cut bullets are archived, not deleted.
5. **Explicit epistemic boundaries:** `tailor_mode: strict|dreamer` and the `**(Aspirational)**` bullet prefix separate verified career evidence from reach-role hypotheses at the data-model level, preventing AI agents from silently hallucinating into application PDFs.
6. **Strict visual-text parity:** Every public fact exists as plain Unicode text—no icon-only labels, no visual rating bars, no hidden keywords.

### Why Not JSON, Raw YAML, or PDF/DOCX?

| Format | Human Editing & Git Diff | LLM Native Read/Write | Lossless Tailoring | Deterministic PDF / ATS |
| :--- | :--- | :--- | :--- | :--- |
| **PDF / DOCX** | Poor (binary / layout-coupled) | Fragile (column interleaving, lost hierarchy) | No (manual copies drift) | Layout-dependent |
| **JSON Resume** | Noisy (braces, quotes, escaped newlines) | Syntax-error prone on long prose edits | No built-in archive layer | Strong |
| **YAML-only (e.g. RenderCV)** | Moderate (prose trapped in YAML strings + design config) | Mixes styling keys with career facts | No built-in archive layer | Strong |
| **`cv-md/1.1` (YAML + CommonMark)** | **Clean plain text & line-level diffs** | **Native token & heading structure** | **Built-in (`## Facts`)** | **100% linear, verified** |

---

## 2. File Structure

A valid `cv-md/1.1` file consists of:
1. A **YAML frontmatter block** delimited by `---` at the top of the file (structured contact, EU metadata, and document/tailoring state only).
2. A **CommonMark body** composed of canonical `##` sections, optionally ending with the non-exported `## Facts` memory bank.

File encoding **must** be UTF-8 (without BOM) with LF line endings.

---

## 3. YAML Frontmatter Schema

```yaml
---
schema: cv-md/1.1
name: Jane Doe
headline: Senior Backend Engineer
location: Amsterdam, Netherlands
work_authorization: EU Citizen (No sponsorship required)
availability: 1 month notice
email: jane@example.com
phone: "+31 6 1234 5678"
links:
  - label: LinkedIn
    url: https://linkedin.com/in/janedoe
  - label: GitHub
    url: https://github.com/janedoe
  - label: Website
    url: https://janedoe.dev
paper: a4
lang: en
---
```

### Field Reference

| Field | Type | Required | Description & Constraints |
| :--- | :--- | :--- | :--- |
| `schema` | string | **Yes** | Must be `cv-md/1.1` (or `cv-md/1.0` for backward compatibility). |
| `name` | string | **Yes** | Full display name (full Unicode/EU diacritics supported). |
| `headline` | string | No | Concise target role or professional title (max ~80 chars). |
| `location` | string | No | City and Country (e.g., `Berlin, Germany` or `Remote, EU`). Never full street address. |
| `work_authorization` | string | No | Optional EU/regional work-right note (e.g., `EU work permit`, `No sponsorship required`). |
| `availability` | string | No | Optional EU/NL/DACH availability or notice-period note rendered subtly in the header line (e.g., `Available immediately`, `1 month notice`). |
| `email` | string | **Yes** | Valid email address. |
| `phone` | string | No | International format with country code (e.g., `"+31 6 1234 5678"`). |
| `links` | list | No | Ordered list of `{ label, url }` objects (`https://` URLs). Recommended max 4 links. |
| `paper` | enum | No | `a4` (default) or `letter`. |
| `lang` | string | No | BCP-47 language tag (default `en`; e.g., `de`, `nl`, `fr`) used for PDF document language metadata (`PDF/UA`). |
| `accent` | string | No | Optional 6-digit hex accent color for PDF rendering (e.g., `#0F766E`; default `#71717A`). |
| `tailor_mode` | enum | No | `strict` (verified-only tailoring) or `dreamer` (aspirational bullets allowed with markers). |
| `tailor_target` | string | No | Human-readable label for the vacancy or slug (e.g., `Senior Backend @ Acme`). |

### Intentionally Omitted Fields (GDPR Hygiene)
The default schema does **not** include `date_of_birth`, `age`, `marital_status`, `nationality`, `id_number`, `street_address`, or `photo`.

---

## 4. Canonical Body Sections

Top-level sections use `##` headings. To maximize ATS taxonomy recognition and LLM consistency, use only these 14 canonical English headings (or their exact localized equivalents if `lang` is non-English):

| Section Heading | Required | Exported to PDF | Recommended Order | Content Format |
| :--- | :--- | :--- | :--- | :--- |
| `## Summary` | No | Yes | 1 | 1 tight paragraph (2–4 lines, ~40–65 words). No bullet lists. |
| `## Experience` | **Yes** | Yes | 2 | Reverse-chronological entries (`###` / optional `####`), including optional 1-line company context and career breaks. |
| `## Projects` | No | Yes | 3 | Reverse-chronological or priority-ordered entries (`###`). |
| `## Skills` | No | Yes | 4 | Categorized bullet list (`- **Category:** Item 1, Item 2`). |
| `## Education` | No | Yes | 5 | Reverse-chronological entries (`###`). |
| `## Languages` | No | Yes | 6 | Bullet list with CEFR levels (`- **Language:** Level`). |
| `## Certifications` | No | Yes | 7 | Compact bullet list with issuer, date/expiry, optional credential ID & verify link (`- **Name** — Issuer (YYYY-MM) \| [Verify](url)`). |
| `## Awards` | No | Yes | 8 | Compact bullet list (`- **Award** — Grantor (YYYY) — Optional 1-line context`). |
| `## Speaking` | No | Yes | 9 | Compact bullet list (`- **Talk Title** — Event (YYYY-MM) \| [Slides](url)`). |
| `## Publications` | No | Yes | 10 | Compact bullet list (`- **Title** — Venue (YYYY)` with optional link). |
| `## Volunteering` | No | Yes | 11 | Reverse-chronological entries (`### Role — Organization`) or compact bullets. |
| `## Courses` | No | Yes | 12 | Compact bullet list for bootcamps, MOOCs, or executive training (`- **Course** — Provider (YYYY)`). |
| `## Interests` | No | Yes | 13 | Optional 1–2 concise lines max (`- **Interests:** Item 1, Item 2`). |
| `## Facts` | No | **No** | 14 | **Markdown-only memory bank.** Categorized `Name — Description` bullets + optional `###` subheadings storing candidate facts, preferences, and trimmed items for lossless tailoring. |

*Note*: For junior candidates (0–2 years), `## Education` may be placed before `## Experience`.

### 4.1 Localized EU Canonical Headings (`nl`, `de`, `fr`)

When `lang` is Dutch (`nl`), German (`de`), or French (`fr`), the validator, renderer, verifier, and tailor pipeline recognize these localized headings as canonical equivalents with zero `NON_CANONICAL_SECTION` warnings:

| Canonical (`en`) | Dutch (`nl`) | German (`de`) | French (`fr`) |
| :--- | :--- | :--- | :--- |
| `Summary` | `Profiel`, `Samenvatting`, `Over mij` | `Profil`, `Zusammenfassung`, `Kurzprofil`, `Über mich` | `Profil`, `Résumé`, `À propos` |
| `Experience` | `Werkervaring`, `Ervaring` | `Berufserfahrung`, `Erfahrung` | `Expérience`, `Expérience professionnelle`, `Expériences`, `Expériences professionnelles` |
| `Projects` | `Projecten` | `Projekte` | `Projets` |
| `Skills` | `Vaardigheden`, `Competenties` | `Kenntnisse`, `Fähigkeiten`, `Kompetenzen` | `Compétences` |
| `Education` | `Opleiding`, `Opleidingen` | `Ausbildung`, `Bildung`, `Studium` | `Formation`, `Formations`, `Éducation` |
| `Languages` | `Talen` | `Sprachen`, `Sprachkenntnisse` | `Langues` |
| `Certifications` | `Certificeringen`, `Certificaten` | `Zertifizierungen`, `Zertifikate` | `Certifications`, `Certificats` |
| `Awards` | `Prijzen`, `Onderscheidingen`, `Prijzen & Onderscheidingen` | `Auszeichnungen`, `Preise` | `Prix`, `Distinctions`, `Prix et distinctions` |
| `Speaking` | `Lezingen`, `Sprekerservaring`, `Presentaties` | `Vorträge` | `Conférences`, `Interventions` |
| `Publications` | `Publicaties` | `Publikationen`, `Veröffentlichungen` | `Publications` |
| `Volunteering` | `Vrijwilligerswerk` | `Ehrenamt`, `Engagement` | `Bénévolat` |
| `Courses` | `Cursussen`, `Trainingen` | `Kurse`, `Weiterbildung`, `Fortbildungen` | `Cours`, `Formations complémentaires` |
| `Interests` | `Interesses`, `Hobby's` | `Interessen`, `Hobbys` | `Centres d'intérêt`, `Intérêts` |
| `Facts` | `Feiten` | `Fakten` | `Faits` |

---

## 5. Section Syntax Rules

### 5.1 Date Format
- Stored in Markdown as `YYYY-MM` (preferred), `YYYY` (acceptable for education/older roles), or `Present`.
- Ranges use an en-dash with spaces: `YYYY-MM – YYYY-MM` or `YYYY-MM – Present`.
- The PDF renderer formats `YYYY-MM` cleanly as `MMM YYYY` (e.g., `2023-04` → `Apr 2023`) while preserving unambiguous parsing.

### 5.2 `## Experience`

#### Standard Single-Role Entry (with Optional 1-Line Company Context)
```markdown
### <Role Title> — <Company Name>
*<Start> – <End> | <City, Country (Optional: Remote/Hybrid)>*

Optional 1-line company context for startups or lesser-known employers (e.g., Series A fintech, 45 employees, €12M ARR).

- <Impact bullet 1>
- <Impact bullet 2>
```
- Separator between Role and Company is an em-dash (` — `).
- Metadata line immediately below `###` is italicized (`*...*`), separating Date Range and Location with ` | `. Location is optional.
- Optional single plain-text paragraph immediately below the metadata line gives recruiters and LLMs quick company scale/domain context without spending an achievement bullet. Keep it to 1 line max.

#### Multiple Roles / Promotions at One Company
```markdown
### <Company Name>
*<Overall Start> – <Overall End> | <City, Country>*

#### <Most Recent Role Title> *(<Start> – <End>)*
- <Impact bullet 1>

#### <Previous Role Title> *(<Start> – <End>)*
- <Impact bullet 1>
```

#### Independent / Freelance / Consulting
```markdown
### <Role Title> — Independent (Freelance)
*<Start> – <End> | <City, Country (Remote, EU)>*

- **Client: <Client Name>** — <Impact bullet>
```

#### Career Break / Sabbatical / Parental Leave
Modern EU best practice: represent planned gaps concisely inside `## Experience` so ATS and LLM timeline parsers do not misread a gap as missing data:
```markdown
### Career Break — Relocation & Independent Study
*2023-06 – 2024-01 | Amsterdam, Netherlands*

- Relocated to the Netherlands, completed Dutch A2 coursework, and built open-source Python CLI tooling.
```

### 5.3 `## Projects`
```markdown
### <Project Name> — <Optional Role or Short Tagline>
*<Start> – <End> | [Link Label](https://example.com)*

- <Impact or architecture bullet>
```

### 5.4 `## Skills`
Categorized key-value bullets (3–6 categories recommended; never visual ratings):
```markdown
- **Languages:** Go, Python, TypeScript, SQL
- **Infrastructure:** Kubernetes, Terraform, AWS, PostgreSQL, Redis, Kafka
- **Practices:** Distributed Systems, OpenTelemetry, CI/CD
```

### 5.5 `## Education`
```markdown
### <Degree & Field> — <Institution Name>
*<Start YYYY> – <End YYYY> | <City, Country>*

- Optional single-line highlight (e.g., thesis topic, honors, relevant focus).
```

### 5.6 `## Languages` (CEFR Standard)
```markdown
- **English:** C2 (Proficient / Working Language)
- **Dutch:** B1 (Intermediate)
- **German:** A2 (Basic)
```
Valid CEFR tokens: `A1`, `A2`, `B1`, `B2`, `C1`, `C2`, `Native` (plus localized native equivalents: `Moedertaal`, `Muttersprache`, `Langue maternelle`, `Natif`).

### 5.7 `## Certifications`

Use `## Certifications` strictly for accredited vendor, industry, or regulatory credentials (e.g., AWS, CNCF, Meta Blueprint, Google Ads, PMP, CFA). Place informal MOOCs, workshops, or bootcamps under `## Courses` or `## Facts` so recruiters can scan verified credentials cleanly.

```markdown
## Certifications

- **CKA: Certified Kubernetes Administrator** — CNCF (2024-05 – 2027-05, ID: `LF-98231`) | [Verify](https://training.linuxfoundation.org/certification/verify/)
- **AWS Solutions Architect – Associate** — Amazon Web Services (2024-02) | [Verify](https://credly.com/badges/example)
- **Meta Certified Media Buying Professional** — Meta (2025-01)
```

- **Required parts:** Bold certification name (`**Name**`) and issuer (`— Issuer`).
- **Optional metadata in parentheses:** Issue date (`YYYY-MM` or `YYYY`), validity range (`YYYY-MM – YYYY-MM`), and/or credential ID (`ID: \`...\``).
- **Optional verification link:** Append ` | [Verify](https://...)` for clickable PDF verification.

### 5.8 Optional Sections: `## Awards`, `## Speaking`, `## Publications`, `## Volunteering`, `## Courses`, `## Interests`

All optional sections render in the single-column layout (compact spacing for bullet-only sections):

```markdown
## Awards

- **Dutch Interactive Awards (Gold — E-Commerce)** — Emerce (2024) — Checkout redesign lifting conversion by 18%

## Speaking

- **Designing ATS- and LLM-Readable CVs** — PyData Amsterdam (2025-09) | [Slides](https://example.com/slides)

## Publications

- **Zero-Downtime Schema Migrations at Scale** — [Engineering Blog](https://example.com/post) (2025)

## Volunteering

### Mentor — TechGrounds Amsterdam
*2023-03 – Present | Amsterdam, Netherlands*

- Mentored 12 career-switchers on backend engineering fundamentals and code reviews.

## Courses

- **Reforge Growth Series** — Reforge (2024)

## Interests

- **Interests:** Trail running, open-source typography, modular synthesizers
```

- Keep `## Interests` strictly to **1–2 concise lines** (never a multi-paragraph hobby essay).

### 5.9 `## Facts` (Markdown-Only Memory Bank — Not Exported to PDF)

`## Facts` is an optional, canonical, **non-rendered** section stored only in `.md` files. It solves the lossy-compression problem of CV editing and AI tailoring:

- **Never exported to PDF:** `cvfmt render` completely omits `## Facts`, and `cvfmt render --verify` asserts that `## Facts` content does not leak into the PDF text layer.
- **Format:** Categorized **Name — Description** bullets (`- **<Type: Name>** — <Description>`), optionally grouped under `###` subheadings (e.g., `### Target Roles & Preferences`, `### Extra Metrics & Context`, `### Archived Roles & Projects`, `### Dreamer rationale`).
- **Self-contained tailoring:** When creating a tailored CV from a master CV (or tweaking an existing CV), `## Facts` is carried forward and any trimmed/hidden items are moved into `## Facts` so every `.md` file remains lossless and re-tailorable.
- **Validation behavior:** `[TODO: ...]` markers and non-date `###` subheadings inside `## Facts` do **not** fail `cvfmt validate` or block PDF rendering. Skills mentioned only in `## Facts` do **not** count as public evidence for `## Skills` (since recruiters and ATS parsers never see `## Facts`).
- **Privacy note:** Because `## Facts` may hold private context (notice period, target compensation, candid notes), avoid publishing the raw `.md` file publicly without reviewing `## Facts` first.

```markdown
## Facts

### Target Roles & Preferences
- **Preference: Notice Period** — 1 month; open to remote EU or hybrid Amsterdam.

### Archived Projects & Skills
- **Project: Retail Checkout Redesign** — Created new checkout flow for a retail client; gained +2% conversion lift.
- **Skill: Origami** — Advanced modular paper folding (personal interest; keep off PDF).
```

### 5.10 Epistemic Tailoring Markers (`strict` vs. `dreamer`)

- **Strict tailored CVs** (`tailor_mode: strict` or absent): renderable bullets must be verifiable; no `**(Aspirational)**` prefix is permitted (`ASPIRATIONAL_IN_STRICT` hard error).
- **Dreamer CVs** (`tailor_mode: dreamer`): inferred or reach-role claims in renderable sections **must** start with `**(Aspirational)** `. Validation emits `ASPIRATIONAL_BULLET` warnings; `cvfmt render` strips aspirational bullets from PDFs by default unless `--allow-aspirational` is passed explicitly for an internal gap-analysis export.

---

## 6. Validation & Linting Contract

| Severity | Code | Rule | Behavior |
| :--- | :--- | :--- | :--- |
| **Error** | `SCHEMA_VERSION` | Missing or unsupported `schema` (not `cv-md/1.1` or `cv-md/1.0`) | Fail validation / block render |
| **Error** | `MISSING_NAME` | Missing frontmatter `name` | Fail validation / block render |
| **Error** | `INVALID_EMAIL` | Missing or malformed `email` | Fail validation / block render |
| **Error** | `INVALID_PAPER` | Invalid `paper` value (not `a4` or `letter`) | Fail validation / block render |
| **Error** | `INVALID_ACCENT` | Invalid `accent` value (not 6-digit hex) | Fail validation / block render |
| **Error** | `MISSING_EXPERIENCE` | Missing `## Experience` (or localized equivalent) | Fail validation / block render |
| **Error** | `INVALID_DATE` | Malformed date string (not `YYYY-MM`, `YYYY`, or `Present`) | Fail validation / block render |
| **Error** | `UNRESOLVED_TODO` | Unresolved `[TODO: ...]` in frontmatter or renderable body | Fail validation (overrideable via `--allow-todos`; `[TODO]` inside `## Facts` is ignored) |
| **Error** | `ASPIRATIONAL_IN_STRICT` | `**(Aspirational)**` bullet without `tailor_mode: dreamer` | Fail validation / block render |
| **Warning** | `NON_CANONICAL_SECTION` | Non-canonical `##` heading (outside EN/NL/DE/FR table) | Warn about ATS taxonomy risk |
| **Warning** | `MISSING_CEFR_LEVEL` | `## Languages` entry lacks a valid CEFR / native token | Warn about EU convention |
| **Warning** | `MISSING_LANGUAGES` | No `## Languages` section present | Soft EU market reminder |
| **Warning** | `ASPIRATIONAL_BULLET` | Aspirational bullet when `tailor_mode: dreamer` | Warn before submitting |
| **Warning** | `UNGROUNDED_SKILLS` | `## Skills` item not referenced in `## Experience` or `## Projects` | Warn about LLM rubric evidence gap |
| **Warning** | *(post-render)* | Rendered PDF exceeds 2 pages (or overflows <5 lines onto an extra page) | Warn during `--verify` |

---

## 7. Complete Golden Example (`cv-md/1.1`)

```markdown
---
schema: cv-md/1.1
name: Lukas Müller
headline: Senior Backend Engineer
location: Amsterdam, Netherlands
work_authorization: EU Citizen
availability: 1 month notice
email: lukas.mueller@example.eu
phone: "+31 6 2345 6789"
links:
  - label: LinkedIn
    url: https://linkedin.com/in/lukasmueller
  - label: GitHub
    url: https://github.com/lukasmueller
paper: a4
lang: en
---

## Summary

Backend engineer with 7 years of experience building high-throughput payment and data platforms in Go and Python across European fintech teams. Focused on distributed reliability, low-latency APIs, and pragmatic cloud infrastructure.

## Experience

### Acme Payments
*2021-03 – Present | Amsterdam, Netherlands (Hybrid)*

#### Senior Backend Engineer *(2023-04 – Present)*
- Reduced p95 checkout API latency from 420ms to 110ms across 12 Go services handling 40K req/s by redesigning Redis caching and PostgreSQL connection pooling.
- Led zero-downtime migration of a €180M/month SEPA settlement pipeline from a monolith to event-driven Kafka workers.
- Mentored 4 engineers and introduced automated load testing in CI, cutting severity-1 production incidents by 60%.

#### Backend Engineer *(2021-03 – 2023-03)*
- Built an idempotent webhook delivery service in Go processing 2M merchant events/day with 99.98% delivery SLA.
- Automated multi-region AWS infrastructure provisioning with Terraform, reducing environment setup time from 3 days to 25 minutes.

### NordCloud Analytics — Software Engineer
*2019-06 – 2021-02 | Berlin, Germany*

- Developed Python ETL pipelines ingesting 1.5B daily clickstream events into BigQuery and PostgreSQL.
- Cut monthly cloud compute spend by 28% (€14K/month) by migrating batch jobs to spot instances and optimizing SQL partitioning.

## Skills

- **Languages:** Go, Python, SQL, TypeScript
- **Data & Messaging:** PostgreSQL, Redis, Kafka, BigQuery
- **Infrastructure:** AWS, Kubernetes, Terraform, Docker, GitHub Actions, OpenTelemetry

## Education

### M.Sc. Computer Science — Technical University of Munich
*2017-10 – 2019-05 | Munich, Germany*

## Languages

- **German:** Native
- **English:** C2 (Proficient / Working Language)
- **Dutch:** B1 (Intermediate)

## Facts

### Target Roles & Preferences
- **Preference: Work Setup** — Open to hybrid Amsterdam or remote EU; 1 month notice period.

### Archived Projects & Context
- **Project: Internal TypeScript Admin Portal** — Built merchant reconciliation UI at Acme (2022); omitted from PDF to keep focus on backend systems.
```

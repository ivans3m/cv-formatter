# Specification: Canonical Markdown CV Format (`cv-md/1.1`)

**Status:** Draft v1.1 *(backward-compatible with `cv-md/1.0`)*  
**Scope:** Single source-of-truth plain-text CV format designed for equal readability by humans, ATS parsers, LLMs, and deterministic PDF rendering.  
**Default Target:** European market (A4, CEFR languages, GDPR-clean personal metadata).

---

## 1. Design Principles

1. **Readable as plain text**: Valid CommonMark Markdown with zero custom template tags or conditional syntax.
2. **Unambiguous entity binding**: Roles, companies, dates, locations, and bullets follow a strict, predictable hierarchy so neither ATS parsers nor LLMs misattribute tenure or achievements.
3. **Visual-text parity**: Every piece of information exists as plain Unicode text. No icon-only labels, no visual rating bars, no hidden text.
4. **One schema, two file roles**: The exact same schema is used for both a ready-to-send CV (`cv.md`, target 1–2 pages) and an optional career archive (`cv-master.md`, uncapped length).

---

## 2. File Structure

A valid CV Markdown file consists of:
1. A **YAML frontmatter block** delimited by `---` at the top of the file (structured contact & document metadata only; no career prose).
2. A **CommonMark body** composed of canonical `##` sections.

File encoding **must** be UTF-8 (without BOM), LF line endings.

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

Top-level sections use `##` headings. To maximize ATS taxonomy recognition and LLM consistency, use only these canonical English headings (or their exact localized equivalents if `lang` is non-English):

| Section Heading | Required | Recommended Order | Content Format |
| :--- | :--- | :--- | :--- |
| `## Summary` | No | 1 | 1 tight paragraph (2–4 lines, ~40–65 words). No bullet lists. |
| `## Experience` | **Yes** | 2 | Reverse-chronological entries (`###` / optional `####`), including optional 1-line company context and career breaks. |
| `## Projects` | No | 3 | Reverse-chronological or priority-ordered entries (`###`). |
| `## Skills` | No | 4 | Categorized bullet list (`- **Category:** Item 1, Item 2`). |
| `## Education` | No | 5 | Reverse-chronological entries (`###`). |
| `## Languages` | No | 6 | Bullet list with CEFR levels (`- **Language:** Level`). |
| `## Certifications` | No | 7 | Compact bullet list with issuer, date/expiry, optional credential ID & verify link (`- **Name** — Issuer (YYYY-MM) \| [Verify](url)`). |
| `## Awards` | No | 8 | Compact bullet list (`- **Award** — Grantor (YYYY) — Optional 1-line context`). |
| `## Speaking` | No | 9 | Compact bullet list (`- **Talk Title** — Event (YYYY-MM) \| [Slides](url)`). |
| `## Publications` | No | 10 | Compact bullet list (`- **Title** — Venue (YYYY)` with optional link). |
| `## Volunteering` | No | 11 | Reverse-chronological entries (`### Role — Organization`) or compact bullets. |
| `## Courses` | No | 12 | Compact bullet list for bootcamps, MOOCs, or executive training (`- **Course** — Provider (YYYY)`). |
| `## Interests` | No | 13 | Optional 1–2 concise lines max (`- **Interests:** Item 1, Item 2`). |
| `## Facts` | No | 14 | **Markdown-only (never exported to PDF).** Categorized `Name — Description` bullets + optional `###` subheadings storing candidate facts, preferences, and trimmed items for lossless tailoring. |

*Note*: For junior candidates (0–2 years), `## Education` may be placed before `## Experience`.

### 4.1 Localized EU Canonical Headings (`nl`, `de`, `fr`)

When `lang` is Dutch (`nl`), German (`de`), or French (`fr`), the validator, Typst renderer, verifier, and tailor pipeline recognize these localized headings as canonical equivalents with zero `NON_CANONICAL_SECTION` warnings:

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

All optional sections render in the single-column Warm Editorial layout (compact spacing for bullet-only sections):

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

`## Facts` is an optional, canonical, **non-rendered** section stored only in `.md` files. It solves the lossy-compression problem of CV editing and tailoring:

- **Never exported to PDF**: `cvfmt render` completely omits `## Facts`, and `cvfmt render --verify` asserts that `## Facts` content does not leak into the PDF text layer.
- **Format**: Categorized **Name — Description** bullets (`- **<Type: Name>** — <Description>`), optionally grouped under `###` subheadings (e.g., `### Target Roles & Preferences`, `### Extra Metrics & Context`, `### Archived Roles & Projects`).
- **Self-contained tailoring**: When creating a tailored CV from a master CV (or tweaking an existing CV), `## Facts` is carried forward and any trimmed/hidden items are moved into `## Facts` so every `.md` file remains lossless and re-tailorable.
- **Validation behavior**: `[TODO: ...]` markers and non-date `###` subheadings inside `## Facts` do **not** fail `cvfmt validate` or block PDF rendering. Skills mentioned only in `## Facts` do **not** count as public evidence for `## Skills` (since recruiters and ATS parsers never see `## Facts`).
- **Privacy note**: Because `## Facts` may hold private context (notice period, target compensation, candid notes), avoid publishing the raw `.md` file publicly without reviewing `## Facts` first.

### 5.10 Role tailoring & dreamer markers

- **Strict tailored CVs** (`tailor_mode: strict` or absent): renderable bullets must be verifiable; no `**(Aspirational)**` prefix.
- **Dreamer CVs** (`tailor_mode: dreamer`): imagined or inferred claims in renderable sections **must** start with `**(Aspirational)** `. Validation emits `ASPIRATIONAL_BULLET` warnings; `cvfmt render` omits aspirational bullets unless `--allow-aspirational`.
- **CLI strict tailor**: `cvfmt tailor JOB.txt --base cv-master.md -o cv-target.md --mode strict` performs deterministic reorder/trim without LLM summary rewrites.

```markdown
## Facts

### Target Roles & Preferences
- **Preference: Notice Period** — 1 month; open to remote EU or hybrid Amsterdam.

### Archived Projects & Skills
- **Project: Retail Checkout Redesign** — Created new checkout flow for a retail client; gained +2% conversion lift.
- **Skill: Origami** — Advanced modular paper folding (personal interest; keep off PDF).
```

---

## 6. Validation & Linting Contract

| Severity | Rule | Behavior |
| :--- | :--- | :--- |
| **Error** | Missing or unsupported `schema` | Fail validation / block render |
| **Error** | Missing `name` or invalid `email` | Fail validation / block render |
| **Error** | Invalid `paper` value (not `a4` or `letter`) | Fail validation / block render |
| **Error** | Malformed date string (not `YYYY-MM`, `YYYY`, or `Present`) | Fail validation / block render |
| **Error** | Unresolved `[TODO: ...]` placeholder in frontmatter or renderable body sections | Fail validation (overrideable with `--allow-todos`; `[TODO]` inside non-exported `## Facts` is ignored) |
| **Warning** | Non-canonical `##` section heading | Warn about ATS taxonomy risk |
| **Warning** | `## Skills` item not referenced anywhere in `## Experience` or `## Projects` | Warn about LLM rubric evidence gap |
| **Warning** | Missing `## Languages` section | Soft EU market reminder |
| **Warning** | Rendered PDF exceeds 2 pages (or overflows <5 lines onto an extra page) | Warn after compilation |
| **Error** | `**(Aspirational)**` in renderable sections without `tailor_mode: dreamer` | Fail validation (`ASPIRATIONAL_IN_STRICT`) |
| **Warning** | Aspirational bullet when `tailor_mode: dreamer` | Warn (`ASPIRATIONAL_BULLET`) |

---

## 7. Complete Golden Example (`cv-md/1.1`)

```markdown
---
schema: cv-md/1.1
name: Lukas Müller
headline: Senior Backend Engineer
location: Amsterdam, Netherlands
work_authorization: EU Citizen
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
```

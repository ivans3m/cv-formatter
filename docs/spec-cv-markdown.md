# Specification: Canonical Markdown CV Format (`cv-md/1.0`)

**Status:** Draft v1.0  
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
schema: cv-md/1.0
name: Jane Doe
headline: Senior Backend Engineer
location: Amsterdam, Netherlands
work_authorization: EU Citizen (No sponsorship required)
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
---
```

### Field Reference

| Field | Type | Required | Description & Constraints |
| :--- | :--- | :--- | :--- |
| `schema` | string | **Yes** | Must be `cv-md/1.0`. |
| `name` | string | **Yes** | Full display name (full Unicode/EU diacritics supported). |
| `headline` | string | No | Concise target role or professional title (max ~80 chars). |
| `location` | string | No | City and Country (e.g., `Berlin, Germany` or `Remote, EU`). Never full street address. |
| `work_authorization` | string | No | Optional EU/regional work-right note (e.g., `EU work permit`, `No sponsorship required`). |
| `email` | string | **Yes** | Valid email address. |
| `phone` | string | No | International format with country code (e.g., `"+31 6 1234 5678"`). |
| `links` | list | No | Ordered list of `{ label, url }` objects (`https://` URLs). Recommended max 4 links. |
| `paper` | enum | No | `a4` (default) or `letter`. |
| `lang` | string | No | BCP-47 language tag (default `en`; e.g., `de`, `nl`, `fr`) used for PDF document language metadata (`PDF/UA`). |

### Intentionally Omitted Fields (GDPR Hygiene)
The default schema does **not** include `date_of_birth`, `age`, `marital_status`, `nationality`, `id_number`, `street_address`, or `photo`.

---

## 4. Canonical Body Sections

Top-level sections use `##` headings. To maximize ATS taxonomy recognition and LLM consistency, use only these canonical English headings (or their exact localized equivalents if `lang` is non-English):

| Section Heading | Required | Recommended Order | Content Format |
| :--- | :--- | :--- | :--- |
| `## Summary` | No | 1 | 1 tight paragraph (2–4 lines, ~40–65 words). No bullet lists. |
| `## Experience` | **Yes** | 2 | Reverse-chronological entries (`###` / optional `####`). |
| `## Projects` | No | 3 | Reverse-chronological or priority-ordered entries (`###`). |
| `## Skills` | No | 4 | Categorized bullet list (`- **Category:** Item 1, Item 2`). |
| `## Education` | No | 5 | Reverse-chronological entries (`###`). |
| `## Languages` | No | 6 | Bullet list with CEFR levels (`- **Language:** Level`). |
| `## Certifications` | No | 7 | Compact bullet list (`- **Name** — Issuer (YYYY)`). |
| `## Publications` | No | 8 | Compact bullet list (`- **Title** — Venue (YYYY)` with optional link). |

*Note*: For junior candidates (0–2 years), `## Education` may be placed before `## Experience`.

---

## 5. Section Syntax Rules

### 5.1 Date Format
- Stored in Markdown as `YYYY-MM` (preferred), `YYYY` (acceptable for education/older roles), or `Present`.
- Ranges use an en-dash with spaces: `YYYY-MM – YYYY-MM` or `YYYY-MM – Present`.
- The PDF renderer formats `YYYY-MM` cleanly as `MMM YYYY` (e.g., `2023-04` → `Apr 2023`) while preserving unambiguous parsing.

### 5.2 `## Experience`

#### Standard Single-Role Entry
```markdown
### <Role Title> — <Company Name>
*<Start> – <End> | <City, Country (Optional: Remote/Hybrid)>*

- <Impact bullet 1>
- <Impact bullet 2>
```
- Separator between Role and Company is an em-dash (` — `).
- Metadata line immediately below `###` is italicized (`*...*`), separating Date Range and Location with ` | `. Location is optional.

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
Valid CEFR tokens: `A1`, `A2`, `B1`, `B2`, `C1`, `C2`, `Native`.

### 5.7 `## Certifications` & `## Publications`
```markdown
## Certifications

- **CKA: Certified Kubernetes Administrator** — CNCF (2024)

## Publications

- **Zero-Downtime Schema Migrations at Scale** — [Engineering Blog](https://example.com/post) (2025)
```

---

## 6. Validation & Linting Contract

| Severity | Rule | Behavior |
| :--- | :--- | :--- |
| **Error** | Missing or unsupported `schema` | Fail validation / block render |
| **Error** | Missing `name` or invalid `email` | Fail validation / block render |
| **Error** | Invalid `paper` value (not `a4` or `letter`) | Fail validation / block render |
| **Error** | Malformed date string (not `YYYY-MM`, `YYYY`, or `Present`) | Fail validation / block render |
| **Error** | Unresolved `[TODO: ...]` placeholder in body or frontmatter | Fail validation (overrideable only with `--allow-todos`) |
| **Warning** | Non-canonical `##` section heading | Warn about ATS taxonomy risk |
| **Warning** | `## Skills` item not referenced anywhere in `## Experience` or `## Projects` | Warn about LLM rubric evidence gap |
| **Warning** | Missing `## Languages` section | Soft EU market reminder |
| **Warning** | Rendered PDF exceeds 2 pages (or overflows <5 lines onto an extra page) | Warn after compilation |

---

## 7. Complete Golden Example (`cv-md/1.0`)

```markdown
---
schema: cv-md/1.0
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

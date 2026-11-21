# Research 04: Standardized Markdown CV Data Structure

## Executive Summary

Existing CV-as-code formats optimize for either machines ([JSON Resume](https://jsonresume.org/)) or a single rendering engine ([RenderCV](https://rendercv.com/) YAML). Neither reads naturally as a human document, and both add syntactic noise for LLMs and plain-text editors.

Our recommended format is **Frontmatter + Canonical Markdown (`.md`)**:
- **YAML Frontmatter** holds structured header/contact metadata and minimal document config (e.g., `paper: a4`).
- **Standard CommonMark Body** holds the actual CV content using canonical `##` section headings, predictable `###` entry headers, a structured metadata line for dates/location, and standard `-` bullets.

It is immediately legible in any text editor or GitHub preview, token-efficient and unambiguous for LLMs, and deterministic to parse into an AST for PDF rendering.

---

## 1. Prior Art Comparison

| Dimension | JSON Resume | RenderCV (YAML) | Europass XML/PDF | **Proposed: Canonical Markdown (`.md`)** |
| :--- | :--- | :--- | :--- | :--- |
| **Human readability** | Low (braces, quotes, `\n` escapes) | Medium (config-file feel) | Low | **High** (reads like a clean document) |
| **LLM comprehension** | Good, but token-heavy | Good, slightly verbose | Poor | **Optimal** (native LLM format) |
| **Deterministic parsing** | Strict JSON Schema | Strict JSON Schema | Strict XML | **Strict via Frontmatter + AST rules** |
| **Design decoupling** | Full (external themes) | Coupled (`design:` block in file) | Rigid | **Decoupled** (optional `paper` / `accent` hint only) |
| **Editability by non-devs** | Hard | Medium | Web UI only | **Easy** (any Markdown editor) |

---

## 2. Proposed Canonical Markdown Structure (Draft v0.1)

### Frontmatter (Metadata Only — No Prose)

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
paper: a4 # a4 (default) | letter
---
```

**Design notes on frontmatter:**
- **GDPR-clean by default**: No `date_of_birth`, `nationality`, `marital_status`, `street_address`, or `photo` fields in the default template.
- **Explicit `work_authorization` (optional)**: High-value in cross-border EU hiring; prevents recruiter guesswork without exposing sensitive PII.
- **Explicit `schema` version**: Enables clean forward compatibility and strict CLI validation.

### Canonical Body Sections (Ordered for EU Recruiter & ATS Parsing)

Only universally recognized `##` headings are used:

1. `## Summary` *(optional, 2–4 lines max; plain paragraph)*
2. `## Experience` *(required; reverse-chronological)*
3. `## Projects` *(optional; open-source, side projects, or key engagements)*
4. `## Skills` *(recommended; categorized key-value lines)*
5. `## Education` *(required or optional for very senior profiles)*
6. `## Languages` *(strongly recommended for EU; CEFR levels)*
7. `## Certifications` *(optional)*
8. `## Publications` *(optional)*

### Entry Syntax (Unambiguous Binding of Role, Company, Location, Dates)

#### Standard Experience Entry
```markdown
## Experience

### Senior Backend Engineer — Acme Payments
*2023-04 – Present | Amsterdam, Netherlands (Hybrid)*

- Reduced p95 checkout API latency from 420ms to 110ms across 12 Go services handling 40K req/s by redesigning Redis caching and connection pooling.
- Led migration of €180M/month SEPA settlement pipeline from monolith to event-driven Kafka workers with zero downtime.
- Mentored 4 mid-level engineers and introduced automated load testing in CI, cutting production incidents by 60%.
```

#### Multiple Roles / Promotions at One Company
Represent promotions without duplicating the company or confusing total tenure math:
```markdown
### Acme Payments
*2021-01 – Present | Amsterdam, Netherlands*

#### Senior Backend Engineer *(2023-04 – Present)*
- Led migration of €180M/month SEPA settlement pipeline...

#### Backend Engineer *(2021-01 – 2023-03)*
- Built idempotent webhook delivery service processing 2M events/day...
```

#### Consulting / Freelance Engagements
Explicitly mark engagement type so overlapping dates do not look like parsing errors:
```markdown
### Principal AI Consultant — Independent (Freelance)
*2024-01 – Present | Haarlem, Netherlands (Remote, EU)*

- **Client: FinTech Co.** — Designed RAG evaluation harness over 150K compliance documents, improving citation precision from 68% to 94%.
- **Client: Retail Group** — Cut AWS inference spend by €9K/month by distilling classification workloads to smaller models.
```

#### Categorized Skills & CEFR Languages
```markdown
## Skills

- **Languages:** Go, Python, TypeScript, SQL
- **Infrastructure:** Kubernetes, Terraform, AWS, PostgreSQL, Redis, Kafka
- **Practices:** Distributed Systems, Observability (OpenTelemetry), CI/CD

## Languages

- **English:** C2 (Proficient / Working Language)
- **Dutch:** B1 (Intermediate)
- **German:** A2 (Basic)
```

---

## 3. Master CV vs. Tailored CV: Tradeoff Analysis & Recommendation

You mentioned being unsure whether the format should support a "master CV" (with tags/filters to generate tailored versions) or stay a single ready-to-send CV.

| Option | Pros | Cons |
| :--- | :--- | :--- |
| **A. Built-in conditional syntax** (e.g., `<!-- tags: backend, fintech -->` or YAML filters inside one file) | Single file holds entire career history; CLI can filter deterministically. | Pollutes plain-text readability; adds custom syntax that breaks pure Markdown ergonomics; LLMs and humans still need to rewrite summaries and reorder bullets for real tailoring (tag filtering alone produces clunky CVs). |
| **B. One schema, two file roles (`cv-master.md` → `cv-<target>.md`)** | **Zero extra syntax**; every `.md` file is 100% clean, readable, and directly renderable; tailoring is handled naturally by the **Agent Skill** (which can read `cv-master.md` + a job description and output a tight 1–2 page `cv-acme.md` in the exact same schema). | Requires keeping `cv-master.md` updated as the source of truth when adding new achievements. |

### Recommendation: **Option B (One Schema, Two File Roles)**
Keep the Markdown format completely free of template tags or conditional logic. A user who only wants one CV just maintains `cv.md`. A user who applies to varied roles maintains `cv-master.md` (same schema, no 2-page cap) and uses the Skill to generate a clean, 1–2 page tailored `cv-<role>.md` whenever needed.

---

## 4. Validation & Linting Rules (for CLI & Skill)

- **Hard errors** (block PDF export):
  - Missing required frontmatter (`name`, `email`).
  - Invalid date format (must be `YYYY-MM`, `YYYY`, or `Present`).
  - Unresolved `[TODO: ...]` placeholders left over from silent-mode rewriting.
- **Soft warnings** (allow export, print actionable feedback):
  - Non-canonical `##` section heading (warns about ATS taxonomy risk).
  - Rendered PDF exceeds 2 pages (or overflows by <5 lines onto page 3).
  - Skill listed in `## Skills` never appears in `## Experience` or `## Projects` (LLM rubric evidence gap).
  - Missing `## Languages` section (EU market reminder).

---

## References

- [JSON Resume Schema](https://jsonresume.org/)
- [RenderCV](https://rendercv.com/)
- [Reactive Resume](https://rxresu.me/)
- [Europass](https://europass.europa.eu/)

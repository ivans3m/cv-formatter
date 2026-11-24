# Reference: Canonical Markdown CV Schema (`cv-md/1.1`)

## Frontmatter (YAML, UTF-8, LF)

```yaml
---
schema: cv-md/1.1
name: Full Name
headline: Target Role or Title
location: City, Country
work_authorization: EU Citizen # optional
availability: 1 month notice # optional (EU/NL/DACH availability or notice period)
email: name@example.com
phone: "+31 6 1234 5678" # optional
links:
  - label: LinkedIn
    url: https://linkedin.com/in/username
  - label: GitHub
    url: https://github.com/username
paper: a4 # a4 (default) | letter
lang: en  # BCP-47 language tag (default: en)
---
```

- **Required**: `schema` (`cv-md/1.1`; `cv-md/1.0` remains accepted for backward compatibility), `name`, `email`.
- **Omit by default (GDPR)**: `date_of_birth`, `age`, `marital_status`, `nationality`, `street_address`, `photo`.

## Canonical `##` Sections

Use only these canonical top-level headings (or their recognized `nl`/`de`/`fr` localized equivalents when `lang` is non-English; junior CVs may place `## Education` before `## Experience`):

1. `## Summary` — 1 tight paragraph (2–4 lines, ~40–65 words). No bullets.
2. `## Experience` *(required)* — Reverse-chronological entries (optional 1-line company context paragraph; optional Career Break / Sabbatical entry).
3. `## Projects` — Open-source, portfolio, or key technical projects.
4. `## Skills` — 3–6 categorized key-value bullets.
5. `## Education` — Reverse-chronological degrees.
6. `## Languages` — CEFR levels (`A1`, `A2`, `B1`, `B2`, `C1`, `C2`, `Native`, or localized `Moedertaal` / `Muttersprache` / `Langue maternelle`).
7. `## Certifications` — Accredited credentials with issuer, date/expiry, optional credential ID & verify link.
8. `## Awards` — Honors, industry awards, hackathons, scholarships (compact bullets).
9. `## Speaking` — Conference talks, panels, podcasts, workshops (compact bullets).
10. `## Publications` — Articles, papers, books (compact bullets with optional links).
11. `## Volunteering` — Pro bono work, OSS maintainership, mentoring (`### Role — Organization` or compact bullets).
12. `## Courses` — Structured bootcamps, MOOCs, executive education (compact bullets; keeps `## Certifications` clean).
13. `## Interests` — Optional 1–2 concise lines max (`- **Interests:** ...`).
14. `## Facts` *(optional, Markdown-only — **never exported to PDF**)* — Candidate memory bank storing omitted roles/projects, extra metrics, skills, and interview context for future tailoring.

Recognized localized EU headings (`nl` / `de` / `fr`): `Profiel` / `Werkervaring` / `Vaardigheden` / `Opleiding` / `Talen` / `Certificeringen` / `Feiten`, `Berufserfahrung` / `Kenntnisse` / `Ausbildung` / `Sprachen` / `Zertifizierungen` / `Fakten`, `Expérience professionnelle` / `Compétences` / `Formation` / `Langues` / `Certificats` / `Faits` (see `docs/spec-cv-markdown.md` §4.1 for the full table).

## Entry Patterns

### Standard Experience Entry (with Optional 1-Line Company Context)
```markdown
### <Role Title> — <Company Name>
*<YYYY-MM> – <YYYY-MM|Present> | <City, Country (Optional: Remote/Hybrid)>*

Optional 1-line company context for startups or non-household-name employers.

- <Impact bullet 1>
- <Impact bullet 2>
```

### Career Break / Sabbatical / Parental Leave (inside `## Experience`)
```markdown
### Career Break — Relocation & Independent Study
*<YYYY-MM> – <YYYY-MM> | <City, Country>*

- Brief 1-line summary of focus during the break.
```

### Multiple Roles / Promotions at One Company
```markdown
### <Company Name>
*<Overall Start> – <Overall End> | <City, Country>*

#### <Most Recent Role> *(<Start> – <End>)*
- <Impact bullet>

#### <Previous Role> *(<Start> – <End>)*
- <Impact bullet>
```

### Freelance / Consulting
```markdown
### <Role Title> — Independent (Freelance)
*<Start> – <End> | <City, Country (Remote, EU)>*

- **Client: <Client Name>** — <Impact bullet>
```

### Skills, Education, Languages, Certifications, Publications
```markdown
## Skills

- **Languages:** Go, Python, SQL
- **Infrastructure:** AWS, Kubernetes, Terraform

## Education

### <Degree & Field> — <Institution Name>
*<YYYY-MM|YYYY> – <YYYY-MM|YYYY> | <City, Country>*

## Languages

- **English:** C2 (Proficient / Working Language)
- **Dutch:** B1 (Intermediate)

## Certifications

- **CKA: Certified Kubernetes Administrator** — CNCF (2024-05 – 2027-05, ID: `LF-98231`) | [Verify](https://example.com/verify)

## Awards

- **Award Name** — Grantor (2024) — Optional 1-line context

## Speaking

- **Talk Title** — Conference Name (2025-09) | [Slides](https://example.com/slides)

## Publications

- **Article Title** — [Venue](https://example.com) (2025)

## Volunteering

### Mentor — TechGrounds Amsterdam
*2023-03 – Present | Amsterdam, Netherlands*

- Mentored 12 career-switchers on backend engineering fundamentals.

## Courses

- **Reforge Growth Series** — Reforge (2024)

## Interests

- **Interests:** Trail running, open-source typography
```

## Date Rules
- Use `YYYY-MM`, `YYYY`, or `Present`.
- Separate ranges with spaced en-dash: `2023-04 – Present`.

## `## Facts` (Markdown-Only Memory Bank)

- Stored in `.md` files only; `cvfmt render` completely omits `## Facts` from PDF output.
- Use categorized **Name — Description** bullets (`- **<Type: Name>** — <Description>`) and optional `###` subheadings (e.g., `### Target Roles & Preferences`, `### Extra Metrics & Context`, `### Archived Roles & Projects`).
- Always carry `## Facts` into tailored `.md` files and park any trimmed/hidden items here so nothing is ever lost.

```markdown
## Facts

### Target Roles & Preferences
- **Preference: Notice Period** — 1 month; open to remote EU or hybrid Amsterdam.

### Archived Projects & Skills
- **Project: Retail Checkout Redesign** — Created new checkout flow for a retail client; gained +2% conversion lift.
- **Skill: Origami** — Advanced modular paper folding (personal interest; keep off PDF).
```

## Tailoring metadata (optional)

- `tailor_mode: strict` — verified-only tailored CV (default when tailoring for applications).
- `tailor_mode: dreamer` — allows `**(Aspirational)**` bullets in renderable sections (gap-analysis drafts).
- `tailor_target: "<Role or vacancy label>"` — used when archiving trimmed bullets under `## Facts`.

See also `skills/cv-tailor/` and `cvfmt tailor`.

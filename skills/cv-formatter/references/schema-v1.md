# Reference: Canonical Markdown CV Schema (`cv-md/1.1`)

## Frontmatter (YAML, UTF-8, LF)

```yaml
---
schema: cv-md/1.1
name: Full Name
headline: Target Role or Title
location: City, Country
work_authorization: EU Citizen # optional
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

Use only these canonical top-level headings (in this recommended order; junior CVs may place `## Education` before `## Experience`):

1. `## Summary` — 1 tight paragraph (2–4 lines, ~40–65 words). No bullets.
2. `## Experience` *(required)* — Reverse-chronological entries.
3. `## Projects` — Open-source, portfolio, or key technical projects.
4. `## Skills` — 3–6 categorized key-value bullets.
5. `## Education` — Reverse-chronological degrees.
6. `## Languages` — CEFR levels (`A1`, `A2`, `B1`, `B2`, `C1`, `C2`, `Native`).
7. `## Certifications` — Compact bullets.
8. `## Publications` — Compact bullets with optional links.
9. `## Facts` *(optional, Markdown-only — **never exported to PDF**)* — Candidate memory bank storing omitted roles/projects, extra metrics, skills, and interview context for future tailoring.

## Entry Patterns

### Standard Experience Entry
```markdown
### <Role Title> — <Company Name>
*<YYYY-MM> – <YYYY-MM|Present> | <City, Country (Optional: Remote/Hybrid)>*

- <Impact bullet 1>
- <Impact bullet 2>
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

- **CKA: Certified Kubernetes Administrator** — CNCF (2024)

## Publications

- **Article Title** — [Venue](https://example.com) (2025)
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

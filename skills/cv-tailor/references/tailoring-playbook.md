# Tailoring playbook (strict)

## Inputs

- Base: `cv-master.md` or any `cv-md/1.1` with optional `## Facts`
- JD: pasted text, `.md`, or URL (summarize if long)

## Steps

1. **Extract JD signals**: role title, seniority, must-have tech, domain (fintech, payments, etc.), geography, language requirements.
2. **Map evidence**: For each must-have, locate a supporting bullet in Experience/Projects or promotable fact in `## Facts`.
3. **Summary (2–3 lines)**: Mirror JD terminology where truthful; never add tools or metrics not in the source.
4. **Experience order**: Most relevant roles first; within roles, strongest JD-aligned bullets first.
5. **Prune**: Fit 1 page (&lt;5 yrs) or 2 pages (5+ yrs). Move trimmed bullets to `## Facts` under `### Archived for <target>`:
   - `- **Experience / <Company>** — <original bullet>`
6. **Skills**: 3–6 categories; JD-aligned skills first; drop ungrounded skills or move context to Facts.
7. **Frontmatter**: Set `tailor_mode: strict`, `tailor_target`, optionally update `headline`.

## Output checklist

- Valid `cv-md/1.1`, `email` present
- No `**(Aspirational)**` in renderable sections
- `## Facts` present and self-contained
- User warned not to publish raw `.md` if Facts contain private notes
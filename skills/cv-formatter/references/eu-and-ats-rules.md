# Reference: EU Market, ATS & LLM Screening Rules

## European Market Defaults

- **Paper size**: `a4` default (`letter` only for US-focused applications).
- **Length**: 1 page for early-career (0–4 years); 2 pages max for mid-to-senior (5+ years). Never spill 2–4 orphan lines onto page 3.
- **No Europass**: Do not mirror Europass's verbose multi-column layout for private-sector/tech roles.
- **GDPR hygiene**: City & Country only (never full home street address). Omit date of birth, age, marital status, nationality, ID numbers, and photos by default.
- **Work authorization & availability**: Include `work_authorization` in frontmatter when helpful for cross-border EU hiring (e.g., `EU Citizen`, `EU work permit`, `No sponsorship required`), and optional `availability` (e.g., `Available immediately`, `1 month notice`) when relevant in NL/DACH screening.
- **Languages**: Always use **CEFR levels** (`A1`, `A2`, `B1`, `B2`, `C1`, `C2`, or `Native`) instead of vague words like "Good" or "Conversational".
- **Career breaks**: Represent planned gaps (relocation, parental leave, sabbatical) concisely inside `## Experience` as `### Career Break — <Focus>` with standard dates so timeline parsers never treat them as missing data.

## ATS & Automated HR Parser Constraints

- **Single-column linear flow**: Never use Markdown tables to lay out experience, dates, or skills.
- **Canonical headings**: Stick strictly to `Summary`, `Experience`, `Projects`, `Skills`, `Education`, `Languages`, `Certifications`, `Awards`, `Speaking`, `Publications`, `Volunteering`, `Courses`, `Interests`, `Facts` (or their recognized `nl`/`de`/`fr` localized equivalents). Creative headings ("My Journey", "Superpowers") break Greenhouse/Workday/Textkernel taxonomy classification.
- **Exact target job title**: If targeting a specific role (e.g., `Senior Backend Engineer`), reflect the standard title truthfully in `headline` or `Summary` so recruiter database searches surface the profile.
- **Zero visual-only data**: Never include star ratings, dot scales (`4/5`), or progress bars.

## LLM Screening & EU AI Act Constraints

- **Tight entity binding**: Keep `Role`, `Company`, `Dates`, and `Location` directly above the role's bullets so LLM structured extractors never conflate adjacent jobs or double-count tenure.
- **Evidence-grounded skills**: Rubric-based AI screeners penalize flat keyword dumps. Every major technology in `## Skills` should have concrete usage in `## Experience` or `## Projects`.
- **Zero manipulation**: Never add hidden text, white-on-white keywords, or prompt-injection lines. Modern screeners run text-vs-visual discrepancy checks and flag manipulation.
- **Human-in-the-loop reality**: Under EU AI Act (Annex III, Point 4(a)) and GDPR Article 22, AI tools surface structured evidence for human reviewers—concrete numbers, scope, and verifiable outcomes win both machine rubrics and the 7.4-second human F-pattern scan.

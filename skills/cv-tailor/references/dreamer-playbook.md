# Dreamer playbook

Dreamer mode produces a **benchmark CV** and **gap analysis**, not a submission-ready file.

## Process

1. Parse JD must-haves vs master CV + Facts coverage.
2. For each gap (missing metric, unclear scope, absent JD keyword with partial evidence), draft the **strongest plausible** addition.
3. Mark every invented or inferred renderable claim:
   - Bullet: `- **(Aspirational)** <text>`
4. Log in chat and in `## Facts`:

```markdown
### Dreamer rationale
- **Gap: Kafka at scale** — JD requires event streaming; master CV mentions migrations but not Kafka — aspirational bullet added pending user confirmation.
```

5. Set `tailor_mode: dreamer` and `tailor_target` in frontmatter.

## User handoff

End with:

- **Verified** (safe to keep as-is)
- **Aspirational** (must edit or delete before applying)
- **Suggested questions** to convert aspirational → verified (3–5)

Never render a dreamer PDF for the user unless they explicitly want a gap-analysis PDF (`cvfmt render --allow-aspirational`).
---
name: cv-tailor
description: Tailors an existing cv-md/1.1 master CV to a specific role or job description in strict mode (verified facts only) or dreamer mode (aspirational benchmarks clearly marked). Preserves ## Facts for lossless re-tailoring. Use when the user has cv-master.md plus a JD, or asks to tailor, target a vacancy, or dreamer mode.
license: MIT
metadata:
  version: "1.0"
  schema: "cv-md/1.1"
  parent_skill: cv-formatter
---

# CV Tailor (`cv-md/1.1`)

Tailor a **master** or existing `cv-md/1.1` file to a **target role or job description** without losing candidate data. Always carry **`## Facts`** forward.

## References (load as needed)

- [references/tailoring-playbook.md](./references/tailoring-playbook.md) — strict JD alignment workflow
- [references/dreamer-playbook.md](./references/dreamer-playbook.md) — autonomous gap-fill + labeling
- [references/strict-vs-dreamer.md](./references/strict-vs-dreamer.md) — mode selection
- Schema & writing rules: [../cv-formatter/references/schema-v1.md](../cv-formatter/references/schema-v1.md), [../cv-formatter/references/writing-and-humanization.md](../cv-formatter/references/writing-and-humanization.md)
- EU/ATS: [../cv-formatter/references/eu-and-ats-rules.md](../cv-formatter/references/eu-and-ats-rules.md)

## Mode selection

| User cue | Mode |
| :--- | :--- |
| "Tailor for this role", "match this JD", strict, verified only, ready to apply | **Strict** |
| "Dreamer mode", "imagine the strongest CV", gap analysis, benchmark draft | **Dreamer** |

Set YAML when saving:

- Strict: `tailor_mode: strict` and `tailor_target: "<Role @ Company or slug>"`
- Dreamer: `tailor_mode: dreamer` (same `tailor_target`)

## Strict workflow (summary)

1. Read master CV + full JD; inventory facts including `## Facts`.
2. Rewrite **Summary** and **headline** using JD vocabulary **only** where supported by existing evidence.
3. Reorder and emphasize **Experience** / **Projects** bullets; demote low-signal items into `## Facts` under `### Archived for <tailor_target>`.
4. Align **Skills** with JD keywords when evidence exists in Experience/Projects (or Facts you promote truthfully).
5. Output `cv-<slug>.md`; suggest `cvfmt validate` and `cvfmt render --verify`.

Optional local CLI for mechanical reorder/trim (no summary LLM):  
`cvfmt tailor jd.txt --base cv-master.md -o cv-target.md --mode strict --target-title "..."`

## Dreamer workflow (summary)

1. Same inputs; infer seniority and must-have JD themes.
2. Run a **silent** extended interview (do not ask the user 20 questions): list top gaps (metrics, scope, tools).
3. Fill gaps with **plausible** content prefixed with `**(Aspirational)**` on renderable bullets.
4. Store rationales in `## Facts` → `### Dreamer rationale`.
5. Chat reply: table of **Verified vs aspirational** items the user must confirm before applying.

Dreamer prep bundle (no LLM in CLI):  
`cvfmt tailor jd.txt --base cv-master.md --mode dreamer --prepare ./bundle/`

## Guardrails

Same as cv-formatter: zero hidden keywords, zero AI slop, no unmarked invention in strict mode. Dreamer aspirational lines must keep the `**(Aspirational)**` prefix in renderable sections.
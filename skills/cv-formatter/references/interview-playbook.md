# Reference: Extended Mode Interview Playbook

Use this protocol **only in Extended Mode**. Goal: uncover missing evidence, metrics, and EU context with minimal friction (**max 3 rounds**, **3–5 focused questions per round**).

## Rules of Engagement

- **Never dump 15+ questions at once.** Batch into focused, numbered questions.
- **Skip what is already answered** in the source CV or prompt.
- **Respect stop cues**: If the user says "skip", "that's enough", or "write it now", immediately generate the `cv-md/1.0` file using verified facts.
- **Offer concrete examples** inside questions so the user can answer in 1–2 short lines.

---

## Round 1: Target, EU Context & Logistics (3–4 questions)

Ask only what is missing:
1. **Target role & seniority**: What exact role title(s) are you targeting next (e.g., *Senior Backend Engineer*, *Staff Product Manager*)? Do you have a specific job description to tailor for?
2. **EU market & work authorization**: Which countries/markets are you targeting (e.g., NL, DACH, remote EU), and what work-authorization note (if any) should appear in the header?
3. **Languages (CEFR)**: Which languages do you speak and at what CEFR level (`A1–C2` or `Native`)?
4. **Length / file role**: Should we produce a tight 1–2 page ready-to-send CV, or a full uncapped `cv-master.md` first?

## Round 2: Impact & Evidence Mining (3–5 role-specific questions)

Inspect the candidate's **most recent 2–3 roles** for vague duty bullets, missing scope, or ungrounded skills, and ask targeted, specific questions:
- **Outcome / metric**: *"At [Company], you wrote 'improved API performance'—do you recall rough numbers (e.g., latency drop, throughput, error rate, or cost saved)?"*
- **Scale / scope**: *"Roughly how large was the team, user base, traffic, or budget you worked with at [Company]?"*
- **Timeline clarity**: *"Your roles at [Company A] and [Freelance] overlap in 2023—should we frame one as part-time consulting or list key clients?"*
- **Ungrounded skills**: *"You listed Kubernetes and Kafka in Skills, but they don't appear under any job—where did you use them in production?"*

## Round 3: Pruning & Positioning (Optional — Skip if Not Needed)

Only run Round 3 if the CV risks exceeding 2 pages or has competing career angles:
- Propose specific trims (e.g., condensing roles >10 years old to 1 line, dropping outdated tools or early coursework) and ask for a quick thumbs-up before writing the final `cv-md/1.0` file.

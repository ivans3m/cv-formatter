# Research 02: AI / LLM Screening & Recruiter Copilots

## Executive Summary

Recruiting teams increasingly pair traditional ATS databases with **LLM-based screening, summarization, and structured extraction pipelines**—either built into modern ATS tools (like Ashby's criteria matching) or via recruiter copilots where raw CV text is evaluated against a job description and rubric.

In Europe, this sits directly under the **EU AI Act (Regulation (EU) 2024/1689)** and **GDPR Article 22**, which classify recruitment and CV screening AI as **High-Risk** and mandate human oversight, transparency, and evidence-based evaluation. For CV design, this creates a clear mandate: **make factual evidence effortless to extract, unambiguously scoped, and completely free of manipulation or AI-generated fluff.**

---

## 1. How LLM Screening Pipelines Actually Process a CV

Most production AI screening workflows follow a three-stage pipeline:

1. **Document-to-Text Extraction**: The uploaded PDF/DOCX is run through a parser (`pypdf`, `pdfplumber`, `Docling`, or OCR) to produce plain text or Markdown.
   - *Implication*: If the PDF's text layer is clean and linear, the LLM sees a near-identical representation of our source Markdown. If the PDF has broken columns or tables, the LLM hallucinates or misattributes roles.
2. **Unstructured-to-Structured Extraction**: The text is passed to an LLM with a strict output schema (Pydantic / JSON Schema / function calling) to extract:
   - Candidate identity, location, work authorization, languages.
   - Chronological employment entries (`company`, `title`, `start_date`, `end_date`, `location`, `achievements`, `technologies`).
   - Total years of experience and domain-specific years (e.g., years of Python or people management).
3. **Rubric-Based Evidence Evaluation**: The model evaluates the structured profile against the job description's required and preferred criteria, outputting a tier/score **plus direct verbatim quotes/evidence** from the CV for human review.

---

## 2. What Causes LLMs to Misread or Under-Rank Good Candidates

- **Ambiguous Entity Binding**: When dates, job titles, and companies are visually separated (e.g., dates in a left column, titles on the right), text extraction detaches them. LLMs frequently assign achievements from Job B to Job A or miscalculate tenure.
- **Unscoped Skills Dumps**: Listing 40 technologies in a flat "Skills" section without connecting them to actual roles makes rubric-based LLMs lower confidence (*"Candidate lists Kubernetes in skills, but no work experience mentions using it"*).
- **Vague Responsibility Prose**: Bullets like *"Worked on backend services and helped improve performance"* give a rubric evaluator zero verifiable evidence. Concrete bullets (*"Reduced p95 API latency from 420ms to 110ms across 12 Go microservices serving 40K req/s"*) map directly to seniority rubrics.
- **Promotions / Multiple Roles at One Company**: If internal promotions aren't clearly nested or dated, LLMs either double-count total years of experience or collapse the entire tenure under the oldest/newest title.
- **Overlapping Freelance / Consulting Roles**: Without explicit labeling (e.g., `Freelance` / `Contract` / `Client: X`), overlapping date ranges look like parsing errors or inflated tenure.

---

## 3. Empirical Research Findings (Bias, Self-Preference & Prompt Injection)

Recent peer-reviewed and preprint research highlights three critical phenomena:

1. **AI Self-Preference Bias** (*Xu, Li, & Jiang*, [arXiv:2509.00462](https://arxiv.org/abs/2509.00462)):
   - LLM-based screeners show measurable preference for resumes generated or heavily rewritten by the *same* model family over human-written text.
   - **Design takeaway**: Rather than gaming a specific model's stylistic tics (which backfires with humans and competing models), the winning strategy is **high factual density, crisp structure, and concrete evidence**—which scores well across *all* rubric-grounded models and humans.
2. **Prompt Injection in Resumes** (*Baxi et al.*, [arXiv:2606.27287](https://arxiv.org/abs/2606.27287); *Zhang et al.*, [arXiv:2605.28999](https://arxiv.org/abs/2605.28999)):
   - A large-scale USENIX Security measurement of ~200K real resumes found roughly **1% contain hidden prompt injections** (e.g., white-on-white or 1pt text telling an AI to rank the candidate first).
   - Modern screening pipelines now actively run **text-vs-visual discrepancy checks** (comparing PDF text layers against rendered page images via Vision-Language Models) to flag and disqualify hidden text.
   - **Design takeaway**: **Zero hidden text, zero invisible keywords, zero meta-instructions to AI.** What the human sees on the page must be 100% identical to the underlying text layer.
3. **Human-in-the-Loop & EU Regulatory Reality**:
   - Under **EU AI Act (Regulation (EU) 2024/1689), Annex III, Point 4(a)** ([EUR-Lex](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)), AI systems for recruitment, CV filtering, and candidate evaluation are classified as **High-Risk AI** (transparency obligations active August 2026; full high-risk deployer obligations including human oversight and Fundamental Rights Impact Assessments enforceable December 2027).
   - Combined with **GDPR Article 22** (restrictions on solely automated decisions), European hiring pipelines are legally pushed toward **evidence-surfacing copilots with human review**, not black-box auto-rejectors.

---

## 4. Actionable Design Constraints for CV Formatter

| Constraint | Applies To | Requirement |
| :--- | :--- | :--- |
| **Strict visual-text parity** | PDF Renderer & Skill | Never embed hidden text, invisible keywords, or AI-directed comments. Text layer === visible text. |
| **Explicit role-to-date-to-company binding** | Schema & PDF | Every experience entry keeps `Role`, `Company`, `Location`, and `Date Range` tightly grouped in a predictable pattern directly above its bullets. |
| **Skills grounded in experience** | Skill (Silent & Extended) | Every key skill in the Skills section should ideally have traceable evidence in at least one Experience or Project bullet. |
| **Evidence-first bullets** | Skill (Extended Mode) | Prompt the candidate for concrete scope (team size, traffic, budget, latency, revenue, users) so rubric-based AI screeners can cite verifiable evidence. |
| **Clean promotion & consulting syntax** | Schema | Support clear representation of multiple roles at one company and freelance/client engagements without corrupting tenure math. |
| **Markdown-native fidelity** | Schema | Since LLMs natively excel at Markdown headings (`#`, `##`, `###`), lists (`-`), and explicit labels, the `.md` file itself is already an ideal LLM-ingestible artifact (e.g., for direct upload or agent workflows). |

---

## References

- Xu, J., Li, G., & Jiang, J. Y. (2025). *AI Self-preferencing in Algorithmic Hiring: Empirical Evidence and Insights*. [arXiv:2509.00462](https://arxiv.org/abs/2509.00462)
- Zhang, M., Jia, Y., Tan, Z., Jiang, S., Gong, N. Z., Chen, T., & Song, D. (2026). *Measuring Real-World Prompt Injection Attacks in LLM-based Resume Screening* (USENIX Security). [arXiv:2605.28999](https://arxiv.org/abs/2605.28999)
- Baxi, P., Xu, J., Jiang, J. Y., & Jasin, S. (2026). *Prompt Injection in Automated Résumé Screening with Large Language Models: Single and Multi-Injection Settings* (ACL). [arXiv:2606.27287](https://arxiv.org/abs/2606.27287)
- European Union. *Regulation (EU) 2024/1689 (EU Artificial Intelligence Act)*. [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)

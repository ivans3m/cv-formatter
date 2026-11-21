# Research Plan: Human- & LLM-Readable CV Format and Tooling

## Objective

Before writing any code or locking in a Markdown schema, this research phase establishes evidence-based best practices across every layer of the system: how recruiters, ATS software, and LLMs actually read CVs; what makes a Markdown schema both pleasant to edit and unambiguous to parse; how an interactive rewriting skill should behave; and which PDF generation pipeline produces clean typography without breaking text extraction.

---

## Research Areas

### 1. ATS & Automated HR Parsing Systems
*Goal: Understand what modern and legacy HR pipelines actually extract from CVs, and what silently breaks them.*

- **Key systems to study**: Workday, Greenhouse, Lever, Ashby, iCIMS, Taleo, BambooHR, and common resume parsing APIs (e.g., Sovren/Textkernel, Affinda, RChilli).
- **Questions to answer**:
  - How do ATS parsers extract text from PDFs (reading order, multi-column failures, tables, text boxes, headers/footers, custom icon fonts, ligatures)?
  - Which section headings are universally recognized vs. misclassified?
  - How are dates, job titles, companies, locations, and overlapping/freelance roles parsed?
  - Keyword matching vs. semantic/vector matching: what actually matters today?
- **Deliverable**: `research/01-ats-parsing.md`

### 2. AI / LLM Screening & Recruiter Copilots
*Goal: Understand how LLM-based screening, summarization, and matching pipelines consume CVs (both Markdown and PDF text).*

- **Questions to answer**:
  - What structural patterns maximize factual extraction accuracy by LLMs (roles, timelines, scope, tech stack, metrics, domain expertise)?
  - What causes LLMs to misattribute achievements, conflate adjacent jobs, or miss skills?
  - How do Markdown structure, explicit key-value metadata, and semantic headings affect LLM comprehension vs. raw PDF-extracted text?
  - Prompt-injection and formatting hygiene: what patterns trigger false-positive spam/manipulation flags in AI screeners?
- **Deliverable**: `research/02-llm-screening.md`

### 3. Human CV Best Practices & Recruiter UX
*Goal: Synthesize proven human-readability and content principles so the output is genuinely strong, not just machine-friendly.*

- **Questions to answer**:
  - Visual hierarchy and the 6–10 second initial recruiter scan (F-pattern, scannability, whitespace, typographic contrast).
  - Content frameworks: XYZ (Google), CAR/STAR, quantifying impact without fabricating numbers, action verbs, avoiding AI clichés and hollow buzzwords.
  - Regional & role variations: 1-page vs. 2-page norms, US vs. EU/UK conventions (photo, location, work authorization, languages), IC vs. leadership vs. consulting/freelance timelines.
  - Skills sections: grouped/categorized skills vs. flat keyword dumps; avoiding meaningless self-rated progress bars.
- **Deliverable**: `research/03-human-cv-best-practices.md`

### 4. Standardized Markdown CV Data Structure
*Goal: Design a canonical `.md` format that is readable as plain text, deterministic to parse, and rich enough for clean PDF rendering.*

- **Prior art to benchmark**:
  - [JSON Resume](https://jsonresume.org/)
  - [RenderCV](https://rendercv.com/)
  - [Reactive Resume](https://rxresu.me/)
  - [Europass](https://europass.europa.eu/)
  - Plain Markdown CV templates (e.g., Pandoc/WeasyPrint/Typst-based repos).
- **Questions to answer**:
  - Should metadata live in YAML frontmatter + structured Markdown body, or pure Markdown?
  - What is the minimal required schema vs. optional sections (Summary, Experience, Projects, Education, Skills, Certifications, Languages, Publications, Volunteering)?
  - How should entries with multiple roles at the same company, consulting clients, or date ranges ("Present", career breaks) be represented?
  - How strict should validation/linting be so both humans and LLMs can author valid files reliably?
- **Deliverable**: `research/04-markdown-schema-design.md`

### 5. Agent Skill Architecture (Silent vs. Extended Mode)
*Goal: Define how the CV-rewriting skill ingests messy inputs and produces high-signal, truthful CVs.*

- **Questions to answer**:
  - Supported input formats (PDF, DOCX, plain text, Markdown, LinkedIn export, unstructured notes) and ingestion pitfalls.
  - **Silent mode**: Rules for faithful restructuring, de-jargoning, anti-hallucination guardrails (never inventing metrics or tools), and marking missing/ambiguous data (`[TODO]` or structured notes).
  - **Extended mode**: Designing a focused, low-friction interview flow (batched follow-up questions prioritized by impact: target role, missing metrics, scope/team size, clarifying vague bullets, tailoring emphasis).
  - Tone & humanization rules: eliminating generic LLM prose while preserving the candidate's authentic voice.
- **Deliverable**: `research/05-skill-design.md`

### 6. Markdown-to-PDF Pipeline & Minimalist Typography
*Goal: Select the simplest, cleanest rendering engine that guarantees both modern aesthetics and flawless text extraction.*

- **Candidates to evaluate**:
  - **Typst** (fast, single binary, modern typography, clean PDF output, native tagging support).
  - **HTML/CSS → Headless Chromium / Playwright** (familiar CSS print layout, easy styling, needs verification on text layer & file size).
  - **WeasyPrint** (Python, CSS Paged Media, clean PDFs, system library dependencies to consider).
  - **Pandoc + LaTeX** (mature, heavy toolchain).
- **Questions to answer**:
  - How does each tool's PDF behave under `pdftotext`, `pdfplumber`, `pypdf`, and copy-paste?
  - Does it support Tagged PDF / logical reading order, embedded Unicode fonts, clickable links, and clean page breaks (no orphaned headings or split bullets)?
  - What typographic defaults (font pairing, margins, line height, hierarchy, monochrome/subtle accent palette, A4 vs. US Letter) achieve a timeless, modern minimalist look?
- **Deliverable**: `research/06-pdf-rendering-and-design.md`

### 7. Verification & Quality Benchmarks
*Goal: Define how we will objectively test both the skill and the PDF output before calling v1 done.*

- **Questions to answer**:
  - Automated PDF text-extraction round-trip checks (Markdown → PDF → `pdftotext` → compare semantic fidelity).
  - LLM extraction test: feed the generated PDF text to an LLM and verify 100% accuracy on roles, dates, companies, skills, and metrics.
  - Visual review rubric across edge cases (1-page junior CV, 2-page senior/executive CV, multi-role company progression, non-ASCII names/diacritics, long URLs).
- **Deliverable**: `research/07-evaluation-framework.md`

---

## Suggested Execution Order

1. **Foundations (Parallel)**: Areas 1 (ATS), 2 (LLM Screening), and 3 (Human Best Practices) — these define the *requirements* for what a great CV must contain and avoid.
2. **Format & Design (Parallel)**: Areas 4 (Markdown Schema) and 6 (PDF Rendering & Typography) — grounded directly in the constraints found in step 1.
3. **Workflow & Verification (Parallel)**: Areas 5 (Skill Design) and 7 (Evaluation Framework) — tying the schema, writing rules, and testing together.
4. **Synthesis**: Consolidate findings into formal specs in `docs/` before starting any implementation.

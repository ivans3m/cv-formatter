"""Schema validator and ATS/LLM linter for cv-md/1.0 documents."""

from __future__ import annotations

import re

from cvfmt.models import (
    CANONICAL_SECTIONS,
    CANONICAL_SECTIONS_LOWER,
    CVDocument,
    NON_RENDERED_SECTIONS,
    SUPPORTED_SCHEMAS,
    ValidationIssue,
    ValidationResult,
)


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_HEX_COLOR_RE = re.compile(r"^#?[0-9a-fA-F]{6}$")
_DATE_TOKEN_RE = re.compile(r"^(\d{4}(-\d{2})?|Present)$")
_TODO_RE = re.compile(r"\[TODO(?::[^\]]*)?\]", re.IGNORECASE)
_SKILL_BULLET_RE = re.compile(r"^\*\*([^:*]+):?\*\*:?\s*(.+)$")
_CEFR_TOKEN_RE = re.compile(r"\b(A1|A2|B1|B2|C1|C2|Native)\b", re.IGNORECASE)


def _validate_date_range(date_range: str) -> bool:
    """Validate 'YYYY-MM – Present', 'YYYY – YYYY', or single 'YYYY-MM'/'YYYY'."""
    if " – " in date_range:
        parts = [p.strip() for p in date_range.split(" – ")]
    elif " — " in date_range:
        parts = [p.strip() for p in date_range.split(" — ")]
    elif " - " in date_range:
        parts = [p.strip() for p in date_range.split(" - ")]
    else:
        parts = [date_range.strip()]

    if len(parts) not in (1, 2):
        return False

    for token in parts:
        if not _DATE_TOKEN_RE.match(token):
            return False
        if "-" in token:
            month = int(token.split("-")[1])
            if not (1 <= month <= 12):
                return False
    return True


def _extract_skill_items(doc: CVDocument) -> list[str]:
    skills: list[str] = []
    for section in doc.sections:
        if section.title.lower() == "skills":
            for bullet in section.bullets:
                m = _SKILL_BULLET_RE.match(bullet)
                rhs = m.group(2) if m else bullet
                for item in rhs.split(","):
                    cleaned = re.sub(r"\([^)]*\)", "", item).strip()
                    if cleaned:
                        skills.append(cleaned)
    return skills


def _experience_and_projects_text(doc: CVDocument) -> str:
    chunks: list[str] = []
    for section in doc.sections:
        if section.title.lower() in ("experience", "projects"):
            chunks.extend(section.paragraphs)
            chunks.extend(section.bullets)
            for entry in section.entries:
                chunks.append(entry.heading)
                chunks.extend(entry.paragraphs)
                chunks.extend(entry.bullets)
                for sr in entry.sub_roles:
                    chunks.append(sr.title)
                    chunks.extend(sr.bullets)
    return "\n".join(chunks).lower()


def validate_cv(doc: CVDocument, *, allow_todos: bool = False) -> ValidationResult:
    """Validate a parsed CVDocument against cv-md/1.1 (and cv-md/1.0) rules."""
    result = ValidationResult()
    fm = doc.frontmatter

    # 1. Frontmatter hard errors
    if fm.schema_version not in SUPPORTED_SCHEMAS:
        supported = ", ".join(repr(s) for s in SUPPORTED_SCHEMAS)
        result.issues.append(
            ValidationIssue(
                severity="error",
                code="SCHEMA_VERSION",
                message=f"Frontmatter 'schema' must be one of {supported} (got {fm.schema_version!r}).",
                line=1,
            )
        )

    if not fm.name or not fm.name.strip():
        result.issues.append(
            ValidationIssue(
                severity="error",
                code="MISSING_NAME",
                message="Frontmatter 'name' is required.",
                line=1,
            )
        )

    email_is_todo = bool(allow_todos and fm.email and _TODO_RE.search(fm.email))
    if not email_is_todo and (not fm.email or not _EMAIL_RE.match(fm.email.strip())):
        result.issues.append(
            ValidationIssue(
                severity="error",
                code="INVALID_EMAIL",
                message=f"Frontmatter 'email' must be a valid email address (got {fm.email!r}).",
                line=1,
            )
        )

    if fm.paper not in ("a4", "letter"):
        result.issues.append(
            ValidationIssue(
                severity="error",
                code="INVALID_PAPER",
                message=f"Frontmatter 'paper' must be 'a4' or 'letter' (got {fm.paper!r}).",
                line=1,
            )
        )

    if fm.accent is not None and not _HEX_COLOR_RE.match(fm.accent.strip()):
        result.issues.append(
            ValidationIssue(
                severity="error",
                code="INVALID_ACCENT",
                message=f"Frontmatter 'accent' must be a 6-digit hex color like '#71717A' (got {fm.accent!r}).",
                line=1,
            )
        )

    # 2. Unresolved [TODO: ...] markers (skip non-rendered sections like ## Facts)
    non_rendered_ranges = [
        (s.line, s.end_line)
        for s in doc.sections
        if s.title.lower() in NON_RENDERED_SECTIONS and s.line > 0
    ]

    def _in_non_rendered(line_no: int) -> bool:
        return any(start <= line_no <= end for start, end in non_rendered_ranges)

    if not allow_todos:
        fm_str = str(doc.raw_frontmatter)
        if _TODO_RE.search(fm_str):
            result.issues.append(
                ValidationIssue(
                    severity="error",
                    code="UNRESOLVED_TODO",
                    message="Unresolved [TODO] placeholder found in frontmatter.",
                    line=1,
                )
            )
        for idx, line in enumerate(doc.raw_body.splitlines(), start=doc.body_start_line):
            if _in_non_rendered(idx):
                continue
            if _TODO_RE.search(line):
                result.issues.append(
                    ValidationIssue(
                        severity="error",
                        code="UNRESOLVED_TODO",
                        message="Unresolved [TODO] placeholder found in document body.",
                        line=idx,
                    )
                )

    # 3. Section & date checks
    section_names_lower = {s.title.lower() for s in doc.sections}
    if "experience" not in section_names_lower:
        result.issues.append(
            ValidationIssue(
                severity="error",
                code="MISSING_EXPERIENCE",
                message="Document must include an '## Experience' section.",
            )
        )

    for section in doc.sections:
        if section.title.lower() not in CANONICAL_SECTIONS_LOWER:
            result.issues.append(
                ValidationIssue(
                    severity="warning",
                    code="NON_CANONICAL_SECTION",
                    message=(
                        f"Section '## {section.title}' is non-canonical and may hurt ATS parsing. "
                        f"Recommended: {', '.join(CANONICAL_SECTIONS)}."
                    ),
                    line=section.line,
                )
            )

        if section.title.lower() in NON_RENDERED_SECTIONS:
            continue

        for entry in section.entries:
            if entry.date_range and not _validate_date_range(entry.date_range):
                result.issues.append(
                    ValidationIssue(
                        severity="error",
                        code="INVALID_DATE",
                        message=(
                            f"Invalid date range {entry.date_range!r} in '{entry.heading}'. "
                            "Expected 'YYYY-MM – YYYY-MM', 'YYYY-MM – Present', or 'YYYY'."
                        ),
                        line=entry.line,
                    )
                )
            for sr in entry.sub_roles:
                if sr.date_range and not _validate_date_range(sr.date_range):
                    result.issues.append(
                        ValidationIssue(
                            severity="error",
                            code="INVALID_DATE",
                            message=(
                                f"Invalid sub-role date range {sr.date_range!r} in '{sr.title}'."
                            ),
                            line=sr.line,
                        )
                    )

        # EU CEFR check for Languages section
        if section.title.lower() == "languages":
            for bullet in section.bullets:
                if not _CEFR_TOKEN_RE.search(bullet):
                    result.issues.append(
                        ValidationIssue(
                            severity="warning",
                            code="MISSING_CEFR_LEVEL",
                            message=(
                                f"Language entry {bullet!r} lacks a CEFR level (A1–C2 or Native)."
                            ),
                            line=section.line,
                        )
                    )

    # 4. EU Languages reminder
    if "languages" not in section_names_lower:
        result.issues.append(
            ValidationIssue(
                severity="warning",
                code="MISSING_LANGUAGES",
                message="No '## Languages' section found (recommended for EU market with CEFR levels).",
            )
        )

    # 5. LLM evidence check: skills grounded in Experience/Projects
    skills = _extract_skill_items(doc)
    if skills:
        evidence_text = _experience_and_projects_text(doc)
        ungrounded = [
            s for s in skills if not re.search(rf"(?<!\w){re.escape(s.lower())}(?!\w)", evidence_text)
        ]
        if ungrounded:
            preview = ", ".join(ungrounded[:6])
            extra = f" (+{len(ungrounded) - 6} more)" if len(ungrounded) > 6 else ""
            result.issues.append(
                ValidationIssue(
                    severity="warning",
                    code="UNGROUNDED_SKILLS",
                    message=(
                        f"Skills not explicitly mentioned in Experience/Projects: {preview}{extra}. "
                        "Rubric-based LLM screeners prefer skills backed by role evidence."
                    ),
                )
            )

    return result

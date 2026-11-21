"""Parser for cv-md/1.0 Markdown files (YAML frontmatter + canonical CommonMark)."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from cvfmt.models import CVDocument, Entry, Frontmatter, Section, SubRole


_FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)
_H2_RE = re.compile(r"^##\s+(.+?)\s*$")
_H3_RE = re.compile(r"^###\s+(.+?)\s*$")
_H4_RE = re.compile(r"^####\s+(.+?)\s*$")
_BULLET_RE = re.compile(r"^[-*]\s+(.+?)\s*$")
_ITALIC_LINE_RE = re.compile(r"^\*(.+?)\*\s*$")
_SUBROLE_DATE_RE = re.compile(r"^(.*?)\s+\*\(([^)]+)\)\*\s*$")
_TITLE_SPLIT_RE = re.compile(r"\s+[—–]\s+|\s+--\s+")


def split_frontmatter(text: str) -> tuple[dict, str, int]:
    """Split YAML frontmatter from Markdown body.

    Returns (frontmatter_dict, body_text, body_start_line).
    """
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text, 1

    raw_yaml = match.group(1)
    data = yaml.safe_load(raw_yaml) or {}
    if not isinstance(data, dict):
        raise ValueError("YAML frontmatter must be a key-value mapping.")

    body = text[match.end() :]
    body_start_line = text[: match.end()].count("\n") + 1
    return data, body, body_start_line


def _parse_entry_heading(heading: str) -> tuple[str, str | None]:
    for sep in (" — ", " -- ", " – "):
        if sep in heading:
            left, right = heading.split(sep, 1)
            return left.strip(), right.strip()
    return heading.strip(), None


def _parse_meta_line(meta: str) -> tuple[str | None, str | None]:
    """Split '*2023-04 – Present | Amsterdam, Netherlands*' into (date_range, location)."""
    if "|" in meta:
        left, right = meta.split("|", 1)
        return left.strip() or None, right.strip() or None
    return meta.strip() or None, None


def parse_cv_text(text: str, source_path: str | None = None) -> CVDocument:
    """Parse cv-md/1.0 Markdown text into a structured CVDocument."""
    raw_fm, body, body_start_line = split_frontmatter(text)
    frontmatter = Frontmatter.model_validate(raw_fm)

    sections: list[Section] = []
    current_section: Section | None = None
    current_entry: Entry | None = None
    current_subrole: SubRole | None = None
    expecting_meta = False

    paragraph_buf: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph_buf
        if not paragraph_buf:
            return
        para = " ".join(p.strip() for p in paragraph_buf if p.strip())
        paragraph_buf = []
        if not para:
            return
        if current_entry is not None and current_subrole is None:
            current_entry.paragraphs.append(para)
        elif current_section is not None:
            current_section.paragraphs.append(para)

    for offset, raw_line in enumerate(body.splitlines()):
        line_no = body_start_line + offset
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            continue

        m_h2 = _H2_RE.match(stripped)
        if m_h2:
            flush_paragraph()
            current_section = Section(title=m_h2.group(1).strip(), line=line_no)
            sections.append(current_section)
            current_entry = None
            current_subrole = None
            expecting_meta = False
            continue

        m_h3 = _H3_RE.match(stripped)
        if m_h3:
            flush_paragraph()
            if current_section is None:
                current_section = Section(title="", line=line_no)
                sections.append(current_section)
            heading_text = m_h3.group(1).strip()
            primary, secondary = _parse_entry_heading(heading_text)
            current_entry = Entry(
                heading=heading_text,
                primary=primary,
                secondary=secondary,
                line=line_no,
            )
            current_section.entries.append(current_entry)
            current_subrole = None
            expecting_meta = True
            continue

        m_h4 = _H4_RE.match(stripped)
        if m_h4:
            flush_paragraph()
            expecting_meta = False
            raw_sub = m_h4.group(1).strip()
            m_sub = _SUBROLE_DATE_RE.match(raw_sub)
            if m_sub:
                sub_title = m_sub.group(1).strip()
                sub_date = m_sub.group(2).strip()
            else:
                sub_title = raw_sub
                sub_date = None
            current_subrole = SubRole(title=sub_title, date_range=sub_date, line=line_no)
            if current_entry is not None:
                current_entry.sub_roles.append(current_subrole)
            continue

        if expecting_meta and current_entry is not None:
            m_meta = _ITALIC_LINE_RE.match(stripped)
            if m_meta:
                raw_meta = m_meta.group(1).strip()
                date_range, location = _parse_meta_line(raw_meta)
                current_entry.raw_meta = raw_meta
                current_entry.date_range = date_range
                current_entry.location = location
                expecting_meta = False
                continue
            expecting_meta = False

        m_bullet = _BULLET_RE.match(stripped)
        if m_bullet:
            flush_paragraph()
            bullet_text = m_bullet.group(1).strip()
            if current_subrole is not None:
                current_subrole.bullets.append(bullet_text)
            elif current_entry is not None:
                current_entry.bullets.append(bullet_text)
            elif current_section is not None:
                current_section.bullets.append(bullet_text)
            continue

        # Continuation line for an active bullet (indented)
        if raw_line.startswith(("  ", "\t")) and not paragraph_buf:
            target_bullets = (
                current_subrole.bullets
                if current_subrole is not None
                else current_entry.bullets
                if current_entry is not None
                else current_section.bullets
                if current_section is not None
                else None
            )
            if target_bullets:
                target_bullets[-1] = f"{target_bullets[-1]} {stripped}"
                continue

        paragraph_buf.append(stripped)

    flush_paragraph()

    return CVDocument(
        frontmatter=frontmatter,
        sections=sections,
        raw_frontmatter=raw_fm,
        raw_body=body,
        source_path=source_path,
    )


def parse_cv_file(path: str | Path) -> CVDocument:
    """Read and parse a cv-md/1.0 file from disk."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    return parse_cv_text(text, source_path=str(p))

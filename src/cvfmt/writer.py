"""Serialize a CVDocument back to cv-md/1.1 Markdown text."""

from __future__ import annotations

import yaml

from cvfmt.models import CVDocument, Entry, Section, SubRole


def _entry_meta_line(entry: Entry) -> str | None:
    if entry.raw_meta:
        return f"*{entry.raw_meta}*"
    if entry.date_range:
        loc = f" | {entry.location}" if entry.location else ""
        return f"*{entry.date_range}{loc}*"
    return None


def _subrole_heading(sr: SubRole) -> str:
    if sr.date_range:
        return f"#### {sr.title} *({sr.date_range})*"
    return f"#### {sr.title}"


def _section_to_md(section: Section) -> list[str]:
    lines: list[str] = [f"## {section.title}", ""]
    for para in section.paragraphs:
        lines.append(para)
        lines.append("")
    if section.bullets:
        for bullet in section.bullets:
            lines.append(f"- {bullet}")
        lines.append("")
    for entry in section.entries:
        lines.append(f"### {entry.heading}")
        meta = _entry_meta_line(entry)
        if meta:
            lines.append(meta)
            lines.append("")
        for para in entry.paragraphs:
            lines.append(para)
            lines.append("")
        if entry.bullets:
            for bullet in entry.bullets:
                lines.append(f"- {bullet}")
            lines.append("")
        for sr in entry.sub_roles:
            lines.append(_subrole_heading(sr))
            for bullet in sr.bullets:
                lines.append(f"- {bullet}")
            lines.append("")
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def document_to_markdown(doc: CVDocument) -> str:
    """Rebuild cv-md Markdown from a parsed document."""
    fm = doc.frontmatter
    data: dict = {
        "schema": fm.schema_version or "cv-md/1.1",
        "name": fm.name,
    }
    if fm.headline:
        data["headline"] = fm.headline
    if fm.location:
        data["location"] = fm.location
    if fm.work_authorization:
        data["work_authorization"] = fm.work_authorization
    data["email"] = fm.email
    if fm.phone:
        data["phone"] = fm.phone
    if fm.links:
        data["links"] = [{"label": link.label, "url": link.url} for link in fm.links]
    if fm.paper and fm.paper != "a4":
        data["paper"] = fm.paper
    if fm.lang and fm.lang != "en":
        data["lang"] = fm.lang
    if fm.accent:
        data["accent"] = fm.accent
    if fm.tailor_mode:
        data["tailor_mode"] = fm.tailor_mode
    if fm.tailor_target:
        data["tailor_target"] = fm.tailor_target

    yaml_body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False).strip()
    parts: list[str] = ["---", yaml_body, "---", ""]
    for idx, section in enumerate(doc.sections):
        if idx > 0:
            parts.append("")
        parts.extend(_section_to_md(section))
    text = "\n".join(parts).rstrip() + "\n"
    return text
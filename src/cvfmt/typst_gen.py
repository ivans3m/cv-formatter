"""Deterministic Typst generator for cv-md/1.0 documents."""

from __future__ import annotations

import re
from datetime import datetime

from cvfmt.models import CVDocument, Entry, Section, SubRole


_TYPST_ESCAPE_RE = re.compile(r'([\\#$@<>_*`\[\]])')
_INLINE_TOKEN_RE = re.compile(
    r'(\[([^\]]+)\]\((https?://[^)\s]+)\)|\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`)'
)
_YM_RE = re.compile(r"\b(\d{4})-(\d{2})\b")


def escape_typst(text: str) -> str:
    """Escape plain text for safe inclusion inside Typst content blocks."""
    return _TYPST_ESCAPE_RE.sub(r"\\\1", text)


def escape_typst_string(text: str) -> str:
    """Escape a string literal for Typst double-quoted strings."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def format_date_range(date_range: str) -> str:
    """Format '2023-04 – Present' into 'Apr 2023 – Present'."""

    def _repl(match: re.Match[str]) -> str:
        year = int(match.group(1))
        month = int(match.group(2))
        if 1 <= month <= 12:
            return datetime(year, month, 1).strftime("%b %Y")
        return match.group(0)

    normalized = re.sub(r"\s+[–—-]\s+", " – ", date_range.strip())
    return _YM_RE.sub(_repl, normalized)


def md_inline_to_typst(text: str) -> str:
    """Convert simple Markdown inline syntax (**bold**, *italic*, `code`, [label](url)) to Typst."""
    out: list[str] = []
    pos = 0
    for match in _INLINE_TOKEN_RE.finditer(text):
        if match.start() > pos:
            out.append(escape_typst(text[pos : match.start()]))

        if match.group(2) is not None and match.group(3) is not None:
            label = escape_typst(match.group(2))
            url = escape_typst_string(match.group(3))
            out.append(f'#link("{url}")[{label}]')
        elif match.group(4) is not None:
            out.append(f"#strong[{escape_typst(match.group(4))}]")
        elif match.group(5) is not None:
            out.append(f"#emph[{escape_typst(match.group(5))}]")
        elif match.group(6) is not None:
            out.append(f'#raw("{escape_typst_string(match.group(6))}")')

        pos = match.end()

    if pos < len(text):
        out.append(escape_typst(text[pos:]))

    return "".join(out)


def _render_bullets(bullets: list[str], *, compact: bool = False) -> list[str]:
    if not bullets:
        return []
    spacing = "3.5pt" if compact else "4pt"
    lines = [f"#list(tight: true, spacing: {spacing}, marker: [#text(fill: rgb(\"#6B7280\"))[•]],"]
    for b in bullets:
        lines.append(f"  [{md_inline_to_typst(b)}],")
    lines.append(")")
    return lines


def _render_subrole(sr: SubRole) -> list[str]:
    lines: list[str] = []
    left = f'#text(size: 9.5pt, weight: "medium", fill: rgb("#111827"))[{md_inline_to_typst(sr.title)}]'
    right = (
        f'#text(size: 8.8pt, fill: rgb("#6B7280"))[{escape_typst(format_date_range(sr.date_range))}]'
        if sr.date_range
        else ""
    )

    lines.append("#block(breakable: false, above: 7pt, below: 3pt)[")
    if right:
        lines.append("  #grid(columns: (1fr, auto), gutter: 8pt, align: (left + bottom, right + bottom),")
        lines.append(f"    [{left}], [{right}]")
        lines.append("  )")
    else:
        lines.append(f"  {left}")
    if sr.bullets:
        # Keep heading attached to at least first bullet
        lines.append("  #v(3pt)")
        lines.extend("  " + ln for ln in _render_bullets([sr.bullets[0]]))
    lines.append("]")
    if len(sr.bullets) > 1:
        lines.append("#v(1pt)")
        lines.extend(_render_bullets(sr.bullets[1:]))
    return lines


def _render_entry(entry: Entry) -> list[str]:
    lines: list[str] = []

    if entry.secondary:
        title_typst = (
            f'#text(size: 9.8pt, weight: "semibold", fill: rgb("#111827"))[{md_inline_to_typst(entry.primary)}]'
            f'#text(size: 9.8pt, fill: rgb("#6B7280"))[ — ]'
            f'#text(size: 9.8pt, weight: "medium", fill: rgb("#374151"))[{md_inline_to_typst(entry.secondary)}]'
        )
    else:
        title_typst = f'#text(size: 9.8pt, weight: "semibold", fill: rgb("#111827"))[{md_inline_to_typst(entry.primary)}]'

    date_part = format_date_range(entry.date_range) if entry.date_range else ""
    loc_part = entry.location or ""
    meta_pieces = [p for p in (date_part, loc_part) if p]
    meta_typst = (
        f'#text(size: 8.8pt, fill: rgb("#6B7280"))[{md_inline_to_typst("  |  ".join(meta_pieces))}]'
        if meta_pieces
        else ""
    )

    # Keep entry header + metadata + first bullet together to prevent orphaned job headers
    lines.append("#block(breakable: false, above: 9pt, below: 3pt)[")
    if meta_typst:
        lines.append("  #grid(columns: (1fr, auto), gutter: 10pt, align: (left + bottom, right + bottom),")
        lines.append(f"    [{title_typst}], [{meta_typst}]")
        lines.append("  )")
    else:
        lines.append(f"  {title_typst}")

    for p in entry.paragraphs:
        lines.append("  #v(3pt)")
        lines.append(f"  {md_inline_to_typst(p)}")

    if entry.bullets:
        lines.append("  #v(3.5pt)")
        lines.extend("  " + ln for ln in _render_bullets([entry.bullets[0]]))
    lines.append("]")

    if len(entry.bullets) > 1:
        lines.append("#v(1pt)")
        lines.extend(_render_bullets(entry.bullets[1:]))

    for sr in entry.sub_roles:
        lines.extend(_render_subrole(sr))

    return lines


def _render_section(section: Section) -> list[str]:
    lines: list[str] = []
    if section.title:
        lines.append(f"== {escape_typst(section.title)}")

    for p in section.paragraphs:
        lines.append(f"#block(above: 3pt, below: 3pt)[{md_inline_to_typst(p)}]")

    compact_bullets = section.title.lower() in ("skills", "languages", "certifications", "publications")
    if section.bullets:
        lines.append("#v(2pt)")
        lines.extend(_render_bullets(section.bullets, compact=compact_bullets))

    for entry in section.entries:
        lines.extend(_render_entry(entry))

    return lines


def generate_typst(doc: CVDocument, *, paper_override: str | None = None) -> str:
    """Generate a self-contained minimalist Typst document from a CVDocument."""
    fm = doc.frontmatter
    paper_choice = (paper_override or fm.paper or "a4").lower()
    if paper_choice == "letter":
        paper_spec = 'paper: "us-letter", margin: (top: 0.62in, bottom: 0.62in, left: 0.65in, right: 0.65in)'
    else:
        paper_spec = 'paper: "a4", margin: (top: 16mm, bottom: 16mm, left: 17mm, right: 17mm)'

    doc_title = f"{fm.name} — CV" if fm.name else "CV"
    lang = escape_typst_string(fm.lang or "en")

    # Build contact line (strictly inside main body flow, never in page header margins)
    contact_items: list[str] = []
    if fm.location:
        contact_items.append(escape_typst(fm.location))
    if fm.work_authorization:
        contact_items.append(escape_typst(fm.work_authorization))
    if fm.email:
        email_esc = escape_typst_string(fm.email)
        contact_items.append(f'#link("mailto:{email_esc}")[{escape_typst(fm.email)}]')
    if fm.phone:
        contact_items.append(escape_typst(fm.phone))
    for item in fm.links:
        contact_items.append(
            f'#link("{escape_typst_string(item.url)}")[{escape_typst(item.label)}]'
        )

    contact_sep = ' #text(fill: rgb("#9CA3AF"))[ · ] '
    contact_line = contact_sep.join(contact_items)

    lines: list[str] = [
        f'#set document(title: "{escape_typst_string(doc_title)}", author: "{escape_typst_string(fm.name)}")',
        f"#set page({paper_spec}, footer: context {{",
        "  if counter(page).final().first() > 1 {",
        '    align(right, text(size: 8pt, fill: rgb("#9CA3AF"))[Page #counter(page).display("1 of 1", both: true)])',
        "  }",
        "})",
        f'#set text(font: "IBM Plex Sans", size: 9.5pt, fill: rgb("#1F2937"), lang: "{lang}", ligatures: false)',
        "#set par(leading: 0.62em, justify: false)",
        '#show link: set text(fill: rgb("#1E3A5F"))',
        "#set heading(outlined: false)",
        "#show heading.where(level: 1): it => block(above: 0pt, below: 5pt)[",
        '  #text(size: 19.5pt, weight: "bold", fill: rgb("#111827"))[#it.body]',
        "]",
        "#show heading.where(level: 2): it => block(sticky: true, above: 13pt, below: 5pt)[",
        "  #stack(dir: ttb, spacing: 3.5pt,",
        '    text(size: 10.5pt, weight: "semibold", fill: rgb("#111827"))[#it.body],',
        '    line(length: 100%, stroke: 0.5pt + rgb("#E5E7EB")),',
        "  )",
        "]",
        "",
        f"= {escape_typst(fm.name)}",
    ]

    if fm.headline:
        lines.append(
            f'#block(above: 0pt, below: 5pt)[#text(size: 10.5pt, weight: "medium", fill: rgb("#374151"))[{escape_typst(fm.headline)}]]'
        )

    if contact_line:
        lines.append(
            f'#block(above: 0pt, below: 7pt)[#text(size: 8.8pt, fill: rgb("#4B5563"))[{contact_line}]]'
        )
        lines.append('#line(length: 100%, stroke: 0.6pt + rgb("#D1D5DB"))')
        lines.append("#v(2pt)")

    for section in doc.sections:
        lines.append("")
        lines.extend(_render_section(section))

    lines.append("")
    return "\n".join(lines)

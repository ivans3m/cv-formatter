"""Deterministic Warm Editorial Typst generator for cv-md/1.0 documents."""

from __future__ import annotations

import re
from datetime import datetime

from cvfmt.models import CVDocument, Entry, Section, SubRole, is_aspirational_bullet


DEFAULT_ACCENT = "#71717A"  # Refined light-medium neutral grey (Zinc 500)

_TYPST_ESCAPE_RE = re.compile(r'([\\#$@<>_*`\[\]])')
_INLINE_TOKEN_RE = re.compile(
    r'(\[([^\]]+)\]\((https?://[^)\s]+)\)|\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`)'
)
_YM_RE = re.compile(r"\b(\d{4})-(\d{2})\b")
_HEX_RE = re.compile(r"^#?([0-9a-fA-F]{6})$")


def normalize_hex_color(value: str | None) -> str:
    """Validate and normalize a 6-digit hex color to '#RRGGBB'."""
    if not value:
        return DEFAULT_ACCENT
    m = _HEX_RE.match(value.strip())
    if not m:
        raise ValueError(f"Invalid hex color {value!r}. Expected 6-digit hex like '#0F766E' or '71717A'.")
    return f"#{m.group(1).upper()}"


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


def _pdf_bullets(bullets: list[str], *, include_aspirational: bool) -> list[str]:
    if include_aspirational:
        return bullets
    return [b for b in bullets if not is_aspirational_bullet(b)]


def _render_bullets(
    bullets: list[str],
    *,
    compact: bool = False,
    include_aspirational: bool = False,
) -> list[str]:
    bullets = _pdf_bullets(bullets, include_aspirational=include_aspirational)
    if not bullets:
        return []
    # Inter-bullet spacing must always be larger than intra-bullet par(leading: 0.56em ≈ 5.2pt)
    spacing = "6.5pt" if compact else "7.5pt"
    lines = [
        f'#list(tight: false, spacing: {spacing}, body-indent: 0.65em, marker: [#text(fill: rgb("#A1A1AA"))[–]],'
    ]
    for b in bullets:
        lines.append(f"  [{md_inline_to_typst(b)}],")
    lines.append(")")
    return lines


def _render_subrole(sr: SubRole, *, include_aspirational: bool = False) -> list[str]:
    lines: list[str] = []
    left = f'#text(size: 9.4pt, weight: "medium", fill: rgb("#18181B"))[{md_inline_to_typst(sr.title)}]'
    right = (
        f'#text(size: 8.5pt, fill: rgb("#71717A"))[{escape_typst(format_date_range(sr.date_range))}]'
        if sr.date_range
        else ""
    )

    lines.append("#block(sticky: true, breakable: false, above: 8pt, below: 5pt)[")
    if right:
        lines.append("  #grid(columns: (1fr, auto), gutter: 8pt, align: (left + bottom, right + bottom),")
        lines.append(f"    [{left}], [{right}]")
        lines.append("  )")
    else:
        lines.append(f"  {left}")
    lines.append("]")
    if sr.bullets:
        lines.extend(_render_bullets(sr.bullets, include_aspirational=include_aspirational))
    return lines


def _render_entry(entry: Entry, *, include_aspirational: bool = False) -> list[str]:
    lines: list[str] = []

    if entry.secondary:
        title_typst = (
            f'#text(size: 9.8pt, weight: "semibold", fill: rgb("#18181B"))[{md_inline_to_typst(entry.primary)}]'
            f'#text(size: 9.5pt, fill: rgb("#71717A"))[  ·  {md_inline_to_typst(entry.secondary)}]'
        )
    else:
        title_typst = f'#text(size: 9.8pt, weight: "semibold", fill: rgb("#18181B"))[{md_inline_to_typst(entry.primary)}]'

    date_part = format_date_range(entry.date_range) if entry.date_range else ""
    loc_part = entry.location or ""
    meta_pieces = [p for p in (date_part, loc_part) if p]
    meta_typst = (
        f'#text(size: 8.5pt, fill: rgb("#71717A"))[{md_inline_to_typst("  |  ".join(meta_pieces))}]'
        if meta_pieces
        else ""
    )

    # sticky: true keeps header attached to the list below without splitting bullet 1 from bullets 2..N
    lines.append("#block(sticky: true, breakable: false, above: 11pt, below: 5pt)[")
    if meta_typst:
        lines.append("  #grid(columns: (1fr, auto), gutter: 10pt, align: (left + bottom, right + bottom),")
        lines.append(f"    [{title_typst}], [{meta_typst}]")
        lines.append("  )")
    else:
        lines.append(f"  {title_typst}")

    for p in entry.paragraphs:
        lines.append("  #v(4pt)")
        lines.append(f"  {md_inline_to_typst(p)}")
    lines.append("]")

    if entry.bullets:
        lines.extend(_render_bullets(entry.bullets, include_aspirational=include_aspirational))

    for sr in entry.sub_roles:
        lines.extend(_render_subrole(sr, include_aspirational=include_aspirational))

    return lines


def _render_section(section: Section, *, accent: str, include_aspirational: bool = False) -> list[str]:
    lines: list[str] = []
    compact_bullets = section.title.lower() in ("skills", "languages", "certifications", "publications")
    keep_together = (
        compact_bullets
        and not section.entries
        and not section.paragraphs
        and 0 < len(section.bullets) <= 5
    )

    if keep_together:
        lines.append("#block(breakable: false, above: 0pt, below: 0pt)[")
        if section.title:
            lines.append(f"  == {escape_typst(section.title)}")
        lines.append("  #v(2pt)")
        lines.extend(
            "  " + ln
            for ln in _render_bullets(
                section.bullets, compact=True, include_aspirational=include_aspirational
            )
        )
        lines.append("]")
        return lines

    if section.title:
        lines.append(f"== {escape_typst(section.title)}")

    is_summary = section.title.lower() == "summary"
    for p in section.paragraphs:
        if is_summary:
            lines.append(
                f'#block(width: 100%, fill: rgb("#FAFAF9"), stroke: (left: 2pt + rgb("{accent}")), '
                f'inset: (left: 10pt, right: 8pt, y: 7pt), above: 2pt, below: 4pt)'
                f'[#text(fill: rgb("#27272A"))[{md_inline_to_typst(p)}]]'
            )
        else:
            lines.append(f"#block(above: 2pt, below: 4pt)[{md_inline_to_typst(p)}]")

    if section.bullets:
        lines.append("#v(2pt)")
        lines.extend(
            _render_bullets(
                section.bullets,
                compact=compact_bullets,
                include_aspirational=include_aspirational,
            )
        )

    for entry in section.entries:
        lines.extend(_render_entry(entry, include_aspirational=include_aspirational))

    return lines


def generate_typst(
    doc: CVDocument,
    *,
    paper_override: str | None = None,
    accent_override: str | None = None,
    include_aspirational: bool = False,
) -> str:
    """Generate a self-contained Warm Editorial Typst document from a CVDocument."""
    fm = doc.frontmatter
    paper_choice = (paper_override or fm.paper or "a4").lower()
    if paper_choice == "letter":
        paper_spec = 'paper: "us-letter", margin: (top: 0.66in, bottom: 0.62in, left: 0.70in, right: 0.70in)'
    else:
        paper_spec = 'paper: "a4", margin: (top: 17mm, bottom: 16mm, left: 18mm, right: 18mm)'

    accent = normalize_hex_color(accent_override or fm.accent)
    doc_title = f"{fm.name} — CV" if fm.name else "CV"
    lang = escape_typst_string(fm.lang or "en")

    # Contact line stays strictly inside main body flow (never in page header margins)
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

    contact_sep = ' #text(fill: rgb("#D4D4D8"))[ · ] '
    contact_line = contact_sep.join(contact_items)

    lines: list[str] = [
        f'#set document(title: "{escape_typst_string(doc_title)}", author: "{escape_typst_string(fm.name)}")',
        f"#set page({paper_spec}, footer: context {{",
        "  if counter(page).final().first() > 1 {",
        '    align(right, text(size: 8pt, fill: rgb("#A1A1AA"))[Page #counter(page).display("1 of 1", both: true)])',
        "  }",
        "})",
        f'#set text(font: "IBM Plex Sans", size: 9.3pt, fill: rgb("#27272A"), lang: "{lang}", ligatures: false)',
        "#set par(leading: 0.56em, spacing: 0.65em, justify: false)",
        f'#show link: set text(fill: rgb("{accent}"))',
        "#set heading(outlined: false)",
        "#show heading.where(level: 1): it => block(above: 0pt, below: 3pt)[",
        '  #text(size: 24pt, weight: "semibold", fill: rgb("#18181B"), tracking: -0.02em)[#it.body]',
        "]",
        "#show heading.where(level: 2): it => block(sticky: true, above: 15pt, below: 6pt)[",
        "  #grid(columns: (auto, 1fr), gutter: 10pt, align: horizon,",
        f'    text(size: 10pt, weight: "semibold", fill: rgb("{accent}"))[#it.body],',
        '    line(length: 100%, stroke: 0.5pt + rgb("#E4E4E7")),',
        "  )",
        "]",
        "",
        f"= {escape_typst(fm.name)}",
    ]

    if fm.headline:
        lines.append(
            f'#block(above: 0pt, below: 5pt)[#text(size: 10.5pt, weight: "regular", fill: rgb("#71717A"))[{escape_typst(fm.headline)}]]'
        )

    if contact_line:
        lines.append(
            f'#block(above: 0pt, below: 4pt)[#text(size: 8.6pt, fill: rgb("#71717A"))[{contact_line}]]'
        )

    for section in doc.renderable_sections:
        lines.append("")
        lines.extend(
            _render_section(section, accent=accent, include_aspirational=include_aspirational)
        )

    lines.append("")
    return "\n".join(lines)

"""Round-trip parse -> write -> parse structural checks."""

from __future__ import annotations

from pathlib import Path

from cvfmt.parser import parse_cv_file, parse_cv_text
from cvfmt.writer import document_to_markdown


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def _section_signature(doc) -> list[tuple[str, list[str], list[tuple[str, str | None, str | None, str | None, list[str], list[tuple[str, str | None, list[str]]]]]]]:
    sig = []
    for section in doc.sections:
        entries_sig = [
            (
                entry.heading,
                entry.raw_meta,
                entry.date_range,
                entry.location,
                list(entry.bullets),
                [(sr.title, sr.date_range, list(sr.bullets)) for sr in entry.sub_roles],
            )
            for entry in section.entries
        ]
        sig.append((section.title.lower(), list(section.bullets), entries_sig))
    return sig


def test_writer_roundtrip_golden_fixtures() -> None:
    for name in ("junior-eu-1page.md", "senior-eu-2page.md", "consultant-multirole.md"):
        original = parse_cv_file(FIXTURES_DIR / name)
        roundtrip = parse_cv_text(document_to_markdown(original))
        assert original.frontmatter == roundtrip.frontmatter
        assert _section_signature(original) == _section_signature(roundtrip)


def test_writer_roundtrip_tailor_metadata_meta_and_facts_archive() -> None:
    md = """---
schema: cv-md/1.1
name: Alex Dev
headline: Staff Backend Engineer
location: Amsterdam, Netherlands
email: alex@example.com
tailor_mode: strict
tailor_target: Staff Backend @ Acme
---

## Experience

### Acme Payments — Platform
*2022-01 – Present | Amsterdam, Netherlands (Hybrid)*

Core payments platform team.

- Built Go settlement pipeline.

#### Tech Lead *(2023-06 – Present)*
- Led 6 engineers across 3 payment rails.

## Skills

- **Core:** Go

## Languages

- **English:** C2

## Facts

- **Preference: Notice Period** — 1 month.

### Archived for Staff Backend @ Acme
- **Experience / Earlier Role** — Maintained legacy PHP monolith.
"""
    original = parse_cv_text(md)
    roundtrip = parse_cv_text(document_to_markdown(original))

    assert roundtrip.frontmatter == original.frontmatter
    assert roundtrip.frontmatter.tailor_mode == "strict"
    assert roundtrip.frontmatter.tailor_target == "Staff Backend @ Acme"
    assert _section_signature(original) == _section_signature(roundtrip)

    exp = next(s for s in roundtrip.sections if s.title.lower() == "experience")
    assert exp.entries[0].raw_meta == "2022-01 – Present | Amsterdam, Netherlands (Hybrid)"
    assert exp.entries[0].paragraphs == ["Core payments platform team."]

    facts = roundtrip.facts_section
    assert facts is not None
    assert facts.bullets == ["**Preference: Notice Period** — 1 month."]
    assert len(facts.entries) == 1
    assert facts.entries[0].heading == "Archived for Staff Backend @ Acme"
    assert facts.entries[0].bullets == ["**Experience / Earlier Role** — Maintained legacy PHP monolith."]
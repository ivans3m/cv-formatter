"""Post-render PDF text-layer round-trip verifier for ATS and LLM readability."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber
from pypdf import PdfReader

from cvfmt.models import CVDocument, NON_RENDERED_SECTIONS, canonical_section_key


@dataclass
class VerificationReport:
    page_count: int = 0
    link_count: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    extracted_text: str = ""

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _strip_md_inline(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\(https?://[^)\s]+\)", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text


def _extract_pdf_text_and_links(pdf_path: Path) -> tuple[str, str, int, set[str]]:
    """Extract text via both pypdf and pdfplumber, plus URI link annotations."""
    reader = PdfReader(str(pdf_path))
    page_count = len(reader.pages)
    pypdf_chunks: list[str] = []
    uris: set[str] = set()

    for page in reader.pages:
        pypdf_chunks.append(page.extract_text() or "")
        annots = page.get("/Annots") or []
        for annot_ref in annots:
            annot = annot_ref.get_object()
            action = annot.get("/A")
            if action and "/URI" in action:
                uris.add(str(action["/URI"]))

    plumber_chunks: list[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            plumber_chunks.append(page.extract_text() or "")

    return "\n".join(pypdf_chunks), "\n".join(plumber_chunks), page_count, uris


def verify_pdf(doc: CVDocument, pdf_path: str | Path) -> VerificationReport:
    """Verify PDF text-layer fidelity, reading order, contact visibility, and links."""
    path = Path(pdf_path)
    pypdf_text, plumber_text, page_count, uris = _extract_pdf_text_and_links(path)

    report = VerificationReport(
        page_count=page_count,
        link_count=len(uris),
        extracted_text=plumber_text,
    )

    norm_pypdf = _normalize_ws(pypdf_text)
    norm_plumber = _normalize_ws(plumber_text)

    if not norm_plumber:
        report.errors.append("Extracted PDF text layer is empty.")
        return report

    # 1. Contact visibility in body text (proves nothing was stripped as header artifact)
    fm = doc.frontmatter
    for label, value in (
        ("name", fm.name),
        ("email", fm.email),
        ("phone", fm.phone or ""),
        ("availability", fm.availability or ""),
    ):
        if value and value not in norm_plumber:
            report.errors.append(f"Contact field '{label}' ({value!r}) missing from PDF text layer.")

    # 2. Clickable URI annotations
    expected_urls = {f"mailto:{fm.email}"} if fm.email else set()
    for link in fm.links:
        expected_urls.add(link.url)
    for url in expected_urls:
        if url not in uris:
            report.errors.append(f"Expected clickable PDF link annotation missing: {url}")

    # 3. Reading order fidelity: renderable section titles & entry headings must appear in exact order
    cursor = 0
    renderable_chunks: list[str] = [
        v for v in (fm.name, fm.headline, fm.location, fm.work_authorization, fm.availability) if v
    ]
    for section in doc.renderable_sections:
        if section.title:
            renderable_chunks.append(section.title)
            idx = norm_plumber.find(section.title, cursor)
            if idx == -1:
                report.errors.append(
                    f"Section heading '{section.title}' missing or out of reading order in PDF text."
                )
            else:
                cursor = idx + len(section.title)
        renderable_chunks.extend(_strip_md_inline(p) for p in section.paragraphs)
        renderable_chunks.extend(_strip_md_inline(b) for b in section.bullets)
        for entry in section.entries:
            plain_primary = _strip_md_inline(entry.primary)
            renderable_chunks.append(_strip_md_inline(entry.heading))
            if entry.location:
                renderable_chunks.append(_strip_md_inline(entry.location))
            renderable_chunks.extend(_strip_md_inline(p) for p in entry.paragraphs)
            renderable_chunks.extend(_strip_md_inline(b) for b in entry.bullets)
            for sr in entry.sub_roles:
                renderable_chunks.append(_strip_md_inline(sr.title))
                renderable_chunks.extend(_strip_md_inline(b) for b in sr.bullets)
            idx = norm_plumber.find(plain_primary, cursor)
            if idx == -1:
                report.errors.append(
                    f"Entry heading '{plain_primary}' missing or out of reading order in PDF text."
                )
            else:
                cursor = idx + len(plain_primary)

    renderable_text = "\n".join(renderable_chunks)
    norm_renderable = _normalize_ws(renderable_text)

    # 4. Unicode diacritics & ligature-prone words fidelity across BOTH extractors (renderable text only)
    source_words = set(re.findall(r"\b\w*(?:fi|fl|[^\x00-\x7F])\w*\b", renderable_text))
    for word in sorted(source_words):
        if len(word) < 2:
            continue
        if word not in norm_plumber:
            report.errors.append(f"Unicode/ligature word {word!r} corrupted in pdfplumber text layer.")
        if word not in norm_pypdf:
            report.errors.append(f"Unicode/ligature word {word!r} corrupted in pypdf text layer.")

    # 5. Anti-leak check: non-exported sections (e.g. '## Facts') must never appear in the rendered PDF
    non_rendered_sections = [
        s for s in doc.sections if canonical_section_key(s.title) in NON_RENDERED_SECTIONS
    ]
    for hidden_sec in non_rendered_sections:
        fact_items: list[str] = []
        fact_items.extend(hidden_sec.paragraphs)
        fact_items.extend(hidden_sec.bullets)
        for entry in hidden_sec.entries:
            fact_items.append(entry.heading)
            fact_items.extend(entry.paragraphs)
            fact_items.extend(entry.bullets)
            for sr in entry.sub_roles:
                fact_items.append(sr.title)
                fact_items.extend(sr.bullets)
        for raw_item in fact_items:
            plain_item = _normalize_ws(_strip_md_inline(raw_item))
            if len(plain_item) >= 8 and plain_item not in norm_renderable and plain_item in norm_plumber:
                report.errors.append(
                    f"Non-exported '## {hidden_sec.title}' content leaked into PDF text layer: {plain_item[:60]!r}."
                )

    # 6. Page count sanity
    if page_count > 2:
        report.warnings.append(
            f"Rendered PDF is {page_count} pages (EU best practice is 1–2 pages max)."
        )

    return report
